# Decision: publish explicit compatible-agent practical cases

Status: proposed

## Problem
Claude Code, Gemini and Droid need individual practical articles for the actual supported
compatible mode, without implying native vendor login or complete qualification.

## Decision
Publish three Chinese coding cases with complete executed SDK attachments, actual
downloaded programs and generated reports. Explain model/key/endpoint selection,
CLI/SDK/HTTP use, independent execution, extension, ownership and cleanup.

## API Design
N/A — no API changes. Use existing claude_byok, gemini_byok and native droid_byok named methods.

## Alternatives considered
A vendor account narrative or whole-template pass would exceed available evidence.
Do not relabel an authored protocol adapter as the vendor's native endpoint.

## Dependencies
Refs https://github.com/Alibaba-Agent-Sandbox/blogs/issues/16 and source evidence
https://github.com/Alibaba-Agent-Sandbox/awesome-templates/issues/244.
Immutable producer evidence is in commit e8d44eb5b1b8f656efdd1100036f9dcda146bee1,
.agents/evidence/verify/2026-10-27-more-provider-practices in awesome-templates.
All three templates retain Beta because native vendor commands require credentials.

## Test Strategy
Match actual completed native-compatible core and fresh CLI/full SDK/direct HTTP
receipts. Download and independently execute all generated programs. Post/link/
frontmatter validation, explicit website sync/build, three bilingual routes and nine
exact original assets, configured-secret scan and diff check.

## Acceptance criteria
Source evidence current-head CI/merge, article CI/review/merge, website deployment
and public readback. Full50-template/article request remains incomplete.
