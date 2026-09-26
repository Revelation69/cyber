# Cyber learning projects

**Live simulator: [Open Core 1 Lab](http://35.178.246.210)** · [Deployment record](infra/deployment.md)

- [Academy capstone](Project_01.md): the existing infrastructure and security project brief.
- [Core 1 simulator](simulator/README.md): a complete legacy 220-1101 practice app with 90 questions and five interactive labs.
- [AWS deployment](infra/README.md): infrastructure, GitHub Actions, operations, rollback and costs.

## Run the simulator locally

```bash
cd simulator
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python app.py
```

Open http://localhost:8080. Or use `HTTP_PORT=8080 docker compose up --build -d` from the simulator directory.

The simulator is independent practice material, not an official CompTIA exam or score predictor. It intentionally uses the legacy 220-1101 blueprint. The original source prompt, review and revised specification are in [simulator/docs](simulator/docs).

## Pipeline

Pull requests run application tests, infrastructure validation and a real container HTTP smoke test. Updates to `main` pass the same checks, then publish an immutable image to ECR and deploy it to the EC2 host through Systems Manager. GitHub uses OIDC and a repository/branch-scoped role; AWS access keys are not stored in GitHub.
