---
title: "Publish your template to the Registry: from directory to merge"
summary: A template is a directory plus one index entry. This post goes through what to create, how to verify it locally, what to check before opening the pull request, and when it shows up in the Registry.
date: 2026-10-12
category: tutorial
tags: [templates, registry]
authors: [Alibaba-Agent-Sandbox]
---

The Registry lists two kinds of entries: templates and providers. This post covers source templates only; for providers see the [publish guide](https://registry.agent-sandbox.cn/en/publish/).

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

Add one entry under the right section of `awesome-templates.yaml`: `name`, `description`, `repo`, `path`, `tags`, `author`, `status`.

Fill in the entry following the [contribution guide](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/CONTRIBUTING.md); maintainers review it before listing. `official` and `community` describe maintenance ownership, while `experimental` marks work the author is still developing. These labels do not decide whether a provider can launch the template or replace concrete usage and test records.

## 3. Verify locally

The commands below retain this article’s pinned Python SDK source environment for local validation. Public PyPI client/server 0.3.1a5 is now available; the host installation and runtime pinned in a template Dockerfile are separate. For new contributions, follow the template repository’s current contributor guide and CI dependencies. Run from the template repository root:

```bash
python3 -m pip install "agent-sandbox-server @ https://github.com/Alibaba-Agent-Sandbox/python-sdk/archive/e86cb0be24e0083a27396b260298e7cf27b660d6.tar.gz#subdirectory=server-sdk" httpx -r scripts/requirements-spec.txt
python3 scripts/check_template.py my-template
python3 scripts/run_local_e2e.py
```

Every template that has a `commands.py` has to pass.

## 4. Help readers run the template

Explain the required configuration, how to launch and call the application, and how to clean up. For an application template based on `_skeleton/`, configure Express and use a CLI build supporting the template's specification version. Specification 5 templates require the coordinated CLI update; CLI 0.4.17 predates this format. Follow the [current installation instructions](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.md):

```bash
export ABX_SERVER_TOKEN="<YOUR_APPLICATION_TOKEN>"
abx --provider alicloud-express template launch ./my-template
```

The template declares its startup/readiness commands and all services in `provides`. Launch starts that environment once; readers do not choose a workflow. Commands that need a prompt, password or workspace are invoked afterward with their documented arguments.

Before launching, configure Docker, ACR and Express credentials, and replace the example application token with a value you generate. Keep generation2, `start_cmd` and `ready_cmd` in `template.yaml`; the image has no `CMD` or `ENTRYPOINT`. After catalog merge, replace `./my-template` in the command with `alibaba-agent-sandbox/awesome-templates//my-template` to use the catalog source. Continue the README with actual named-command, Python SDK and HTTP POST examples, plus cleanup instructions for the sandbox, prepared template and image. See the [usage guide](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.md) for platform configuration and complete calling examples.

## 5. Check before you submit

- Attach concrete usage records to the PR: source commit, provider, build method, commands or model tasks executed, and cleanup results. Keep the README's verified section limited to those actual results; identify unrun or skipped checks separately. Maintainers use these records to review the contribution requirements. Listing alone does not mean every platform and feature was tested.
- The startup command starts the template, every declared service is ready, and application commands work as documented, with matching parameters and results.
- No hard-coded secrets and no code that runs at install time.
- Update the version in `template.yaml` when runtime behavior, dependencies, defaults, arguments or resources change, and explain compatibility changes in both README languages.

## After the merge

Once merged into `main`, the repository notifies the Registry to rebuild, and the Registry also pulls on its own every hour. Confirm on the [Registry templates page](https://registry.agent-sandbox.cn/en/templates/): readers can find your template and follow the configuration and launch instructions for their selected platform.
