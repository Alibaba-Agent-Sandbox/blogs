# Independent post pinning verification — 2026-11-10

Result: PASS (local producer checks only; joint website delivery remains separate).

Base: `a618ddfc0f2ee607836b3e6df4ccb77aba744475`.
Changed scope: `CONTRIBUTING.md`, both `_template/index.*.md` files,
`scripts/validate.py`, `scripts/test_validate.py`, validation CI and these records.
Tracking: [website Issue #87](https://github.com/Alibaba-Agent-Sandbox/website/issues/87).

## Environment and results

- Python 3.13.13 and PyYAML 6.0.3 in a temporary virtual environment. Initial system
  Python invocation failed because PyYAML was unavailable; installing the README's
  declared prerequisite in the isolated environment resolved that setup failure.
- EXPECTED FAIL: the new regression against the original validator from the base
  revision rejects the test expectation for all six malformed `pinned` values.
  The original validator accepted those values because it did not inspect `pinned`.
- PASS: `python -m unittest discover -s scripts -p 'test_*.py'`: two tests, covering
  omission, true/false, independently featured posts, combined flags and rejection
  of quoted strings, integers, null and a list. Exit 0.
- PASS: `python scripts/validate.py`: 59 article directories, zero problems. Exit 0.
- PASS: `git diff --check` and local links in the new engineering records.

The validation workflow runs the new regression before the existing article scan.
Its hosted Python 3.12 execution and PR state are checked at delivery time.
No published article, cloud resource or credentials changed. No website rendering,
blog ordering or deployment pass is inferred from these producer-only checks.
