"""Behavioral tests for integrity, scoring, persistence, and API boundaries.

Run from the simulator directory: python -m unittest discover -s tests -v
"""

import copy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
from threading import Barrier
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import (  # noqa: E402
    COOKIE_NAME, DOMAINS, DURATION, RAID_KEYS, create_app, grade_exam,
    question_credit, validate_bank,
)


class ExamTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = str(Path(self.temp.name) / "exams.sqlite3")
        self.now = 1_800_000_000
        self.config = {"TESTING": True, "DATABASE": self.database, "NOW": lambda: self.now}
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.bank = self.app.config["BANK"]

    def tearDown(self):
        self.temp.cleanup()

    def start(self):
        response = self.client.post("/api/exam", json={})
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def raw_exam(self):
        cookie = self.client.get_cookie(COOKIE_NAME).value
        key = hashlib.sha256(cookie.encode()).hexdigest()
        connection = sqlite3.connect(self.database)
        try:
            value = connection.execute("SELECT payload FROM exams WHERE token_hash = ?", (key,)).fetchone()[0]
            return json.loads(value)
        finally:
            connection.close()

    def save(self, question_id, answer):
        response = self.client.patch("/api/exam", json={"question_id": question_id, "answer": answer})
        self.assertEqual(response.status_code, 200, response.get_json())
        return response.get_json()

    def command(self, command):
        response = self.client.post("/api/exam/command", json={"command": command})
        self.assertEqual(response.status_code, 200, response.get_json())
        return response.get_json()

    def test_bank_invariants(self):
        validate_bank(self.bank)
        self.assertEqual(len(self.bank), 90)
        self.assertEqual(sum(q["kind"] == "pbq" for q in self.bank), 5)
        self.assertGreaterEqual(sum(q["kind"] == "multiple" for q in self.bank), 12)
        broken = copy.deepcopy(self.bank)
        broken[5]["domain"] = 99
        with self.assertRaises(ValueError):
            validate_bank(broken)
        broken = copy.deepcopy(self.bank)
        broken[5]["answer"] = ["not-an-option"]
        with self.assertRaises(ValueError):
            validate_bank(broken)

    def test_public_schema_contains_no_answer_key_or_pilot_identities(self):
        self.assertEqual(self.client.get("/api/exam").status_code, 404)
        response = self.client.post("/api/exam", json={})
        public = response.get_json()
        for question in public["questions"]:
            self.assertFalse({"answer", "expected", "weight", "explanation", "pilot"} & set(question))
        self.assertNotIn("pilots", public)
        self.assertNotIn("bank", public)
        self.assertIsNone(public["report"])
        self.assertEqual(public["remaining_seconds"], DURATION)
        self.assertEqual(public["deadline"], self.now + DURATION)
        cookie = response.headers["Set-Cookie"]
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=Strict", cookie)
        self.assertIn("no-store", response.headers["Cache-Control"])
        for path in ("/data/questions.json", "/static/../data/questions.json", "/app.py", "/instance/exams.sqlite3"):
            self.assertEqual(self.client.get(path).status_code, 404)

    def test_random_pilots_are_five_choice_items_and_differ_across_attempts(self):
        self.start()
        first = self.raw_exam()
        first_token = self.client.get_cookie(COOKIE_NAME).value
        self.start()
        second = self.raw_exam()
        self.assertEqual(len(set(first["pilots"])), 5)
        self.assertTrue(all(item.startswith("q-") for item in first["pilots"]))
        self.assertNotEqual(first["pilots"], second["pilots"])
        self.assertNotEqual(first_token, self.client.get_cookie(COOKIE_NAME).value)
        self.assertNotEqual(first["id"], second["id"])

    def test_zero_and_perfect_scores_through_api(self):
        self.start()
        zero = self.client.post("/api/exam/submit", json={}).get_json()["report"]
        self.assertEqual((zero["score"], zero["earned"], zero["possible"], zero["passed"]), (100, 0, 730, False))
        self.start()
        for question in self.bank:
            if question.get("lab") == "raid":
                continue
            answer = question["expected"] if question["kind"] == "pbq" else question["answer"]
            self.save(question["id"], answer)
        for command in ("raid status", "raid identify SN-B204", "raid replace SN-B204 SN-E505", "raid rebuild"):
            self.command(command)
        perfect = self.client.post("/api/exam/submit", json={}).get_json()["report"]
        self.assertEqual((perfect["score"], perfect["earned"], perfect["possible"], perfect["passed"]), (900, 730, 730, True))
        self.assertTrue(all(domain["percent"] == 100 for domain in perfect["domains"]))
        self.assertTrue(all(item["correct"] for item in perfect["review"]))
        self.assertEqual(len(perfect["review"]), 90)
        self.assertTrue(all("weight" not in item and "pilot" not in item for item in perfect["review"]))

    def test_pilots_have_zero_score_and_domain_impact(self):
        self.start()
        exam = self.raw_exam()
        before = grade_exam(exam, self.now, "submitted")
        for question in self.bank:
            if question["id"] in exam["pilots"]:
                exam["answers"][question["id"]] = question["answer"]
        after = grade_exam(exam, self.now, "submitted")
        for field in ("score", "passed", "earned", "possible", "domains"):
            self.assertEqual(before[field], after[field])
        self.assertEqual(sum(d["possible"] for d in after["domains"]), 730)
        self.assertEqual(after["possible"], 730)
        for domain in after["domains"]:
            expected = sum(q["weight"] for q in self.bank if q["domain"] == domain["id"] and q["id"] not in exam["pilots"])
            self.assertEqual(domain["possible"], expected)

    def test_score_rounding_and_pass_threshold(self):
        self.start()
        exam = self.raw_exam()
        scored_choices = [q for q in self.bank if q["kind"] != "pbq" and q["id"] not in exam["pilots"]]
        router = next(q for q in self.bank if q.get("lab") == "router")
        exam["answers"][router["id"]] = router["expected"]
        for question in scored_choices[:-1]:
            exam["answers"][question["id"]] = question["answer"]
        below = grade_exam(exam, self.now, "submitted")
        self.assertEqual(below["earned"], 524)
        self.assertEqual(below["score"], 674)
        self.assertFalse(below["passed"])
        final_question = scored_choices[-1]
        exam["answers"][final_question["id"]] = final_question["answer"]
        above = grade_exam(exam, self.now, "submitted")
        self.assertEqual(above["earned"], 530)
        self.assertEqual(above["score"], 681)
        self.assertTrue(above["passed"])
        # An exactly achievable 675: all 80 scored choices (480), two router
        # fields (20), and one of the two POST fields (25), totaling 525.
        exam["answers"] = {q["id"]: q["answer"] for q in scored_choices}
        exam["answers"][router["id"]] = dict(list(router["expected"].items())[:2])
        post = next(q for q in self.bank if q.get("lab") == "post")
        exam["answers"][post["id"]] = dict(list(post["expected"].items())[:1])
        boundary = grade_exam(exam, self.now, "submitted")
        self.assertEqual(boundary["earned"], 525)
        self.assertEqual(boundary["score"], 675)
        self.assertTrue(boundary["passed"])

    def test_multiple_response_requires_exact_set(self):
        self.start()
        exam = self.raw_exam()
        question = next(q for q in self.bank if q["kind"] == "multiple")
        for answer in ([], question["answer"][:-1]):
            exam["answers"][question["id"]] = answer
            self.assertEqual(question_credit(question, exam["answers"], exam["raid"]), 0)
        wrong = next(o["id"] for o in question["options"] if o["id"] not in question["answer"])
        exam["answers"][question["id"]] = question["answer"][:-1] + [wrong]
        self.assertEqual(question_credit(question, exam["answers"], exam["raid"]), 0)
        exam["answers"][question["id"]] = list(reversed(question["answer"]))
        self.assertEqual(question_credit(question, exam["answers"], exam["raid"]), 1)

    def test_pbq_partial_credit_and_vm_host_constraints(self):
        self.start()
        router = next(q for q in self.bank if q.get("lab") == "router")
        first_field = next(iter(router["expected"]))
        self.save(router["id"], {first_field: router["expected"][first_field]})
        exam = self.raw_exam()
        self.assertAlmostEqual(float(question_credit(router, exam["answers"], exam["raid"])), 1 / len(router["expected"]))
        vms = next(q for q in self.bank if q.get("lab") == "vms")
        answer = copy.deepcopy(vms["expected"])
        self.save(vms["id"], answer)
        exam = self.raw_exam()
        self.assertEqual(question_credit(vms, exam["answers"], exam["raid"]), 1)
        # Exceeding either aggregate budget invalidates all CPU/RAM criteria;
        # the three independent storage placements still earn credit.
        for resource, limit in (("cpu", 16), ("ram", 64)):
            answer = copy.deepcopy(vms["expected"])
            answer[f"db_{resource}"] = limit
            exam["answers"][vms["id"]] = answer
            self.assertAlmostEqual(float(question_credit(vms, exam["answers"], exam["raid"])), 1 / 3)

    def test_server_deadline_ignores_client_clock_and_freezes_before_save(self):
        started = self.start()
        question = self.bank[5]
        self.now += 17
        self.assertEqual(self.client.get("/api/exam").get_json()["remaining_seconds"], DURATION - 17)
        for field in ("deadline", "started_at", "remaining_seconds", "server_now", "status", "pilots"):
            response = self.client.patch("/api/exam", json={field: 9999999999})
            self.assertEqual(response.status_code, 400)
        self.now = started["deadline"]
        expired = self.save(question["id"], question["answer"])
        self.assertEqual(expired["status"], "expired")
        self.assertNotIn(question["id"], expired["answers"])
        self.assertEqual(expired["report"]["score"], 100)
        self.assertEqual(expired["report"]["elapsed_seconds"], DURATION)
        self.assertEqual(expired["report"]["submitted_at"], started["deadline"])
        self.assertEqual(expired["remaining_seconds"], 0)
        self.now += 300
        repeated = self.client.post("/api/exam/submit", json={}).get_json()
        self.assertEqual(expired["report"], repeated["report"])

    def test_submission_is_idempotent_and_immutable(self):
        self.start()
        question = self.bank[5]
        saved = self.save(question["id"], question["answer"])
        self.now += 31
        first = self.client.post("/api/exam/submit", json={}).get_json()
        self.assertEqual(first["status"], "submitted")
        self.assertEqual(first["report"]["elapsed_seconds"], 31)
        self.now += 100
        second = self.client.post("/api/exam/submit", json={}).get_json()
        self.assertEqual(first["report"], second["report"])
        ignored = self.save(question["id"], [])
        self.assertEqual(ignored["answers"], saved["answers"])
        raid = self.command("raid status")
        self.assertFalse(raid["raid"]["diagnosed"])
        self.assertEqual(raid["report"], first["report"])

    def test_resume_persists_answers_navigation_timer_and_cli_across_apps(self):
        started = self.start()
        question = self.bank[5]
        response = self.client.patch("/api/exam", json={"question_id": question["id"], "answer": question["answer"], "flagged": True, "current_index": 5})
        self.assertEqual(response.status_code, 200)
        self.command("raid status")
        token = self.client.get_cookie(COOKIE_NAME).value
        self.now += 42
        restarted = create_app(self.config).test_client()
        restarted.set_cookie(COOKIE_NAME, token)
        resumed = restarted.get("/api/exam").get_json()
        self.assertEqual(resumed["id"], started["id"])
        self.assertEqual(resumed["deadline"], started["deadline"])
        self.assertEqual(resumed["remaining_seconds"], DURATION - 42)
        self.assertEqual(resumed["answers"][question["id"]], question["answer"])
        self.assertIn(question["id"], resumed["flags"])
        self.assertEqual(resumed["current_index"], 5)
        self.assertTrue(resumed["raid"]["diagnosed"])
        restarted.post("/api/exam/submit", json={})
        self.assertEqual(self.client.get("/api/exam").get_json()["status"], "submitted")

    def test_session_token_cannot_be_replaced_by_public_exam_id(self):
        exam = self.start()
        stranger = self.app.test_client()
        stranger.set_cookie(COOKIE_NAME, exam["id"])
        self.assertEqual(stranger.get("/api/exam").status_code, 404)
        self.assertEqual(stranger.post("/api/exam/submit", json={}).status_code, 404)

    def test_concurrent_saves_do_not_lose_other_question_answers(self):
        self.start()
        token = self.client.get_cookie(COOKIE_NAME).value
        barrier = Barrier(2)

        def write(question):
            client = self.app.test_client()
            client.set_cookie(COOKIE_NAME, token)
            barrier.wait(timeout=5)
            response = client.patch("/api/exam", json={"question_id": question["id"], "answer": question["answer"]})
            return response.status_code

        questions = self.bank[5:7]
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(list(pool.map(write, questions)), [200, 200])
        answers = self.client.get("/api/exam").get_json()["answers"]
        for question in questions:
            self.assertEqual(answers[question["id"]], question["answer"])

    def test_json_origin_and_body_guards(self):
        for path in ("/api/exam", "/api/exam/command", "/api/exam/submit"):
            self.assertEqual(self.client.post(path, data="{}").status_code, 415)
            self.assertEqual(self.client.post(path, json={}, headers={"Origin": "https://attacker.example"}).status_code, 403)
            self.assertEqual(self.client.post(path, json={}, headers={"Origin": "null"}).status_code, 403)
            self.assertEqual(self.client.post(path, json={}, headers={"Sec-Fetch-Site": "cross-site"}).status_code, 403)
        self.assertEqual(self.client.post("/api/exam", json={}, headers={"Origin": "http://localhost"}).status_code, 201)
        for payload in ([], None, "value", 1):
            response = self.client.post("/api/exam", data=json.dumps(payload), content_type="application/json")
            self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.post("/api/exam", data="{bad", content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post("/api/exam", json={"deadline": 0}).status_code, 400)
        oversized = self.client.patch("/api/exam", json={"answer": "a" * 40000})
        self.assertEqual(oversized.status_code, 413)

    def test_input_validation_rolls_back_all_changes(self):
        started = self.start()
        single = next(q for q in self.bank if q["kind"] == "single")
        router = next(q for q in self.bank if q.get("lab") == "router")
        raid = next(q for q in self.bank if q.get("lab") == "raid")
        invalid = [
            {}, {"current_index": -1}, {"current_index": 90}, {"current_index": True},
            {"question_id": "bad", "answer": []}, {"answer": []},
            {"question_id": single["id"], "answer": ["unknown"]},
            {"question_id": single["id"], "answer": [single["answer"][0]] * 2},
            {"question_id": single["id"], "answer": single["answer"][0]},
            {"question_id": single["id"], "flagged": 1},
            {"question_id": single["id"], "answer": single["answer"], "current_index": 100},
            {"question_id": router["id"], "answer": {"bogus": "value"}},
            {"question_id": router["id"], "answer": []},
            {"question_id": raid["id"], "answer": {"rebuilt": True}},
        ]
        for payload in invalid:
            with self.subTest(payload=payload):
                self.assertEqual(self.client.patch("/api/exam", json=payload).status_code, 400)
        after = self.client.get("/api/exam").get_json()
        self.assertEqual(after["answers"], {})
        self.assertEqual(after["flags"], [])
        self.assertEqual(after["current_index"], started["current_index"])
        vms = next(q for q in self.bank if q.get("lab") == "vms")
        for value in (True, -1, "nan", "inf", 1.5, {}, [], "not a number", 999999):
            response = self.client.patch("/api/exam", json={"question_id": vms["id"], "answer": {"db_cpu": value}})
            self.assertEqual(response.status_code, 400, value)
        cleared = self.save(vms["id"], {"db_cpu": ""})
        self.assertEqual(cleared["answers"][vms["id"]], {})

    def test_raid_sequence_and_no_shell_or_milestone_forgery(self):
        self.start()
        for command in ("raid rebuild", "raid replace SN-B204 SN-E505", "raid identify SN-B204", "rm -rf /", "raid status; touch /tmp/unsafe", "raid identify SN-A103"):
            state = self.command(command)["raid"]
            self.assertFalse(any(state[key] for key in RAID_KEYS))
        self.assertIn("FAILED", self.command("raid drives")["raid"]["history"][-1]["output"])
        self.assertFalse(self.raw_exam()["raid"]["diagnosed"])
        for index, command in enumerate(("raid status", "raid identify SN-B204", "raid replace SN-B204 SN-E505", "raid rebuild")):
            state = self.command(command)["raid"]
            self.assertEqual([state[key] for key in RAID_KEYS], [n <= index for n in range(4)])
        self.assertIn("OPTIMAL", self.command("raid status")["raid"]["history"][-1]["output"])
        state = self.command("clear")["raid"]
        self.assertEqual(state["history"], [])
        self.assertTrue(all(state[key] for key in RAID_KEYS))
        for payload in ({"command": "raid status", "rebuilt": True}, {"command": "x" * 201}, {"command": "raid\nstatus"}, {"command": 1}):
            self.assertEqual(self.client.post("/api/exam/command", json=payload).status_code, 400)

    def test_metadata_and_health(self):
        self.assertEqual(self.client.get("/healthz").get_json()["status"], "ok")
        metadata = self.client.get("/api/meta").get_json()
        self.assertEqual(metadata["exam_code"], "220-1101")
        self.assertEqual(metadata["duration_seconds"], DURATION)
        self.assertEqual(metadata["domains"], DOMAINS)
        self.assertIn("retired", metadata["disclaimer"])


if __name__ == "__main__":
    unittest.main()
