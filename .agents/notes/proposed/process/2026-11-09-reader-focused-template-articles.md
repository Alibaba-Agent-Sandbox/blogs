# Decision: Reader-focused application article and template entry links

Status: proposed

## Problem

The managed Agents article included internal acceptance and resource-deletion
timelines while leaving readers to inspect a smoke runner for business calls.
Template-based articles also lacked a consistent immediate path to their template.
The user requested useful scenarios, complete invocation examples and removal of
engineering audit prose from the public reading flow.

## Decision

Rewrite the existing Chinese managed Agents article around value, resources,
deployment, the two-turn CSV task, direct HTTP/Python integration, customization
and ordinary cleanup. Add downloadable Bash/curl and Python/httpx examples and
the existing CSV fixture. Add explicit Registry/source or managed-guide links at
the beginning of all articles with an established catalog association. Custom
examples identify their actual base template; general articles remain unassigned.
Preserve all six draft statuses and all historical engineering evidence/assets.
Document both authoring rules in the contributor guide.

## API Design

No product API, CLI, SDK, schema or website implementation changes. CLI 0.5.10
manages deployment; terminal business requests use curl. Python 0.4.0a7 provides
the managed runtime, not a dedicated Gateway client SDK; examples use HTTPX.
Both clients use the existing Gateway and keep Sandbox management credentials
outside the business application.

## Alternatives considered

Removing only the quoted cleanup paragraph would leave the audit-oriented
narrative and incomplete call examples. Adding a new cross-repository metadata/UI
contract is unnecessary for immediate, explicit article links. A product SDK,
new package release or repeated paid cloud run is outside this documentation task.

## Dependencies

Existing template 0.1.4, CLI 0.5.10 and client/server 0.4.0a7 contracts; current
website Markdown ingestion. Template source and prior business acceptance:
https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/296.
The preceding article and immutable engineering supplement remain historical:
https://github.com/Alibaba-Agent-Sandbox/blogs/pull/33.

## Test Strategy

Run the existing blog validator, snippet/client syntax checks, exact association
and draft-preservation checks, Registry/source-link checks, and website ingestion,
Astro checks/build with rendered links/downloads. Exercise the two client examples
against a local HTTP fixture for success, pagination, empty 202 bodies, uncertain
execution, non-retried creation errors and malformed CSV. Those fixture checks
do not establish a new cloud/model result. Independently review design, contract
and final narrative before publishing.

## Acceptance criteria

The public article contains the complete reader workflow and usable client
downloads without internal hash/statistics/journal/deletion-timeline prose.
All explicitly template-based articles have accurate quick links; translations,
original bodies outside the rewritten article and draft flags remain intact.
Current-head CI and required review pass before merge; verify normal publication.
No new cloud resources or package release is required.

## Evidence

[Verification](../../../evidence/verify/2026-11-09-reader-focused-template-articles.md).
