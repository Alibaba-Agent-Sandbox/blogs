# Decision: Synchronize current article guidance and delivered engineering records

Status: implemented

## Problem

Recent runtime and template changes were missing from current article installation/API guidance. The record index still called delivered practical cases proposed and foregrounded source-only installation decisions. The current bilingual untrusted-code example also relied on a provider interpreter call for base, although the supported default path is process execution.

## Decision

Use published client 0.3.1a5 and standard AsyncSandbox file/process operations with finally cleanup in the current bilingual walkthrough. Preserve the publishing article's pinned validation environment while acknowledging the public release. Link the current installation and scoped template evidence from the bilingual repository README. Move delivered case decisions to implemented and supersede obsolete installation/entry decisions, with traceable links.

Keep all five pinned practical cases, runnable/generated attachments and existing verification files byte-identical. Current guidance and historical reproductions have different purposes. Do not mechanically replace version strings inside captured experiments or add status badges to the articles.

## API Design

N/A — this decision does not involve API changes. The example consumes existing AsyncSandbox.create, files.write, commands.run and kill methods; no persistent interpreter or new cloud execution is claimed.

## Alternatives considered

Updating every historical version would invalidate reproduction claims. Adding only a release summary would leave an unusable current walkthrough. Duplicating the full cross-repository audit would obscure ownership; use absolute links to the producer records instead.

## Dependencies

- https://github.com/Alibaba-Agent-Sandbox/blogs/issues/11
- https://github.com/Alibaba-Agent-Sandbox/blogs/pull/7
- https://github.com/Alibaba-Agent-Sandbox/blogs/pull/8
- https://github.com/Alibaba-Agent-Sandbox/python-sdk/pull/105
- https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/149
- https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/210

## Test Strategy

Validate post metadata and references, parse both Python examples, inspect public SDK method signatures and execute the deterministic CSV computation locally with a temporary fixture. Verify local Markdown links and ADR states, compare every historical evidence/case attachment byte with the baseline, and run the repository's normal CI. Read back the existing five published case titles and the updated articles after normal website ingestion. These checks do not repeat cloud experiments.

## Acceptance criteria

Both current walkthrough languages use the supported process/file path and public client package. Current README and record navigation explain delivered work and retain accurate historical boundaries. Old experiment bytes remain unchanged; relevant checks pass with actual delivery recorded separately.
