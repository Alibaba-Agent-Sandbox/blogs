# Five developer journey cases verification

Date: 2026-10-24 UTC
Result: PASS — scoped runtime, local editorial and integration acceptance; remote delivery tracked separately below.

Base blogs revision: `1409dc6e5a697b9075f2e2c0b6337b4201a9fed0`.
Scope: five new `posts/developer-journey-*` directories, this record, the decision note and
record index. Existing posts remain unchanged. The user requested these five public practical
cases; this is documentation of real experiments, not an all-provider production certification.

## Published artifacts and real runtime acceptance

Tests use the official checksum-verified Linux x86_64 CLI 0.4.12 and a fresh official PyPI
client/server 0.3.1a2 installation on Python 3.12.13. The independently tested npm installation
also reports 0.4.12; its tarball matches registry SHA512 integrity and SHA1 metadata. These
host distributions do not replace the runtime server pinned inside individual templates.

| Case | Final real execution | Cleanup |
| --- | --- | --- |
| CLI installation | Official binary and isolated npm/global-prefix installs; create, JSON info, exec, bounded list visibility; lifecycle script 9.47 seconds | Exact owned sandbox info reports NotFound |
| Authored Qwen application | Own Python setup; remote Node 24.16.0/Qwen 0.23.0/server 0.3.1a1; SDK/CLI/actual HTTP invoice result 51.30; 200/400/401; actual model file edits and four held-out calculations; 88.94 seconds | Exact owned sandbox info reports NotFound |
| Registry python-hello | Public source `565e546a3e1d814e840062cbdd5da4ba295e16a6`, official steps preparation, READY before create; 40 captured commands, 29 assertions, 52.826 seconds; SDK/HTTP/CLI/files/process/PTY | Exact owned sandbox and template both absent |
| One-sentence add | Public CLI fresh model generation with qwen3.8-max; create 331.54 seconds, READY at 60 seconds; 50/50 assertions; generated/embedded/cloud source bytes agree | Typed SandboxNotFoundError and exact template NotFound |
| One-call data | Three public PyPI runs: documentation, orders and propagated exception; independent csv/Decimal oracle; 10 input rows, 6 valid, 1 duplicate, 3 invalid; 19310 cents | Each observes one automatic DELETE 204 followed by exact GET 404; no fallback deletion |

The published runnable attachments are the exact files used in the final cloud runs, verified
by SHA256. Only selected sanitized evidence is included. Private recovery IDs, credentials,
model traces and raw control-plane metadata are excluded. Case 4 retains both its separately
labeled source-candidate snapshot and the final public-version generated snapshot without
hand-editing either model output.

## Documentation and integration checks

- `python scripts/validate.py`: 8 posts, zero problems.
- Source AST, SVG XML, JSON parsing and relative attachment links: pass on 83 selected files (15 Python, 7 SVG, 41 JSON, 46 relative links).
- Known credential values, raw UUID/resource identifiers, private host paths and ANSI scan: pass.
- Source manifests match the exact executed attachments; the three data proof hashes match
  their summary. Independent review verifies factual distinctions and runtime evidence; its current article hashes match all five final bodies. See the adjacent `2026-10-24-developer-journey-cases-review.json`.
- All eleven referenced public pages/Issues returned HTTP 200. Final article/asset links are checked again after publication.
- `BLOGS_SOURCE=<intended checkout> npm run sync:blogs`, `npm run check` and `npm run build`
  are exercised through the website integration. The all-five preview has 8 posts, 33 routes,
  zero Astro errors/warnings and nine existing informational hints.
- Desktop/mobile rendered inspection found the original Registry/prompt cover aspect ratios
  were clipped by the website hero. Article-owned covers were revised; no global UI change.
  Final rebuilt covers pass desktop inspection; the data article also passes mobile inspection.

`git diff --cached --check` reports two trailing spaces in the captured PTY prompt lines
of the historical/final `terminal.txt` evidence. These bytes are deliberately preserved to
keep the reviewed evidence manifests valid; executable source has no whitespace errors.

## Limits and retained failures

The early harness path, list visibility, cleanup-message and timestamp-precision mistakes are
kept separate from product defects. A previous larger numerical generated build remains open
in [CLI Issue 131](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/issues/131). The final
generated README still overstates source-directory writability; observed permissions and the
unproven root cause are recorded in [CLI Issue 132](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/issues/132).
The add business does not need to write its source directory. Tests use an owned writable home
directory for file capabilities and do not change generated permissions to manufacture a pass.

The generation timeout is explicitly configured to 1200 seconds; the cloud build wait remains
600 seconds. Neither successful add execution nor runtime pip timings establish a fix for the
larger build. Other providers/platforms, arbitrary models, general financial input, Docker/ACR
cloud deployment and destructive Team/key/quota/Volume mutations are not certified here.

## Delivery boundary

Runtime fixes and public artifacts are delivered through
[CLI PR 129](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/129),
[SDK PR 94](https://github.com/Alibaba-Agent-Sandbox/python-sdk/pull/94),
[template PR 202](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/202),
[SDK docs PR 93](https://github.com/Alibaba-Agent-Sandbox/python-sdk/pull/93) and
[website PR 38](https://github.com/Alibaba-Agent-Sandbox/website/pull/38).

This pre-merge record does not claim the new blog PR is merged or the articles are publicly
served. Required CI, exact remote merge state and public page/asset hashes are checked after
submission; post-merge evidence is recorded separately without rewriting merged history.
