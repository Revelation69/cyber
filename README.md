# Cyber learning projects

**Simulator address: [Core 1 Lab](http://35.178.246.210)** · [Deployment record](infra/deployment.md)

- [Academy capstone](Project_01.md): the existing infrastructure and security project brief.
- [Core 1 simulator](simulator/README.md): a 220-1201 practice app with 90 questions and five interactive labs.
- [AWS deployment](infra/README.md): infrastructure, GitHub Actions, operations, rollback and costs.

The EC2 instance is stopped as of 30 September 2026. Automatic AWS deployment is paused (`AWS_DEPLOY_ENABLED=false`). The complete replacement question bank `1201-2026.09-v2` is ready in this repository; it has not been deployed to the stopped host.

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

After the instance is deliberately restarted and Systems Manager is online, re-enable `AWS_DEPLOY_ENABLED` and dispatch the simulator workflow on `main` to deploy the current form. Restarting the instance alone serves the previously installed image. Start a new exam attempt after deployment to use v2; existing attempts preserve their original form.
