"""Small CSV exercise: repair aggregation, then add --with-share support.

The starter intentionally keeps only the last row of each month. Preserve the
command-line interface and the original tests while completing the exercise.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from pathlib import Path


def summarize(source: Path, target: Path, *, with_share: bool = False) -> None:
    totals: dict[str, Decimal] = {}
    with source.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            month = row["month"]
            amount = Decimal(row["amount"])
            if month in totals:
                totals[month] += amount
            else:
                totals[month] = amount

    grand_total = sum(totals.values())
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as handle:
        if with_share:
            writer = csv.DictWriter(handle, fieldnames=["month", "total", "share"])
            writer.writeheader()
            for month, total in sorted(totals.items()):
                share = total / grand_total if grand_total != 0 else Decimal("0")
                writer.writerow({
                    "month": month,
                    "total": f"{total:.2f}",
                    "share": f"{share:.6f}"
                })
        else:
            writer = csv.DictWriter(handle, fieldnames=["month", "total"])
            writer.writeheader()
            for month, total in sorted(totals.items()):
                writer.writerow({"month": month, "total": f"{total:.2f}"})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--with-share", action="store_true")
    args = parser.parse_args()
    summarize(args.source, args.target, with_share=args.with_share)


if __name__ == "__main__":
    main()
