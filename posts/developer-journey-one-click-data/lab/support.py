"""Local evidence helpers: credentials come only from the process environment."""

import os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRIVATE = ROOT / ".private"
PRIVATE.mkdir(mode=0o700, exist_ok=True)
(ROOT / "evidence").mkdir(exist_ok=True)
VALUES = {
    k: v
    for k, v in os.environ.items()
    if v and k.startswith(("ABX_", "OPENAI_", "ALICLOUD_", "ALIBABA_CLOUD_", "E2B_"))
}


def environment():
    return dict(os.environ)


def redact(text):
    for value in sorted(set(VALUES.values()), key=len, reverse=True):
        if len(value) >= 6:
            text = text.replace(value, "<redacted>")
    text = re.sub(
        r"(?i)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "<resource-id>",
        text,
    )
    text = re.sub(r"\bc-[0-9a-f]{8}-[0-9a-f]{8}-[0-9a-f]{12}\b", "<container-id>", text)
    text = re.sub(
        r"(?i)([\"\']?(?:account_?id|team_?id|resourcegroup_?id)[\"\']?\s*[:=]\s*[\"\']?)[A-Za-z0-9_-]+",
        r"\1<resource-id>",
        text,
    )
    text = re.sub(r"(?i)(Bearer\s+)[A-Za-z0-9._~+/=-]+", r"\1<redacted>", text)
    return text
