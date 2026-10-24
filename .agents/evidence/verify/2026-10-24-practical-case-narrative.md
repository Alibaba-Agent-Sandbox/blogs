# Practical case narrative verification

Date: 2026-10-24 UTC
Result: PASS for scoped editorial and local integration checks.
Base: `821aca4eaefa75770d715f0a56d80bb546ad3046`.

## Scope
Five Chinese article bodies, their five covers, the Registry workflow figure and the orders
chart label. Existing URLs, runnable code, generated snapshots, evidence and manifests remain
unchanged. The current user requested usage cases instead of acceptance-report narratives.

## Checks performed
- `python scripts/validate.py`: 8 posts, zero problems.
- Relative article links: 17 targets exist. Python examples: 13 AST parses pass. Shell examples:
  37 `bash -n` parses pass. SVG XML: all seven figures parse.
- All 71 files under the articles' `lab/` and `proof/` directories compare byte-for-byte with
  the published base commit. No earlier engineering evidence was rewritten.
- `git diff --check`: pass on the scoped edit.
- `BLOGS_SOURCE=<intended checkout> npm run sync:blogs`: eight posts synchronized through the
  supported integration. Node 22.22.2 and the existing lockfile-installed website dependencies.
- `npm run check`: 73 files, zero errors/warnings, nine existing informational hints.
- `npm run build`: 33 routes built successfully.
- All five rendered desktop article openings and revised covers inspected: titles, descriptions,
  figures and contents use developer tasks without assertion counters or acceptance banners.

## Editorial review
The practical flow covers setup, running the example, consuming useful outputs and managing
resource lifetime. Do not fabricate a customer story. Retain relevant application-authentication,
model/dependency, generated-workdir and interruption limitations. The orders are explicitly
synthetic and their fixed-format monetary assumptions remain stated. Historical runtime evidence
is supporting material, not the main article narrative.

Runtime and cloud tests were not rerun: this change modifies prose and diagrams only. Existing
real-backend acceptance remains in the unchanged prior records and attachments; syntax and
rendering checks here do not claim fresh cloud execution.

## Delivery boundary
Required latest-head PR CI and normal merge are checked on submission. Website publication
and actual page/figure readback are checked after deployment, recorded separately without
rewriting this pre-merge record.
