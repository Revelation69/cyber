"""Exercise a running simulator and optionally verify Docker restart persistence.

python tests/smoke_http.py --base-url http://127.0.0.1:8081 --restart-container
Creates a disposable test attempt; it does not alter another browser's session.
"""

import argparse
import http.cookiejar
import json
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--restart-container", action="store_true")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def request(path, method="GET", payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(base + path, data=data, method=method,
                                     headers={"Content-Type": "application/json", "Origin": base})
        with opener.open(req, timeout=10) as response:
            return json.load(response)

    assert request("/healthz")["status"] == "ok"
    exam = request("/api/exam", "POST", {})
    assert len(exam["questions"]) == 90
    assert exam["remaining_seconds"] <= 5400
    for question in exam["questions"]:
        assert not {"answer", "expected", "explanation", "weight", "pilot"}.intersection(question)
    choice = next(q for q in exam["questions"] if q["kind"] == "single")
    selected = [choice["options"][0]["id"]]
    saved = request("/api/exam", "PATCH", {
        "question_id": choice["id"], "answer": selected, "flagged": True, "current_index": 5,
    })
    request("/api/exam/command", "POST", {"command": "raid status"})

    if args.restart_container:
        subprocess.run(["docker", "compose", "restart", "simulator"],
                       cwd=Path(__file__).resolve().parents[1], check=True)
        deadline = time.monotonic() + 30
        while True:
            try:
                if request("/healthz")["status"] == "ok":
                    break
            except (OSError, urllib.error.URLError):
                if time.monotonic() >= deadline:
                    raise
            time.sleep(0.5)

    resumed = request("/api/exam")
    assert resumed["id"] == exam["id"]
    assert resumed["deadline"] == exam["deadline"]
    assert resumed["answers"][choice["id"]] == selected
    assert resumed["flags"] == saved["flags"]
    assert resumed["current_index"] == 5
    assert resumed["raid"]["diagnosed"] is True
    report = request("/api/exam/submit", "POST", {})["report"]
    assert 100 <= report["score"] <= 900
    assert len(report["review"]) == 90
    assert len(report["domains"]) == 5
    assert report["possible"] == 730
    assert request("/api/exam/submit", "POST", {})["report"] == report
    assert request("/api/exam", "PATCH", {"question_id": choice["id"], "answer": []})["report"] == report
    print("PASS: HTTP health, public-bank isolation, saves, flags, navigation, timer, RAID, report and immutable submission.")
    if args.restart_container:
        print("PASS: Docker restart preserved the same attempt, answers and deadline.")


if __name__ == "__main__":
    main()
