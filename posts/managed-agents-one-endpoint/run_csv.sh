#!/usr/bin/env bash
# Two-turn CSV exercise. Requires Bash, curl and jq; no code runs on the host.
set -euo pipefail

: "${AGENTS_API_BASE_URL:?Set AGENTS_API_BASE_URL first}"
: "${AGENTS_API_KEY:?Set AGENTS_API_KEY first}"
for tool in curl jq; do
  command -v "$tool" >/dev/null || { echo "Missing dependency: $tool" >&2; exit 1; }
done
base=${AGENTS_API_BASE_URL%/}
output=${1:-results}
if [[ -e "$output" ]] && { [[ ! -d "$output" ]] || [[ -n $(ls -A "$output") ]]; }; then
  echo "Choose a new or empty output directory." >&2
  exit 1
fi
mkdir -p "$output"
scratch=$(mktemp -d)
sid= fid= submission= operation=
run_id="$(date +%s)-$$-$RANDOM"
session_key="csv-session-$run_id"
second_key="csv-share-$run_id"
finish() {
  local status=$?
  trap - EXIT
  if [[ $status != 0 ]]; then
    [[ -z "$sid" ]] || printf 'session: %s\n' "$sid" >&2
    [[ -z "$fid" ]] || printf 'file: %s\n' "$fid" >&2
    [[ -z "$submission" ]] || printf 'submission: %s\n' "$submission" >&2
    [[ -z "$operation" ]] || printf 'close_operation: %s\n' "$operation" >&2
    printf 'session_request_key: %s\nsecond_request_key: %s\n' "$session_key" "$second_key" >&2
    echo "Query the saved IDs before retrying. A client timeout does not cancel remote work." >&2
  fi
  rm -rf "$scratch"
  exit "$status"
}
trap finish EXIT

# These temporary response files are replaced per request and removed on exit.
request() {
  local method=$1 path=$2 expected=$3 code
  shift 3
  if ! code=$(curl --silent --show-error --connect-timeout 10 --max-time 30 \
      -X "$method" -H "Authorization: Bearer $AGENTS_API_KEY" \
      -D "$scratch/headers" -o "$scratch/body" -w '%{http_code}' \
      "$base$path" "$@"); then
    echo "Gateway request failed: $method $path" >&2
    return 1
  fi
  if [[ "$code" != "$expected" ]]; then
    echo "HTTP $code from $method $path (expected $expected)." >&2
    return 1
  fi
}

submission_header() {
  local line
  while IFS= read -r line; do
    line=${line%$'\r'}
    case "$line" in
      [Xx]-[Aa][Gg][Ee][Nn][Tt]-[Ss][Aa][Nn][Dd][Bb][Oo][Xx]-[Ss][Uu][Bb][Mm][Ii][Ss][Ss][Ii][Oo][Nn]-[Ii][Dd]:*)
        submission=${line#*:}
        submission=${submission# }
        [[ -n "$submission" ]] && return 0
        ;;
    esac
  done < "$scratch/headers"
  echo "The response has no Submission ID header." >&2
  return 1
}

wait_submission() {
  local deadline=$((SECONDS + 660)) status
  while (( SECONDS < deadline )); do
    request GET "/v1/agent-sandbox/sessions/$sid/submissions/$submission" 200
    status=$(jq -er '.status' "$scratch/body")
    case "$status" in
      completed)
        turn=$(jq -er '.turn_id' "$scratch/body")
        request GET "/v1/agents/sessions/$sid/turns/$turn" 200
        jq -e '.status == "completed"' "$scratch/body" >/dev/null || {
          echo "The saved turn is not completed." >&2; return 1;
        }
        return 0
        ;;
      failed|cancelled|uncertain)
        echo "Agent submission ended with status $status." >&2
        return 1
        ;;
    esac
    sleep 1
  done
  echo "Waiting timed out; the remote submission may still be running." >&2
  return 1
}

download() {
  local turn_id=$1 name=$2 local_name=${3:-$2} cursor= artifact_id page
  for ((page=0; page<100; page++)); do
    local query_args=(--get --data-urlencode limit=100 --data-urlencode order=asc)
    [[ -z "$cursor" ]] || query_args+=(--data-urlencode "after=$cursor")
    request GET "/v1/agents/sessions/$sid/artifacts" 200 "${query_args[@]}"
    artifact_id=$(jq -r --arg t "$turn_id" --arg p "outputs/$name" \
      '.data[] | select(.turn_id == $t and .path == $p) | .id' "$scratch/body")
    if [[ -n "$artifact_id" ]]; then
      request GET "/v1/agents/sessions/$sid/artifacts/$artifact_id/content" 200
      cp "$scratch/body" "$output/$local_name"
      return 0
    fi
    if ! jq -e '.has_more == true' "$scratch/body" >/dev/null; then
      break
    fi
    cursor=$(jq -er '.last_id' "$scratch/body")
  done
  echo "The completed turn did not publish outputs/$name." >&2
  return 1
}

