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
only. Explain the actual template two-turn workflow, its download assertions and
Close/Delete. Historical independent program/heldout checks retain their exact
versions in the historical engineering supplement; they are not relabeled as
current0.1.4 output or new core delivery prerequisites.
Write final outcomes only after the corresponding run is recorded.

The article will distinguish the tested distribution from unpublished candidates,
completed turns from publication, terminal cancellation from active cancellation,
and public deletion from independent compute/resource absence. The user narrowed
final delivery to the unified Gateway, actual Sandbox Agent workflow, practical
article and resource release. Preserve real failed attempts and all19 old appendices
in one historical engineering supplement, with unchanged asset/version associations.
Do not require a new version, API/upgrade matrix or cross-repository publication.

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
- [Published CLI0.5.10 deployment readiness PR238](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/238).
- [Template PR296](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/296).

These links identify the existing implementation owners. No new cross-repository
publication or qualification is a prerequisite for this article. Formal public
CLI0.5.10 and SDK0.4.0a7 were independently installed for the current run.

## Test Strategy

Use the actual normal public deployment and its template Gateway-only two-turn
model/file check, then retain the safe report and actual command/assertion summaries.
The current hook did not preserve source originals for the article; never borrow
older generated files as current attachments or rerun only to obtain them. Confirm exact owned resource
absence independently after application cleanup. Then run the blog validator,
relative-link/record checks, secret review and applicable website preview.

## Acceptance criteria

- Each executed article step has its real command/request and actual output or exit.
- The two actual Agent turns and downloaded CSV assertions are represented faithfully; current source-original retention limits are explicit.
- Adapter, protocol, distribution and environment limits are stated accurately.
- Older API/cancel/upgrade claims remain versioned engineering history, separate from the core reader workflow.
- Temporary resources are released or a concrete unresolved resource is disclosed.
- Article assets and source helpers are reviewed; credentials and raw private logs are absent.
- Required blog checks and publication review pass before a non-draft merge.
