# Verification: Current developer journeys

- Date: 2026-10-25
- Result: PARTIAL — four final public-release cases pass; the OpenSandbox Registry case is pending its public-source run.
- Issue: https://github.com/Alibaba-Agent-Sandbox/blogs/issues/14
- Baseline: public website installer CLI 0.5.1, official PyPI client 0.4.0a1, Linux/Python 3.13. Model and provider credentials were injected from the process environment; values are excluded.

## Earlier public-release baseline tasks

1. Fresh website installer verified its checksum and installed CLI 0.5.1. Express base create/info/exec hello/list/kill and an independent not-found lookup passed.
2. Qwen Code 0.23.0 was installed in a sandbox created by the public SDK. It performed a real model edit of calculator.py, wrote REPORT.md and passed four independent arithmetic checks. invoice_total returned 51.30 through SDK, CLI and POST. Missing parameters returned 400; requests without both application credentials and with both credentials wrong returned 401. The exact sandbox was deleted and absence confirmed.
3. Declarative Pandas processing returned 6 clean rows and 19310 cents from the 10-row input, matching an independent local csv/Decimal oracle. Documentation and deliberate-failure cases also ran remotely. Each run recorded exactly one create/delete and independent HTTP 404, without fallback cleanup.

## Baseline failures retained

- Public standalone `template launch` failed E4001 for its missing provider source directory (CLI Issue 156).
- Public sentence generation omitted base.image and embedded stale commands.py bytes; it stopped before cloud creation (CLI Issue 157).
- A model-correction candidate still generated invalid YAML and was discarded; it is not the final implementation.
- The old Registry article pinned spec v4 source: native deployment/create/exec succeeded but capabilities correctly rejected the obsolete cached manifest. Its exact sandbox/template were cleaned and absence confirmed.
- The old Qwen auth-negative test removed only Authorization while retaining a valid application X-Access-Token, so its 401 assertion was invalid. Corrected requests passed; this was a test defect, not an authentication bypass.

## Source-candidate reruns

Three fresh real model-to-Express deterministic recipe candidates passed 50/51/51 assertions. The final ordered candidate includes independent cloud/local source SHA256 equality, CLI files/system/process/PTY, SDK/POST arithmetic cases, non-root application directory write/read/delete and exact sandbox/template absence. Candidate package identity remained 0.5.1; these are not public 0.5.1 fixed-package claims. Full details belong to CLI PR159.

## Commands and local checks

- `python -m venv` followed by official PyPI `agent-sandbox-client==0.4.0a1`, PyYAML 6.0.3 and httpx: PASS.
- `python -m pip check`: PASS.
- `python scripts/validate.py`: 8 posts, 0 problems (intermediate prose).

## Final public CLI 0.5.3 / Python 0.4.0a2 reruns

