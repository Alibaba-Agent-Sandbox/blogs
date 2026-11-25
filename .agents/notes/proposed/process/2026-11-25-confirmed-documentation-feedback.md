# Decision: Correct confirmed documentation feedback

Status: proposed

## Problem

The English and Chinese repository READMEs still announce an expected stable 1.0.0 release on November 15, 2026, a date already in the past.

## Decision

Remove the expired date and unfulfilled stable-release forecast from both README languages while retaining the accurate preview and possible-breaking-change notice. Do not invent a replacement date or change package/runtime versions.

## API Design

N/A — this decision does not involve API changes.

## Alternatives considered

Replacing the date with a new forecast would publish an unapproved commitment. Removing all preview information would hide a relevant current limitation.

## Dependencies

The maintainer’s confirmed documentation feedback. This documentation-only correction changes no executable content or publication contract.

## Test Strategy

Check changed Markdown links, bilingual wording, seven-section note structure and git diff hygiene. Use existing owner documentation gates where available. Runtime, image, deployment and model behavior are unchanged, so this prose correction does not require new cloud resources.

## Acceptance criteria

Both README languages retain the preview warning and omit the expired release forecast. Local links, record structure and diff checks pass; required remote gates pass before merge.

## Evidence

[Local documentation verification](../../../evidence/verify/2026-11-25-confirmed-documentation-feedback.md).
