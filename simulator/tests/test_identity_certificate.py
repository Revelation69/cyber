"""Identity, certificate authorization and compatibility across the 1201 upgrade."""
import copy
import hashlib
import json
import sqlite3
import test_app
import unittest
from app import COOKIE_NAME, DOMAINS, BLUEPRINT, grade_exam, create_app, validate_bank


class CertificateTests(unittest.TestCase):
    setUp = test_app.ExamTests.setUp
    tearDown = test_app.ExamTests.tearDown
    start = test_app.ExamTests.start
    raw_exam = test_app.ExamTests.raw_exam
    # Reuse the isolated application helpers, not a production-only test bypass.
    def replace_snapshot(self, exam):
        token = self.client.get_cookie(COOKIE_NAME).value
        with sqlite3.connect(self.database) as connection:
            connection.execute("UPDATE exams SET payload=? WHERE token_hash=?",
                               (json.dumps(exam), hashlib.sha256(token.encode()).hexdigest()))

    def perfect_snapshot(self):
        exam = self.raw_exam()
        for q in exam["bank"]:
            if q.get("lab") == "raid":
                exam["raid"].update(q["expected"])
            else:
                exam["answers"][q["id"]] = q.get("expected", q.get("answer"))
        return exam

    def test_candidate_name_required_normalized_and_immutable(self):
        for name in ("", "   ", None, True, ["Alex"], "x" * 81, "123", "A\nB",
                     "A\u202eB", "<script>alert(1)</script>"):
            self.assertEqual(self.client.post("/api/exam", json={"candidate_name": name}).status_code, 400)
        self.assertEqual(self.client.post("/api/exam", json={}).status_code, 400)
        name = "  Jose\u0301   李 O’Connor  "
        response = self.client.post("/api/exam", json={"candidate_name": name})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["candidate_name"], "José 李 O’Connor")
        self.assertEqual(self.client.patch("/api/exam", json={"candidate_name": "Someone else"}).status_code, 400)
        self.assertEqual(self.client.post("/api/exam/submit", json={"candidate_name": "Someone else"}).status_code, 400)
        token = self.client.get_cookie(COOKIE_NAME).value
        resumed = create_app(self.config).test_client()
        resumed.set_cookie(COOKIE_NAME, token)
        self.assertEqual(resumed.get("/api/exam").get_json()["candidate_name"], "José 李 O’Connor")

    def test_certificate_denied_to_strangers_active_and_failed_attempts(self):
        self.assertEqual(self.client.get("/api/exam/certificate").status_code, 404)
        self.start()
        self.assertEqual(self.client.get("/api/exam/certificate").status_code, 403)
        failed = self.client.post("/api/exam/submit", json={}).get_json()
        self.assertIsNone(failed["report"]["certificate"])
        self.assertEqual(self.client.get("/api/exam/certificate?score=900&candidate_name=Forged").status_code, 403)

    def test_named_passing_certificate_escaped_private_and_stable(self):
        self.client.post("/api/exam", json={"candidate_name": "Renée & 李 O’Connor"})
        self.replace_snapshot(self.perfect_snapshot())
        report = self.client.post("/api/exam/submit", json={}).get_json()["report"]
        self.assertEqual(report["certificate"]["score"], 900)
        self.assertEqual(report["certificate"]["candidate_name"], "Renée & 李 O’Connor")
        response = self.client.get("/api/exam/certificate?candidate_name=Forged&score=100")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/html")
        self.assertIn("no-store", response.headers["Cache-Control"])
        html = response.get_data(as_text=True)
        self.assertIn("Renée &amp; 李 O’Connor", html)
        self.assertNotIn("Forged", html)
        self.assertIn("900 / 900", html)
        self.assertIn("NOT AN OFFICIAL COMPTIA CERTIFICATION", html)
        self.assertNotIn("220-1101", html)
        self.now += 1000
        self.assertEqual(self.client.get("/api/exam/certificate").data, response.data)
        self.assertEqual(self.app.test_client().get("/api/exam/certificate").status_code, 404)
        # Beginning another attempt cannot reuse the previous passing certificate.
        self.start()
        self.assertEqual(self.client.get("/api/exam/certificate").status_code, 403)

    def test_expired_pass_issues_certificate_from_original_deadline(self):
        started = self.start()
        self.replace_snapshot(self.perfect_snapshot())
        self.now = started["deadline"] + 10
        expired = self.client.get("/api/exam").get_json()
        self.assertEqual(expired["status"], "expired")
        self.assertEqual(expired["report"]["certificate"]["issued_at"], started["deadline"])
        self.assertEqual(self.client.get("/api/exam/certificate").status_code, 200)

    def test_retired_attempts_are_rejected_on_every_session_endpoint(self):
        for version in ("1201-2026.09-v2", "1201-2026.09-v1", None):
            for status in ("active", "submitted", "expired"):
                for method, path, body in (
                    ("GET", "/api/exam", None),
                    ("PATCH", "/api/exam", {"current_index": 12}),
                    ("POST", "/api/exam/command", {"command": "raid status"}),
                    ("POST", "/api/exam/submit", {}),
                    ("GET", "/api/exam/certificate", None),
                ):
                    with self.subTest(version=version, status=status, path=path):
                        self.start()
                        exam = self.perfect_snapshot()
                        exam["status"] = status
                        exam["report"] = grade_exam(exam, self.now, "submitted") if status != "active" else None
                        if version is None:
                            exam.pop("bank_version")
                            exam.pop("exam_code")
                        else:
                            exam["bank_version"] = version
                        self.replace_snapshot(exam)
                        response = self.client.open(path, method=method, json=body)
                        self.assertEqual(response.status_code, 409)
                        data = response.get_json()
                        self.assertEqual(data["code"], "exam_reset")
                        self.assertEqual(data["bank_version"], BLUEPRINT["bank_version"])
                        self.assertFalse({"questions", "answers", "report", "certificate"} & data.keys())
                        self.assertIn("Max-Age=0", response.headers["Set-Cookie"])
                        self.assertEqual(response.headers["Cache-Control"], "no-store")
                        self.assertIsNone(self.client.get_cookie(COOKIE_NAME))

    def test_new_attempt_has_no_retired_answers_flags_or_elapsed_time(self):
        old = self.start()
        exam = self.perfect_snapshot()
        exam["bank_version"] = "1201-2026.09-v2"
        exam["flags"] = ["pbq-1"]
        exam["current_index"] = 78
        exam["raid"].update({"diagnosed": True, "identified": True, "replaced": True, "rebuilt": True})
        self.replace_snapshot(exam)
        old_token = self.client.get_cookie(COOKIE_NAME).value
        self.now += 1800
        fresh = self.start()  # Direct POST also works without a preliminary GET reset.
        self.assertNotEqual(old["id"], fresh["id"])
        self.assertNotEqual(old_token, self.client.get_cookie(COOKIE_NAME).value)
        self.assertEqual(fresh["bank_version"], BLUEPRINT["bank_version"])
        self.assertEqual(fresh["remaining_seconds"], 5400)
        self.assertEqual(fresh["current_index"], 0)
        self.assertEqual(fresh["answers"], {})
        self.assertEqual(fresh["flags"], [])
        self.assertIsNone(fresh["report"])
        self.assertFalse(any(fresh["raid"][key] for key in ("diagnosed", "identified", "replaced", "rebuilt")))
        # Knowing an old token cannot retrieve the new exam or continue its old one.
        retired_client = self.app.test_client()
        retired_client.set_cookie(COOKIE_NAME, old_token)
        self.assertEqual(retired_client.get("/api/exam").status_code, 409)
        self.assertEqual(self.client.get("/api/exam").get_json()["id"], fresh["id"])

    def test_old_tab_cannot_write_into_new_attempt_using_shared_cookie(self):
        old = self.start()
        fresh = self.start()
        fresh_cookie = self.client.get_cookie(COOKIE_NAME).value
        cases = [
            {"X-Exam-Bank": "", "X-Exam-Id": ""},
            {"X-Exam-Bank": "1201-2026.09-v2", "X-Exam-Id": fresh["id"]},
            {"X-Exam-Bank": BLUEPRINT["bank_version"], "X-Exam-Id": old["id"]},
        ]
        for headers in cases:
            for path, method, body in (
                ("/api/exam", "PATCH", {"question_id": self.bank[5]["id"], "answer": self.bank[5]["answer"]}),
                ("/api/exam/command", "POST", {"command": "raid status"}),
                ("/api/exam/submit", "POST", {}),
            ):
                response = self.client.open(path, method=method, json=body, headers=headers)
                self.assertEqual(response.status_code, 409)
                self.assertNotIn("Set-Cookie", response.headers)
                self.assertEqual(self.client.get_cookie(COOKIE_NAME).value, fresh_cookie)
        unchanged = self.client.get("/api/exam").get_json()
        self.assertEqual(unchanged["id"], fresh["id"])
        self.assertEqual(unchanged["answers"], {})
        self.assertEqual(unchanged["status"], "active")
        self.assertFalse(unchanged["raid"]["diagnosed"])
        self.assertIsNone(unchanged["report"])

    def test_objective_coverage_and_domain_mapping_are_enforced(self):
        meta = self.client.get("/api/meta").get_json()
        self.assertEqual(len(meta["blueprint"]["objectives"]), 27)
        self.assertEqual([d["weight"] for d in DOMAINS], [13, 23, 25, 11, 28])
        self.assertEqual([d["count"] for d in DOMAINS], [12, 21, 22, 10, 25])
        for alteration in ({"objective": "5.99"}, {"objective": "3.1"}, {"sources": []}):
            bank = copy.deepcopy(self.bank)
            bank[0].update(alteration)
            with self.assertRaises(ValueError):
                validate_bank(bank)
