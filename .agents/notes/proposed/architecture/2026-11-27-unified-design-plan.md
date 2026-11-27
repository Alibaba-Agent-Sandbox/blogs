# Decision: Document verified unified workflows as source-owned practice articles
Status: proposed

## Problem

Practice articles must explain a useful application and show what a reader can actually build and call. The unified design changes installation, client selection, authentication and lifecycle behavior, but those decisions alone do not make its examples runnable. Publishing a future workflow or presenting mock results as a real use case would mislead readers.

This proposal assigns blog-source work. It does not publish an article or establish that a target capability exists.

## Decision

Write or revise articles only around a scoped, verified reader task. Keep new material in draft until its required packages, template and business path are available. Fix article sources in `posts/`; the website consumes those sources through its normal integration.

| Task | Deliverable | Order and observable completion |
| --- | --- | --- |
| BLOG-01 | Affected-article inventory and version boundaries | First. Identify which current instructions change and which are historical records; do not rewrite history or perform an unrelated catalog-wide rewrite. Record the required product/template versions for each proposed update. |
| BLOG-02 | A complete application-oriented practice path | After the relevant runtime/template releases and real business result. Explain value, scenario and customization; include the actual source, necessary configuration, applicable CLI/HTTP/SDK calls, expected versus observed output and resource cleanup. |
| BLOG-03 | Helper, SDK-only or Agent explanation where the task uses it | After those exact integrations are available. Demonstrate source helper preparation without mandatory npm/PyPI publication, explicit application dependencies, or actual Skill/MCP use; explain where files are read and what resource the caller owns. |
| BLOG-04 | Source validation and website publication integration | After article evidence and review. Validate frontmatter/assets/links, preview the synced website output, then publish through the normal repository workflow with a verified final public page. |

BLOG-03 is conditional on the article's subject; it is not a requirement to place every interface into every article. All interfaces claimed as supported by that article must be shown truthfully. If a service has no dedicated SDK, show the actual HTTP client used instead of inventing a package.

## API Design

N/A — this decision does not involve API changes. Articles consume published CLI/SDK interfaces and real service routes. They must not define a new compatibility promise or substitute a design example for an implemented client.

An article tied to a specific template starts with quick links to its Registry detail page and source or hosted usage instructions. Custom examples identify their real base template. Configuration explains each credential's purpose and actual source; normal automatic authentication is demonstrated only when the verified release implements it. SDK-only examples keep their own explicit dependencies/configuration and do not rely on CLI installation or HOME state.

Cleanup instructions name the user's actual operations and ownership: local close, owned instance deletion, template deletion, application data lifecycle and any retained shared resources. Detailed journals, resource audit timelines, receipt files and verification counts remain in owner engineering evidence.

## Alternatives considered

- Publish a target-design walkthrough before implementation: rejected for a practice article because the reader cannot complete it with the claimed products.
- Treat schema validation, version output or MCP handshake as a successful case: rejected because none proves the business result.
- Write article copies directly in the website repository: rejected because this repository owns post text and assets.
- Rebuild a large verification matrix only to obtain article screenshots: rejected; use a controlled verified path and existing owner evidence, with additional execution only where needed to substantiate the article.

## Dependencies

The companion records below target `main`. Each link becomes available when that owner's planning PR merges; publishing a plan does not establish product delivery.

- [Template implementation and business verification](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/.agents/notes/proposed/architecture/2026-11-27-unified-design-plan.md).
- [CLI](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/blob/main/.agents/notes/proposed/architecture/2026-11-27-unified-design-plan.md), [Python SDK](https://github.com/Alibaba-Agent-Sandbox/python-sdk/blob/main/.agents/notes/proposed/architecture/2026-11-27-unified-design-plan.md) and [Node SDK](https://github.com/Alibaba-Agent-Sandbox/nodejs-sdk/blob/main/.agents/notes/proposed/architecture/2026-11-27-unified-design-plan.md).
- [Registry entries](https://github.com/Alibaba-Agent-Sandbox/registry/blob/main/.agents/notes/proposed/architecture/2026-11-27-unified-design-plan.md) and [website integration](https://github.com/Alibaba-Agent-Sandbox/website/blob/main/.agents/notes/proposed/architecture/2026-11-27-unified-design-plan.md).

The article's owner record must cite the actual tested revisions and available releases before it clears draft status. A merged upstream implementation without the required artifact or business result does not clear that gate.

## Test Strategy

Validate this proposal's structure and links without cloud work. For article changes, follow the post template and run `python scripts/validate.py`. Verify source/Registry links, language-specific website routes and relative assets. Keep dates/categories consistent when both translations exist.

Review each claimed outcome against the cited real execution and artifacts. Re-run a changed code path when existing evidence does not substantiate it; use the supported public installation path and preserve failures and cleanup results. Do not fabricate outputs or expose credentials, private IDs or raw sensitive logs.

Sync the intended source revision into the website and inspect the rendered article when content/schema/assets require it. A merge can trigger publication, so confirm draft status and publication readiness before delivery. Frontmatter validation and rendering success remain separate from product verification.

## Acceptance criteria

- BLOG-01 through BLOG-04 name a concrete reader task and the artifacts that make it usable; planning completion is not article or product completion.
- The main path has a real business result and complete configuration, invocation and owned-resource cleanup instructions. A lack of a dedicated SDK is stated accurately.
- Source helper, SDK-only and Agent claims are supported by the corresponding executed paths. Mock/expected outputs and missing coverage are labelled honestly.
- Template-specific posts provide Registry and source/usage quick links, explain customization and keep internal implementation/acceptance history out of user instructions.
- Required validation and affected website integration pass. Both language versions remain consistent when both exist.
- Future-only content stays draft. Publication occurs only after the claimed release and usable path are confirmed, and the resulting public page is checked before reporting it published.

Document validation and review disposition: [verification](../../../evidence/verify/2026-11-27-unified-design-plan.md).
