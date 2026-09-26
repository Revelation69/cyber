#!/usr/bin/env bash
# Only the immutable ECR digest is supplied by the deployment role.
set -Eeuo pipefail
source /etc/core1/deploy.env
digest=${1:?An image digest is required}
[[ "$digest" =~ ^sha256:[0-9a-f]{64}$ ]] || { echo 'Invalid image digest.' >&2; exit 2; }
[[ -f /etc/core1/bootstrap-complete ]] || { echo 'Host bootstrap is incomplete.' >&2; exit 1; }
mountpoint -q /var/lib/core1
exec 9>/var/lock/core1-deploy.lock
flock -n 9 || { echo 'Another deployment is in progress.' >&2; exit 1; }
image="$REPOSITORY@$digest"
registry=${REPOSITORY%%/*}
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$registry"
docker pull "$image"

# Snapshot SQLite consistently before changing the running version.
if docker inspect core1-app >/dev/null 2>&1; then
  docker exec core1-app python -c 'import sqlite3; import time; source=sqlite3.connect("/data/exams.sqlite3"); destination=sqlite3.connect("/backups/predeploy-"+str(int(time.time()))+".sqlite3"); source.backup(destination); destination.close(); source.close()'
fi

# Check the candidate against an isolated empty DB before interrupting the app.
docker rm -f core1-candidate 2>/dev/null || true
docker run -d --name core1-candidate --read-only --tmpfs /tmp:size=64m \
  --tmpfs /data:uid=10001,gid=10001,mode=0700,size=32m --cap-drop ALL \
  --security-opt no-new-privileges:true "$image"
candidate_ok=false
for attempt in $(seq 1 30); do
  if docker exec core1-candidate python -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:8080/healthz",timeout=2)' >/dev/null 2>&1; then
    candidate_ok=true; break
  fi
  sleep 2
done
if [[ "$candidate_ok" != true ]]; then
  docker logs --tail=50 core1-candidate
  docker rm -f core1-candidate
  exit 1
fi
docker rm -f core1-candidate

previous=false
if docker inspect core1-app >/dev/null 2>&1; then
  docker rm -f core1-previous 2>/dev/null || true
  docker stop --time 30 core1-app
  docker rename core1-app core1-previous
  previous=true
fi

rollback() {
  echo 'Deployment failed; restoring the previous container.' >&2
  docker logs --tail=50 core1-app 2>/dev/null || true
  docker rm -f core1-app 2>/dev/null || true
  if [[ "$previous" == true ]]; then
    docker rename core1-previous core1-app
    docker start core1-app
  fi
}
trap rollback ERR
secure=false
origin=''
if [[ -n "$DOMAIN" ]]; then secure=true; origin="https://$DOMAIN"; fi
docker run -d --name core1-app --restart unless-stopped --init \
  --publish 127.0.0.1:8080:8080 --read-only --tmpfs /tmp:size=64m \
  --cap-drop ALL --security-opt no-new-privileges:true \
  --log-opt max-size=10m --log-opt max-file=3 \
  -e SIMULATOR_DATABASE=/data/exams.sqlite3 \
  -e SIMULATOR_COOKIE_SECURE="$secure" -e SIMULATOR_PUBLIC_ORIGIN="$origin" \
  -v /var/lib/core1/app:/data -v /var/lib/core1/backups:/backups "$image"
healthy=false
for attempt in $(seq 1 30); do
  if curl --fail --silent http://127.0.0.1:8080/healthz >/dev/null; then healthy=true; break; fi
  sleep 2
done
[[ "$healthy" == true ]]
trap - ERR
printf '%s\n' "$image" > /var/lib/core1/current-image
# Keep bounded local backups and reclaim only old unused Docker images.
find /var/lib/core1/backups -name 'predeploy-*.sqlite3' -type f -mtime +14 -delete
docker image prune --force --filter until=168h
echo "Healthy deployment: $image"
