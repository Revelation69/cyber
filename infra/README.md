# AWS deployment

Target: account **727646487479**, **eu-west-2**, stack **core1-simulator**. The initial service uses HTTP on an Elastic IP. It contains practice exams, with no login or payment flow. A single host is appropriate for a small learning project; it is not highly available.

See the [deployment record](deployment.md) for the live URL, resource IDs and verified release.

## Resources and cost

CloudFormation creates a t3.micro (1 GiB RAM, standard CPU credits), an encrypted 8 GiB root disk, an encrypted 8 GiB data disk, one public IPv4 address, a private ECR image repository, a VPC, and scoped IAM/Systems Manager resources. Only port 80 is open; there is no SSH ingress. Session Manager provides administration. IMDSv2 is required.

Budget roughly **US$14/month** for continuous operation before tax, traffic and credits. London Linux t3.micro compute was quoted by the AWS Pricing API at $0.0118/hour on 26 September 2026. Public IPv4, EBS and ECR add charges. The instance type is Free Tier eligible, but account Free Tier coverage could not be confirmed; do not assume this deployment is free. Stopping EC2 stops compute billing, but storage and the allocated public IP remain billable.

## Provision

Use an authenticated operator AWS profile, preferably IAM Identity Center/SSO, with permission to create these resources. Do not commit keys or add long-lived AWS credentials to GitHub. Verify the account before provisioning:

```bash
aws --profile YOUR_PROFILE --region eu-west-2 sts get-caller-identity
python scripts/render_template.py
python -m pip install -r infra/requirements.txt
cfn-lint infra/cloudformation.json
aws --profile YOUR_PROFILE --region eu-west-2 cloudformation deploy \
  --stack-name core1-simulator --template-file infra/cloudformation.json \
  --capabilities CAPABILITY_IAM --no-fail-on-empty-changeset
aws --profile YOUR_PROFILE --region eu-west-2 cloudformation describe-stacks \
  --stack-name core1-simulator --query 'Stacks[0].Outputs'
```

If the account already has the GitHub OIDC provider, pass `ExistingOidcProviderArn` instead of creating another. The default trust subject was verified through the repository OIDC settings: `repo:Revelation69@97466660/cyber@1327682549:ref:refs/heads/main`. This repository uses GitHub's immutable owner/repository IDs. Recheck the subject before using this template for another repository or a GitHub environment.

Bootstrap installs Docker, matches the dedicated EBS disk by volume ID, mounts it at `/var/lib/core1`, and runs the pinned Caddy reverse proxy. Wait for `/etc/core1/bootstrap-complete` before deploying. CloudFormation creation alone does not prove bootstrap succeeded. Inspect `/var/log/cloud-init-output.log` through Systems Manager if it fails.

## GitHub Actions configuration

Set repository Actions variables from stack outputs:

| Variable | Stack output |
| --- | --- |
| `AWS_DEPLOY_ROLE_ARN` | `DeploymentRoleArn` |
| `AWS_ECR_REPOSITORY` | `RepositoryUri` |
| `AWS_INSTANCE_ID` | `InstanceId` |
| `AWS_DEPLOY_DOCUMENT` | `DeploymentDocument` |
| `APP_URL` | `AppUrl` |
| `AWS_DEPLOY_ENABLED` | `true`, set after the host is ready |

The region and account guard are explicit in `.github/workflows/simulator.yml`. Pushes to main and manual workflow runs test the app, build and push an image, then pass its immutable digest to a fixed SSM document. Pull requests only test. The OIDC role can push this repository's images and invoke this host's deployment document; it cannot provision infrastructure or run arbitrary SSM documents. Actions are pinned to commit SHAs.

The workflow checks 17 behavioral tests, JavaScript and shell syntax, reproducible CloudFormation output, cfn-lint, and the real production container over HTTP. Deployment checks the new image in a temporary container before switching the application and verifies public health afterwards.

## Persistence, backups and rollback

SQLite resides at `/var/lib/core1/app/exams.sqlite3` on the dedicated encrypted volume. Each deployment takes a consistent SQLite backup into `/var/lib/core1/backups` before changing the app. Backups older than 14 days are pruned during deployment. These are local backups on the same disk, not offsite disaster recovery or scheduled daily backups. Add EBS snapshots/AWS Backup before storing valuable long-term data.

The host automatically restarts the previous container if the new app fails its health check. To deploy an earlier successful version, run the workflow manually with its ECR `sha256:...` digest in `image_digest`. The latest 20 images are retained in ECR. Check the workflow summary for the deployed digest and SSM command ID.

Rollback changes the container; it does not automatically restore a database backup. Future database migrations need backward compatibility or a deliberate backup/restore procedure. Never overwrite a live SQLite file; stop the app and preserve the original database/WAL files before restoring.

## Operations and cleanup

Use SSM Session Manager or an operator-authorized Run Command to inspect `docker ps`, `docker logs --tail=100 core1-app`, `docker logs --tail=100 core1-proxy`, `df -h`, and `/var/log/cloud-init-output.log`. Container logs are bounded to three 10 MB files. The app binds only to loopback port 8080; Caddy exposes port 80. HTTP does not encrypt session cookies, so keep this initial deployment limited to practice content.

CloudFormation embeds `infra/bootstrap.sh` and `infra/deploy.sh`; regenerate the JSON after editing them. Updating EC2 user data does not rerun bootstrap on an existing host. Plan and review a host refresh/script installation separately. Replacing a host must preserve and reattach the data volume in the same availability zone. Do not delete/recreate the stack expecting automatic data adoption.

For a domain, point DNS at the Elastic IP, update `DomainName`, enable port 443 through the template, and explicitly apply the generated host configuration changes. Caddy obtains HTTPS certificates; the app then uses secure cookies and a fixed public origin. The current initial deployment intentionally uses plain HTTP.

To pause automatic releases, set `AWS_DEPLOY_ENABLED=false`. To stop compute charges, stop the EC2 instance. To remove the deployment, disable releases first, export any needed data, then delete the CloudFormation stack. **The data EBS volume and ECR repository are retained by design and continue to cost money until explicitly deleted.** Review retained resources and any backups separately. The root disk and Elastic IP are removed with the stack.
