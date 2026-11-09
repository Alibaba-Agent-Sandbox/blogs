# Reader-focused template articles: verification

Date: 2026-11-09. Result: PASS for the local documentation/example checks below.
Remote current-head CI, merge and website publication are separate delivery gates.

## Scope and source

Base: blogs `01e464a0199945ecc48e50fbb19e78e489dcac1d`. Changes are the managed
Agents Chinese article, three downloadable example files, introduction links in
56 other article language files, the bilingual contributor rules and these
repository-owned records. The managed article has no pre-existing English version.
There are 56 associated article directories / 57 language files including the
rewritten article; they cover the 51 catalog IDs. Six drafts remain unpublished.
The three general/custom-template articles without an established catalog ID
are not assigned an invented relationship.

The existing engineering supplement and prior cloud receipts/assets were not
changed. Public prose no longer repeats their internal timestamps, hashes,
acceptance totals, resource inventories or cleanup journal vocabulary.

## Independent design and review

Three collaborators independently reviewed audience fit, fixed CLI/SDK/Gateway
contracts and article-to-template associations before implementation. A subsequent
independent review approved the rewritten article and all 57 linked language files.
The root reviewed both clients and resolved two example concerns: Decimal parse
errors now retain useful resource IDs, and the Bash first artifact page omits an
empty cursor, matching the established public runner.

CLI commands were checked against `v0.5.10:src/cli/commands/app.ts`; public
runtime exports against `v0.4.0a7:client-sdk/src/agent_sandbox/managed_agents/__init__.py`.
HTTP inputs, terminal states, submission headers, relative artifact paths and
Close operations were compared with the managed service and template smoke
implementation. No business CLI command or dedicated consumer SDK was invented.

## Executed checks

| Check | Result |
| --- | --- |
| `python scripts/validate.py` | PASS: 59 article directories, zero problems |
| Article fenced examples: `ast.parse` and `bash -n` | PASS: one Python block, 17 Bash blocks; two CSV blocks retained |
| `python -m py_compile posts/managed-agents-one-endpoint/run_csv.py` and `bash -n posts/managed-agents-one-endpoint/run_csv.sh` | PASS |
| Local HTTP example fixture, independently rerun by root | PASS: Python and Bash each exercise success (27 requests), uncertain second turn (16), create503 (3, only one create POST), malformed CSV (8) |
| Failure behavior | PASS: nonzero exit, known resource/request IDs retained, no automatic resubmit or Close/Delete; no raw secret/model output |
| Success behavior | PASS: upload, same Session/two turns, paginated turn-specific artifacts, CSV checks, Close polling then Session/File deletion; downloaded Agent code never executed locally |
| Template association checks | PASS: all 51 IDs are known; practice slugs match exactly; additional custom cases identify the actual base |
| Quick-link HTTP check | PASS: 51 distinct Registry URLs including English base return200 with matching titles; source/managed-guide paths exist |
| Existing article preservation | PASS: all frontmatter and bodies outside the rewritten article are unchanged after removing the one added link paragraph; six draft flags preserved |
| `BLOGS_SOURCE=<blog-checkout> npm run sync:blogs` in isolated website preview | PASS: 59 articles ingested |
| `npm run check` in website preview | PASS: zero errors/warnings, seven existing hints |
| `npm run build` in website preview | PASS: 1,269 pages built |
| Rendered output and downloads | PASS: article Registry link and HTTPX/client links render; all three downloadable assets match their source bytes |
| `git diff --check` | PASS |

Website preview revision: `5718311bbb03abc4084d8ee89b2ae87f2d523244`, using its
existing installed dependencies and unchanged package lock. Product repositories
and the previous worktrees' unrelated modifications were preserved.

The first patch operation attempted delete/add of the same article in one patch
and was rejected without modifying it. The subsequent full-file write succeeded.
No failed operation was treated as completed validation.

## Limits and cleanup

The client checks use a local HTTP fixture; they do not run a new model, Sandbox,
database or FC deployment. The article's earlier Qwen business result retains its
original template0.1.4 acceptance scope. No new cloud resources, credential copies,
Actions secrets, SDK/CLI release or manual website deployment was needed.
Temporary local fixture servers terminate after the checks.
