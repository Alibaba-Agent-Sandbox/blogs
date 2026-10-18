---
title: "Publish your template to the Registry: from directory to merge"
summary: A template is a directory plus one index entry. This post goes through what to create, how to verify it locally, what to check before opening the pull request, and when it shows up in the Registry.
date: 2026-10-12
category: tutorial
tags: [templates, registry]
authors: [Alibaba-Agent-Sandbox]
---

The Registry lists two kinds of entries: templates and providers. This post covers templates only; for providers see the [publish guide](https://registry.agent-sandbox.cn/en/publish/).

Templates live in [awesome-templates](https://github.com/Alibaba-Agent-Sandbox/awesome-templates). Publishing means opening a pull request there.

## 1. Create the directory

Start from `_skeleton/` in a source checkout of awesome-templates and create a kebab-case directory at the repository root. The directory name, `name` in `template.yaml` and `path` in the index must be the same string.

```text
my-template/
  template.yaml
  Dockerfile
  commands.py
  e2e_test.py
  README.md
  README.zh-CN.md
```

Add its design document under `docs/design/` and follow the [template spec](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/template-spec.md).

For keys the template needs, list only the variable names in `template.yaml` and leave the values empty. **Never commit a real secret.**

## 2. Add the index entry

Add one entry under the right section of `awesome-templates.yaml`: `name`, `description`, `repo`, `path`, `tags`, `author`, `capabilities`, `status`.

Keep new or incompletely verified templates `experimental`. Follow the spec's L0/L1/L2 requirements before promotion; an `official` upstream-agent claim also needs L3. A successful image build alone does not establish provider or model acceptance.

## 3. Verify locally

Install the paired runtime prerequisite from the accepted immutable Python SDK source (the example does not assume PyPI publication), then run from the template repository root:

```bash
python3 -m pip install "agent-sandbox-server @ https://github.com/Alibaba-Agent-Sandbox/python-sdk/archive/e86cb0be24e0083a27396b260298e7cf27b660d6.tar.gz#subdirectory=server-sdk" httpx pyyaml
python3 scripts/check_template.py my-template
python3 scripts/run_local_e2e.py
```

Every template that has a `commands.py` has to pass.

## 4. The README says three things

What the template is, how to deploy it and how to run its e2e:

```bash
abx template deploy ./my-template --generation 2 --alias my-template-review -y
python3 scripts/run_local_e2e.py
```

Deploy needs the CLI, Docker, ACR configuration and Express credentials. Use an alias you own. Keep generation2, `start_cmd` and `ready_cmd` in `template.yaml`; the image has no `CMD` or `ENTRYPOINT`. After catalog merge, consumers can use `abx template install alibaba-agent-sandbox/awesome-templates//<name>`. Each template's English/Chinese README must explain CLI, Python SDK and HTTP POST usage, authentication and cleanup. This article checks command syntax; it does not record a fresh cloud deployment.

## 5. Check before you submit

- Say which exact source and provider you verified. Add a provider to `tested_on` and the Verified table only with a passing evidence file, including owned-resource cleanup. Keep missing credentials, skipped models and untested providers explicit.
- Every declared capability is implemented, and nothing undeclared is quietly supported.
- No hard-coded secrets and no code that runs at install time.
- Raise the version on every update.

## After the merge

Once merged into `main`, the repository notifies the Registry to rebuild, and the Registry also pulls on its own every hour. Confirm on the [Registry templates page](https://registry.agent-sandbox.cn/en/templates/): your template appears with its capability tags and commands you can copy.
