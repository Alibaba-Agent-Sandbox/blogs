#!/usr/bin/env python3
"""Run the article's two-turn CSV exercise through one managed Agents Gateway.

Requires httpx==0.28.1. Downloaded Agent code is saved, never executed locally.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal
import io
import os
from pathlib import Path
import sys
import time
import uuid

import httpx


FIRST_TASK = (
    "Repair the existing /workspace/agents-api-demo/aggregate.py so repeated months accumulate Decimal amounts. "
    "Preserve its CLI: python /workspace/agents-api-demo/aggregate.py INPUT OUTPUT [--with-share]. "
    "Do not change /workspace/agents-api-demo/tests/test_aggregate.py. Run those original tests. "
    "Read /workspace/input/sales.csv and run the repaired program to write /workspace/outputs/summary.csv "
    "with exactly month,total, months ascending and totals to two decimals. Do not implement --with-share yet. "
    "Preserve the CSV input. Copy the actual repaired source to /workspace/outputs/aggregate.py. "
    "Write /workspace/outputs/report.md explaining the repair and both monthly totals."
)
SECOND_TASK = (
    "Continue the same workspace and modify the existing /workspace/agents-api-demo/aggregate.py to implement "
    "--with-share. The share is each total divided by the grand total, at least six decimal places; "
    "use 0.000000 when the grand total is zero. Preserve the default month,total mode. "
    "Do not change /workspace/agents-api-demo/tests/test_aggregate.py; run those original tests again. "
    "Run python /workspace/agents-api-demo/aggregate.py /workspace/input/sales.csv "
    "/workspace/outputs/summary-with-share.csv --with-share. Preserve summary.csv and copy the actual "
    "modified source to /workspace/outputs/aggregate.py."
)


class DemoError(Exception):
    """An actionable failure without raw server responses or credentials."""


def run(output: Path, context: dict[str, str]) -> None:
    base, token = os.environ.get("AGENTS_API_BASE_URL"), os.environ.get("AGENTS_API_KEY")
    if not base or not token:
        raise DemoError("Set AGENTS_API_BASE_URL and AGENTS_API_KEY first.")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise DemoError("Choose a new or empty output directory.")
    output.mkdir(parents=True, exist_ok=True)
    run_id = uuid.uuid4().hex
    context["session_request_key"] = "csv-session-" + run_id
    context["second_request_key"] = "csv-share-" + run_id

    with httpx.Client(base_url=base.rstrip("/"),
                      headers={"Authorization": "Bearer " + token}, timeout=30,
                      follow_redirects=False) as api:
        def request(method: str, path: str, status: int = 200, **kwargs) -> httpx.Response:
            response = api.request(method, path, **kwargs)
            if response.status_code != status:
                raise DemoError(f"HTTP {response.status_code} from {method} {path} (expected {status}).")
            return response

        def wait_submission(submission_id: str) -> str:
            context["submission"] = submission_id
            deadline = time.monotonic() + 660
            while time.monotonic() < deadline:
                value = request("GET", f"/v1/agent-sandbox/sessions/{context['session']}/submissions/{submission_id}").json()
                if value["status"] in {"completed", "failed", "cancelled", "uncertain"}:
                    if value["status"] != "completed":
                        raise DemoError("Agent submission ended with status " + value["status"] + ".")
                    turn_id = value["turn_id"]
                    turn = request("GET", f"/v1/agents/sessions/{context['session']}/turns/{turn_id}").json()
                    if turn["status"] != "completed":
                        raise DemoError("The saved turn is not completed.")
                    return turn_id
                time.sleep(1)
            raise DemoError("Waiting timed out; the remote submission may still be running.")

        def download(turn_id: str, name: str, local_name: str | None = None) -> bytes:
            params: dict[str, str | int] = {"limit": 100, "order": "asc"}
            for _ in range(100):
                page = request("GET", f"/v1/agents/sessions/{context['session']}/artifacts", params=params).json()
                for item in page["data"]:
                    if item.get("turn_id") == turn_id and item.get("path") == "outputs/" + name:
                        content = request("GET", f"/v1/agents/sessions/{context['session']}/artifacts/{item['id']}/content").content
                        (output / (local_name or name)).write_bytes(content)
                        return content
                if not page.get("has_more"):
                    break
                if not page.get("last_id"):
                    raise DemoError("Artifact pagination did not return its next cursor.")
                params["after"] = page["last_id"]
            raise DemoError("The completed turn did not publish outputs/" + name + ".")

        models = request("GET", "/v1/models").json()["data"]
        if not models:
            raise DemoError("The deployment has no available model.")
        model = os.environ.get("AGENTS_API_MODEL") or models[0]["id"]
        if model not in {row["id"] for row in models}:
            raise DemoError("AGENTS_API_MODEL is not listed by this deployment.")
        with Path(__file__).with_name("sales.csv").open("rb") as source:
            uploaded = request("POST", "/v1/files", data={"purpose": "user_data"},
                               files={"file": ("sales.csv", source, "text/csv")}).json()
        context["file"] = uploaded["id"]
        created = request("POST", "/v1/agents/sessions", 201,
                          headers={"Idempotency-Key": context["session_request_key"]},
                          json={"agent": {"model": model}, "input": FIRST_TASK,
                                "x_agent_sandbox": {"input_files": [
                                    {"file_id": context["file"], "path": "/workspace/input/sales.csv"}]}})
        context["session"] = created.json()["id"]
        first_turn = wait_submission(created.headers["X-Agent-Sandbox-Submission-Id"])
        summary = download(first_turn, "summary.csv")
        check_csv(summary, False)
        first_source = download(first_turn, "aggregate.py", "aggregate-first.py")
        download(first_turn, "report.md")
        print("First turn: January 30.00, February 10.00; summary and repaired source downloaded.")

        accepted = request("POST", f"/v1/agents/sessions/{context['session']}/events", 202,
                           headers={"Idempotency-Key": context["second_request_key"]},
                           json={"events": [{"type": "agent.session.input.message", "input": SECOND_TASK}]})
        second_turn = wait_submission(accepted.headers["X-Agent-Sandbox-Submission-Id"])
        check_csv(download(second_turn, "summary-with-share.csv"), True)
        if download(second_turn, "aggregate.py", "aggregate-with-share.py") == first_source:
            raise DemoError("The second turn did not modify the source.")
        print("Second turn: shares 0.750000 and 0.250000; updated source downloaded.")

        closed = request("POST", f"/v1/agent-sandbox/sessions/{context['session']}/close", 202, json={}).json()
        context["close_operation"] = closed["id"]
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            operation = request("GET", f"/v1/agent-sandbox/operations/{closed['id']}").json()
            if operation["status"] == "succeeded":
                break
            if operation["status"] in {"failed", "requires_reconcile"}:
                raise DemoError("Session close ended with status " + operation["status"] + ".")
            time.sleep(1)
        else:
            raise DemoError("Session close is still pending; continue querying its operation.")
        request("DELETE", f"/v1/agents/sessions/{context['session']}")
        context.pop("session")
        context.pop("submission", None)
        context.pop("close_operation")
        request("DELETE", f"/v1/files/{context['file']}")
        context.pop("file")
        print("Session closed; public session and input file deleted.")
        print("Results saved to " + str(output))


def check_csv(content: bytes, with_share: bool) -> None:
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    rows = list(reader)
    if reader.fieldnames != (["month", "total", "share"] if with_share else ["month", "total"]):
        raise DemoError("The CSV columns do not match the task.")
    if [(row["month"], Decimal(row["total"])) for row in rows] != [
        ("2026-01", Decimal("30.00")), ("2026-02", Decimal("10.00"))
    ]:
        raise DemoError("The downloaded monthly totals do not match the input.")
    if with_share and any(not Decimal(row["share"]).is_finite()
                          or abs(Decimal(row["share"]) - Decimal(row["total"]) / Decimal(40)) > Decimal("0.000001")
                          for row in rows):
        raise DemoError("The downloaded shares do not match the totals.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, default=Path("results"), help="New or empty download directory")
    args = parser.parse_args()
    context: dict[str, str] = {}
    try:
        run(args.output, context)
    except (DemoError, httpx.HTTPError, OSError, ValueError, KeyError, ArithmeticError) as error:
        print("Error: " + (str(error) if isinstance(error, DemoError) else type(error).__name__), file=sys.stderr)
        for name, value in context.items():
            print(f"{name}: {value}", file=sys.stderr)
        if context:
            print("Query the saved IDs before retrying. A client timeout does not cancel remote work.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
