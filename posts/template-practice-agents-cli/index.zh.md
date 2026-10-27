---
title: 在同一个沙箱切换 Qwen 与 Codex，提交编码任务并延续原生会话
summary: 显式配置模型服务，通过受限 Agents API 使用两种原生编码代理，再独立下载和运行文件。
date: 2026-10-27
category: case
tags: [templates, agents-cli, coding]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

同一个工作区可以用不同的编码代理处理任务。本例在极速版沙箱里运行固定版本 Qwen Code 和 Codex，向原生会话提交生成程序的请求，再向同一会话追问。最终从独立文件接口取回代码，运行结果精确为 `Hello from the sandbox`。

这是本地 Agents API：实际执行的是已安装的 CLI，不是 OpenAI 托管 Agents 服务。接口只开放版本、显式 Codex 配置准备和六个会话/运行时入口；原生 CLI 仍有沙箱用户的工作区工具权限。

## 准备模型与平台

本例使用 CLI0.5.7/client-server0.4.0a6、Codex0.162.1、Qwen Code0.23.0 和 Node24.16.0。按[平台配置指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)准备极速版沙箱 API Key、连接地址、地域、Docker、构建权限和镜像仓库。

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export OPENAI_API_KEY='<YOUR_MODEL_API_KEY>'
export OPENAI_BASE_URL='<YOUR_MODEL_API_BASE>'
export OPENAI_MODEL='<YOUR_AUTHORIZED_MODEL_ID>'
abx template launch Alibaba-Agent-Sandbox/awesome-templates//agents-cli --sandbox-timeout 1800 --yes
export SANDBOX_ID='<launch 返回的沙箱 ID>'
abx run "$SANDBOX_ID" agents_version
```

Qwen 使用 Chat Completions，Codex 使用 Responses。同一 endpoint 同时支持两种协议时，可在一个实例中使用两个适配器；否则分别启动实例并设置匹配的 Key、endpoint 和模型。API Key 模式不启动 OAuth，也不继承本机账号。

## 显式准备 Codex 的原生配置

Codex 会话前执行：

```bash
abx run "$SANDBOX_ID" agents_configure_codex
```

返回 `configured:true`、`wire_api:responses`、`credential_written:false`。配置文件只保存环境变量引用，不保存密钥；关闭原生 WebSockets，使用 HTTP Responses。相同配置可重复准备；其他已有配置和符号链接会被保留并报错，此时在新实例选择新的 CODEX_HOME。

## 选择适配器并生成实际文件

下载 [quickstart.py](./quickstart.py)，在上述环境中运行：

```bash
export AGENTS_ADAPTER=qwen-code
python quickstart.py
```

脚本连接 launch 已经启动的9000服务，创建会话、提交消息、轮询输出，并从独立提供方文件接口下载 generated_hello.py 和 GENERATED_REPORT.md。应用 HTTP 策略关闭了通用文件和 shell 路由，所以文件导出使用提供方 SDK。

实际 Qwen 生成的程序见 [qwen-generated.py](./qwen-generated.py)，Codex 的结果见 [codex-generated.py](./codex-generated.py)。两者取回后分别在只读、无网络、有资源上限的独立 Python 容器运行，stdout 都是 `Hello from the sandbox` 加换行。

使用另一适配器时先保存/移除自己的上一次同名输出，避免把旧文件当作新产物，再设置 `AGENTS_ADAPTER=codex` 执行完整示例。本文两种适配器的完整 SDK 与直接 HTTP 入口分别产生新文件和报告，六份业务程序独立运行通过。

## 使用 HTTP 会话并继续追问

按[直接调用指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)解析9000端口，保留网关头、路径、查询和应用认证。

创建 `POST /v1/agents/sessions`：

```json
{"adapter":"qwen-code","agent":{"model":"<YOUR_MODEL_ID>"},"environment":{"type":"self_hosted","workspace_directory":"/home/user/workspace"}}
```

对返回的 ID 请求 `POST /v1/agents/sessions/<id>/events`：

```json
{"events":[{"type":"agent.session.input.message","input":[{"role":"user","content":[{"type":"input_text","text":"Create generated_hello.py that prints exactly Hello from the sandbox, and GENERATED_REPORT.md explaining the program. Preserve unrelated files."}]}]}]}
```

202 表示入队。用有期限的轮询读取 session 状态和 `/items?limit=100&order=asc`；遇到 error/failed 停止。等待出现新输出且回到 idle 后，仍应独立读取和运行文件，不能把 idle 当作编辑成功。

向同一个 ID 再发送消息即可恢复原生对话。实际流程中，两种代理都在第二轮把上一轮给出的唯一代码写入新文件，追问没有重传该代码；原版持久状态中的两轮均已完成，独立文件内容与原代码相符。不同会话并不构成操作系统权限隔离，它们仍属于同一沙箱用户。

## 切换模型和二次开发

本例同一个实例的启动配置为 qwen3.8-max，先为两种原生代理的会话显式选择 qwen3.8-flash，再用 max 完成 SDK/HTTP 业务。保持相同 endpoint/Key 时，在新 session 的 agent.model 选择自己有权限的另一个模型；更换 Key 或 endpoint 时修改启动变量并 launch 新实例。

业务开发可把输入源码和原始测试上传到自己的目录，让会话选择这个已有 workspace_directory；要求保留原始测试、生成报告和目标文件，再从独立接口运行检查。原生会话请求只接受已发布的字段，不要把 SDK 内部 AgentSpec 的 permissions 等字段直接放入公共请求。全部命令、六个运行时/会话路由及边界见[模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/agents-cli/README.zh-CN.md)。

## 导出与结束

原生工具可能修改工作区，先保存所需源码和报告。此受限模板没有开放取消或删除会话路由，客户端断开不表示取消；结束当前拥有的实例可以停止其中工作：

```bash
abx kill "$SANDBOX_ID"
```

SDK close 只关闭连接。预备模板和镜像按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)只删除自己的精确资源。本例的实例、预备模板、本地和远端镜像均独立确认不存在。
