"""Identity, certificate authorization and compatibility across the 1201 upgrade."""
import copy
import hashlib
import json
import sqlite3
import test_app
import unittest
from app import COOKIE_NAME, DOMAINS, LEGACY_DOMAINS, grade_exam, create_app, validate_bank


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

    def test_legacy_active_and_completed_sessions_keep_original_identity(self):
        self.start()
        exam = self.perfect_snapshot()
        for field in ("candidate_name", "exam_code", "bank_version", "domains"):
            exam.pop(field)
        self.replace_snapshot(exam)
        old = self.client.get("/api/exam").get_json()
        self.assertEqual(old["exam_code"], "220-1101")
        self.assertEqual(old["domains"], LEGACY_DOMAINS)
        self.assertIn("retired", old["disclaimer"])
        report = self.client.post("/api/exam/submit", json={}).get_json()["report"]
        self.assertTrue(report["passed"])
        self.assertEqual([d["blueprint_weight"] for d in report["domains"]], [15, 20, 25, 11, 29])
        self.assertIsNone(report["certificate"])
        self.assertEqual(self.client.get("/api/exam/certificate").status_code, 403)
        fresh = self.start()
        self.assertEqual(fresh["exam_code"], "220-1201")
        self.assertEqual(fresh["domains"], DOMAINS)

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
