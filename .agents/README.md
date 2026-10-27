# Engineering records: blogs

Pending: [unified template launch tutorial](notes/proposed/process/2026-10-25-unified-template-launch.md) · [verification](evidence/verify/2026-10-25-unified-template-launch.md). Current publication guidance uses one startup without a workflow selector; pinned historical cases retain their original scope.

Current documentation: [public installation and supported walkthrough](notes/implemented/process/2026-10-24-current-documentation-sync.md) · [verification](evidence/verify/2026-10-24-current-documentation-sync.md).

- Current articles use the public client installation and documented process/file or application interfaces. CLI 0.4.17 and Python 0.3.1a5 are release identities, not proof that every post ran again on them.
- The five practical cases were delivered in [PR #7](https://github.com/Alibaba-Agent-Sandbox/blogs/pull/7) and rewritten for usage in [PR #8](https://github.com/Alibaba-Agent-Sandbox/blogs/pull/8). Their pinned CLI 0.4.12/Python 0.3.1a2 scripts, generated snapshots and evidence remain historical.
- [PR #10](https://github.com/Alibaba-Agent-Sandbox/blogs/pull/10) removed verification-stage promotion from the publishing tutorial. Catalog maintenance labels do not certify runtime behavior.
- [CLI #132](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/issues/132) is now closed; its old generated snapshot and the prior failure record remain unchanged. [CLI #131](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/issues/131) is still open. Default template smoke and HTTP wait-time fixes do not establish a fix for that generated environment build.

The links below include historical and superseded decisions. Immutable verification files describe their original date, versions and scope.

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

- [Accepted SDK source recipe](notes/superseded/2026-10-18-accepted-sdk-source.md).

- [Consumer entry compatibility](notes/superseded/2026-10-19-consumer-entries.md) · [verification](evidence/verify/2026-10-19-consumer-entries.md)

- [Use current Express CLI in the bilingual walkthrough](notes/implemented/process/2026-10-22-current-express-cli-examples.md) · [verification](evidence/verify/2026-10-22-current-express-cli-examples.md)

Developer journey cases: [decision](notes/implemented/feature/2026-10-24-developer-journey-cases.md) · [verification](evidence/verify/2026-10-24-developer-journey-cases.md).

- [Practical case narrative](notes/implemented/process/2026-10-24-practical-case-narrative.md) · [verification](evidence/verify/2026-10-24-practical-case-narrative.md).

- [Template publication guidance](notes/implemented/process/2026-10-24-template-publication-guidance.md) · [verification](evidence/verify/2026-10-24-template-publication-guidance.md).

Historical installation/source-pin decisions are superseded by the current public-installation and explicit SDK-entry guidance above. Their original assumptions and evidence are retained, not rewritten as current recommendations.

- [Template practice series](notes/proposed/feature/2026-10-27-template-practice-series.md) · [verification](evidence/verify/2026-10-27-template-practice-series.md).

- [More template practice cases](notes/proposed/feature/2026-10-27-template-practice-more.md) · [verification](evidence/verify/2026-10-27-template-practice-more.md).

- [Interpreter expenses practical case](notes/proposed/feature/2026-10-27-interpreter-expenses-case.md) · [verification](evidence/verify/2026-10-27-interpreter-expenses-case.md).

- [Crush practical delivery case](notes/proposed/feature/2026-10-27-crush-practice-case.md) · [verification](evidence/verify/2026-10-27-crush-practice-case.md).
