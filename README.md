# Cyber learning projects

**Live simulator: [Core 1 Lab](http://35.178.246.210)** · [Deployment record](infra/deployment.md)

- [Academy capstone](Project_01.md): the existing infrastructure and security project brief.
- [Core 1 simulator](simulator/README.md): a 220-1201 practice app with 90 questions and five interactive labs.
- [AWS deployment](infra/README.md): infrastructure, GitHub Actions, operations, rollback and costs.

The existing EC2 instance was restarted on 30 September 2026 and is serving the complete replacement bank **1201-2026.09-v2** from application commit `4401dc0`. [Deployment run 36693084534](https://github.com/Revelation69/cyber/actions/runs/36693084534) passed both testing and AWS deployment. Live HTTP checks passed for saved progress, scoring, RAID commands and named mock certificates. Automatic AWS deployment is enabled (`AWS_DEPLOY_ENABLED=true`).

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

Start a new exam attempt to use v2; existing attempts preserve their original question set and progress. If the instance is stopped again, pause automatic deployment until it is restarted and Systems Manager is online. Restarting an instance alone does not install newer repository changes; a pipeline deployment is still required.
