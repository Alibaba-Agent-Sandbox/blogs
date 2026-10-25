"""abx-nl-python-add-a-b-305f54 — sandbox command server."""
from __future__ import annotations

import os

from agent_sandbox.server import command, start


@command("add", description="Add two integers a and b.")
def add(a: int, b: int) -> int:
    """Add two integers and return their sum."""
    return a + b


# Bind the port only when run as main, so a platform --commands import does not serve.
if __name__ == "__main__":
    start(int(os.environ.get("ABX_SERVER_PORT", "9000")))