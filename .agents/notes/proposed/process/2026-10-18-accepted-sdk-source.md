# Decision: Point current source-install examples to the accepted native SDK
Status: proposed

## Problem

The paired archive recipe installs a source revision before the accepted auth,
mutation recovery and builtin native-transport fixes. Runtime version0.3.0 alone
does not identify those changes.

## Decision

Update current English/Chinese post archive URLs to accepted immutable
SDK e86cb0be24e0083a27396b260298e7cf27b660d6. Keep both distributions on the same
commit and preserve historical records, frontmatter, assets and article behavior.
Correct the companion publishing post: complete bilingual file/design requirements, experimental-until-verified status, local source runtime prerequisites, existing generation2 deploy syntax and provider evidence/cleanup boundaries. No instruction to delete an existing shared template. Sync website snapshots from canonical posts rather than editing copies.

## API Design

No API or publication change. Source installation includes the accepted fixes;
public package-index availability is not claimed.

## Alternatives considered

- Keep the older pin: readers miss the accepted native reliability fix.
- Use mutable main: loses the tested source identity.
- Edit only the website copy: violates article ownership.

## Dependencies

Accepted runtime: https://github.com/Alibaba-Agent-Sandbox/python-sdk/pull/57.
Website integration: https://github.com/Alibaba-Agent-Sandbox/website/pull/6.

## Test Strategy

Fresh venv executes both displayed archive installs, imports matching0.3.0
packages and passes pip check. Validate every post and website sync/check/build.
This verifies installation, not a new execution of every tutorial/cloud scenario.

## Acceptance criteria

- Both language source URLs and both distributions use the tested same commit.
- Blog validation and website rendering integration pass.
- No index publication, cloud or historical-evidence claim is inflated.
