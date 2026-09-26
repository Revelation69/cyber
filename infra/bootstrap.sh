#!/usr/bin/env bash
# Embedded by render_template.py after /etc/core1/deploy.env is written.
set -Eeuo pipefail
source /etc/core1/deploy.env
dnf install -y docker jq
command -v aws
systemctl enable --now amazon-ssm-agent

# Match the dedicated data volume by its NVMe serial; never format the root disk.
device=''
for attempt in $(seq 1 120); do
  device=$(lsblk -dn -o NAME,SERIAL | awk -v serial="${DATA_VOLUME//-/}" '$2 == serial {print "/dev/" $1}')
  [[ -n "$device" ]] && break
  sleep 5
done
[[ -b "$device" ]] || { echo 'Dedicated EBS data volume did not attach.' >&2; exit 1; }
if ! blkid "$device" >/dev/null 2>&1; then
  mkfs.ext4 -L core1-data "$device"
fi
mkdir -p /var/lib/core1
volume_uuid=$(blkid -s UUID -o value "$device")
grep -q "UUID=$volume_uuid " /etc/fstab || printf 'UUID=%s /var/lib/core1 ext4 defaults,nofail 0 2\n' "$volume_uuid" >> /etc/fstab
mount /var/lib/core1
mountpoint -q /var/lib/core1
mkdir -p /etc/systemd/system/docker.service.d
cat > /etc/systemd/system/docker.service.d/core1-volume.conf <<'UNIT'
[Unit]
RequiresMountsFor=/var/lib/core1
UNIT
systemctl daemon-reload
systemctl enable --now docker
mkdir -p /var/lib/core1/app /var/lib/core1/backups /var/lib/core1/caddy-data /var/lib/core1/caddy-config
chown 10001:10001 /var/lib/core1/app /var/lib/core1/backups
chmod 700 /var/lib/core1/backups

site_address=':80'
[[ -z "$DOMAIN" ]] || site_address="$DOMAIN"
cat > /etc/core1/Caddyfile <<EOF
$site_address {
  encode gzip
  reverse_proxy 127.0.0.1:8080
}
EOF
docker pull "$CADDY_IMAGE"
docker rm -f core1-proxy 2>/dev/null || true
docker run -d --name core1-proxy --restart unless-stopped --network host \
  --read-only --tmpfs /tmp:size=32m --cap-drop ALL --cap-add NET_BIND_SERVICE \
  --security-opt no-new-privileges:true --log-opt max-size=10m --log-opt max-file=3 \
  -v /etc/core1/Caddyfile:/etc/caddy/Caddyfile:ro \
  -v /var/lib/core1/caddy-data:/data -v /var/lib/core1/caddy-config:/config "$CADDY_IMAGE"
touch /etc/core1/bootstrap-complete
echo 'Core 1 host ready for an image deployment through Systems Manager.'
