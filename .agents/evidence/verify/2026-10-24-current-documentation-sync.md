# Current article and engineering-record synchronization

Date: 2026-10-24 UTC
Result: PASS for current local document/API checks and existing-case publication readback; remote CI and updated-article publication are separate gates.
Base: 312165333eb73346da7e1fa136f56cb578e12614.
Issue: https://github.com/Alibaba-Agent-Sandbox/blogs/issues/11

## Scope and retained history

Update the repository README and current bilingual untrusted-code/publishing guidance. Mark the delivered five-case and practical-narrative decisions implemented after checking PRs #7 and #8 are actually merged; supersede obsolete source-only installation and SDK-entry decisions. Existing evidence, all five pinned practical-case articles, executable attachments, generated snapshots and proof files remain byte-identical.

Normal system-verified HTTPS readback returned 200 for all five existing practical-case pages, with the source titles present. This confirms publication, not another execution of their model or cloud tasks. CLI #132 is now closed; CLI #131 remains open. No historical failure record is rewritten.

## Checks

Environment: Python 3.13.13 and PyYAML 6.0.3.

- Initial system Python could not collect the post validator because PyYAML was missing; the prior turn's disposable SDK venv was also unavailable. No product assertion failed. A new isolated environment installed PyYAML 6.0.3 and public agent-sandbox-client 0.3.1a5 from https://pypi.org/simple, including its matching server dependency.
- `python scripts/validate.py`: PASS, 8 posts and zero problems.
- `python -m pip check`: PASS. Imported public client and server both report 0.3.1a5.
- Both revised Python code blocks parse; their isolated deterministic CSV calculation matches the article output. This check redirects only the fixture file into a temporary directory and does not execute sandbox lifecycle calls.
- Public SDK source confirms the existing async create/kill and file/process interfaces. An initial checker incorrectly expected the class-level decorated kill descriptor to satisfy `inspect.iscoroutinefunction`; source inspection confirms its async implementation. No SDK change was made.
- Final verification: 26 relative Markdown links resolve, all ADR states match their directories, and 91 historical evidence/practical-case files are byte-identical to the base. `git diff --check` passes. A draft checker treated a Markdown example inside inline code as a real link; the final check excludes fenced/inline examples.

No runtime code, article schema, assets or rendering implementation changes. No cloud resources are created, no cloud matrix is rerun, and no new runtime acceptance is claimed. Website ingestion and public article readback follow normal merge; original evidence stays immutable.
