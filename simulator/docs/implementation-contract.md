# Current implementation contract

See the [revised specification](comptia_core1_simulator_prompt.revised.md), [curriculum audit](curriculum.md) and [README](../README.md).

`POST /api/exam` requires exactly `{"candidate_name":"Alex Morgan"}`. Each attempt stores its exam code, bank version, name and domain blueprint. `GET /api/exam/certificate` returns private HTML only for a completed passing named 220-1201 attempt. Print styling supports saving it as PDF. Questions expose objective references and explanations only in the submitted review. Only attempts matching the running exam code and bank version can be served. Retired snapshots return `409` with `code=exam_reset` and clear the session cookie; they cannot be saved, submitted or used to retrieve old certificates. A new named attempt starts empty with a full deadline.

Session writes (`PATCH /api/exam`, `POST /api/exam/command`, `POST /api/exam/submit`) require `X-Exam-Bank` and `X-Exam-Id` matching the loaded attempt. Missing or mismatched headers also return `409 exam_reset`, but keep a current cookie intact so a stale tab cannot log out the fresh tab. Retired records may remain in the database/backups; they are not accessible through the app.

The frontend clears pending answers and commands on reset, returns to the name-entry screen and checks metadata when the tab becomes visible and every 30 seconds while visible and idle. The HTML is not cached; the release updates the script asset version. Previously loaded older frontends need a page reload.
