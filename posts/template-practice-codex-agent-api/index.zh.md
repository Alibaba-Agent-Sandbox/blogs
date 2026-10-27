---
title: 用 Codex 会话 API 继续处理同一份代码
summary: 配置 Codex CLI 0.162.1 与项目会话 API 的独立模型，操作现有代码，取回真实程序，并把命令或会话入口接入自己的应用。
date: 2026-10-27
category: case
tags: [templates, models, codex-agent-api]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

一个后台轮次修复已有 normalizer.py，并生成 normalization-report.json。任务返回后，独立进程重新运行六项固定检查；随后通过 SSE 在同一线程继续，生成原报告的真实 SHA256 与输出项数。续接保持第一次的源文件和报告不变，最后再次运行原检查。

本例使用 Codex CLI 0.162.1 与项目会话 API、极速版、CLI `0.5.7`、Python client/server `0.4.0a6`。
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
export ABX_LLM_API_KEY='<YOUR_MODEL_API_KEY>'
export ABX_LLM_BASE_URL='<YOUR_RESPONSES_BASE_URL>'
export CODEX_MODEL='<YOUR_AUTHORIZED_MODEL_ID>'
abx template launch Alibaba-Agent-Sandbox/awesome-templates//codex-agent-api --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
abx run "$SANDBOX_ID" codex_version
abx run "$SANDBOX_ID" agent_status
```

endpoint、Key、确切模型 ID 必须属于同一授权服务，并支持 **Responses**。
API base 使用服务提供的前缀，通常为 `/v1`，不追加具体 API 路径。
平台 API Key、模型 Key、应用令牌分别配置。每一轮都调用原版 codex exec --json，后续轮次恢复同一原生线程。保存代理配置与会话分别管理，后台监控负责读取输出和期限；事件采用有限重放缓冲。这里按项目 HTTP 合同使用，不假设兼容任意 OpenAI SDK 方法。

## 从代码任务到实际文件

上面的现有代码案例保留已有约束，实际改源文件并取回报告。
自己的项目可以先上传明确的工作目录，约定允许修改的文件和交付要求，
在任务返回后独立运行自己的检查并审阅差异。

再用完整的小任务生成一个程序：

```bash
ABX_HTTP_TIMEOUT=420 abx run "$SANDBOX_ID" codex --json-args '{"prompt":"Create generated_hello.py that prints exactly Hello from the sandbox, and GENERATED_REPORT.md explaining the program. Preserve unrelated existing files.","timeout_s":300}'
abx download "$SANDBOX_ID" /home/user/workspace/generated_hello.py ./generated_hello.py
python generated_hello.py
```

实际输出为 `Hello from the sandbox`。配套的 [report.txt](./report.txt) 是原生任务生成的说明原文。
任务返回若包含 exit_code，先确认其为零，再查看真实文件。
模型输出与任务期限分别受模型服务和 command_timeout/timeout_s 影响；
HTTP 客户端等待与 1800 秒实例寿命独立，断开客户端不保证远端任务取消。

## Python、HTTP 与项目扩展

[quickstart.py](./quickstart.py) 是实际执行的完整 SDK 示例：保留实例 ID 与环境，
运行 `python quickstart.py`。它连接当前实例，用独立应用令牌调用 `codex`。
需要的结果通过文件 API 或 abx download 导出，再交给自己的程序。

HTTP 用户按[直接 HTTP 指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)
解析 9000 端口，保留网关头、路径、查询，再添加应用认证。向
`POST /commands/codex` 发送上面的直接 JSON 对象，不加 args 包装层。
三个调用入口分别完成了新任务；每次先删除自己的上一轮输出，再下载并独立运行当前程序。

会话工作流从 POST /v1/agents 保存配置开始，用 GET /v1/agents/{id} 读回，再 POST /v1/agents/sessions 引用该配置。后台任务可以选择 background:true、stream:false，随后读取状态与 items；需要继续时 POST 同一会话的 events，stream:true 接收 SSE。artifact_id 是工作区相对路径的 URL-safe base64，GET artifacts 读取 UTF-8 文本，DELETE artifacts 删除自己的文件。删除会话会终止其当前 CLI/工具进程组。上述保存配置查询、实际文件读取与删除、活动后台会话删除和删除后独立查询均已实际调用；其他 CRUD 与同线程续接来自前面的真实代码案例。

二次开发可以从自己的模板副本固定额外依赖，上传项目、提交任务、运行已有检查、下载差异。
保留原生程序的版本和授权。扩展权限或接入其他工具时，按自己的业务验证实际行为。
全部参数、返回类型与上游边界见[模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/codex-agent-api/README.zh-CN.md)。

## 更换模型与结束任务

保存产物后 export 新的模型 ID，重新 launch 同一模板，使用新实例 ID；更换服务时同步更换
Key 与 base。已运行的应用不会因本机再次 export 而重新配置。本例确实用两种分别配置的模型
完成了实际工作，没有推断其他服务或订阅的可用性。

```bash
abx kill "$SANDBOX_ID"
```

SDK close 只关闭连接。预备模板和镜像按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)
只删除自己的资源。本例所用云实例、预备模板及本次镜像均独立确认不存在。
