"""Standalone, server-authoritative 220-1201 practice exam.

The RAID terminal is a small state machine. No command is executed on the host.
The question bank and persisted exam snapshots must never be served as static files.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import secrets
import sqlite3
import time
import unicodedata
import uuid
from collections import Counter
from contextlib import closing
from fractions import Fraction
from datetime import datetime, timezone
from urllib.parse import urlsplit

from flask import Flask, jsonify, request, render_template
from werkzeug.exceptions import HTTPException


ROOT = Path(__file__).resolve().parent
DURATION = 90 * 60
COOKIE_NAME = "core1_exam"
LEGACY_DOMAINS = [
    {"id": 1, "name": "Mobile Devices", "weight": 15, "count": 14},
    {"id": 2, "name": "Networking", "weight": 20, "count": 18},
    {"id": 3, "name": "Hardware", "weight": 25, "count": 22},
    {"id": 4, "name": "Virtualization and Cloud Computing", "weight": 11, "count": 10},
    {"id": 5, "name": "Hardware and Network Troubleshooting", "weight": 29, "count": 26},
]
DOMAINS = [
    {"id": 1, "name": "Mobile Devices", "weight": 13, "count": 12},
    {"id": 2, "name": "Networking", "weight": 23, "count": 21},
    {"id": 3, "name": "Hardware", "weight": 25, "count": 22},
    {"id": 4, "name": "Virtualization and Cloud Computing", "weight": 11, "count": 10},
    {"id": 5, "name": "Hardware and Network Troubleshooting", "weight": 28, "count": 25},
]
EXAM_CODE = "220-1201"
BLUEPRINT = json.loads((ROOT / "data" / "blueprint.json").read_text())
PUBLIC_FIELDS = {
    "id", "kind", "domain", "title", "prompt", "options", "select_count",
    "lab", "briefing", "fields", "reference",
}
RAID_KEYS = ("diagnosed", "identified", "replaced", "rebuilt")
LEGACY_DISCLAIMER = (
    "Independent legacy CompTIA A+ 220-1101 practice. This retired exam is not the "
    "current certification exam. Original practice questions; not affiliated with "
    "or endorsed by CompTIA. Scores use an illustrative practice formula, not "
    "CompTIA's confidential scoring model."
)
DISCLAIMER = (
    "Independent CompTIA A+ Core 1 (220-1201) practice, mapped to objectives document "
    "version 4.0. Original questions; not affiliated with or endorsed by CompTIA. "
    "This practice score and any mock certificate are not an official exam result "
    "or CompTIA certification."
)


class InvalidInput(ValueError):
    pass


def validate_bank(bank):
    """Fail at startup if the authored bank violates the exam blueprint."""
    if not isinstance(bank, list) or len(bank) != 90:
        raise ValueError("The question bank must contain exactly 90 questions.")
    expected_ids = [f"pbq-{n}" for n in range(1, 6)] + [f"q-{n:03}" for n in range(1, 86)]
    if [q.get("id") for q in bank] != expected_ids:
        raise ValueError("Question IDs/order must be pbq-1..5 then q-001..085.")
    if Counter(q.get("domain") for q in bank) != {d["id"]: d["count"] for d in DOMAINS}:
        raise ValueError("Question domain counts do not match the blueprint.")
    if sum(q.get("kind") == "multiple" for q in bank) < 12:
        raise ValueError("At least twelve multiple-response questions are required.")
    labs = ("router", "raid", "wifi", "vms", "post")
    for index, q in enumerate(bank):
        if q.get("exam_code") != EXAM_CODE or q.get("objective") not in BLUEPRINT["objectives"]:
            raise ValueError(f"Missing or invalid 220-1201 objective: {q.get('id')}")
        if int(q["objective"].split(".")[0]) != q["domain"]:
            raise ValueError(f"Objective/domain mismatch: {q['id']}")
        if not q.get("sources") or not set(q["sources"]) <= {s["id"] for s in BLUEPRINT["sources"]}:
            raise ValueError(f"Missing or unknown sources: {q['id']}")
        if not all(isinstance(q.get(k), str) and q[k].strip() for k in ("title", "prompt", "explanation")):
            raise ValueError(f"Missing question text: {q.get('id')}")
        if index < 5:
            if q.get("kind") != "pbq" or q.get("lab") != labs[index] or q.get("weight") != 50:
                raise ValueError(f"Invalid PBQ: {q['id']}")
            if not isinstance(q.get("expected"), dict) or not q["expected"]:
                raise ValueError(f"Missing PBQ rubric: {q['id']}")
            if q["lab"] != "raid":
                fields = q.get("fields", [])
                if len({f["id"] for f in fields}) != len(fields):
                    raise ValueError(f"Duplicate PBQ field: {q['id']}")
                if {f["id"] for f in fields} != set(q["expected"]):
                    raise ValueError(f"PBQ fields must match its rubric: {q['id']}")
        else:
            options = q.get("options", [])
            ids = [option["id"] for option in options]
            answers = q.get("answer", [])
            if q.get("kind") not in ("single", "multiple") or q.get("weight") != 6:
                raise ValueError(f"Invalid choice question: {q['id']}")
            if len(ids) < 3 or len(ids) != len(set(ids)) or not answers or not set(answers) <= set(ids):
                raise ValueError(f"Invalid options/answers: {q['id']}")
            if len(answers) != len(set(answers)) or q.get("select_count") != len(answers):
                raise ValueError(f"Invalid selection count: {q['id']}")
            if (q["kind"] == "single") != (len(answers) == 1):
                raise ValueError(f"Invalid choice kind: {q['id']}")
    if {q["objective"] for q in bank} != set(BLUEPRINT["objectives"]):
        raise ValueError("Every numbered 220-1201 objective needs at least one item.")


def normalize_name(value):
    if not isinstance(value, str) or any(unicodedata.category(c).startswith("C") for c in value):
        raise InvalidInput("Enter a name using visible characters only.")
    name = " ".join(unicodedata.normalize("NFC", value).split())
    if not 1 <= len(name) <= 80 or not any(c.isalpha() for c in name) or any(c in "<>" for c in name):
        raise InvalidInput("Enter a name of 1–80 characters, including a letter and no angle brackets.")
    return name


def initial_raid():
    return {
        "history": [{"command": "", "output": "Storage controller simulator ready. Type help for supported commands. This is a mock terminal."}],
        **{key: False for key in RAID_KEYS},
    }


def run_raid_command(raid, command):
    """Interpret an exact allowlist. Never invoke a shell or execute user code."""
    normalized = " ".join(command.split()).lower()
    if normalized == "clear":
        raid["history"] = []
        return
    if normalized == "help":
        output = (
            "Commands: help | raid status | raid drives | raid identify <serial> | "
            "raid replace <failed-serial> <spare-serial> | raid rebuild | clear\n"
            "Inspect the array, identify the failed disk, replace it using the compatible spare, then rebuild."
        )
    elif normalized == "raid status":
        raid["diagnosed"] = True
        if raid["rebuilt"]:
            output = "Array: RAID 5 | State: OPTIMAL | Rebuild: 100% | All members healthy."
        elif raid["replaced"]:
            output = "Array: RAID 5 | State: DEGRADED | Replacement SN-E505 ready. Rebuild required."
        else:
            output = "Array: RAID 5 | State: DEGRADED | Failed member: SN-B204 (bay 2). One disk redundancy lost."
    elif normalized == "raid drives":
        output = (
            "Bay 1: SN-A103 | 2 TB SAS | ONLINE\n"
            + ("Bay 2: SN-E505 | 2 TB SAS | ONLINE\n" if raid["rebuilt"] else
               "Bay 2: SN-E505 | 2 TB SAS | READY FOR REBUILD\n" if raid["replaced"] else
               "Bay 2: SN-B204 | 2 TB SAS | FAILED\n")
            + "Bay 3: SN-C305 | 2 TB SAS | ONLINE\n"
            + ("Spare: none (SN-E505 installed)." if raid["replaced"] else "Spare: SN-E505 | 2 TB SAS | AVAILABLE, compatible.")
        )
    elif normalized == "raid identify sn-b204":
        if not raid["diagnosed"]:
            output = "Inspect the array with raid status before identifying a disk."
        elif raid["replaced"]:
            output = "SN-B204 has already been replaced."
        else:
            raid["identified"] = True
            output = "Identify LED active: bay 2, serial SN-B204. Failed member confirmed."
    elif normalized == "raid replace sn-b204 sn-e505":
        if not raid["identified"]:
            output = "Identify the failed member before replacing it."
        elif raid["replaced"]:
            output = "SN-E505 is already installed in bay 2."
        else:
            raid["replaced"] = True
            output = "SN-B204 removed; compatible replacement SN-E505 installed in bay 2. Ready to rebuild."
    elif normalized == "raid rebuild":
        if not raid["replaced"]:
            output = "Install the compatible replacement before rebuilding."
        elif raid["rebuilt"]:
            output = "Array already optimal. No rebuild needed."
        else:
            raid["rebuilt"] = True
            output = "Simulated rebuild: 100%. Array OPTIMAL; RAID 5 redundancy restored."
    else:
        output = "Unsupported command or serial. Type help. This simulator accepts only the listed RAID commands."
    raid["history"].append({"command": command, "output": output})
    raid["history"] = raid["history"][-150:]


def same_value(field, actual, expected):
    if actual is None or actual == "":
        return False
    if field == "reservation_mac":
        return str(actual).strip().lower().replace("-", ":") == str(expected).strip().lower().replace("-", ":")
    if isinstance(expected, bool):
        return actual is expected
    if isinstance(expected, (int, float)):
        return not isinstance(actual, bool) and actual == expected
    return isinstance(actual, str) and actual.strip() == str(expected).strip()


def question_credit(question, answers, raid):
    if question["kind"] != "pbq":
        answer = answers.get(question["id"], [])
        return Fraction(int(bool(answer) and set(answer) == set(question["answer"])))
    rubric = question["expected"]
    answer = raid if question["lab"] == "raid" else answers.get(question["id"], {})
    overcommitted = False
    if question["lab"] == "vms":
        cpu = sum(answer.get(f"{vm}_cpu", 0) or 0 for vm in ("db", "vdi", "web"))
        ram = sum(answer.get(f"{vm}_ram", 0) or 0 for vm in ("db", "vdi", "web"))
        overcommitted = cpu > 16 or ram > 64
    matched = sum(
        same_value(field, answer.get(field), expected)
        and not (overcommitted and field.endswith(("_cpu", "_ram")))
        for field, expected in rubric.items()
    )
    return Fraction(matched, len(rubric))


def grade_exam(exam, submitted_at, reason):
    domains = exam.get("domains", LEGACY_DOMAINS)
    domain_points = {d["id"]: [Fraction(0), 0] for d in domains}
    earned = Fraction(0)
    possible = 0
    review = []
    pilots = set(exam["pilots"])
    for question in exam["bank"]:
        credit = question_credit(question, exam["answers"], exam["raid"])
        if question["id"] not in pilots:
            points = credit * question["weight"]
            earned += points
            possible += question["weight"]
            domain_points[question["domain"]][0] += points
            domain_points[question["domain"]][1] += question["weight"]
        is_pbq = question["kind"] == "pbq"
        answer = (
            {key: exam["raid"][key] for key in RAID_KEYS} if question.get("lab") == "raid"
            else exam["answers"].get(question["id"], {} if is_pbq else [])
        )
        review.append({
            "id": question["id"], "correct": credit == 1,
            "credit": float(credit), "answer": answer,
            "expected": question["expected"] if is_pbq else question["answer"],
            "explanation": question["explanation"],
            "objective": question.get("objective"),
            "sources": question.get("sources", []),
        })
    score = 100 + math.floor(Fraction(800) * earned / possible + Fraction(1, 2))
    certificate = None
    if score >= 675 and exam.get("exam_code") == EXAM_CODE and exam.get("candidate_name"):
        certificate = {
            "id": "MOCK-1201-" + exam["id"],
            "candidate_name": exam["candidate_name"], "exam_code": EXAM_CODE,
            "score": score, "issued_at": submitted_at,
            "bank_version": exam["bank_version"],
        }
    return {
        "score": score, "passed": score >= 675,
        "candidate_name": exam.get("candidate_name", ""),
        "exam_code": exam.get("exam_code", "220-1101"), "certificate": certificate,
        "earned": round(float(earned), 4), "possible": possible,
        "elapsed_seconds": max(0, min(DURATION, submitted_at - exam["started_at"])),
        "domains": [{
            "id": d["id"], "name": d["name"], "blueprint_weight": d["weight"],
            "percent": round(float(domain_points[d["id"]][0] / domain_points[d["id"]][1]) * 100, 1),
            "earned": round(float(domain_points[d["id"]][0]), 4),
            "possible": domain_points[d["id"]][1],
        } for d in domains],
        "review": review, "submitted_at": submitted_at, "reason": reason,
    }


def normalize_answer(question, answer):
    if question["kind"] != "pbq":
        if not isinstance(answer, list) or not all(isinstance(v, str) for v in answer):
            raise InvalidInput("Choice answers must be an array of option IDs.")
        valid_options = {o["id"] for o in question["options"]}
        if len(answer) != len(set(answer)) or not set(answer) <= valid_options:
            raise InvalidInput("Answer contains duplicate or unknown option IDs.")
        if len(answer) > question["select_count"]:
            raise InvalidInput(f"Select at most {question['select_count']} options.")
        return answer
    if question["lab"] == "raid":
        raise InvalidInput("Use the RAID command endpoint; milestones cannot be edited.")
    if not isinstance(answer, dict):
        raise InvalidInput("Lab answers must be an object of field values.")
    fields = {f["id"]: f for f in question["fields"]}
    if not set(answer) <= set(fields):
        raise InvalidInput("Unknown lab field.")
    normalized = {}
    for field_id, value in answer.items():
        field = fields[field_id]
        if value is None or value == "":
            continue
        if field["type"] == "number":
            if isinstance(value, bool) or not isinstance(value, (int, float, str)):
                raise InvalidInput("Numeric lab fields require a whole number.")
            try:
                number = float(value)
            except (ValueError, OverflowError):
                raise InvalidInput("Numeric lab fields require a whole number.") from None
            if not math.isfinite(number) or number != int(number):
                raise InvalidInput("Numeric lab fields require a finite whole number.")
            if number < field.get("min", 0) or number > field.get("max", 1_000_000):
                raise InvalidInput(f"{field['label']} is outside the allowed range.")
            normalized[field_id] = int(number)
        else:
            if not isinstance(value, str) or len(value) > 512:
                raise InvalidInput("Lab text fields must contain at most 512 characters.")
            value = value.strip()
            if field["type"] == "select" and value not in {str(o["value"]) for o in field["options"]}:
                raise InvalidInput(f"Unknown selection for {field['label']}.")
            normalized[field_id] = value
    return normalized


def apply_patch_to_exam(exam, payload):
    allowed = {"question_id", "answer", "flagged", "current_index"}
    if not payload or not set(payload) <= allowed:
        raise InvalidInput("Provide question_id, answer, flagged, or current_index only.")
    if "current_index" in payload:
        index = payload["current_index"]
        if type(index) is not int or not 0 <= index < len(exam["bank"]):
            raise InvalidInput("current_index must be an integer from 0 to 89.")
    if "answer" in payload or "flagged" in payload or "question_id" in payload:
        question_id = payload.get("question_id")
        if not isinstance(question_id, str):
            raise InvalidInput("A valid question_id is required.")
        question = next((q for q in exam["bank"] if q["id"] == question_id), None)
        if question is None:
            raise InvalidInput("Unknown question_id.")
        if "flagged" in payload and type(payload["flagged"]) is not bool:
            raise InvalidInput("flagged must be true or false.")
        if "answer" in payload:
            answer = normalize_answer(question, payload["answer"])
            exam["answers"][question_id] = answer
        if "flagged" in payload:
            flags = set(exam["flags"])
            if payload["flagged"]:
                flags.add(question_id)
            else:
                flags.discard(question_id)
            exam["flags"] = sorted(flags)
    if "current_index" in payload:
        exam["current_index"] = payload["current_index"]


def public_exam(exam, now):
    return {
        "id": exam["id"], "status": exam["status"],
        "exam_code": exam.get("exam_code", "220-1101"),
        "bank_version": exam.get("bank_version", "1101-legacy"),
        "candidate_name": exam.get("candidate_name", ""),
        "domains": exam.get("domains", LEGACY_DOMAINS),
        "disclaimer": DISCLAIMER if exam.get("exam_code") == EXAM_CODE else LEGACY_DISCLAIMER,
        "questions": [{k: v for k, v in q.items() if k in PUBLIC_FIELDS} for q in exam["bank"]],
        "answers": exam["answers"], "flags": exam["flags"],
        "current_index": exam["current_index"], "started_at": exam["started_at"],
        "deadline": exam["deadline"], "server_now": now,
        "remaining_seconds": max(0, exam["deadline"] - now) if exam["status"] == "active" else 0,
        "raid": exam["raid"], "report": exam["report"],
    }


def create_app(config=None):
    app = Flask(__name__, static_folder=str(ROOT / "static"), template_folder=str(ROOT / "templates"))
    app.config.from_mapping(
        DATABASE=os.environ.get("SIMULATOR_DATABASE", str(ROOT / "instance" / "exams.sqlite3")),
        BANK_PATH=str(ROOT / "data" / "questions.json"),
        COOKIE_SECURE=os.environ.get("SIMULATOR_COOKIE_SECURE", "false").lower() == "true",
        PUBLIC_ORIGIN=os.environ.get("SIMULATOR_PUBLIC_ORIGIN", ""),
        MAX_CONTENT_LENGTH=32 * 1024,
        NOW=lambda: int(time.time()),
    )
    if config:
        app.config.update(config)
    bank = json.loads(Path(app.config["BANK_PATH"]).read_text())
    validate_bank(bank)
    app.config["BANK"] = bank
    database = Path(app.config["DATABASE"])
    database.parent.mkdir(parents=True, exist_ok=True)

    def connect():
        connection = sqlite3.connect(str(database), timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    with closing(connect()) as connection:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("CREATE TABLE IF NOT EXISTS exams (token_hash TEXT PRIMARY KEY, payload TEXT NOT NULL)")

    def token_hash():
        token = request.cookies.get(COOKIE_NAME, "")
        if not 32 <= len(token) <= 128:
            return None
        return hashlib.sha256(token.encode()).hexdigest()

    def read_exam(connection):
        key = token_hash()
        row = connection.execute("SELECT payload FROM exams WHERE token_hash = ?", (key,)).fetchone() if key else None
        return (key, json.loads(row["payload"])) if row else (None, None)

    def save_exam(connection, key, exam):
        connection.execute("UPDATE exams SET payload = ? WHERE token_hash = ?", (json.dumps(exam), key))

    def expire(exam, now):
        if exam["status"] == "active" and now >= exam["deadline"]:
            exam["status"] = "expired"
            exam["report"] = grade_exam(exam, exam["deadline"], "expired")

    def json_object():
        payload = request.get_json()
        if not isinstance(payload, dict):
            raise InvalidInput("Request body must be a JSON object.")
        return payload

    @app.before_request
    def protect_mutations():
        if request.path.startswith("/api/") and request.method in ("POST", "PATCH", "PUT", "DELETE"):
            if request.mimetype != "application/json":
                return jsonify(error="Use Content-Type: application/json."), 415
            if request.headers.get("Sec-Fetch-Site") not in (None, "same-origin", "none"):
                return jsonify(error="Cross-origin requests are not allowed."), 403
            origin = request.headers.get("Origin")
            allowed_origin = app.config["PUBLIC_ORIGIN"].rstrip("/") or request.host_url.rstrip("/")
            if origin and (origin == "null" or origin.rstrip("/") != allowed_origin):
                return jsonify(error="Cross-origin requests are not allowed."), 403
            # Older browser requests may send a Referer but omit Origin.
            referer = request.headers.get("Referer")
            if referer and not origin:
                parsed = urlsplit(referer)
                if f"{parsed.scheme}://{parsed.netloc}" != allowed_origin:
                    return jsonify(error="Cross-origin requests are not allowed."), 403

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(InvalidInput)
    def invalid_input(error):
        return jsonify(error=str(error)), 400

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(error=error.description), error.code

    @app.errorhandler(sqlite3.OperationalError)
    def database_error(error):
        app.logger.error("Database operation failed: %s", error)
        return jsonify(error="Storage is temporarily unavailable. Please retry."), 503

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    @app.get("/healthz")
    def healthz():
        with closing(connect()) as connection:
            connection.execute("SELECT 1 FROM exams LIMIT 1").fetchone()
        return jsonify(status="ok")

    @app.get("/api/meta")
    def meta():
        return jsonify(exam_code=EXAM_CODE, duration_seconds=DURATION, question_count=len(bank),
                       domains=DOMAINS, disclaimer=DISCLAIMER, blueprint=BLUEPRINT)

    @app.post("/api/exam")
    def start_exam():
        payload = json_object()
        if set(payload) != {"candidate_name"}:
            raise InvalidInput("Enter your candidate_name before beginning the exam.")
        candidate_name = normalize_name(payload["candidate_name"])
        now = int(app.config["NOW"]())
        token = secrets.token_urlsafe(32)
        key = hashlib.sha256(token.encode()).hexdigest()
        exam = {
            "id": str(uuid.uuid4()), "status": "active", "bank": bank,
            "exam_code": EXAM_CODE, "bank_version": BLUEPRINT["bank_version"],
            "candidate_name": candidate_name, "domains": DOMAINS,
            "answers": {}, "flags": [], "current_index": 0,
            "started_at": now, "deadline": now + DURATION,
            "pilots": secrets.SystemRandom().sample([q["id"] for q in bank if q["kind"] != "pbq"], 5),
            "raid": initial_raid(), "report": None,
        }
        connection = connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            old_key, old_exam = read_exam(connection)
            if old_exam:
                expire(old_exam, now)
                save_exam(connection, old_key, old_exam)
            connection.execute("INSERT INTO exams (token_hash, payload) VALUES (?, ?)", (key, json.dumps(exam)))
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        response = jsonify(public_exam(exam, now))
        response.set_cookie(COOKIE_NAME, token, max_age=30 * 24 * 60 * 60, httponly=True, secure=app.config["COOKIE_SECURE"] or request.is_secure, samesite="Strict", path="/")
        return response, 201

    @app.get("/api/exam/certificate")
    def certificate():
        # Only this browser's completed, passing snapshot can issue a certificate.
        # Names, scores, dates and eligibility cannot be supplied via URL parameters.
        with closing(connect()) as connection:
            _, exam = read_exam(connection)
        if exam is None:
            return jsonify(error="No saved exam in this browser."), 404
        report = exam.get("report") or {}
        cert = report.get("certificate")
        if (exam["status"] == "active" or not report.get("passed") or not cert
                or exam.get("exam_code") != EXAM_CODE):
            return jsonify(error="A named, passing 220-1201 attempt is required for a mock certificate."), 403
        issued = datetime.fromtimestamp(cert["issued_at"], timezone.utc).strftime("%d %B %Y")
        return render_template("certificate.html", certificate=cert, issued=issued)

    @app.route("/api/exam", methods=["GET", "PATCH"])
    @app.post("/api/exam/command")
    @app.post("/api/exam/submit")
    def exam_session():
        connection = connect()
        try:
            # Acquire the write lock before reading: simultaneous saves cannot
            # overwrite one another or race a timer-triggered submission.
            connection.execute("BEGIN IMMEDIATE")
            key, exam = read_exam(connection)
            if exam is None:
                return jsonify(error="No saved exam in this browser. Start a new attempt."), 404
            now = int(app.config["NOW"]())
            expire(exam, now)
            if exam["status"] == "active" and request.method != "GET":
                payload = json_object()
                if request.path.endswith("/submit"):
                    if payload:
                        raise InvalidInput("Submission accepts an empty JSON object only.")
                    exam["status"] = "submitted"
                    exam["report"] = grade_exam(exam, now, "submitted")
                elif request.path.endswith("/command"):
                    if set(payload) != {"command"} or not isinstance(payload["command"], str):
                        raise InvalidInput("Provide a command string only.")
                    command = payload["command"].strip()
                    if not command or len(command) > 200 or any(ord(c) < 32 for c in command):
                        raise InvalidInput("Command must be a single line of 1–200 characters.")
                    run_raid_command(exam["raid"], command)
                else:
                    apply_patch_to_exam(exam, payload)
            save_exam(connection, key, exam)
            connection.commit()
            return jsonify(public_exam(exam, now))
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    return app


# A module-level app supports `gunicorn app:app`. Tests create isolated apps.
app = create_app()

if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "8080")), debug=False)
