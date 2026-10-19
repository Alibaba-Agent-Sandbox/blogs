# Engineering records: blogs

Current review: [installation guidance](notes/proposed/process/2026-10-16-installation-review.md).
Validation: [verification record](evidence/verify/2026-10-16-installation-review.md).

This version-controlled directory records why this repository changes and how the change was
verified. Scope: post structure, frontmatter, examples, assets and publication integration. New engineering records use English.
Read [README.md](../README.md) and existing contributor/test instructions first.

## Ownership and layout

A record belongs to the repository that owns the modified files. For changes spanning
repositories, keep a scoped record in each owner and link related Issues, PRs and records
using absolute GitHub URLs. Do not use sibling-relative links or duplicate another owner's ADR.

- `notes/proposed/<category>/YYYY-MM-DD-<slug>.md`: decisions pending acceptance.
- `notes/implemented/<category>/YYYY-MM-DD-<slug>.md`: accepted decisions reflected in the code.
- `notes/rejected/YYYY-MM-DD-<slug>.md`: rejected decisions, with rationale (flat directory).
- `notes/superseded/YYYY-MM-DD-<slug>.md`: replaced decisions (flat; add `Superseded-by:`).
- `evidence/verify/YYYY-MM-DD-<slug>.md`: point-in-time validation summaries.

Categories are `architecture`, `feature` and `process`. Create directories only when needed.
The ADR `Status:` must match its directory; move the file and update status together.
Local implementation does not establish a PR's merge state.

## What every change records

Include an ADR or short process note and verification evidence with each change, including
docs, tests and configuration. Reuse a relevant unmerged task record when appropriate.
The note records problem, decision, rationale, affected files/contracts and acceptance criteria.
Use the following ADR sections in order; routine changes may keep them brief:

~~~markdown
# Decision: A descriptive title

Status: proposed

## Problem
## Decision
## API Design
## Alternatives considered
## Dependencies
## Test Strategy
## Acceptance criteria
~~~

Use `N/A — this decision does not involve API changes.` when appropriate.
An optional `## Evidence` section links to verification and Issue/PR URLs.

## Verification evidence

Record date, tested revision or exact scoped files, environment relevant to the check,
actual commands and exit results, behavior verified, and checks not run with reasons.
Use `Result: PASS | PARTIAL | BLOCKED | FAIL`; required missing checks prevent completion.
Document resource cleanup when tests create resources. Keep established template/provider
acceptance evidence in place and link to it instead of copying raw logs.

Merged evidence is immutable. Add a new dated file for a later run; use a distinct suffix
for multiple runs on the same date. Do not include secrets, personal data, machine-local
paths or unsanitized logs. A mock run, local runtime run and real-backend run are separate claims.

## Contribution workflow

For an authorized contribution, the normal path is scoped branch → implementation and tests →
PR → merge after required CI and reviews. A reproducible bug or unresolved problem should
reuse an existing owner Issue or receive a focused Issue with reproduction and acceptance
criteria. Routine docs/process changes can reference the original request instead.
Follow local Issue/PR templates and security reporting rules.

Preserve pre-existing work; stage only this task's paths/hunks and use Conventional Commits.
Include a local ADR/note and verification evidence in every PR. Link the Issue and explain
behavior, validation and limitations. Inspect CI/review on the latest head before merging
with the allowed method. Do not bypass protection or required review. Verify remote merged
state and Issue resolution; a pending queue entry is not a merge.
Explicit local-only, draft-only, review-only and no-merge instructions limit this workflow.
If access or a required gate blocks publication, finish safe local work, retain concrete
drafts/patches and report the blocker without claiming an Issue, PR or merge exists.

- [Accepted SDK source recipe](notes/proposed/process/2026-10-18-accepted-sdk-source.md).

- [Consumer entry compatibility](notes/proposed/process/2026-10-19-consumer-entries.md) · [verification](evidence/verify/2026-10-19-consumer-entries.md)
