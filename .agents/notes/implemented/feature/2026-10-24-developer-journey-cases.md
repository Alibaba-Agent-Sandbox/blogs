# Decision: Publish five reproducible developer journey cases

Status: implemented

## Problem
The user requested a new developer's public-documentation journey covering CLI installation,
an authored Qwen application, a Registry template, one-sentence generation and one-call data
processing. Articles must describe actual cloud behavior and retain reproducible evidence,
rather than infer successful deployment from generation or submission.

## Decision
Publish five Chinese practical cases with original SVG diagrams, explicitly selected runnable
attachments and sanitized verification summaries. Keep historical failed attempts separate
from final passes. Check public installation artifacts and the website integration before
publishing. Final public CLI/SDK executions have passed; remove draft flags only for reviewed complete cases.

## API Design
No library API changes. Examples consume public CLI, ProviderSandbox, application-client and
declarative APIs. Examples distinguish host client/server distributions from the runtime server
in each template. Application requests use resolved bindings and their authentication headers.

## Alternatives considered
Publishing screenshots or model completion messages alone does not establish behavior.
Publishing the whole experiment workspace risks exposing recovery identifiers and credentials.
Hand-editing generated source and calling that a successful fresh generation would obscure the
result. These alternatives are rejected in favor of source hashes, explicit scope and real runs.

## Dependencies
- CLI fixes: https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/129
- SDK runtime fix: https://github.com/Alibaba-Agent-Sandbox/python-sdk/pull/94
- Template guide fix: https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/202
- SDK documentation fix: https://github.com/Alibaba-Agent-Sandbox/python-sdk/pull/93
- Website install entry: https://github.com/Alibaba-Agent-Sandbox/website/pull/38

## Test Strategy
Run the repository frontmatter/local-reference validator, source syntax and source-hash checks,
strict known-secret/resource-identifier scans and public link checks. Sync the posts through the
website's supported BLOGS_SOURCE entry, check/build and inspect desktop/mobile rendering.
Runtime acceptance uses actual published artifacts, independent business expectations and
exact owned-ID cleanup, including the data decorator exception path. Record skips and unresolved
limits explicitly. Verify the merged posts and public website URLs/assets after publication.

## Acceptance criteria
Each scenario has a detailed article, runnable complete files, an original figure, explicit
versions/prerequisites, observed results and cleanup instructions. Published evidence contains no
credentials, account identifiers or private logs. The small generated add application's success
does not claim to resolve the larger numeric environment's bounded build timeout. Required CI
and independent review pass; actual remote merge and website publication are read back.

## Delivery confirmation

Merged in https://github.com/Alibaba-Agent-Sandbox/blogs/pull/7. Current public page/title readback is recorded in [the later synchronization evidence](../../../evidence/verify/2026-10-24-current-documentation-sync.md); original verification files remain unchanged.
