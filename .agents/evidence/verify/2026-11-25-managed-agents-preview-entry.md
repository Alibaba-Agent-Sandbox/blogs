# Managed Agents article preview entry — 2026-11-25

Result: PASS — scoped article validation and publication prerequisites passed.
Final PR delivery and website ingestion are tracked in the linked pull request.

Baseline: 4a36152b8a800872e3a528bfa9abdcb1b54b80e1. Three current-usage paragraphs
in posts/managed-agents-one-endpoint/index.zh.md require source installation.
The article has no English sibling. Its historical case explicitly identifies
template 0.1.4 / CLI 0.5.10 and a fixed template commit; those claims and attachments
must remain unchanged.

Independent API and parent reviews approved an exact published 0.6.0-alpha.2 npm preview entry
and official registry URL, with no new cloud/model claim, native resource commands,
dependency update or six-Harness draft inclusion. Real topic readback is required
before publication.

The web browsing service could not access the two topic URLs or npm metadata;
direct public HTTP readback is being used as a fallback. No cloud resource,
image, database or package release is needed or authorized by this article edit.

## Local checks

The initial system-Python unit-test import failed because PyYAML was absent; no
product test ran in that attempt. A separate virtual environment installed the
documented dependency, PyYAML 6.0.4, under Python 3.13. The repository unit command
then passed two tests; scripts/validate.py checked 59 posts with zero problems.
The changed installation Bash block passes bash -n and git diff --check passes.

Compared the article directory against the baseline: all 54 attachments are
byte-for-byte unchanged. Front matter, the original case/version attribution and
fixed historical source reference are unchanged. There is no invented English
translation or rewritten historical business execution.

Public npm metadata returned HTTP 200 for @agent-sandbox/cli 0.6.0-alpha.2 with the
matching version. The version-specific installation guide and existing Registry
template page also returned HTTP 200. Both requested topic URLs returned HTTP 404,
so their new article links are prepared but this change must not publish until
real pages are available. Installation availability does not establish a new
managed cloud or model acceptance run.

## Publication prerequisites and independent review

Both canonical topic URLs subsequently returned anonymous HTTP 200, with the
Agents API topic heading, the managed-agents-one-endpoint article link and the
agents-api template link in their actual HTML bodies. The initial 404 results
remain the earlier observation; they were not treated as successful publication.

Parent and API reviewers completed the final scoped review. The first candidate
0e1f6ed822d38a94da1a2e0e68f16f8a9badf48e passed
[Validate posts 45608628051](https://github.com/Alibaba-Agent-Sandbox/blogs/actions/runs/45608628051).
The evidence-only update is subject to the same normal CI before merge.

Delivery: [Blogs PR45](https://github.com/Alibaba-Agent-Sandbox/blogs/pull/45).
No cloud runtime or model was rerun; the article continues to attribute its
business results to their original versions.
