# Revised simulator specification — CompTIA A+ Core 1 (220-1201)

Build original practice aligned to the current published English 220-1201 V15 objectives, document version 4.0. Preserve the user-supplied initial 220-1101 prompt separately as historical input.

- Use 90 items: 85 choice questions and five interactive labs, with counts 12/21/22/10/25 across Mobile, Networking, Hardware, Virtualization/Cloud and Troubleshooting. Map all 27 numbered objectives; validate keys, source IDs and domain assignments.
- Use practical, original scenarios with plausible alternatives, explicit selection counts, sufficient facts for an unambiguous answer and explanations. Do not use exam dumps, claim actual exam questions, or promise calibrated exam-equivalent difficulty.
- Provide SOHO addressing/DHCP, simulated RAID repair, mobile connectivity/application support, VM allocation and POST diagnosis labs. Do not execute terminal input on the host.
- Keep the server-controlled 90-minute deadline, autosaves, flags, navigation, cookie session, immutable results, partial lab credit and diagnostic domain report. The five random unscored pilots and 100–900 linear practice formula are illustrative simulator rules, not asserted CompTIA psychometrics.
- Ask for a candidate name before starting; validate 1–80 visible Unicode characters and freeze it with the attempt. A display name is acceptable. Store it only with the session-backed attempt.
- For a submitted/expired passing 220-1201 attempt, issue a private printable mock certificate with the frozen name, score, exam code, issue date and reference. Label it as independent, unproctored practice, not an official CompTIA certification. Deny active, failed and legacy attempts.
- For each replacement bank, retire older attempts. Do not return their questions, reports or certificates. Require a fresh named attempt with empty progress and a new timer. Bind writes to the loaded attempt ID and bank version so stale browser tabs cannot overwrite a fresh session. Preserve operational records/backups without serving the retired form.
- Deploy through the existing tested GitHub OIDC/ECR/SSM pipeline. Keep the encrypted persistent database and predeployment backup. Validate unit behavior, real HTTP workflows, certificate behavior and retired-attempt reset before release.
