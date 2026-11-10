# Verification: recent blogs change records

- Date: 2026-11-10
- Result: PASS (records-only checks; implementation gates remain separate)
- Scope: `.agents/README.md`, the recent-change process note and this evidence.
- Source revision inspected: `eceef44f732fb9e2f4387f177c57f922b692a000`.
- Mainline revision inspected: `eceef44f732fb9e2f4387f177c57f922b692a000`.
- Remote query timestamp: `2026-11-10T14:48:35.682193+00:00`.
- Environment: Linux, Git, Python 3; source and remote metadata inspection only.

## Commands and observations

- `git fetch origin --prune`: exit 0 in the owning source repository.
- `git status --short --branch`: the selected worktree was clean before this edit.
- `git log origin/main --first-parent --since=2026-11-05 -8`: inspected source history.
- `git rev-parse HEAD` and `git rev-parse origin/main`: revisions listed above.
- GitHub REST GET repository PR and Actions runs: remote metadata queried separately
  from any claim of executing tests locally. Authenticated REST supplied a consistent metadata snapshot.

## Prior source CI snapshot

This branch contains records only and has no coordinated implementation PR.
Its source is the mainline revision above; older CI is not claimed as a new run.

## Local records validation

- Scoped inline Markdown check below: exit 0; staged relative links resolved.
- One-off ADR/scope/privacy validation: PASS; seven ordered required sections,
  proposed lifecycle, 3 intended files, tracked index membership,
  no machine paths or credential-pattern matches. All 69
  relative links in the scoped documents resolved, including the existing README index.
- `git diff --cached --check -- .agents`: exit 0.
- Reviewed the staged `.agents` diff; no runtime/configuration/public article changes.
- Initial `python3 scripts/validate.py`: exit 1 because the system Python lacked PyYAML.
- An existing project virtualenv was unavailable because its interpreter link did not resolve.
- Prepared an isolated virtualenv and installed the workflow-required PyYAML (6.0.3);
  no repository dependency file changed.
- In that activated virtualenv, `python -m unittest discover -s scripts -p 'test_*.py'`:
  exit 0, 2 tests passed.
- In that activated virtualenv, `python scripts/validate.py`: exit 0, 59 posts,
  0 problems. No article source was modified.

Reproducible scoped link check, run from this repository after staging:

```bash
python3 - <<'PY'
from pathlib import Path
import re, subprocess
files = subprocess.check_output(
    ["git", "diff", "--cached", "--name-only"], text=True).splitlines()
for name in files:
    assert name.startswith(".agents/") and name.endswith(".md")
    path = Path(name)
    text = path.read_text()
    for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", text):
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
            continue
        assert (path.parent / target.split("#", 1)[0]).exists(), (name, target)
print("Scoped staged Markdown links: PASS")
PY
```


## Not verified and cleanup

No runtime, Docker, cloud, model, performance or new package-publication check was
run for this records-only change. Earlier acceptance retains its original scope.
No cloud resources were created, changed or deleted. Required implementation gates
remain with their existing PRs; this task does not declare those PRs complete.
