# Decision: Blog reader experience and rendering ownership

Status: proposed

## Problem

The user requested a page/control screenshot audit including every published blog page. Article summaries have inconsistent visual height on home and related cards; list rows, covers, reading outlines, code blocks and mobile layout require review.

## Decision

Keep article and asset ownership in this repository. Shared blog presentation changes belong to the website. Review the actual published posts and both locale routes, preserving explicit language fallbacks, draft state, featured labels and independent pinning. Do not rewrite article facts merely to make a visual claim.

## API Design

No new runtime API. Existing template identities, provider declarations and public package interfaces remain owned by their source repositories.

## Alternatives considered

Avoid treating screenshots alone as functional proof, hiding page overflow, adding dummy catalog entries, or publishing internal acceptance logs as user guidance. The audit combines screenshots, observable control behavior and scoped visual review.

## Dependencies

Shared UI originates in https://github.com/Alibaba-Agent-Sandbox/website and is consumed by https://github.com/Alibaba-Agent-Sandbox/registry. Blog source remains in https://github.com/Alibaba-Agent-Sandbox/blogs. GitHub authentication initially failed and was later restored. Rendering changes are tracked by https://github.com/Alibaba-Agent-Sandbox/website/pull/96.

## Test Strategy

Run scripts/validate.py against this source revision and sync the intended source into a website preview for rendering review. Frontmatter validation is separate from browser/layout review. Record two post-fix review rounds and any source-baseline or remote workflow blockers explicitly.

## Acceptance criteria

Finish the initial page/state inventory and screenshot analyses before product UI fixes. Make the scoped corrections, run required checks, and complete two screenshot review rounds. Preserve incomplete results and distinguish current live content from the available source snapshots. Deliver via scoped commits and PRs only after remote checks and required reviews pass; no bypass or direct main push.
