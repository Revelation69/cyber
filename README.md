# Cyber learning projects

**AWS deployment removed on 3 October 2026.** The simulator is offline; source code remains available for local use. [Deployment and teardown record](infra/deployment.md).

- [Academy capstone](Project_01.md): the existing infrastructure and security project brief.
- [Core 1 simulator](simulator/README.md): a 220-1201 practice app with 90 questions and five interactive labs.
- [AWS deployment](infra/README.md): infrastructure, GitHub Actions, operations, rollback and costs.

The current repository release is **1201-2026.10-v3**, a complete replacement of all 90 questions. This release resets access to older saved attempts: reload the site, enter your name and begin a fresh exam. Answers, flags, lab progress and elapsed time from older forms are not carried over. Automatic AWS deployment is disabled and its AWS targets have been removed.

Deployment verified on **2 October 2026**: application commit `301c138`, [successful test and deploy pipeline](https://github.com/Revelation69/cyber/actions/runs/37057436550). All 30 backend tests and 5 frontend controller tests passed. Live checks confirmed the complete v3 bank, retirement of a saved v2 attempt, fresh progress and timer, stale-tab protection, grading and a named mock certificate. Browser visual verification was unavailable because of the browser access policy.

## Run the simulator locally

```bash
cd simulator
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python app.py
```

Open http://localhost:8080. Or use `HTTP_PORT=8080 docker compose up --build -d` from the simulator directory.

The simulator is independent practice material, not an official CompTIA exam or score predictor. It uses the 220-1201 objectives (document version 4.0), requires a candidate name and issues printable mock certificates for passing attempts. The original source prompt, review and revised specification are in [simulator/docs](simulator/docs).

## Pipeline

Pull requests run application tests, infrastructure validation and a real container HTTP smoke test. When `AWS_DEPLOY_ENABLED=true`, updates to `main` pass the same checks, then publish an immutable image to ECR and deploy it to the EC2 host through Systems Manager. GitHub uses OIDC and a repository/branch-scoped role; AWS access keys are not stored in GitHub.

The AWS stack, both disks, public IP and image repository have been deleted. Saved AWS attempts and local database backups were deleted with the data disk. Rehosting requires provisioning new resources and deliberately reconfiguring deployment; the existing pipeline remains disabled.
