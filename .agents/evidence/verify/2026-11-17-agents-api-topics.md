# Verification: Agent API topic discovery

Date:2026-11-17. Result:PASS for the local website/content scope; overall runtime publication remains BLOCKED.
Base source:2186eedd320a77cbe8cad73c38ffc2d3b67608b6; scoped task diff adds/revises the owner's Agent API topic, source content or integration files and records.
Environment:Linux, Node22.22.2; Python3.13.13 for catalog/blog/browser checks; locked Node installs and Registry pinned requirements.

## Owner checks

- `python scripts/validate.py`:60 posts checked,0 problems (rerun after wording updates).
- Intended blog checkout synced into the website; its Astro check and full build passed.
- New English/Chinese guide has matching date/category and valid tag/summary/frontmatter.
- Historical Qwen business files/results remain unchanged; only article wording and tag discovery changed.

- `git diff --check`:passed. New owner record relative-link checks passed.

## Actual browser coverage

The website-owned `scripts/verify-agents-api-topics.py` ran with Playwright1.56.0/Chromium141
against both local built previews. Eight page combinations (Registry/website × Chinese/English
×390/1440px) passed HTTP200, no horizontal overflow, no page JavaScript errors, preserved
language-topic route, discovery from each list and historical generic-template redirect.
Registry rendered six distinct catalog-backed hosted template links. The blog topic rendered
actual tagged articles, with explicitly separate native Sandbox background reading.
Sixteen full-page screenshots cover dark/light themes; those are captures, not sixteen
manual or functional passes. Root/reviewer manually inspected Registry Chinese desktop/light
and English mobile/dark, website Chinese desktop/light and English mobile/dark. The reviewed
text, card spacing, single-column articles, distinct development limits and mobile stacking
were readable. Other captured combinations were automated layout checks, not each individually
claimed as visually reviewed.

The first browser script expected relative language hrefs, while existing shared client code
normalizes them to absolute URLs; it failed before claiming pass. The assertion now compares
the same destination suffix. Initial theme screenshots were captured during the existing
transition; a350ms settled capture corrected the observation, without changing page styling.
The final browser run passed. Both sites' shared UI source was unchanged.

## Scope and limitations

Two independent post-change review rounds are tracked by the parent task; this record does
not replace that gate. Development template/source links target the reviewed task branch and
must exist before public publication; switch to delivered immutable/main refs when appropriate.
Do not describe conceptual guides or historical/native Sandbox cases as six new real-model
acceptance runs. OpenCode completed-tool observations cannot guarantee a deadline from real
tool start; full-Turn deadline/cancellation/cleanup remain distinct. The older DeepSeek
compatible-harness article is distinct from the new official DSH implementation.

No cloud resource, real model task, vendor login, package release or production site deployment
was performed by these checks. Images and runtime a8 are still subject to their own publication
and real-component gates. Existing borrowed services were not touched.
