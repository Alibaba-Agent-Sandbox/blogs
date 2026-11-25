# Decision: Use the published preview in the managed Agents article

Status: proposed

## Problem

The published managed-agents-one-endpoint article still requires a source CLI in
three current-usage paragraphs. The official 0.6.0-alpha.2 npm release now supplies
those application commands. The article also needs navigation to the Agents API
topic pages after those pages are live.

## Decision

Replace only the current installation requirement with the exact published preview
and an explicit official-registry installation command. Preserve the original
0.1.4 / CLI 0.5.10 case attribution, fixed source link and all result attachments.
Add first-paragraph topic links only after both destinations return the expected
published page. Do not include the separate six-Harness draft or native-resource
workflow changes.

## API Design

N/A — this decision does not involve API changes.

## Alternatives considered

Requiring source installation is obsolete for these commands. Rewriting historical
results as preview acceptance would be false. Additional cloud execution, template
dependency changes and a new CLI release are unnecessary for this correction.

## Dependencies

- Published CLI preview: https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/releases/tag/v0.6.0-alpha.2
- Blog topic: https://www.agent-sandbox.cn/topics/agents-api/
- Registry topic: https://registry.agent-sandbox.cn/topics/agents-api/
- Website publication continues to consume this repository's main branch.

## Test Strategy

Validate article front matter, repository unit tests and affected links. Compare
the historical result files and fixed-source references with the baseline. Read
both topic pages before publication and distinguish package installation validation
from a new managed business run.

## Acceptance criteria

The current article names an actually available preview, has a usable installation
command and live topic links, and preserves historical execution claims and assets.
Required repository CI and independent review pass before merge.

## Evidence

[Verification](../../../evidence/verify/2026-11-25-managed-agents-preview-entry.md).
