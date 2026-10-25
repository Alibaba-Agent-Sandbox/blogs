# Decision: Keep developer cases runnable with current public tools

Status: proposed

## Problem
Fresh installation and execution exposed a binary packaging failure, unreliable model-written native recipes, a stale Registry source pin and an incorrect negative-auth test. Historical published proofs cannot establish current package behavior.

## Decision
Repeat the five documented developer tasks from public installation. Update case prose and attachments around ordinary usage after verification, keep old proofs/generated snapshots as historical, and add separate dated current receipts. Correct negative-auth requests by removing both representations of the application token while preserving gateway credentials. Explicitly separate source candidates from published releases.

## API Design
No product API changes in this repository. Case scripts use current CLI, Python client, named commands, HTTP and declarative data processing.

## Alternatives considered
- Relabel historical successes: would not test current tools.
- Convert posts into acceptance reports: would obscure how to use the project.
- Hide blocked steps behind simulation: would not satisfy real model/cloud behavior.

## Dependencies
- https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/158
- https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/159
- https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/163
- https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/167
- https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/170
- https://github.com/Alibaba-Agent-Sandbox/python-sdk/pull/112
- https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/222
- https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/224
- https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/179
- https://github.com/Alibaba-Agent-Sandbox/python-sdk/pull/131
- https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/225
- https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/181
- https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/228
- https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/229
- https://github.com/Alibaba-Agent-Sandbox/blogs/issues/14

## Test Strategy
Fresh website binary and official PyPI venv, real Qwen model artifact edits, SDK/CLI/POST named command equivalence, Registry and generated template capabilities, independent CSV/Decimal oracle, normal/exception resource cleanup. Repository schema validation and website ingestion checks accompany final prose.

## Acceptance criteria
- All five current usage scenarios pass with exact assertions and owned-resource cleanup.
- Any failing baseline and infrastructure limitation remain separately recorded.
- Old merged evidence is preserved and new documentation names only actual published tools.
- Required validation and publication CI pass.

## Evidence
- [Verification](../../../evidence/verify/2026-10-25-current-developer-journeys.md)
