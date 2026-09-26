# 220-1201 upgrade validation — 26 September 2026

- 23 behavioral tests passed: required/normalized Unicode names, immutable identity, passing-only certificates, anonymous-session denial, escaping, stable certificates, expired passes and preserved legacy labels/domain weights.
- All 90 items validate against the new blueprint: counts 12/21/22/10/25, all 27 numbered objectives and valid key/rubric/source references. Twenty items received substantive revisions; all were reviewed and mapped. This checks consistency, not statistical difficulty equivalence.
- The production Docker image built with the private blueprint and certificate templates. Real HTTP checks passed for saves, flags, timer, RAID, immutable submission and a separate 900-point named attempt receiving private certificate HTML.
- Browser checks confirmed mandatory name entry, candidate display, revised lab fields, the passing-certificate link and the named certificate with explicit mock/non-CompTIA wording. The certificate has dedicated A4 landscape print CSS and a Print / Save as PDF action.
- Certificate and name controls were visually inspected. No browser warning/error logs occurred. The new-attempt confirmation explains replacement of access to the previous report/certificate.
- Existing snapshots require no schema rewrite. New attempts snapshot their code, bank version, name and weights. Legacy sessions remain legacy and cannot receive 220-1201 certificates.

GitHub Actions reruns these checks and the certificate HTTP scenario before deployment. A human curriculum panel, large-sample difficulty calibration and load testing have not been performed.

## Historical validation of the initial 220-1101 build

Verified locally and on AWS on 26 September 2026. See the [deployment record](../../infra/deployment.md) for the live infrastructure and pipeline evidence.

## Automated checks

- **17 behavioral tests passed** with `.venv/bin/python -m unittest discover -s tests -v`.
- Bank validation passed: 90 unique items, five labs, 70 single-answer and 15 multiple-response questions; total domain counts 14/18/22/10/26.
- The scoring tests verified 100 for no credit, 900 for a perfect attempt, 674 below threshold, exactly 675 passing, and pilot answers having zero overall/domain score impact.
- Tests covered exact-set multiple response, partial PBQ credit, VM host limits, ordered RAID actions, rejection of forged milestones, invalid input rollback, same-origin/JSON guards, session isolation, concurrent saves, server-controlled expiry, immutable reports and persistence across app instances.
- Public question responses and static paths were checked for private answer/rubric/pilot leakage before submission.
- JavaScript syntax and Python byte-compilation passed. Frontend source was formatted with Prettier.

## Browser checks

The running application was exercised in the Codex in-app browser:

- Start an exam; complete router and enterprise Wi-Fi fields; flag and navigate through the question grid.
- Run RAID help, status, inventory, identify, replacement and rebuild commands; verify the completed milestones.
- Configure all three VMs; observe the host-budget warning at 22/16 vCPUs, then return to an allowed allocation.
- Complete the POST diagnosis using its supplied legend.
- Save single-answer and multiple-response items; verify a third selection is rejected when two are required.
- Navigate back and reload to verify saved answers, flags and current question.
- Start a fresh attempt, clear a previously saved field using keyboard selection/backspace, navigate away/back, and verify the cleared value stays cleared.
- Submit with unanswered questions and a review flag; inspect the scaled score, five domain bars, answer explanations, and a separate attempt with partial lab credit.
- Inspect desktop (1280 px) and mobile (390 px) layouts; mobile document width matched the viewport without horizontal overflow.
- No browser warning/error logs were observed during the exercised flows.

## Container checks

`docker compose build` succeeded using Python 3.11 and the pinned dependency lock. The running container reported healthy, served `/healthz`, and ran as UID/GID 10001 with the Compose read-only filesystem and persistent volume. A startup control-socket path warning was corrected by placing the Gunicorn control socket in `/tmp`.

The real HTTP smoke test passed against the local container:

```bash
.venv/bin/python tests/smoke_http.py --base-url http://127.0.0.1:8081 --restart-container
```

It created its own attempt, saved answers/flags/navigation/RAID progress, restarted the container, and verified the original deadline and saved state survived. Submission returned a 90-item review and five domains; repeated submission and stale answer changes left the report unchanged.

## Limits of validation

These checks establish functional behavior, not certification validity, exhaustive curriculum coverage, a full accessibility audit or public-service load capacity. The CloudFormation/GitHub Actions deployment was exercised on Amazon Linux 2023; the alternative manual Ubuntu/Compose runbook was not used on that host. Retry controls are implemented; prolonged offline operation and all possible multi-tab timing sequences were not exhaustively exercised. Use HTTPS and deployment-appropriate access controls before wider public use.
