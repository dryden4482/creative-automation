#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
SCRIPT_PATH="${BASH_SOURCE[0]-$0}"
SCRIPT_DIR="$(cd "$(dirname "${SCRIPT_PATH}")" && pwd)"
EXAMPLE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CAMPAIGN_ID_FILE="${EXAMPLE_DIR}/campaign_id.txt"
RESPONSE_FILE="$(mktemp)"

if [[ ! -f "${CAMPAIGN_ID_FILE}" ]]; then
  echo "campaign_id.txt not found. Run 1_create_campaign.sh first."
  exit 1
fi

campaign_id="$(cat "${CAMPAIGN_ID_FILE}")"

http_code="$(curl -sS -o "${RESPONSE_FILE}" -w "%{http_code}" -X POST "${API_BASE_URL}/campaigns/${campaign_id}/run")"
cat "${RESPONSE_FILE}"
rm -f "${RESPONSE_FILE}"

if [[ "${http_code}" != "200" ]]; then
  echo
  echo "run campaign failed with HTTP ${http_code}"
  exit 1
fi

echo
