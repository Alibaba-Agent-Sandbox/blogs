# Decision: Make the blogs README a reader entry point

Status: proposed

## Problem

The opening accumulated current/historical version comparisons and acceptance-matrix discussion before readers reached articles. Authoring schema and deployment-notification setup occupied most of the root.

## Decision

Provide separate language READMEs with reading/source links, a short writing/validation path, draft/publication behavior and source ownership. Move the full authoring schema, style and notification setup to CONTRIBUTING.md. Keep article versions and original receipts untouched; no article or asset changes.

A README answers what this repository provides, who it serves, how to start, where to continue, how to contribute and what license applies where established. Detailed migration is a secondary guide, not the project introduction. Public usage stays separate from engineering acceptance and delivery history.

Scoped public files: `CONTRIBUTING.md`, `README.md`, `README.zh-CN.md`.

## API Design

N/A — this decision does not involve API changes. All executable behavior and public exports remain unchanged.

## Alternatives considered

- Only remove the migration heading: leaves each repository's audience and navigation problems unresolved.
- Use one identical README template everywhere: obscures the different needs of library users, catalog users, site contributors and article authors.
- Delete detailed material: useful reference and maintainer instructions should remain available through their owning guides and historical records.

## Dependencies

Existing guides, actual package/source metadata and the owning repositories linked with absolute GitHub URLs. No new runtime dependencies, release, build contract or cloud permissions.

## Test Strategy

Check changed Markdown links and anchors, incoming active links to root README headings, reciprocal language links, fenced Python syntax and the final scoped diff. Run repository documentation/record checks and applicable CI. Review examples against current source and package availability. No cloud mutation or real-model run is needed to validate this prose-only change; document checks do not establish runtime acceptance.

## Acceptance criteria

- The first screen identifies this repository's purpose and primary next action.
- Installation and examples match actual package scope and current source behavior.
- English and Chinese READMEs provide equivalent tasks and links.
- Migration, internal implementation and dated acceptance reports do not dominate the introduction.
- Detailed reference and maintainer material remains reachable.
- Local documentation checks and current-head required CI/review results are recorded honestly.

## Evidence

[Verification](../../../evidence/verify/2026-10-28-readme-audience-review.md).
