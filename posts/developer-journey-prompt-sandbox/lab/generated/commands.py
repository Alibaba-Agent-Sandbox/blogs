"""abx-nl-python-add-a2d900 — sandbox command server."""
from __future__ import annotations

import os

from agent_sandbox.server import command, start


@command("add", description="Add two integers and return the sum.")
def add(a: int, b: int) -> int:
    return a + b


# Bind the port only when run as main, so a platform --commands import does not serve.
if __name__ == "__main__":
    start(int(os.environ.get("ABX_SERVER_PORT", "9000")))