check_csv() {
  local file=$1 with_share=$2 line number=0 month total share extra expected_month expected_total
  while IFS= read -r line || [[ -n "$line" ]]; do
    line=${line%$'\r'}
    number=$((number + 1))
    if [[ $number == 1 ]]; then
      if [[ "$with_share" == yes ]]; then [[ "$line" == month,total,share ]]; else [[ "$line" == month,total ]]; fi || {
        echo "Unexpected CSV columns." >&2; return 1;
      }
      continue
    fi
    case "$number" in
      2) expected_month=2026-01; expected_total=30.00 ;;
      3) expected_month=2026-02; expected_total=10.00 ;;
      *) echo "Unexpected number of CSV rows." >&2; return 1 ;;
    esac
    IFS=, read -r month total share extra <<< "$line"
    [[ "$month" == "$expected_month" && "$total" == "$expected_total" && -z "$extra" ]] || {
      echo "The downloaded monthly totals do not match the input." >&2; return 1;
    }
    if [[ "$with_share" == yes ]]; then
      jq -en --arg value "$share" --arg total "$total" \
        '($value | tonumber) == (($total | tonumber) / 40)' >/dev/null || {
        echo "The downloaded shares do not match the totals." >&2; return 1;
      }
    elif [[ -n "$share" ]]; then
      echo "Unexpected CSV column." >&2; return 1
    fi
  done < "$file"
  [[ $number == 3 ]] || { echo "The CSV needs two monthly rows." >&2; return 1; }
}

request GET /v1/models 200
model=${AGENTS_API_MODEL:-$(jq -er '.data[0].id' "$scratch/body")}
jq -e --arg model "$model" 'any(.data[]; .id == $model)' "$scratch/body" >/dev/null || {
  echo "The selected model is not listed by this deployment." >&2; exit 1;
}
source_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
request POST /v1/files 200 -F purpose=user_data -F "file=@$source_dir/sales.csv;type=text/csv"
fid=$(jq -er '.id' "$scratch/body")
first_task='Repair the existing /workspace/agents-api-demo/aggregate.py so repeated months accumulate Decimal amounts. Preserve its CLI: python /workspace/agents-api-demo/aggregate.py INPUT OUTPUT [--with-share]. Do not change /workspace/agents-api-demo/tests/test_aggregate.py. Run those original tests. Read /workspace/input/sales.csv and run the repaired program to write /workspace/outputs/summary.csv with exactly month,total, months ascending and totals to two decimals. Do not implement --with-share yet. Preserve the CSV input. Copy the actual repaired source to /workspace/outputs/aggregate.py. Write /workspace/outputs/report.md explaining the repair and both monthly totals.'
jq -n --arg model "$model" --arg file "$fid" --arg task "$first_task" \
  '{agent:{model:$model},input:$task,x_agent_sandbox:{input_files:[{file_id:$file,path:"/workspace/input/sales.csv"}]}}' > "$scratch/request"
request POST /v1/agents/sessions 201 -H 'Content-Type: application/json' \
  -H "Idempotency-Key: $session_key" --data-binary "@$scratch/request"
sid=$(jq -er '.id' "$scratch/body")
submission_header
wait_submission
download "$turn" summary.csv
check_csv "$output/summary.csv" no
download "$turn" aggregate.py aggregate-first.py
download "$turn" report.md
echo "First turn: January 30.00, February 10.00; summary and repaired source downloaded."

second_task='Continue the same workspace and modify the existing /workspace/agents-api-demo/aggregate.py to implement --with-share. The share is each total divided by the grand total, at least six decimal places; use 0.000000 when the grand total is zero. Preserve the default month,total mode. Do not change /workspace/agents-api-demo/tests/test_aggregate.py; run those original tests again. Run python /workspace/agents-api-demo/aggregate.py /workspace/input/sales.csv /workspace/outputs/summary-with-share.csv --with-share. Preserve summary.csv and copy the actual modified source to /workspace/outputs/aggregate.py.'
jq -n --arg task "$second_task" '{events:[{type:"agent.session.input.message",input:$task}]}' > "$scratch/request"
request POST "/v1/agents/sessions/$sid/events" 202 -H 'Content-Type: application/json' \
  -H "Idempotency-Key: $second_key" --data-binary "@$scratch/request"
submission_header
wait_submission
download "$turn" summary-with-share.csv
check_csv "$output/summary-with-share.csv" yes
download "$turn" aggregate.py aggregate-with-share.py
if cmp -s "$output/aggregate-first.py" "$output/aggregate-with-share.py"; then
  echo "The second turn did not modify the source." >&2; exit 1
fi
echo "Second turn: shares 0.750000 and 0.250000; updated source downloaded."

request POST "/v1/agent-sandbox/sessions/$sid/close" 202 -H 'Content-Type: application/json' --data '{}'
operation=$(jq -er '.id' "$scratch/body")
deadline=$((SECONDS + 60))
while (( SECONDS < deadline )); do
  request GET "/v1/agent-sandbox/operations/$operation" 200
  status=$(jq -er '.status' "$scratch/body")
  case "$status" in
    succeeded) break ;;
    failed|requires_reconcile) echo "Session close ended with status $status." >&2; exit 1 ;;
  esac
  sleep 1
done
[[ "$status" == succeeded ]] || { echo "Session close is still pending; continue querying its operation." >&2; exit 1; }
request DELETE "/v1/agents/sessions/$sid" 200
sid= submission= operation=
request DELETE "/v1/files/$fid" 200
fid=
echo "Session closed; public session and input file deleted."
echo "Results saved to $output"
