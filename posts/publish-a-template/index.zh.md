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

在仓库根目录建一个 kebab-case 的目录。目录名、`template.yaml` 里的 `name`、索引里的 `path` 必须是同一个字符串。

```text
my-template/
  template.yaml
  Dockerfile
  commands.py
  e2e_test.py
  README.md
```

`template.yaml` 里需要的密钥，只写变量名，值留空，**不要提交真实密钥**。

## 2. 写索引记录

在 `awesome-templates.yaml` 对应的分区加一条：`name`、`description`、`repo`、`path`、`tags`、`author`、`capabilities`、`status`。

`status` 取 `official`、`community` 或 `experimental`。社区提交从 `community` 开始。

## 3. 本地验证

在仓库根目录运行：

```bash
python3 scripts/run_local_e2e.py
```

每个带 `commands.py` 的模板都必须通过。

## 4. README 要说清三件事

模板是什么、怎么部署、怎么跑它的 e2e：

```bash
abx template init -t python ./my-template
abx template deploy ./my-template -y --generation 2 \
  --start-cmd 'agent-sandbox-server serve --port 9000 --commands /home/user/app/commands.py' \
  --ready-cmd 'agent-sandbox-server healthcheck --port 9000'
python3 scripts/run_local_e2e.py
```

`--start-cmd` 和 `--ready-cmd` 只在 `--generation 2` 下生效。镜像不写 `CMD` 或 `ENTRYPOINT`，由平台的启动命令运行 `agent-sandbox-server`。如果同名模板已经是 generation 1，先删掉（`abx template delete <id> -y`）。模板进了目录之后，别人用 `abx template install alibaba-agent-sandbox/awesome-templates//<name>` 安装。`abx deploy` 就是 `abx template deploy`。

## 5. 提 PR 前自查

- 写明你验证了什么。没有真实后端可测，就在 README 里说明。
- 声明的能力都真的实现了，没有声明的能力不要悄悄支持。
- 没有写死的密钥，没有安装时执行的代码。
- 每次更新都提高版本号。

## 合并之后

合并到 `main` 后，仓库会通知 Registry 重新构建；Registry 也会每小时自己拉取一次。可以在 [Registry 的模板页](https://registry.agent-sandbox.cn/templates/)确认，你的模板会带着能力标签和可复制的安装命令出现。
