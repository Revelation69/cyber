#!/usr/bin/env bash
# CI entrypoint: send only an immutable digest to the fixed SSM document.
set -Eeuo pipefail
: "${AWS_INSTANCE_ID:?}" "${AWS_DEPLOY_DOCUMENT:?}" "${IMAGE_DIGEST:?}" "${APP_URL:?}"
[[ "$IMAGE_DIGEST" =~ ^sha256:[0-9a-f]{64}$ ]] || { echo 'Invalid image digest.' >&2; exit 2; }
command_id=$(aws ssm send-command --instance-ids "$AWS_INSTANCE_ID" \
  --document-name "$AWS_DEPLOY_DOCUMENT" --document-version '$LATEST' \
  --parameters "ImageDigest=$IMAGE_DIGEST" --timeout-seconds 600 \
  --comment "Core 1 GitHub deployment ${GITHUB_SHA:-manual}" \
  --query Command.CommandId --output text)
echo "Waiting for Systems Manager command $command_id"
for attempt in $(seq 1 120); do
  status=$(aws ssm get-command-invocation --command-id "$command_id" \
    --instance-id "$AWS_INSTANCE_ID" --query Status --output text 2>/dev/null || true)
  case "$status" in
    Success) break ;;
    Failed|TimedOut|Cancelled|Cancelling)
      aws ssm get-command-invocation --command-id "$command_id" --instance-id "$AWS_INSTANCE_ID" \
        --query '{Status:Status,Output:StandardOutputContent,Error:StandardErrorContent}'
      exit 1 ;;
  esac
  sleep 5
done
[[ "$status" == Success ]] || { echo 'Deployment did not finish within ten minutes.' >&2; exit 1; }
curl --fail --retry 5 --retry-delay 3 --max-time 20 "${APP_URL%/}/healthz"
echo "Application is healthy at $APP_URL"
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
  printf '### Deployment verified\n\n- URL: %s\n- Image: `%s`\n- SSM command: `%s`\n' "$APP_URL" "$IMAGE_DIGEST" "$command_id" >> "$GITHUB_STEP_SUMMARY"
fi
