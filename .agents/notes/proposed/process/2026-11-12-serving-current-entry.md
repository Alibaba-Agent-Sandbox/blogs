# Decision: Current managed Agents serving entry

Status: proposed

## Problem

The current article retained old app build/plan/apply and whole-repository clone
steps behind a version banner. The user explicitly requested the complete
Serving-template usage path be updated after the CLI simplification.

## Decision

Show template init by catalog name, named root deploy/status/logs/recover/delete,
private binding setup and the still-required Python/httpx business-hook setup.
Preserve the original business HTTP clients, artifacts and case results with
explicit 0.1.4/CLI0.5.10 attribution and a fixed source reproduction link.

## API Design

No Gateway API or business-client behavior change. Python uses httpx, not an
invented dedicated Gateway SDK.

## Alternatives considered

Leaving only a generic old-version banner obscured the current user workflow.
Removing Python setup would break the actual afterReady business script. New
cloud deployments or changing image dependencies are unnecessary for this prose.

## Dependencies

Current CLI: https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/248.
Template source: https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/306.
Generated website snapshots must come from this source.

## Test Strategy

Validate frontmatter, existing script tests, shell/Python code syntax, links,
source/asset byte preservation, and website sync/build/rendered links. Actual
source acquisition and preview are verified at the template owner.

## Acceptance criteria

All current deployment/manage commands resolve to supported entries. Historical
results are attributed to their actual versions. No new cloud/model claim,
credential disclosure or business script modification.

## Evidence

[Verification](../../../evidence/verify/2026-11-12-serving-current-entry.md).
