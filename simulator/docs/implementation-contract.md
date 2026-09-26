# Implementation contract

Standalone Flask + SQLite application, local port 8080, static vanilla HTML/CSS/JS. No linkage to SabiSales. Exam is explicitly legacy 220-1101 practice; scoring is an illustrative practice formula, not CompTIA's confidential model.

## Bank

`data/questions.json` is a JSON array with exactly 90 items: five PBQs first, then 85 choice questions. Total primary domain counts: 1=14, 2=18, 3=22, 4=10, 5=26. PBQ domains: router=2, raid=3, wifi=1, vms=4, post=5. Thus choice domain counts 13/17/21/9/25. At least 12 multiple-response questions.

Public question: `id` (pbq-1..pbq-5, q-001..q-085), `kind` (`single`, `multiple`, `pbq`), `domain` (integer), `title`, `prompt`, optional `options` (array of `{id,text}`), `select_count` (choice only), `lab` (`router`, `raid`, `wifi`, `vms`, `post`), `briefing` (array of strings), `fields` (array of `{id,label,type,options?,group?,min?,max?}`; types text, number, select; select options `{value,label}`). Optional `reference` is plain text, not HTML. All static questions authored as original educational content.

Private fields: `answer` (array of choice ids), `expected` (PBQ field-value map), `weight` (choice=6, PBQ=50), `explanation` (text). Never return private fields or pilot IDs before submission. Question fields must not contain default correct responses.

PBQ expected field IDs: router `ssid`, `security`, `broadcast`, `reservation_mac`, `reservation_ip`; wifi `ssid`, `eap`, `phase2`, `radius`, `ca_validation`; vms `db_cpu`, `db_ram`, `db_path`, `vdi_cpu`, `vdi_ram`, `vdi_path`, `web_cpu`, `web_ram`, `web_path` (numeric values in cores/GiB, host 16 cores/64 GiB, no overcommit; all CPU+RAM criteria earn zero when either aggregate limit exceeded, independent storage criteria retain credit); post `component`, `remediation`; raid expected booleans `diagnosed`, `identified`, `replaced`, `rebuilt`. Configuration PBQs award equal credit per expected field. CLI milestones award equal credit, enforce ordered valid actions. Backend never accepts client edits to RAID milestones.

RAID simulation is a mock CLI, never a shell. Commands `help`, `raid status`, `raid drives`, `raid identify SN-B204`, `raid replace SN-B204 SN-E505`, `raid rebuild`, `clear`. Array RAID5 with active SN-A103 / failed SN-B204 / active SN-C305; compatible spare SN-E505. Must inspect status before identify, identify before replace, replace before rebuild. CLI state in session `raid: {history:[{command,output}], diagnosed,identified,replaced,rebuilt}`. Questions and initial RAID output must make failed serial discoverable. Server uses these milestones directly for scoring.

## Session API

JSON, same origin, HttpOnly session cookie. `GET /api/meta`: `{exam_code:"220-1101",duration_seconds:5400,question_count:90,domains:[{id,name,weight,count}],disclaimer:string}`.

`POST /api/exam` starts a new exam; `GET /api/exam` resumes (404 when no session); `PATCH /api/exam` accepts `{question_id?,answer?,flagged?,current_index?}`; `POST /api/exam/command` accepts `{command}`; `POST /api/exam/submit` freezes result, idempotently. Mutations use `Content-Type: application/json`. All return session object: `{id,status,questions,answers,flags,current_index,started_at,deadline,server_now,remaining_seconds,raid,report}`. Times are epoch seconds. `status` active/submitted/expired. Any request after deadline freezes as expired before attempting mutation. `GET /healthz` returns 200 JSON. Errors `{error:string}` with suitable status.

Server deadline is authoritative and persists in SQLite along with answers, flags, current index, pilot IDs, CLI state and frozen report. Exactly five randomly chosen choice questions are pilots per attempt; excluded from score and domain denominators. Multiple response requires the exact set. Empty answers earn zero. Practice score `100 + floor(800 * earned / possible + 0.5)`; pass at >=675. Every nonpilot question contributes its weight. Domain percentages reflect weighted scored points, not item counts or the blueprint weight.

Report: `{score,passed,earned,possible,elapsed_seconds,domains:[{id,name,blueprint_weight,percent,earned,possible}],review:[{id,correct,credit,answer,expected,explanation}],submitted_at,reason}`. Review includes all 90 items but no pilot identities, no per-item weights. PBQ `correct` means full credit. Explanation/expected answers only appear on submitted/expired sessions.

Frontend: start/resume, 90-minute timer, autosave with visible status and retry, grid with unanswered/answered/flagged/current, multiple-select count hints, five usable labs, skip/back/next, unanswered warning before submit, accessible result/report/review, reset/new attempt. Await in-flight saves before navigation and submission. No answer-key data in static JS. Handle expiry and connection errors.
