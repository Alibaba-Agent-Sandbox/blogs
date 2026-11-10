# Decision: Index recent changes to reader-focused articles and independent pinning
Status: proposed

## Problem

Recent implementation, user-experience changes and delivery status are spread across
owner records, pull requests and workspace reports. The user requested that recent
changes be retained under each owning repository's `.agents/` and pushed.

## Decision

Keep this dated index in blogs; link existing canonical decisions and immutable
verification instead of copying their reports or rewriting historical acceptance.
This index adds no product behavior and does not change any older ADR's lifecycle.

### Owner changes and canonical records

Merged recent changes make template practice articles actionable, add early Registry/source links, and define pinned independently of featured. The managed Agents article describes the real single-Gateway business workflow, available HTTP integration and user-owned cleanup. Historical fixed-release tutorials retain their actual version context. Blog content remains owned here.

- [Reader-focused template articles](../../../notes/proposed/process/2026-11-09-reader-focused-template-articles.md).
- [Article verification](../../../evidence/verify/2026-11-09-reader-focused-template-articles.md).
- [Independent post pinning](../../../notes/proposed/feature/2026-11-10-independent-post-pinning.md).
- [Pinning validation](../../../evidence/verify/2026-11-10-independent-post-pinning.md).
- [Managed Agents practice](../../../notes/proposed/feature/2026-11-06-managed-agents-best-practice.md).
- [Current community QR](../../../notes/proposed/process/2026-11-10-refresh-community-qr.md).

### Mainline and candidate boundary

- Mainline observed: `eceef44f732fb9e2f4387f177c57f922b692a000`.
- Candidate/source observed before this records commit: `eceef44f732fb9e2f4387f177c57f922b692a000`.
- A dedicated records-only branch starts from the refreshed origin/main; no implementation PR is inherited.
- The unified source CLI is different from published CLI 0.5.10. This task does
  not issue npm/PyPI releases, deploy sites or certify changed templates.

Recent mainline changes, inspected from the refreshed Git history:

| Date | Commit | Change |
| --- | --- | --- |
| 2026-11-10 | [eceef44f732f](https://github.com/Alibaba-Agent-Sandbox/blogs/commit/eceef44f732fb9e2f4387f177c57f922b692a000) | docs: replace community QR image and join link (#37) |
| 2026-11-10 | [8d9b01650036](https://github.com/Alibaba-Agent-Sandbox/blogs/commit/8d9b0165003638f9f7bdb58f1c98bce72eba9a18) | docs: announce preview release schedule and developer community (#36) |
| 2026-11-10 | [514ba3fe85a2](https://github.com/Alibaba-Agent-Sandbox/blogs/commit/514ba3fe85a283160c814555e60a1d15b34b676d) | feat: define independent blog post pinning (#35) |
| 2026-11-09 | [a618ddfc0f2e](https://github.com/Alibaba-Agent-Sandbox/blogs/commit/a618ddfc0f2ee607836b3e6df4ccb77aba744475) | docs: make template articles actionable and easy to find (#34) |
| 2026-11-07 | [01e464a01999](https://github.com/Alibaba-Agent-Sandbox/blogs/commit/01e464a0199945ecc48e50fbb19e78e489dcac1d) | docs: add single-gateway sandbox agent practice (#33) |

### Remaining delivery limits

The unified CLI refactor has no blog-content patch. This records-only branch does not rewrite historical command examples, publish a new article or imply the seven Draft implementation PRs are merged. Rendering/layout remains owned by website.

## API Design

N/A — this decision does not involve API changes. Existing runtime, credential,
source identity and resource ownership contracts remain with their original owners.

## Alternatives considered

- A workspace-only summary cannot travel with an independent checkout.
- Copying all cross-repository reports duplicates authority and may expose private logs.
- Marking all proposed records implemented would confuse source work with accepted delivery.
- Combining unrelated local changes or permission-only differences in this commit
  would conceal the actual records scope.

## Dependencies

Existing owner records and GitHub PR/commit state. Coordinated implementation is
tracked in [CLI Issue #244](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/issues/244).
Each repository retains its own branch, record, verification and push.

## Test Strategy

Check the new record structure, relative links, pinned Git source revisions and
scoped diff; run the owner's applicable documentation/health checks. Query PR/CI
state separately from local checks. Do not run cloud tests solely to validate prose.

## Acceptance criteria

- Recent owner work is reachable from `.agents/README.md` with dated source references.
- Merged, Draft, failed, unrun and planned work remain distinguishable.
- Existing historical evidence and unrelated work remain intact.
- Documentation checks and remaining gates are recorded; scoped commits are pushed
  to task branches and remote branch hashes are independently compared.

## Evidence

- [Records verification](../../../evidence/verify/2026-11-10-recent-change-index.md).
