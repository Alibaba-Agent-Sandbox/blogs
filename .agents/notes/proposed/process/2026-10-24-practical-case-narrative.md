# Decision: Present practical cases as developer workflows

Status: proposed

## Problem
The user found the five published case articles read like acceptance reports. Counts of
assertions, evidence hashes, candidate history and release bookkeeping displaced the reader's
actual task. The same framing appeared in the illustrations.

## Decision
Rewrite the five Chinese articles around a concrete use: opening a temporary development
environment, running Qwen and exposing business commands, using a Python Registry template,
generating a small API, and processing an orders CSV. Explain preparation, meaningful steps,
outputs and useful next actions. Rework the covers and workflow illustration accordingly.

For user-facing practical cases, keep verification material as supporting engineering records
and attachments rather than the narrative. Preserve relevant authentication, dependency,
permissions and lifecycle limitations without turning the article into a test report. Do not
invent a customer deployment or business outcome to make an example sound more realistic.

## API Design
N/A — this decision does not involve API changes. Existing executable attachments, captured
results, source hashes and generated snapshots remain byte-identical. URLs remain stable.

## Alternatives considered
Changing only titles would leave the original acceptance-oriented structure and diagrams.
Deleting the supporting material would lose reproducibility and history. Retain that material
while rewriting the articles and figures around developer use.

## Dependencies
The prior published cases are in https://github.com/Alibaba-Agent-Sandbox/blogs/pull/7.
Website consumes the blog repository through its existing build integration; no website code
or public runtime package changes are needed.

## Test Strategy
Validate frontmatter, links, code-block syntax, SVG XML and the scoped diff. Compare executable
and evidence attachments with the published baseline. Sync the intended blog checkout into
the website, run check/build and inspect rendered articles. Observe required PR CI and verify
public content after normal merge and deployment. Do not repeat unrelated cloud experiments
for an editorial change.

## Acceptance criteria
All five articles and their figures describe practical developer workflows. Setup and commands
remain usable, known limitations remain relevant and accurate, prior evidence remains intact,
and the updated public pages are read back after publication.
