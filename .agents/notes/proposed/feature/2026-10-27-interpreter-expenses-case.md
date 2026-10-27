# Decision: Publish a useful interpreter case with the actual error boundary

Status: proposed

## Problem
Every template needs its own practical article based on real use. The managed
interpreter can summarize and plot, but failing code was observed executing twice.

## Decision
Publish a monthly expenses case with the unchanged executed script, actual JSON
and actual PNG. Explain persistent contexts, outputs, configuration, extensions
and cleanup. Explain the known exception replay defect and process alternative;
do not describe this template as fully accepted.

## API Design
N/A — this decision does not change an API. Attach expenses.py using public
AsyncSandbox with explicit same-region/account options and finite owned lifetime.

## Alternatives considered
Omitting useful working tasks would hide a viable data-analysis path. Omitting
the failing boundary or promoting qualification would misstate real behavior.

## Dependencies
https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/252 owns usage and
runtime evidence. https://github.com/Alibaba-Agent-Sandbox/awesome-templates/issues/251
tracks the unresolved managed defect. Refs https://github.com/Alibaba-Agent-Sandbox/blogs/issues/16.

## Test Strategy
Execute the complete attachment, independently parse downloaded JSON/PNG, confirm
owned-instance absence, validate frontmatter/assets, and build article routes.
Separately read back previously merged five practical articles on the public site.

## Acceptance criteria
The one article and actual artifacts publish with clear capabilities and limits.
The overall50-template series and full interpreter qualification remain open.
