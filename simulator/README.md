# Core 1 Lab — 220-1201 practice

A standalone, timed CompTIA A+ Core 1 practice simulator: 90 original questions, five interactive labs, automatic saves, review flags, a question navigator, partial-credit lab scoring, and a diagnostic report. This directory is independent of the other projects in this repository and can be copied or deployed on its own.

**This is original 220-1201 practice, aligned to the current English objectives document version 4.0.** It does not reproduce CompTIA's confidential questions or scoring model. It is not affiliated with or endorsed by CompTIA. Review the [prompt assessment](docs/prompt-review.md), [revised build prompt](docs/comptia_core1_simulator_prompt.revised.md), and [curriculum notes](docs/curriculum.md).

## Run locally

Requirements: Python 3.11 or newer, or Docker with Compose.

```bash
cd simulator
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python app.py
```

Open [localhost:8080](http://localhost:8080). The local Flask server is for development. For a local Gunicorn process instead:

```bash
.venv/bin/gunicorn --bind 127.0.0.1:8080 --workers 2 --threads 4 app:app
```

Or start the production container with a convenient local host port:

```bash
HTTP_PORT=8080 docker compose up --build -d
docker compose ps
curl --fail http://localhost:8080/healthz
```

To stop it, run `docker compose down`. The named database volume is retained. Do not add `--volumes` unless you intend to delete every saved attempt.

## How the exam works

Enter the name to display on your mock certificate before starting. A display name is acceptable; it is saved with the attempt. Names support Unicode, are limited to 80 characters, and cannot be changed after starting. Work through questions in any order, and flag items to revisit. Configuration labs save editable fields; the RAID lab saves each simulated command. The navigator distinguishes completed, unanswered and flagged items. Use the submission confirmation to check incomplete work before ending early.

The browser's HttpOnly cookie identifies its attempt. Reloading or restarting the server preserves a current-version attempt and its original deadline. A release with a new question-bank version requires a fresh attempt. Closing the browser does not pause time. An expired exam is finalized on the next request, using the deadline as its submission time; the open page requests finalization when its countdown ends. Only answers accepted before the deadline count. A completed report remains available in the same browser; clearing cookies removes that browser's access to it. A new attempt replaces the browser's current attempt, not its predecessor's stored record.

The fixed bank contains 70 single-answer, 15 multiple-response and five performance-based items. Repeated attempts reuse these questions; this is deliberate practice, not adaptive testing.

| Domain | Blueprint target | Questions |
| --- | ---: | ---: |
| Mobile Devices | 13% | 12 |
| Networking | 23% | 21 |
| Hardware | 25% | 22 |
| Virtualization and Cloud Computing | 11% | 10 |
| Hardware and Network Troubleshooting | 28% | 25 |

The SOHO addressing, RAID, mobile support, VM allocation and POST labs each belong to one primary reporting domain. Counts include those labs and round the 220-1201 percentages to whole questions. Lab-specific technical assumptions are supplied inside each exercise.

## Mock certificates and existing attempts

Passing named 220-1201 attempts unlock **View / print mock certificate** in the results. Open it and use **Print / Save as PDF**. The server uses the immutable result to supply the candidate name, score, UTC issue date, exam code and reference ID. Active, failed, anonymous and legacy attempts cannot obtain a certificate. It is explicitly an unproctored mock award, not an official CompTIA certificate, certification or identity verification. Save it before starting a new attempt, which replaces access to the previous report in that browser.

The current bank is **1201-2026.10-v3**, reviewed on 2 October 2026, with all 90 questions replaced. See the [curriculum audit](docs/curriculum.md) for objective mapping.

Older saved attempts, including v1, v2 and 220-1101, can no longer resume or expose their questions, reports or certificates. Reload the page and enter your name to start fresh. Old answers, flags, RAID progress and elapsed time are not carried over. Current-version attempts still autosave and resume normally. The server binds writes to both bank version and attempt ID, so an old tab cannot modify a new attempt through shared cookies.

## Scoring

This intentionally transparent practice formula uses 6 points per choice item and 50 points per lab. Exactly five randomly selected choice questions are unscored pilots for each attempt. They are excluded from score and domain denominators; participants never see their identities.

```text
available points = 80 × 6 + 5 × 50 = 730
score = 100 + floor(800 × earned points / available points + 0.5)
practice pass = score >= 675
```

Multiple-response items require the exact correct set. PBQs earn equal credit per correct field or valid milestone. The VM lab grants no CPU/RAM credit if either host limit is exceeded; storage criteria still receive independent credit. A wrong answer never subtracts points. Domain bars show weighted performance excluding pilots; they do not multiply the overall score by the blueprint percentages. Keys and explanations appear only after submission. The initial final report is immutable, including when later requests arrive from another tab.

## Project map

```text
app.py                      Flask API, grading, SQLite persistence, RAID state machine
data/questions.json         Full original bank and private answer rubrics
static/index.html           Application shell
static/styles.css           Responsive workbench styles
static/app.js               Exam, autosave, labs, timer and report interface
tests/test_app.py           Behavioral backend regression suite
tests/smoke_http.py         Live HTTP and optional container-restart check
requirements.txt           Direct dependencies
requirements.lock          Pinned direct and transitive dependencies
Dockerfile                  Non-root Python/Gunicorn image, port 8080
docker-compose.yml         Restart policy, persistent volume, host port 80
docs/                       Review, revised prompt, curriculum, implementation contract
```

The bank is loaded from disk and validated at startup. An attempt stores its own bank snapshot so a later code/bank update does not change an existing exam. SQLite WAL transactions serialize saves and submission. This design targets one host with a persistent local volume; it is not a multi-region or shared-network-filesystem deployment.

## AWS deployment

This repository is deployed through CloudFormation and GitHub Actions. Use the [infrastructure runbook](../infra/README.md) for the active t3.micro host, persistent disk, OIDC pipeline, backups and rollback. The live app is at [35.178.246.210](http://35.178.246.210).

The manual instructions below are an alternative for a separate standalone host. Do not run them on the pipeline-managed host.

## Alternative manual EC2 runbook

### 1. Create a host

In EC2, launch an **Ubuntu Server 24.04 LTS** or **Amazon Linux 2023** instance, for example a `t3.small` with 20 GiB of storage. This is a modest starting size, not a load-tested capacity guarantee. Select your SSH key pair and a public subnet with a public IPv4 address.

Create security-group inbound rules for TCP **22** from **your public IP/32**, and TCP **80** from your testing IP/32. Widen HTTP access only if you intentionally want the practice app reachable by others. A public teaching service should sit behind HTTPS and an appropriate access/rate-limiting layer. Do not open port 8080 on the security group.

From your computer, replace the example values:

```bash
chmod 400 practice-key.pem
ssh -i practice-key.pem ubuntu@EC2_PUBLIC_IP
# For Amazon Linux, use ec2-user instead of ubuntu.
```

### 2A. Install Docker on Ubuntu

Run these commands on a fresh Ubuntu host. They use the [official Docker apt repository](https://docs.docker.com/engine/install/ubuntu/).

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
. /etc/os-release
ARCHITECTURE=$(dpkg --print-architecture)
echo "deb [arch=$ARCHITECTURE signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo docker compose version
```

### 2B. Install Docker on Amazon Linux 2023

Use AWS's packaged Docker Engine and the official Compose plugin release. The [AWS Docker installation guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-docker.html) and [Compose plugin guide](https://docs.docker.com/compose/install/linux/) describe these installation methods.

```bash
sudo dnf update -y
sudo dnf install -y docker git curl
sudo systemctl enable --now docker
COMPOSE_VERSION=v5.5.0
COMPOSE_ARCH=$(uname -m)
COMPOSE_ASSET="docker-compose-linux-$COMPOSE_ARCH"
COMPOSE_TMP=$(mktemp -d)
cd "$COMPOSE_TMP"
curl -fL "https://github.com/docker/compose/releases/download/$COMPOSE_VERSION/$COMPOSE_ASSET" -o "$COMPOSE_ASSET"
curl -fL "https://github.com/docker/compose/releases/download/$COMPOSE_VERSION/$COMPOSE_ASSET.sha256" -o "$COMPOSE_ASSET.sha256"
sha256sum --check "$COMPOSE_ASSET.sha256"
sudo install -d /usr/local/lib/docker/cli-plugins
sudo install -m 0755 "$COMPOSE_ASSET" /usr/local/lib/docker/cli-plugins/docker-compose
cd ~
sudo docker compose version
```

Manual Compose installs require manual updates. Both branches below use `sudo docker`, so adding your login to the root-equivalent Docker group is unnecessary.

### 3. Transfer the simulator

If you have committed the simulator to your own repository, clone it on the host:

```bash
git clone YOUR_REPOSITORY_URL
cd YOUR_REPOSITORY_DIRECTORY/simulator
```

Alternatively, transfer only this standalone application. On your own computer, from this app directory:

```bash
tar --exclude='.venv' --exclude='instance' --exclude='__pycache__' --exclude='.env' --exclude='test-results' --exclude='*.tar.gz' -czf /tmp/core1-simulator.tar.gz .
scp -i practice-key.pem /tmp/core1-simulator.tar.gz ubuntu@EC2_PUBLIC_IP:~/
```

Use `ec2-user` for Amazon Linux. On EC2:

```bash
mkdir -p ~/core1-simulator
tar -xzf ~/core1-simulator.tar.gz -C ~/core1-simulator
cd ~/core1-simulator
```

### 4. Start and verify

```bash
cp .env.example .env
sudo docker compose up --build -d
sudo docker compose ps
sudo docker compose logs --tail=50
curl --fail http://127.0.0.1/healthz
```

Open `http://EC2_PUBLIC_IP` in a browser. A healthy response is `{"status":"ok"}`. Start an attempt, answer an item, reload, confirm it remains saved, and submit to verify a report. If unreachable, check the security-group source IP, public address, route table, container logs and whether host port 80 is already occupied.

The Dockerfile uses Gunicorn, two workers and four threads per worker. The container runs as UID 10001, drops capabilities, and mounts a writable database volume at `/data`. Compose configures automatic restart and bounded logs. Its health check tests both HTTP and database access.

### Configuration, maintenance and backup

| Variable | Default | Purpose |
| --- | --- | --- |
| `HTTP_PORT` | `80` | Compose's published host port |
| `SIMULATOR_DATABASE` | `/data/exams.sqlite3` in Docker | Persistent SQLite database file |
| `SIMULATOR_COOKIE_SECURE` | `false` | Set `true` when the browser connects over HTTPS |
| `SIMULATOR_PUBLIC_ORIGIN` | empty | Optional canonical origin, e.g. `https://practice.example.com`; required if proxying HTTPS to HTTP |
| `HOST` / `PORT` | `127.0.0.1` / `8080` | Local `python app.py` listener only |

For HTTPS behind a reverse proxy or load balancer, set the canonical HTTPS origin and secure cookie flag together, and restrict direct HTTP access to the proxy. No AWS credentials, real Wi-Fi passwords or other secrets are required by the simulator. The app has no user-registration system or account recovery, and browser cookies act as attempt credentials. It now stores the candidate display name with each attempt, but no email addresses. Names are not publicly listed; the browser session controls access. The initial public-IP site uses HTTP, so prefer a display name until HTTPS is configured.

After transferring updated source, rebuild:

```bash
sudo docker compose up --build -d
sudo docker compose ps
```

Create a consistent SQLite backup while the app runs:

```bash
sudo docker compose exec -T simulator python -c 'import sqlite3; source=sqlite3.connect("/data/exams.sqlite3"); destination=sqlite3.connect("/data/backup.sqlite3"); source.backup(destination); destination.close(); source.close()'
sudo docker compose cp simulator:/data/backup.sqlite3 ./backup.sqlite3
```

Protect backups like active session data and keep them outside the application image. Attempts currently remain stored until an operator removes them; plan retention and disk monitoring for sustained use. The Python 3.11 base image is pinned to the digest verified during this build. Refresh that digest and the dependency lock file periodically, then rerun the checks before deployment.

## Validation

```bash
.venv/bin/python -m unittest discover -s tests -v
node --check static/app.js
docker compose config --quiet
docker compose build
```

Against a running test container, also check HTTP behavior and restart persistence:

```bash
.venv/bin/python tests/smoke_http.py --base-url http://127.0.0.1:8080 --restart-container
```

This optional check restarts the `simulator` service and creates its own test attempt; run it outside other users' active sessions. Adjust the URL to your published host port.

Node is only used for the optional JavaScript syntax check, not to serve the application. The regression suite checks scoring, pilot isolation, partial credit, resource limits, deadline enforcement, frozen reports, persistence, concurrent saves, input validation and RAID sequence integrity. See [validation notes](docs/validation.md) for the checks actually run on this build.
