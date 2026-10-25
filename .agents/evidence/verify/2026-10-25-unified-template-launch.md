# Publication tutorial template-launch update

Result: PARTIAL — local documentation validation completed; cross-repository publication and merge remain pending.

Base revision: `03e9d4b8a6abc1384607158ddd97f85776caad97`. Scope: `posts/publish-a-template/index.en.md`, `index.zh.md`, this record and its indexed process note. Existing template/SDK source pins, dates, category, post assets and the five historical developer-journey cases are unchanged.

Validation environment: Linux, Python 3.13, PyYAML 6.0.3.

- `python scripts/validate.py`: PASS — 8 posts, zero problems.
- Current post-source scan found the retired workflow selector only in this bilingual tutorial; no current post bodies declare version 4 manifests or workflow maps.
- Local record links checked for target existence; `git diff --check` checked whitespace.
- No cloud/model experiments were rerun and no cloud resources were created. Documentation validity does not establish specification 5 deployment acceptance.

Website integration is coordinated in the website owner's change. This PR remains draft until the compatible template and consumer changes can be published together.
