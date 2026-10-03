# Teardown — 3 October 2026

The user requested destruction of all AWS resources created for this simulator. Account `727646487479`, region `eu-west-2`.

- Disabled GitHub deployments (`AWS_DEPLOY_ENABLED=false`) and removed the five obsolete deployment-target variables. No workflow deployment was active.
- Stopped the host and deleted CloudFormation stack `core1-simulator`; AWS confirmed `DELETE_COMPLETE`.
- Deleted the retained data volume `vol-0d9d0dbb14934f251`, including saved attempts and on-disk backups, and force-deleted ECR repository `core1-simulator-simulator` with its images.
- Verified removal of the instance, root/data disks, Elastic IP allocation, VPC, deployment roles, GitHub OIDC provider and SSM document. CloudFormation confirmed deletion of all other managed stack resources. No snapshots of either disk remained.
- Checked that no unrelated IAM role depended on the stack-created GitHub OIDC provider before deletion. Unrelated AWS resources were left untouched.

The service is offline. The source and infrastructure templates remain in GitHub for local use or deliberate future reprovisioning. The records below describe former deployments, not live resources.

---

# Deployment record (historical) — 26 September 2026

Former app address: `http://35.178.246.210` (released; no longer this project)

Repository: [Revelation69/cyber](https://github.com/Revelation69/cyber). Local checkout: /Users/michaelajala/Documents/cyber; simulator source is under simulator/.

| Resource | Value |
| --- | --- |
| Account / region | 727646487479 / eu-west-2 |
| CloudFormation stack | core1-simulator — CREATE_COMPLETE |
| Instance | i-0dbcc0971f64573d0 — t3.micro, Amazon Linux 2023 |
| Elastic IP | 35.178.246.210 |
| Retained data volume | vol-0d9d0dbb14934f251 — 8 GiB encrypted gp3 |
| ECR repository | 727646487479.dkr.ecr.eu-west-2.amazonaws.com/core1-simulator-simulator |
| Deployment role | core1-simulator-DeploymentRole-GlSqwyrKV6l9 |
| SSM deployment document | core1-simulator-DeployDocument-X3KYNhG0GTLU |

## Verified release

- [Initial CI](https://github.com/Revelation69/cyber/actions/runs/36261582482): passed, deployment deliberately gated during provisioning.
- [First live release](https://github.com/Revelation69/cyber/actions/runs/36262062968): test and deploy jobs passed, including OIDC authentication, ECR publication, SSM deployment and public health verification.
- Initial source commit: a03d90628dbf7641c74bf575ea4768366987f931.
- Initial image digest: sha256:bf99ae8594f4d1796d92abfde7bf2eaef0f0f18527d5ade55932ddb6932d2a25.
- The public HTTP smoke test passed: 90 questions without pre-submission answer leakage, saves, flags, navigation, timer, RAID state, scoring/report and immutable submission.
- Browser verification reached the public overview and active exam, and saved a completed router configuration with a review flag.
- SSM confirmed the bootstrap-complete marker, the dedicated disk mounted at /var/lib/core1, and the running Caddy proxy.

Repository Actions variables are configured and deployment is enabled. Future main-branch changes to app/infrastructure/pipeline paths trigger checks and an application release. Infrastructure changes still require a separate reviewed CloudFormation operation.

The operator's pre-existing local AWS default profile was used for provisioning; it identifies as the account root. No credentials were copied to the repository or GitHub. Routine deployments use the scoped OIDC role. Use an IAM Identity Center/SSO operator profile for subsequent infrastructure administration.

This is the requested initial public-IP HTTP deployment. Free Tier credits/coverage remain unconfirmed. See the [runbook](README.md) for the approximately $14/month baseline estimate, local backup limits, rollback and cleanup instructions. Current release status and image digests are available in subsequent GitHub Actions run summaries.


## 30 September 2026 — question refresh staged, host stopped

The user stopped EC2 instance `i-0dbcc0971f64573d0`; its state was verified as `stopped`. GitHub repository variable `AWS_DEPLOY_ENABLED` is now `false`. The v2 220-1201 bank is a complete 90-item replacement with backward-compatible saved-attempt handling. It is published to the repository for CI validation, with AWS deployment intentionally skipped. No instance start, infrastructure provisioning or production database change was performed for this update.

To serve the new form later, start the existing instance, wait for its Systems Manager agent to be online, set `AWS_DEPLOY_ENABLED=true`, and manually dispatch the simulator workflow on `main`. The existing image will otherwise remain installed. Starting a new attempt after deployment selects v2; resuming a saved attempt retains its original version.
