# Decision: Describe template publication as a usable contribution

Status: proposed

## Problem

The active bilingual publish-a-template tutorial equates catalog labels with a promotion ladder of runtime checks. It can make readers confuse listing, maintenance and verified provider behavior.

## Decision

Keep this one tutorial practical: create the source directory, submit its index entry for maintainer review, provide concrete launch/API/cleanup instructions and record the exact scope of actual runs. Keep existing schema fields. Replace the retired label-promotion summary with maintenance/development meaning and a link to the owner contribution guide. Use the published public CLI launch entry in the README example.

## API Design

N/A — no schema, status field, executable or API changes in this repository.

## Alternatives considered

Deleting status from the example would misdescribe the current index schema. Repeating the acceptance ladder would preserve the confusion. Rewriting historical case results or all articles is outside this correction.

## Dependencies

The owner normative correction must land before this post is merged: [awesome-templates PR 205](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/205). [CLI 0.4.16 publication](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/blob/af0911a99f7269718f8e6488a835bdd441ab771c/.agents/evidence/verify/2026-10-24-cli-0416-release.md) establishes the installed command version. Tracking: [blogs Issue 9](https://github.com/Alibaba-Agent-Sandbox/blogs/issues/9).

## Test Strategy

Validate all post frontmatter, changed document targets, bilingual consistency and the published CLI help. Review against the owner's actual contribution files. This documentation-only change does not run a new cloud sandbox or model task.

## Acceptance criteria

Readers can distinguish catalog inclusion from the scope of actual usage. English and Chinese match, owner semantics are merged, post CI passes and the website consumes the merged blog source.

## Evidence

[Verification](../../../evidence/verify/2026-10-24-template-publication-guidance.md).
