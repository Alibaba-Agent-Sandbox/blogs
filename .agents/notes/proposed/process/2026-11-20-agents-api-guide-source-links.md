# Decision: Pin Agent API guide links to the reviewed source

Status: proposed

## Problem

A mutable development branch can move or disappear underneath the published selection guide.

## Decision

Pin links in both language variants to the inspected source commit. Registry remains the entry point for current availability.

## API Design

The historical Qwen guide retains its own fixed source and no HTTP behavior changes.

## Alternatives considered

A moving branch or future default branch URL can break recipe references during launch.

## Dependencies

[Blogs PR #43](https://github.com/Alibaba-Agent-Sandbox/blogs/pull/43) and template [PR #312](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/312).

## Test Strategy

Validate articles, check immutable recipe entries over GitHub and sync the corresponding Website snapshot.

## Acceptance criteria

Both language articles point to the same reviewed source without claiming new runtime or cloud acceptance.
