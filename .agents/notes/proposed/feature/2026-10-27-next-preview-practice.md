# Decision: Show real Next and Vite browser editing as a practical case

Status: proposed

## Problem
The preview template needs an article that gets a reader from configuration to a
rendered editable page, with actual browser/HMR results and cleanup.

## Decision
Publish an expense-display page workflow for both fixed Next and Vite toolchains,
attach both actual screenshots, the unchanged executed SDK example and the actual
preview relay with its repository license. Explain exact Vite host, credentials,
raw HTTP alternatives, editing, export and resource ownership.

## API Design
N/A — article/assets only. Application token protects management commands; the
initial preview page has no business login and uses provider access controls.

## Alternatives considered
A running process/version or internal readiness alone cannot show that a browser
renders and updates the page. Do not fabricate screenshots or imply a computed
financial total;51.30 is explicitly authored display content in this case.

## Dependencies
Source PR256 merged77ea826c187200112deb896dbc1b83c8eec904c3 before consumer publication.
Refs https://github.com/Alibaba-Agent-Sandbox/blogs/issues/16 and
https://github.com/Alibaba-Agent-Sandbox/awesome-templates/issues/244.

## Test Strategy
Review actual default Docker/Express core and full CLI/SDK/HTTP/browser case,
external3000/5173 HTML, exact Vite host, HMR without manual reload, independently
absent owned projects/processes/listeners/cloud resources and unchanged code blocks.
Validate article assets/frontmatter and both website language routes.

## Acceptance criteria
The article and exact screenshots/helper/SDK/license publish with current-head
checks. Registry qualification and full50-template completion remain independent.
