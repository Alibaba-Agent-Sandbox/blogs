# Decision: Versioned article entry points after CLI simplification

Status: proposed

## Problem

Unified command changes had landed, but some current examples, contributor text and cross-repository consumers still advertised retired entry points. The user requested complete implementation of the affected ecosystem synchronization.

## Decision

Current general tutorials use the unified source CLI. Versioned practical articles retain their original CLI/template versions, commands, results and attachments, with an explicit version boundary and current template-guide link at the beginning. Preserve template quick links, dates and draft state.

## API Design

No execution API or resource lifecycle change. Command examples follow the current CLI contract.

## Alternatives considered

Blind text replacement was rejected: historical runs and version-pinned cases must remain truthful. Rebuilding every template or repeating cloud matrices for documentation would not validate these text changes. Generated consumers must be refreshed from their actual source rather than hand-patched.

## Dependencies

Current CLI contract: https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/247. Template producer: https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/305. Registry and website consume the reviewed source commits after local validation.

## Test Strategy

Run owner document/link/record checks and relevant actual command or catalog checks. Verify generated consumer snapshots through their normal generators and local site builds. Record missing prerequisites and remote authentication failures separately.

## Acceptance criteria

Current user instructions resolve to supported commands; every catalog template is checked; historical commands have an explicit version/research boundary. Bilingual pages and generated consumers agree. No secrets, acceptance results or release claims are fabricated.

## Evidence

[Verification](../../../evidence/verify/2026-11-12-ecosystem-guidance-sync.md).
