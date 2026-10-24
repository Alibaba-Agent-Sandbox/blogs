"""One call creates, processes CSV remotely, returns verified data, and destroys sandbox."""

import csv
import hashlib
import io
import json
import os
import socket
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from agent_sandbox.declarative import sandbox

WORK = Path(__file__).resolve().parent
REMOTE_MARKER = "orders-case-05-20261024"


@sandbox(template="code-interpreter-v1", envs={"JOURNEY_REMOTE_MARKER": REMOTE_MARKER})
def summarize_orders(csv_text):
    import io
    import os
    import socket
    from decimal import Decimal
    import pandas as pd

    df = pd.read_csv(io.StringIO(csv_text), dtype=str, keep_default_na=False)
    rows_input = len(df)
    df = df.drop_duplicates(subset=["order_id"], keep="first").copy()
    rows_duplicate = rows_input - len(df)
    df["region"] = df["region"].str.strip().str.lower()
    qty = pd.to_numeric(df["quantity"], errors="coerce")
    price = pd.to_numeric(df["unit_price"], errors="coerce")
    valid = (
        df["order_id"].str.strip().ne("")
        & df["region"].isin(["east", "west", "north"])
        & qty.notna()
        & (qty > 0)
        & ((qty % 1) == 0)
        & price.notna()
        & (price >= 0)
    )
    rows_invalid = int((~valid).sum())
    clean = df.loc[valid].copy()
    clean["quantity"] = qty.loc[valid].astype(int)
    clean["revenue_cents"] = [
        int(Decimal(price_text) * 100) * int(count)
        for price_text, count in zip(clean["unit_price"], clean["quantity"])
    ]
    grouped = (
        clean.groupby("region")
        .agg(
            orders=("order_id", "count"),
            units=("quantity", "sum"),
            revenue_cents=("revenue_cents", "sum"),
        )
        .reset_index()
    )
    grouped = grouped.sort_values("region")
    return {
        "rows_input": rows_input,
        "rows_duplicate": rows_duplicate,
        "rows_invalid": rows_invalid,
        "rows_clean": len(clean),
        "summary": grouped.to_dict(orient="records"),
        "revenue_cents": int(grouped["revenue_cents"].sum()),
        "summary_csv": grouped.to_csv(index=False),
        "remote": {
            "hostname": socket.gethostname(),
            "marker": os.getenv("JOURNEY_REMOTE_MARKER"),
            "pandas_version": pd.__version__,
        },
    }


def expected_summary(csv_text):
    """Independent local oracle uses csv + Decimal, not the remote Pandas code."""
    seen = set()
    groups = defaultdict(lambda: {"orders": 0, "units": 0, "revenue_cents": 0})
    duplicate = invalid = count = 0
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    for row in rows:
        if row["order_id"] in seen:
            duplicate += 1
            continue
        seen.add(row["order_id"])
        region = row["region"].strip().lower()
        try:
            quantity = int(row["quantity"])
            price = Decimal(row["unit_price"])
            assert (
                row["order_id"].strip()
                and region in {"east", "west", "north"}
                and quantity > 0
                and price >= 0
            )
        except (ValueError, InvalidOperation, AssertionError):
            invalid += 1
            continue
        count += 1
        groups[region]["orders"] += 1
        groups[region]["units"] += quantity
        groups[region]["revenue_cents"] += int(price * 100) * quantity
    return {
        "rows_input": len(rows),
        "rows_duplicate": duplicate,
        "rows_invalid": invalid,
        "rows_clean": count,
        "summary": [{"region": region, **groups[region]} for region in sorted(groups)],
        "revenue_cents": sum(v["revenue_cents"] for v in groups.values()),
    }


if __name__ == "__main__":
    data = (WORK / "05-orders.csv").read_text()
    expected = expected_summary(data)
    assert "JOURNEY_REMOTE_MARKER" not in os.environ
    result = summarize_orders(data)
    for key, value in expected.items():
        assert result[key] == value, (key, result[key], value)
    assert result["revenue_cents"] == 19310
    assert result["remote"]["marker"] == REMOTE_MARKER
    assert result["remote"]["hostname"] != socket.gethostname()
    assert list(csv.DictReader(io.StringIO(result["summary_csv"]))) == [
        {k: str(v) for k, v in row.items()} for row in expected["summary"]
    ]
    (WORK / "05-summary.csv").write_text(result["summary_csv"])
    # The host identity establishes isolation; keep raw remote host only in private runtime output.
    result["remote"]["hostname"] = "<remote-host-distinct-from-client>"
    report = {
        "input_sha256": hashlib.sha256(data.encode()).hexdigest(),
        "expected": expected,
        "actual": result,
        "assertions_passed": True,
    }
    (WORK / "05-data-result.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
