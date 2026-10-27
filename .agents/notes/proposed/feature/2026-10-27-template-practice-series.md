# Decision: Publish each template experience as a practical case

Status: proposed

## Problem
A catalog entry and passing smoke do not teach a newcomer to complete a task.
The requested series needs one actual experience per template, including useful
results, configuration and customization, without a test-report narrative.

## Decision
Publish one case per completed template under template-practice-<name>. Start
with python-hello expense-file generation and OpenCode code generation, source
repair, session continuation and actual model switching. Include the actual
non-sensitive downloaded files and complete executed SDK snippets. Keep exact
execution evidence in awesome-templates; do not turn historical results into new
claims or publish unexecuted outcomes.

## API Design
N/A — article sources and relative downloadable assets only. Website ingests
blogs/posts through its existing integration. Both new posts are Chinese; the
existing language fallback preserves navigation for English readers.

## Alternatives considered
A generic repeated introduction for every tool would omit real use and limits.
A test diary would not meet the requested practical-case perspective. Do not
publish placeholder articles for cases still missing business/account evidence.

## Dependencies
Refs https://github.com/Alibaba-Agent-Sandbox/blogs/issues/16 and
https://github.com/Alibaba-Agent-Sandbox/awesome-templates/issues/244.
Runtime evidence is owned by awesome-templates, linked below.

## Test Strategy
Validate frontmatter/relative assets, compare attached results against actual
received files and hashes, compile SDK examples, run the generated Python file,
and sync/build a separate website preview with both language routes/assets.

## Acceptance criteria
Each article explains installation, platform/application/model configuration,
use, actual output, secondary development, limits and cleanup. Article claims
match its real source/package/provider receipt. This incremental PR does not
complete the full 50-template series.
