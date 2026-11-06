# Decision: Document the managed Agents single-endpoint workflow from actual results

Status: proposed

## Problem

The managed Agents template places the business Gateway outside per-Session
Sandboxes. Users need one reproducible article covering deployment, actual coding
and file results, continuation, lifecycle behavior and resource release. Earlier
source-only integration and local protocol tests cannot substitute for the final
hosted deployment or a public distribution.

## Decision

Prepare a Chinese practical article with actual commands and sanitized outputs
for every executed step. Keep model credentials, Sandbox management access and
cloud deployment credentials server-side. The business example uses the Gateway
only. Independently validate the actual repaired program inside its owned Sandbox,
preserve original tests, and compare the executed source with downloaded artifacts.
Write final outcomes only after the corresponding run is recorded.

The article will distinguish the tested distribution from unpublished candidates,
completed turns from publication, terminal cancellation from active cancellation,
and public deletion from independent compute/resource absence. Old Sessions and
new Sessions must be checked separately when the model adapter changes during an
application upgrade. Preserve real failed attempts in owner engineering evidence.

## API Design

N/A — this article does not add or change API routes. Examples use the delivered
capabilities and clearly state their supported scope.

## Alternatives considered

- Publishing a design walkthrough with representative output would not establish
  the requested real execution and cleanup results.
- Copying internal acceptance matrices into the article would obscure the reader's
  deployment and application tasks. Keep those in owner engineering evidence.
- Running downloaded model-generated code on the host would cross the intended
  execution boundary. Independent execution remains inside the owned Sandbox.

## Dependencies

- [Runtime and private bridge PR156](https://github.com/Alibaba-Agent-Sandbox/python-sdk/pull/156).
- [CLI deployment lifecycle PR235](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/235).
- [Template PR296](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/296).
- [Registry consumer PR92](https://github.com/Alibaba-Agent-Sandbox/registry/pull/92).

These links identify work under review; they do not assert merge or release state.

## Test Strategy

Use the actual hosted Gateway and actual selected model/adapter, download exact
CSV/source/report artifacts, run independent original and heldout checks in the
owned Sandbox, and retain a sanitized step transcript. Validate only the active
cancel and upgrade/drain behavior actually exercised. Confirm exact owned resource
absence independently after application cleanup. Then run the blog validator,
relative-link/record checks, secret review and applicable website preview.

## Acceptance criteria

- Each executed article step has its real command/request and actual output or exit.
- The two-turn CSV repair/extension and immutable downloads are independently verified.
- Adapter, protocol, distribution and environment limits are stated accurately.
- Any active-cancel, stable-endpoint upgrade or retire claim has its own actual evidence.
- Temporary resources are released or a concrete unresolved resource is disclosed.
- Article assets and source helpers are reviewed; credentials and raw private logs are absent.
- Required blog checks and publication review pass before a non-draft merge.
