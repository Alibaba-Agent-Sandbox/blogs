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

Create a kebab-case directory at the repository root. The directory name, `name` in `template.yaml` and `path` in the index must be the same string.

```text
my-template/
  template.yaml
  Dockerfile
  commands.py
  e2e_test.py
  README.md
```

For keys the template needs, list only the variable names in `template.yaml` and leave the values empty. **Never commit a real secret.**

## 2. Add the index entry

Add one entry under the right section of `awesome-templates.yaml`: `name`, `description`, `repo`, `path`, `tags`, `author`, `capabilities`, `status`.

`status` is `official`, `community` or `experimental`. Community submissions start as `community`.

## 3. Verify locally

From the repository root run:

```bash
python3 scripts/run_local_e2e.py
```

Every template that has a `commands.py` has to pass.

## 4. The README says three things

What the template is, how to deploy it and how to run its e2e:

```bash
abx template init -t python ./my-template
abx template deploy ./my-template -y --generation 2 \
  --start-cmd 'agent-sandbox-server serve --port 9000 --commands /home/user/app/commands.py' \
  --ready-cmd 'agent-sandbox-server healthcheck --port 9000'
python3 scripts/run_local_e2e.py
```

`--start-cmd` and `--ready-cmd` only work with `--generation 2`. The image does not set `CMD` or `ENTRYPOINT`; the platform start command runs `agent-sandbox-server`. If a generation-1 template already uses that name, delete it first (`abx template delete <id> -y`). After the template is in the catalog, other people install it with `abx template install alibaba-agent-sandbox/awesome-templates//<name>`. `abx deploy` is the same command as `abx template deploy`.

## 5. Check before you submit

- Say what you verified. If there was no real backend to test against, say so in the README.
- Every declared capability is implemented, and nothing undeclared is quietly supported.
- No hard-coded secrets and no code that runs at install time.
- Raise the version on every update.

## After the merge

Once merged into `main`, the repository notifies the Registry to rebuild, and the Registry also pulls on its own every hour. Confirm on the [Registry templates page](https://registry.agent-sandbox.cn/en/templates/): your template appears with its capability tags and commands you can copy.
