# Decision: Use verified CLI and paired Python installations

Status: proposed

## Problem

The bilingual untrusted-code article used an unavailable npm CLI and an unrelated
Python package name. The installation PR also lacked repository-owned evidence.

## Decision

Use the published CLI binary installer with PATH and PowerShell guidance. Install
the Python client and server from the same pinned source archive, preserving the
`agent_sandbox` import. Record install verification separately from platform tests.

## API Design

No runtime API changes. Distribution names are `agent-sandbox-client` and
`agent-sandbox-server`; the CLI executable is `abx`.

## Alternatives considered

Keep the old npm/PyPI commands: readers cannot reproduce the article's setup.
Claim native macOS/Windows success based on browser selection: unsupported.

## Dependencies

- [CLI installer](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/blob/main/install.sh)
- [Python source revision](https://github.com/Alibaba-Agent-Sandbox/python-sdk/commit/35da216a300f1e2e84254a1cf4b4a7ea98681505)
- [Website integration PR](https://github.com/Alibaba-Agent-Sandbox/website/pull/2)

## Test Strategy

Validate all post frontmatter, inspect bilingual installation parity and local
links, scan staged files for configured credentials, and inspect the latest PR CI.
Retain the previously executed installer evidence as historical verification.

## Acceptance criteria

- Both translations use matching source pins and correct package names.
- Validation and remote CI pass; required review is honored before merge.
- No claim of native macOS/Windows testing, npm publication, or deployment.

## Evidence

[Verification](../../../evidence/verify/2026-10-16-installation-review.md).
