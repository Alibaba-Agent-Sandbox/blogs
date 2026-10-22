# Decision: Use current Express CLI in the bilingual walkthrough

Status: implemented

## Problem
The published CLI walkthrough still showed rejected create --template and kill --yes, with a separate note requiring translation.

## Decision
Use positional detached create and standard cleanup in both source post languages; regenerate website snapshots using its sync:blogs integration.

## API Design
N/A — this decision does not involve API changes. Proposed diagnostics interfaces, when relevant, are explicitly unimplemented design, not current configuration or routes.

## Alternatives considered
- Keep the obsolete example and ask readers to translate it — repeats an avoidable installed-CLI failure.
- Edit generated website or Registry output directly — loses source ownership and will be overwritten.

## Dependencies
Current Express CLI contract and each repository's own source integration. https://github.com/Alibaba-Agent-Sandbox/blogs/issues/5

## Test Strategy
Run frontmatter validation and website blog sync, Astro check and build.

## Acceptance criteria
Both walkthroughs have supported CLI examples and remain consistent; publication originates in blogs.

## Evidence
- [Verification](../../../evidence/verify/2026-10-22-current-express-cli-examples.md)

## Implementation
The scoped local implementation and validation are recorded above. Remote delivery is tracked by the owner PR; this status is not a claim that publication or merge already occurred. Outstanding gates remain explicit in the verification evidence.
