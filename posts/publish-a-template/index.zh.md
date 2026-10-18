---
title: 把你的模板发布到 Registry：从目录到合并
summary: 模板是一个目录加一条索引记录。这篇按顺序讲清楚要建什么文件、本地怎么验证、提 PR 前自查什么，以及合并后多久能在 Registry 看到。
date: 2026-10-12
category: tutorial
tags: [templates, registry]
authors: [Alibaba-Agent-Sandbox]
---

Registry 收录两类内容：模板和提供方。这篇只讲模板，提供方的流程见[发布指南](https://registry.agent-sandbox.cn/publish/)。

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

在 `awesome-templates.yaml` 对应的分区加一条：`name`、`description`、`repo`、`path`、`tags`、`author`、`capabilities`、`status`。

新模板或未完成验证的模板保持 `experimental`。晋级须满足规范的 L0/L1/L2；声称 `official` 上游 Agent 可用还需要 L3。镜像构建通过并不等于厂商运行或模型验收通过。

## 3. 本地验证

先从已验收的固定 Python SDK 源码安装运行时前置依赖（不假设 PyPI 已发布），再在模板仓库根目录运行：

```bash
python3 -m pip install "agent-sandbox-server @ https://github.com/Alibaba-Agent-Sandbox/python-sdk/archive/e86cb0be24e0083a27396b260298e7cf27b660d6.tar.gz#subdirectory=server-sdk" httpx pyyaml
python3 scripts/check_template.py my-template
python3 scripts/run_local_e2e.py
```

每个带 `commands.py` 的模板都必须通过。

## 4. README 要说清三件事

模板是什么、怎么部署、怎么跑它的 e2e：

```bash
abx template deploy ./my-template --generation 2 --alias my-template-review -y
python3 scripts/run_local_e2e.py
```

还需按[模板规范](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/template-spec.zh-CN.md)补齐 `docs/design/` 中的设计文档。部署需要 CLI、Docker、ACR 配置与 Express 凭据，别名应属于你自己的测试资源。在 `template.yaml` 中保留 generation2、`start_cmd` 和 `ready_cmd`；镜像不设置 `CMD` 或 `ENTRYPOINT`。目录合并后，使用者可运行 `abx template install alibaba-agent-sandbox/awesome-templates//<name>`。每个模板的中英文 README 还要说明 CLI、Python SDK、HTTP POST、鉴权和清理。本文核对了命令语法，不代表一次新的真实云部署验收。

## 5. 提 PR 前自查

- 写明验证的源码与厂商。只有存在包含自有资源清理的通过证据，才把厂商加入 `tested_on` 与 Verified 表；缺凭据、跳过模型和未测厂商应明确保留。
- 声明的能力都真的实现了，没有声明的能力不要悄悄支持。
- 没有写死的密钥，没有安装时执行的代码。
- 每次更新都提高版本号。

## 合并之后

合并到 `main` 后，仓库会通知 Registry 重新构建；Registry 也会每小时自己拉取一次。可以在 [Registry 的模板页](https://registry.agent-sandbox.cn/templates/)确认，你的模板会带着能力标签和可复制的安装命令出现。
