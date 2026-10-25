"""abx-nl-python-add-82e6cf — sandbox command server."""
from __future__ import annotations

import os

from agent_sandbox.server import command, start


@command("add", description="Add two integers and return the result.")
def add(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b


# Bind the port only when run as main, so a platform --commands import does not serve.
if __name__ == "__main__":
    start(int(os.environ.get("ABX_SERVER_PORT", "9000")))