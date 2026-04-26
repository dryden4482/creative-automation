#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
SCRIPT_PATH="${BASH_SOURCE[0]-$0}"
SCRIPT_DIR="$(cd "$(dirname "${SCRIPT_PATH}")" && pwd)"
EXAMPLE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BRIEF_PATH="${EXAMPLE_DIR}/brief.json"
CAMPAIGN_ID_FILE="${EXAMPLE_DIR}/campaign_id.txt"
RESPONSE_FILE="$(mktemp)"

rm -f "${CAMPAIGN_ID_FILE}"

http_code="$(curl -sS -o "${RESPONSE_FILE}" -w "%{http_code}" -X POST "${API_BASE_URL}/campaigns" \
  -H "Content-Type: application/json" \
  --data-binary "@${BRIEF_PATH}")"

if [[ "${http_code}" != "200" ]]; then
  echo "create campaign failed with HTTP ${http_code}"
  cat "${RESPONSE_FILE}"
  rm -f "${RESPONSE_FILE}"
  exit 1
fi

campaign_id="$(python3 -c 'import json,sys; data=json.load(sys.stdin); print(data["campaign_id"]) if "campaign_id" in data else (_ for _ in ()).throw(SystemExit(f"unexpected response: {data}"))' < "${RESPONSE_FILE}")"
rm -f "${RESPONSE_FILE}"
printf '%s\n' "${campaign_id}" > "${CAMPAIGN_ID_FILE}"

printf 'campaign_id=%s\n' "${campaign_id}"
