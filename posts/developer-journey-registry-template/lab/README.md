# Registry python-hello lab

This exact standalone POSIX/Python attachment passed a real Express run with official abx 0.4.12 and public PyPI agent-sandbox-client 0.3.1a2 on 2026-10-24: 29 assertions, 40 captured commands, exact sandbox/template cleanup confirmed. SHA256: `871e2d60fcabeb91c3974607edd898a1b55efce6e313875d407fa691956fc73e`.

The article contains full setup and credential variable names. Install PyYAML 6.0.3 as well. The pinned remote server remains package 0.3.0 from source e2cb27e24fde0a67112f82b8d44af463445a5d1a. The host's optional server package is a separate installation.

Run from a new lab directory after installing dependencies and configuring Express:

```bash
python 03_registry_end_to_end.py --abx "$(command -v abx)" \
  --source-ref 565e546a3e1d814e840062cbdd5da4ba295e16a6 \
  --build-timeout 900 --output ./registry-proof-0412-a2
```

The output directory must not exist. No workspace, .env, harness, local Docker, or private repository is needed. The script creates billable resources and cleans up only exact owned IDs. Do not publish the private recovery directory printed at startup. Inspect output before sharing, including executable paths and terminal controls.

`evidence/release-0412-a2/` contains selected final public proof with original/publication hashes and exact attachment SHA. `evidence/historical-0411-a1/` preserves earlier-version facts and its original manifest, including a prior script hash; it does not describe the current attachment bytes. That historical manifest uses the original evidence-package layout. No historical result has been relabeled as a new-release pass.
