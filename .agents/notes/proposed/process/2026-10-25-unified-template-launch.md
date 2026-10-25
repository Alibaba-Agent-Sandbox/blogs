# Use one template startup in the publication tutorial

Status: proposed

## Problem

The bilingual publication tutorial still asks readers to select `--workflow application` and recommends a CLI version that cannot consume specification 5 manifests.

## Decision

Remove the selector from the current tutorial, describe one startup and all provided services, and link current installation guidance while explicitly identifying the old CLI format boundary. Keep pinned developer-journey cases, assets and historical evidence unchanged.

## API Design

Use `abx --provider alicloud-express template launch ./my-template`. Task-specific business commands remain explicit calls after the template starts.

## Alternatives considered

Keeping the flag would teach a retired author concept. Updating historical case artifacts would falsely imply they were rerun with new consumers.

## Dependencies

- [Template contract migration](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/213).
- [Template Issue](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/issues/212).
- Website consumes these source posts after compatible consumers and publication are ready.

## Test Strategy

Validate frontmatter, bilingual metadata, local links, secret patterns and scoped diff. Check all current post bodies for retired workflow options and schema examples. This prose update does not rerun old cloud or model cases.

## Acceptance criteria

Both languages describe the same direct startup, retain the historical source pins accurately and pass the blog validation gate. Website synchronization and compatible CLI publication must complete before this draft is merged.
