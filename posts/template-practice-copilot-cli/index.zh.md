---
title: 用 Copilot CLI 的自选模型完成代码交付
summary: 配置 Copilot CLI 1.0.100 的独立模型，操作现有代码，取回真实程序，并把命令或会话入口接入自己的应用。
date: 2026-10-27
category: case
tags: [templates, models, copilot-cli]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

先处理已有 calc.py 的缺陷：add(a,b) 原来执行减法，原生代理改为加法并写出 report.txt。原有三个检查文件保持原样，独立进程运行原检查和额外输入均通过。

本例使用 Copilot CLI 1.0.100、极速版、CLI `0.5.7`、Python client/server `0.4.0a6`。
代码修复配置 `qwen3.8-flash`，完整文档流程在另一实例配置 `qwen3.8-max`。
下载的 [generated_hello.py](./generated_hello.py) 独立运行后输出 `Hello from the sandbox`。

## 准备平台和独立模型服务

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
```

按[平台配置](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)
准备极速版 API Key、地域、连接地址、Docker、构建权限和镜像仓库。再设置独立模型：

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export COPILOT_PROVIDER_API_KEY='<YOUR_MODEL_API_KEY>'
export COPILOT_PROVIDER_BASE_URL='<YOUR_CHAT_COMPLETIONS_BASE_URL>'
export COPILOT_MODEL='<YOUR_AUTHORIZED_MODEL_ID>'
abx template launch Alibaba-Agent-Sandbox/awesome-templates//copilot-cli --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
abx run "$SANDBOX_ID" copilot_version
abx run "$SANDBOX_ID" copilot_setup_check
```

endpoint、Key、确切模型 ID 必须属于同一授权服务，并支持 **Chat Completions**。
API base 使用服务提供的前缀，通常为 `/v1`，不追加具体 API 路径。
平台 API Key、模型 Key、应用令牌分别配置。原生 GitHub Copilot CLI 的 BYOK 路径使用自己的兼容模型，不需要 GitHub 登录。allow_write=true 明确允许当前任务的文件编辑；固定工具列表不开放 shell、代理委派和 web 工具。

## 从代码任务到实际文件

上面的现有代码案例保留已有约束，实际改源文件并取回报告。
自己的项目可以先上传明确的工作目录，约定允许修改的文件和交付要求，
在任务返回后独立运行自己的检查并审阅差异。

再用完整的小任务生成一个程序：

```bash
ABX_HTTP_TIMEOUT=420 abx run "$SANDBOX_ID" copilot --json-args '{"prompt":"Create generated_hello.py that prints exactly Hello from the sandbox, and GENERATED_REPORT.md explaining the program. Preserve unrelated existing files.","allow_write":true,"cwd":"/home/user/app","command_timeout":300}'
abx download "$SANDBOX_ID" /home/user/app/generated_hello.py ./generated_hello.py
python generated_hello.py
```

实际输出为 `Hello from the sandbox`。配套的 [report.txt](./report.txt) 是原生任务生成的说明原文。
任务返回若包含 exit_code，先确认其为零，再查看真实文件。
模型输出与任务期限分别受模型服务和 command_timeout/timeout_s 影响；
HTTP 客户端等待与 1800 秒实例寿命独立，断开客户端不保证远端任务取消。

## Python、HTTP 与项目扩展

[quickstart.py](./quickstart.py) 是实际执行的完整 SDK 示例：保留实例 ID 与环境，
运行 `python quickstart.py`。它连接当前实例，用独立应用令牌调用 `copilot`。
需要的结果通过文件 API 或 abx download 导出，再交给自己的程序。

HTTP 用户按[直接 HTTP 指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)
解析 9000 端口，保留网关头、路径、查询，再添加应用认证。向
`POST /commands/copilot` 发送上面的直接 JSON 对象，不加 args 包装层。
三个调用入口分别完成了新任务；每次先删除自己的上一轮输出，再下载并独立运行当前程序。


二次开发可以从自己的模板副本固定额外依赖，上传项目、提交任务、运行已有检查、下载差异。
保留原生程序的版本和授权。扩展权限或接入其他工具时，按自己的业务验证实际行为。
全部参数、返回类型与上游边界见[模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/copilot-cli/README.zh-CN.md)。

## 更换模型与结束任务

保存产物后 export 新的模型 ID，重新 launch 同一模板，使用新实例 ID；更换服务时同步更换
Key 与 base。已运行的应用不会因本机再次 export 而重新配置。本例确实用两种分别配置的模型
完成了实际工作，没有推断其他服务或订阅的可用性。

```bash
abx kill "$SANDBOX_ID"
```

SDK close 只关闭连接。预备模板和镜像按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)
只删除自己的资源。本例所用云实例、预备模板及本次镜像均独立确认不存在。
