# Decision: Agent API topic discovery

Status: proposed

## Problem

Readers need one place to choose the hosted Agent Harness and understand the shared
protocol. Existing native Sandbox practices and old managed results have different scope.

## Decision

Bilingual shared Agent API/Harness selection guide; historical Qwen article identifies fixed source/results and no longer mixes retired binding/deploy/delete instructions with the new recipe.
Keep development/acceptance status explicit; no new real-cloud/model result is inferred.

## API Design

N/A — no business HTTP API changes. Public topic paths are `/topics/agents-api/` on
Registry and `/blog/topics/agents-api/` on the website, with matching `/en/` routes.

## Alternatives considered

Avoided tagging every native Sandbox practice as an accepted hosted application.
Avoided duplicated catalog identities or hand-written website article snapshots.

## Dependencies

- https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/311
- https://github.com/Alibaba-Agent-Sandbox/registry/pull/102
- Article source: https://github.com/Alibaba-Agent-Sandbox/blogs
- Rendering source: https://github.com/Alibaba-Agent-Sandbox/website

## Test Strategy

Run the owner's required local checks and paired browser navigation/layout verification.
Record executed commands, actual failures and scopes separately from cloud acceptance.

## Acceptance criteria

Both languages expose the topics through their lists. The six hosted identities are
unique and link only to real catalog routes or reviewed development source. Actual posts
are aggregated without fabricated case studies. Historical template links remain useful.
Owner records and normal PR/check/review gates accompany delivery.

## Evidence

[Local verification](../../../evidence/verify/2026-11-17-agents-api-topics.md).