These runs use the official website standalone installer, ordinary fresh public PyPI installation, real cloud APIs and a real model where required. Each has separate `proof/public-20261025-cli-0.5.3-sdk-0.4.0a2/` receipts. The paired server publication workflow [40198182884 attempt 2](https://github.com/Alibaba-Agent-Sandbox/python-sdk/actions/runs/40198182884/attempts/2) and CLI [five-platform release 40203181574](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/actions/runs/40203181574), [npm publication 40203562691](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/actions/runs/40203562691) completed successfully. Failed v0.5.2 remains an unpublished immutable tag; these cases use actual public v0.5.3.

1. CLI installation/lifecycle: PASS. Official script verifies SHA, creates a sandbox, runs hello through CLI exec, reads info/list and kills it. Independent public SDK typed NotFound confirms absence. The first standalone run selected version 0.5.3 explicitly. A separate fresh default website installer run (no ABX_VERSION or download-base override, empty HOME, working directory outside the checkout) then selected 0.5.3, verified SHA/PATH and passed real base/code-interpreter lifecycle, files, structured template-info and noisy/silent deadline cleanup checks. Both exact owned sandboxes had independent typed NotFound. The default-install receipts are retained separately alongside this case.
2. Self-written Qwen SDK application: PASS. Node 24.16.0 (required because Qwen 0.23.0 needs >=22 and the base has 20.20.2), exact official archive SHA/SRI, existing SDK uploads, standard npm local-package installation and remote server 0.4.0a2. Real Qwen edits calculator.py and REPORT.md; four independent arithmetic cases pass. SDK/CLI/POST return 51.30; missing args return 400, missing/wrong application credentials return 401. CLI and independent SDK verify absence. Four prior cold-install failures remain in `installation-attempts.json`; omitting optional extensions alone did not fix slow downloads. GNU timeout without kill-after was not a hard 90-second bound. The final example uploads verified official archives and uses kill-after plus the SDK total 300-second deadline, without extending it. Only headless file tools are covered.
3. Registry source: final public Express default source launch fails E7020 before build because this execution host has no Docker. No cloud resource is created. This remains a failure for that provider/path. The original scenario did not require Express; the documented primary case is being changed to the existing real Docker-backed OpenSandbox public Registry runner, pending public-source execution after template PRs 222/224. Candidate or prepared-image results are not substituted for that final run.
4. Sentence-generated application: PASS, 53/53 assertions. Real model, actual standalone CLI 0.5.3 and remote server 0.4.0a2. CLI files/process/PTY/system operations, source-byte identity, non-root writable directory, SDK, POST business cases, 400/401/404 behavior and exact sandbox/template absence. The article links a new captured public-release source directory; older a1 captures remain unchanged.
5. One-call data processing: PASS for data, documentation and deliberate-failure cases. Pandas 3.0.3 processes 10 input rows into 6 valid rows and 19310 cents, matching an independent local csv/Decimal oracle. Each run records exactly one create/delete and independent HTTP 404. No fallback cleanup replaces the decorator's delete.

## Remaining

- Fresh public OpenSandbox Registry template launch, actual host HTTP/API and CLI exec/upload/download round trip using the existing runner.
- Final article rendering/relative links, source hashes, current-release records, normal PR checks and publication.

## Current public CLI 0.5.5 / Python 0.4.0a6 runs

CLI PR179 merged normally at `3f7fa28e16888a5489980dc56c86d6c71c11c4a0` after nine required checks. All five platform builds passed in [40229274612](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/actions/runs/40229274612); the official [v0.5.5 release](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/releases/tag/v0.5.5) and [npm publication 40229548597](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/actions/runs/40229548597) succeeded. The public package has twelve release assets. A fresh public Linux binary and official npm install passed the installed-artifact checker; this is separate from a website default-installer test.

New `proof/public-20261025-cli-0.5.5-sdk-0.4.0a6/` directories preserve current receipts. No older receipt is relabelled.

1. CLI installation and lifecycle: PASS using a fresh official npm install, real base creation, info/list/exec and deletion, plus an independent public SDK typed NotFound lookup.
2. Self-written Qwen SDK application: PASS with exact official host assets uploaded through the SDK, real model file edits and four independent arithmetic checks. SDK, CLI and HTTP return invoice total 51.30; invalid arguments and wrong/missing application credentials return the expected errors. Independent typed NotFound confirms deletion.
3. Registry source: PENDING the final public OpenSandbox default Git/Docker run. The separate Express default Docker E7020 failure remains blocked and is not replaced by native steps results.
4. Sentence-generated application: PASS, 54/54 assertions, a fresh standalone CLI and HOME, first managed Qwen installation, strict single-JSON receipt, actual remote server 0.4.0a6 and independently confirmed sandbox/template absence. Actual generated files and their hashes are captured in a new `generated-public-20261025-0.5.5/` directory. The model README is preserved output; reviewed article instructions remain the guidance.
5. One-call data processing: PASS for the real Pandas processing, documentation and intended-failure examples. Each owns one create/delete. The independent SDK confirms all three exact IDs are absent; the independent local csv/Decimal oracle agrees on six valid rows and 19310 cents.

A separate public CLI-generated MCP application also passed actual loopback HTTP authentication, initialization/catalog and five real cloud tool calls, with independent sandbox/PID absence. Earlier startup-probe failures remain separate receipts; an ASGI-only run is not presented as network HTTP proof.

A separate no-model repeat launches the exact frozen generated source through the public CLI unified launch path. The original README curl (only replacing its application URL) returns HTTP 200/result 8 using Bearer alone. Missing and incorrect application credentials return 401; the owned sandbox and template have independent typed absence. Source and README hashes remain unchanged. This is a separate receipt, not a replacement of the fresh model-generation run.

The final Registry receipt, its actual provider commit, final links/rendering and normal PR review/CI remain pending. This draft remains unpublished.
