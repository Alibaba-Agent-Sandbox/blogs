---
title: 把你的模板发布到 Registry：从目录到合并
summary: 模板是一个目录加一条索引记录。这篇按顺序讲清楚要建什么文件、本地怎么验证、提 PR 前自查什么，以及合并后多久能在 Registry 看到。
date: 2026-10-12
category: tutorial
tags: [templates, registry]
authors: [Alibaba-Agent-Sandbox]
---

Registry 收录两类内容：模板和提供方。这篇只讲源码模板，提供方的流程见[发布指南](https://registry.agent-sandbox.cn/publish/)。

模板放在 [awesome-templates](https://github.com/Alibaba-Agent-Sandbox/awesome-templates) 仓库。发布就是向这个仓库提一个 PR。

## 1. 建目录

从源码仓库的 `_skeleton/` 开始，在仓库根目录建一个 kebab-case 的目录。目录名、`template.yaml` 里的 `name`、索引里的 `path` 必须是同一个字符串。

```text
my-template/
  template.yaml
  Dockerfile
  commands.py
  e2e_test.py
  README.md
  README.zh-CN.md
```

`template.yaml` 里需要的密钥，只写变量名，值留空，**不要提交真实密钥**。

## 2. 写索引记录

在 `awesome-templates.yaml` 对应的分区加一条：`name`、`description`、`repo`、`path`、`tags`、`author`、`status`。

按[贡献指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/CONTRIBUTING.zh-CN.md)填写条目，由维护者审核后收录。`official`、`community` 说明维护归属，`experimental` 表示作者仍在开发；这些标签不决定某个平台能否启动，也不代替具体的使用与测试记录。

## 3. 本地验证

在模板仓库根目录安装当前公开服务端和校验依赖，再运行检查。模板 Dockerfile 中的运行时依赖也要单独指定：

```bash
python3 -m pip install --index-url https://pypi.org/simple "agent-sandbox-server==0.4.0a6" httpx -r scripts/requirements-spec.txt
python3 scripts/check_template.py my-template
python3 scripts/run_local_e2e.py
```

每个带 `commands.py` 的模板都必须通过。

## 4. README 帮使用者跑起来

说明需要哪些配置、怎样启动和调用、用完如何清理。以从 `_skeleton/` 扩展的应用模板为例，配置好极速版后，安装 CLI `0.5.6`；安装方式以[当前使用指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md)为准：

```bash
export ABX_SERVER_TOKEN="<YOUR_APPLICATION_TOKEN>"
abx --provider alicloud-express template launch ./my-template
```

模板声明启动、就绪命令和 `provides` 中的全部服务，一次启动即可使用，不需要选择工作流。需要提示词、密码或工作目录的命令，在启动后按文档参数调用。

还需按[模板规范](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/template-spec.zh-CN.md)补齐 `docs/design/` 中的设计文档。启动前需要 Docker、ACR 配置与 Express 凭据，并把示例中的应用令牌替换为自己生成的值。在 `template.yaml` 中保留 generation2、`start_cmd` 和 `ready_cmd`；镜像不设置 `CMD` 或 `ENTRYPOINT`。目录合并后，把命令中的 `./my-template` 换成 `alibaba-agent-sandbox/awesome-templates//my-template` 即可从目录取用。README 应继续给出实际命名命令、Python SDK 与 HTTP POST 示例，以及沙箱、准备出的模板和镜像的清理步骤。不同平台的配置与完整调用方式见[使用指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md)。

## 5. 提 PR 前自查

- 随 PR 附上具体使用记录：源码提交、平台、构建方式、运行过的命令或模型任务及清理结果。README 的已验证部分只写这些实际结果；未运行或跳过的项目单独说明。维护者据此核对贡献要求，收录本身不表示所有平台和功能都已测试。
- 启动命令能拉起模板，全部声明服务已就绪，应用命令能按 README 使用，参数与返回结果一致。
- 没有写死的密钥，没有安装时执行的代码。
- 当运行行为、依赖、默认值、参数或资源配置改变时，更新 `template.yaml` 的版本，并在中英文 README 说明兼容性变化。

## 合并之后

合并到 `main` 后，仓库会通知 Registry 重新构建；Registry 也会每小时自己拉取一次。可以在 [Registry 的模板页](https://registry.agent-sandbox.cn/templates/)确认，使用者可以找到你的模板，并查看所选平台的配置和启动说明。
