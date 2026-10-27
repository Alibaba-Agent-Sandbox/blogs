#!/usr/bin/env python3
"""Minimal sandbox smoke-test program.

Prints a single fixed line to standard output and exits successfully. It takes
no arguments, reads no configuration, and never touches the filesystem or the
network, so it behaves identically in every environment.
"""

GREETING = "Hello from the sandbox"


def main() -> int:
    """Write the greeting to stdout and report success."""
    print(GREETING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
