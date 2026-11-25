# Decision: Retain blogs Agents API delivery operations

Status: proposed

## Problem

The requested multi-Agent Agents API topic has a reviewed cross-repository plan, but its writing/publication steps need to live with the article source before work starts. New v1 cloud E2E and Codex acceptance are still incomplete.

## Decision

Record the topic plan here without creating or publishing a success article. Reuse bilingual posts and the existing agents-api tag; no new series/CMS model is required. Keep engineering commands/results under .agents and reader-facing instructions under posts only when their actual prerequisites and claimed outcomes are verified.

## API Design

No post, frontmatter, asset, site route or public claim changes in this record-only PR.

### Planned author operations — not a completion claim

1. Require the template owner's new v1 FC/Gateway and Qwen/Codex evidence for each case being claimed. The historical0.1.4 Qwen cloud recipe and the new local Docker Qwen case have different source/scope; neither proves a new Codex cloud result.
2. Write a concise bilingual introduction explaining the business use, one Gateway versus per-Session Sandbox, actual supported Agents, configuration/model protocol differences and useful customization/build/release paths. Provide Registry detail and actual source links at the beginning.
3. Show actual current-source CLI acquisition/deployment/manage/cleanup commands, direct HTTP and Python httpx use. There is no dedicated Gateway SDK; do not invent one or claim arbitrary OpenAI SDK compatibility. Make required keys and their purposes/sources clear; ordinary generated application tokens are not a manual prerequisite.
4. For each verified Agent case retain real tool/file outputs, dependent second-turn results and independently downloaded/runnable artifacts. Preserve original tests. Never turn a synthetic adapter, expected output or edited summary into a real Agent quote. Keep any unfinished content draft:true.
5. Link the existing related practical posts with truthful source/version scope. Do not overwrite pinned historical successes as if rerun on v1. Keep internal hashes, receipt/journal audits, raw logs and test totals in .agents, not article prose.
6. Validate content with the repository's actual entry points:

```sh
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/validate.py
```

7. Coordinate rendered sync/build and actual desktop/mobile links with the website owner. Content still originates in blogs/posts; publication follows the normal main/notify-website workflow after required CI/review. Verify tag discovery, bilingual links, examples/assets and the reciprocal Registry topic links.

No new cloud/RDS/model attempts are needed for this planning note. Record later writing, reproduction, rendering and publication executions under this owner's dated evidence. The template owner retains compute/image/lifecycle evidence; link it rather than duplicating authority.

## Alternatives considered

Publishing placeholders or unverified Agent stories would invent completion. Copying internal verification journals into a tutorial obscures user tasks. Expanding into a new series schema, CMS or navigation system adds learning/maintenance cost without delivering the requested topic.

## Dependencies

Tracking: https://github.com/Alibaba-Agent-Sandbox/awesome-templates/issues/309. Cross-repository links refer to owner branches
and do not assert that pending work is merged or published.

- [awesome-templates owner operations](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/feat/template-v1-migration-20261112/.agents/notes/proposed/process/2026-11-12-agents-api-delivery-operations.md).
- [agent-sandbox owner operations](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/blob/feat/template-v1-parser-20261112/.agents/notes/proposed/process/2026-11-12-agents-api-delivery-operations.md).
- [python-sdk owner operations](https://github.com/Alibaba-Agent-Sandbox/python-sdk/blob/feat/template-v1-runtime-20261112/.agents/notes/proposed/process/2026-11-12-agents-api-delivery-operations.md).
- [registry owner operations](https://github.com/Alibaba-Agent-Sandbox/registry/blob/feat/template-v1-registry-20261112/.agents/notes/proposed/process/2026-11-12-agents-api-delivery-operations.md).

## Test Strategy

For this note, validate frontmatter/content remains unchanged, repository unit/validation commands, relative record links and whitespace. Article/runtime/rendering/cloud checks are future gates and must be recorded separately when executed.

## Acceptance criteria

The writing/publication operations are repository-owned and indexed; no article is published by this note. The eventual topic covers real verified Agents with current CLI/HTTP/programmatic use, bilingual navigation, customization and actionable cleanup.

## Evidence

- [Record-placement verification](../../../evidence/verify/2026-11-12-agents-api-delivery-operations.md).
