# Build a legacy CompTIA A+ Core 1 practice simulator

Create a complete, runnable, self-contained web application for **legacy 220-1101 practice**, with original educational questions. Retain the historical five-domain blueprint requested below. Make clear that it is independent of CompTIA, that 220-1101 is a legacy exam, and that the score is an illustrative practice score rather than CompTIA's actual scoring model or a prediction of certification success.

## Deliverables

Provide all source files, a complete JSON question bank, pinned Python dependencies, a Python 3.11 container exposing port 8080, Docker Compose forwarding host port 80, a persistent SQLite volume, substantive automated tests, and a README with local and AWS EC2 deployment instructions. Include a short explanation of design limitations. Do not claim that an AWS deployment or test has occurred unless it actually has.

## Exam experience

- Offer a clear start screen, a resumable attempt, and a responsive, keyboard-accessible exam workbench.
- Present exactly 90 questions, including five interactive performance-based questions (PBQs) and 85 multiple-choice/multiple-response questions. Include at least 12 multiple-response items and state each required selection count.
- Give each attempt exactly 90 minutes. Store start/deadline timestamps on the server. Reloads, closed tabs, offline time and process restarts must not reset the timer. Expired attempts are frozen and graded before any further answer mutation.
- Autosave answers, navigation and review flags. Show save failures and provide retry. Serialize saves and finish pending saves before navigating or submitting. Do not silently discard failed saves.
- Provide previous/next/skip, a complete question grid, answered and flagged states, and a confirmation showing remaining unanswered questions before early submission.
- Preserve completed reports across reloads. Starting a fresh attempt must be a deliberate action.

## Original question bank and coverage

Write realistic scenarios and plausible distractors. Include a concise explanation for every question, revealed only after submission. Avoid actual exam questions or claims of CompTIA endorsement. Use these counts, including the PBQs:

| Domain | Historical coverage target | Total items | Choice items | PBQ |
| --- | ---: | ---: | ---: | --- |
| 1. Mobile Devices | 15% | 14 | 13 | Enterprise Wi-Fi |
| 2. Networking | 20% | 18 | 17 | SOHO router |
| 3. Hardware | 25% | 22 | 21 | RAID maintenance |
| 4. Virtualization and Cloud Computing | 11% | 10 | 9 | VM allocation |
| 5. Hardware and Network Troubleshooting | 29% | 26 | 25 | POST diagnosis |

These rounded counts approximate the blueprint; each question has one primary reporting domain. Cross-domain labs should be acknowledged.

## Practice scoring rules

These are simulator design choices, not assertions about the live CompTIA exam:

1. Each choice item has weight 6. Single-choice requires the correct option; multiple-response requires the exact correct set, with no negative marking.
2. Each PBQ has weight 50. Award equal partial credit per clearly defined rubric field/milestone. Empty fields earn no credit.
3. Randomly select exactly five of the 85 choice items as unscored pilots at attempt creation. Persist that selection. Exclude them from overall and domain numerators and denominators; never label them in the participant UI or API.
4. Let `E` be earned weighted points and `P` the available points excluding pilots. Calculate `score = 100 + floor(800 * E / P + 0.5)`. The score is bounded by 100 and 900. Practice pass threshold is 675. Use exact arithmetic where possible.
5. Return overall score, practice pass/fail, time used, five domain performance percentages, and a question-by-question explanation/answer review. Domain performance is weighted earned points divided by weighted available points; blueprint coverage percentages are separate labels.
6. Freeze the first final report. Repeated submission, stale requests and multiple tabs must not change it.

## Five interactive PBQs

1. **SOHO router:** supply the required SSID, WPA3-Personal setting, requested broadcast setting, client MAC address and reserved IPv4 address. Use editable configuration fields. Retain the hidden-SSID request only as a task requirement, and explain that it adds no security.
2. **RAID maintenance:** simulate RAID 5 with two healthy members, one failed member and one compatible spare. Provide a discoverable mock command help screen. Track diagnosis, failed-serial identification, correct replacement, and rebuild in order. Never invoke a real shell or storage tool, and reject forged client milestone flags.
3. **Enterprise Wi-Fi:** provide an enterprise SSID, PEAP with MSCHAPv2, and a trusted CA policy. Put the given RADIUS IPv4 address in an AP/controller AAA field, distinct from the client profile. No real credentials are required.
4. **VM allocation:** supply exact vCPU, GiB RAM and storage-path requirements for a database server, VDI client and web server. Host limits are 16 vCPUs and 64 GiB of allocatable RAM, with no overcommit in this exercise. When either aggregate limit is exceeded, all CPU/RAM criteria earn zero; storage criteria are graded independently. Show live allocation totals.
5. **POST diagnosis:** provide a fictional vendor-specific code/LED legend and an observed code. Require the failed component and an appropriate safe remediation; do not assume universal beep codes.

## Backend and deployment requirements

Use Flask with Gunicorn for deployment and SQLite for single-host persistence. Isolate attempts using a cryptographically random HttpOnly, SameSite cookie; enable Secure cookies for HTTPS. Validate request content types, origins, answer shapes and field ranges. Keep question keys and pilot IDs outside static assets. Apply a same-origin Content Security Policy and avoid external runtime assets. CLI input must be handled by an allowlist/state machine only.

Run the container as a non-root user with a health check, read-only filesystem, writable database volume and bounded logs. Explain the environment variables. Provide exact commands for fresh Ubuntu and Amazon Linux 2023 instances, SSH/HTTP security-group setup, Docker/Compose installation, code transfer, startup, checking health/logs, updates and backup. Never deploy to or purchase AWS resources without a supplied destination and authorization. Describe the HTTP example as a restricted demonstration and explain the HTTPS/canonical-origin configuration for wider use.

## Acceptance checks

Verify bank counts/distribution/unique IDs and meaningful answer rubrics; score extremes and pass threshold; pilot zero impact; exact-set answers; PBQ partial credit; VM overcommit; RAID ordering and forged-state rejection; session isolation and restart persistence; authoritative expiry and frozen reports; absence of private data before submission; validation/CSRF protections; and browser launch, answer/save/resume/flag/grid/lab/submit/report flows at desktop and mobile widths. Report exactly which checks ran and any environment limitation.
