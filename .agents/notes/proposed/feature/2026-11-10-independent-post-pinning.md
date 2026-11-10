# Decision: Separate featured labels from blog index pinning

Status: proposed

## Problem
The author guide and templates describe `featured` as a large article pinned above
the blog list. The requested website behavior instead uses a uniform article list,
a label for featured articles and a separate optional pinning action.

## Decision
Document `featured` as a label that changes neither ordering nor article styling.
Add optional boolean `pinned`, defaulting to false, for the website blog index.
Pinned posts appear first, newest first within that group; other website lists keep
their existing ordering. The flags can be used independently or together.

Add `pinned` to the existing boolean validation and demonstrate it as a commented
option in both language templates. No published article is selected for pinning.
Independent review and the parent integration review approved this limited contract.

## API Design
The article front matter gains optional `pinned: true | false`. Omission remains
valid. Non-boolean values fail validation, matching `featured` and `draft`.
Existing required metadata and bilingual date/category checks remain unchanged.

## Alternatives considered
- Keeping `featured` as the pin would preserve the unwanted coupling.
- Migrating existing featured posts to pinned would make an editorial choice the
  user did not request.
- Adding numeric pin priorities or publication scheduling is outside this request.

## Dependencies
The website consumer implements the schema, index ordering and labels. This
repository owns the author contract and validates the input. Track joint delivery in
[website Issue #87](https://github.com/Alibaba-Agent-Sandbox/website/issues/87);
this repository's PR must not close that cross-repository issue alone.

## Test Strategy
Run the existing full article validator plus a focused regression for absent,
boolean, combined featured/pinned and malformed pin values. Run the new tests in
PR CI and validate engineering-record links. Website rendering is verified by the
consumer repository separately.

## Acceptance criteria
- Both author templates describe featured and pinned independently.
- The guide defines defaults, labels and blog-index-only ordering in both languages.
- Existing articles remain valid; malformed pin values fail early.
- No actual article metadata or content is changed.
- Companion website support and both repositories' CI pass before joint completion.

## Evidence
[Local verification](../../../evidence/verify/2026-11-10-independent-post-pinning.md).
