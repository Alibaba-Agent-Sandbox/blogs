# Verification: Template publication tutorial guidance

Date: 2026-10-24
Result: PARTIAL — owner normative correction and final remote CI pending.
Tracking: [Issue 9](https://github.com/Alibaba-Agent-Sandbox/blogs/issues/9).
Base: `c3d90fabab8e091f26d43abdbafbda6c9d4576ec`.
Scope: `posts/publish-a-template/index.en.md`, `posts/publish-a-template/index.zh.md`, and their engineering records only.

## Executed

- Read the source template skeleton, current contribution guide and template specification. The existing status field remains in the index; its maintenance/development wording depends on [owner PR 205](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/205), which must merge first.
- Initial `python scripts/validate.py` failed because PyYAML was absent from the host interpreter. Installed the README-required PyYAML in an isolated virtual environment; the same validator then passed.
- All four new upstream contribution/usage document targets were confirmed as files on the actual awesome-templates main through GitHub's contents API.
- Published CLI 0.4.16 `abx template launch --help` passed. The actual `_skeleton/template.yaml` declares the `application` workflow and the application token variable. This checks the documented entry point, not a new execution of the illustrative my-template directory.
- Independent review identified an obsolete `capabilities` index field and an overbroad version-bump instruction. The source schema-2 entries and owner spec require no such index field; `docs/project-standards.md` limits manifest version changes to runtime/dependency/default/argument/resource changes. Corrected both languages and described declared workflows/application commands instead. No Registry package-version mechanism is introduced.
- Reproduced the old prerequisite omission: the current `_skeleton` static check failed with the explicit missing `jsonschema==4.26.0` diagnostic in the isolated PyYAML environment. Installed the owner's existing `scripts/requirements-spec.txt`; the same skeleton check passed. Both tutorial installation commands now include that file while retaining the existing SDK source pin. This validates static checker prerequisites, not the full local runtime suite.
- `git diff --check` passed. Original post date/category and historical experiment records are unchanged. Both languages carry the same contribution and usage guidance.

## Limits and integration

No cloud resource, image build or model task was created for this prose correction. Existing SDK source installation pins remain unchanged; checker prerequisites use the owner requirements file. No runtime success is inferred from post validation. Website snapshot files are not edited directly; its owner will sync the merged blogs source and validate rendering before claiming deployment.
