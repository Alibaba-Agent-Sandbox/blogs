"""Custom Qwen Code sandbox application; the author owns these commands."""

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import os, subprocess
from agent_sandbox.server import command, start

WORKSPACE = Path("/home/user/journey-qwen/project")


@command(description="Return the installed Qwen Code version")
def qwen_version() -> str:
    return subprocess.check_output(["qwen", "--version"], text=True, timeout=20).strip()


@command(description="Run a bounded real Qwen coding task in the dedicated project")
def repair_calculator(prompt: str) -> dict:
    if not prompt.strip():
        raise ValueError("prompt must not be empty")
    result = subprocess.run(
        [
            "qwen",
            "-p",
            prompt,
            "--auth-type",
            "openai",
            "--model",
            os.environ["OPENAI_MODEL"],
            "--output-format",
            "json",
            "--max-session-turns",
            "8",
            "--max-wall-time",
            "120",
            "--no-chat-recording",
            "--yolo",
        ],
        cwd=WORKSPACE,
        text=True,
        capture_output=True,
        timeout=150,
    )
    (WORKSPACE / "qwen.last.json").write_text(result.stdout)
    (WORKSPACE / "qwen.last.stderr").write_text(result.stderr)
    if result.returncode:
        raise RuntimeError(f"Qwen process failed with exit {result.returncode}")
    return {
        "exit_code": result.returncode,
        "report_exists": (WORKSPACE / "REPORT.md").is_file(),
    }


@command(description="Calculate an exact invoice total with a bounded discount")
def invoice_total(unit_price: str, quantity: int, discount_percent: int = 0) -> dict:
    price = Decimal(unit_price)
    if not price.is_finite() or price < 0:
        raise ValueError("unit_price must be finite and nonnegative")
    if quantity < 0 or not 0 <= discount_percent <= 100:
        raise ValueError("invalid quantity or discount")
    total = (price * quantity * (Decimal(100) - discount_percent) / 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return {
        "total": str(total),
        "quantity": quantity,
        "discount_percent": discount_percent,
    }


if __name__ == "__main__":
    start(9008)
