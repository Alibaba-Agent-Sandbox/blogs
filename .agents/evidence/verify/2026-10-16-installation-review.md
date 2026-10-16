# Verification: Bilingual installation guidance review

- Date: 2026-10-16
- Scope: `posts/agent-runs-untrusted-code/index.en.md`, matching `index.zh.md`,
  and the repository-owned installation records.
- Source reviewed: `bc320aad77ca4e6082a6e4ffcb2ac4ed6bf36f20`.
- Result: PASS for post validation and documentation review; native macOS/Windows
  execution and production publication are not verified.

## Commands and results

- `python scripts/validate.py`: exit 0, 3 posts checked, 0 problems (Python 3.13,
  PyYAML 6.0.3).
- `git diff --check`: exit 0.
- Independent review of both changed translations: same SDK source commit,
  paired client/server installs, binary installer, PATH and PowerShell guidance.
- Latest remote `validate` check on the reviewed content revision: success.
  [Run](https://github.com/Alibaba-Agent-Sandbox/blogs/actions/runs/38838114082).
- Record/link and configured-secret scans are performed before the record commit.

## Evidence boundaries

The earlier business session executed the Linux CLI checksum/install and the paired
Python install/import/pip-check successfully; its outputs remain in the workspace's
historical artifacts. This review does not relabel those results as new native OS
runs. Website rendering/integration is owned by the linked website PR. A new CI run
is required after this record commit. No cloud resources were created.
