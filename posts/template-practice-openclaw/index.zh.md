---
title: 通过 OpenClaw 原生网关汇总费用，并在同一会话继续追问
summary: 配置自己的模型服务与独立网关认证，完成费用汇总、上下文追问和可重复使用的对话接口。
date: 2026-10-27
category: case
tags: [templates, openclaw, gateway]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

一个对话网关的价值在于接住真实业务消息并保留会话上下文。本例通过原版 OpenClaw 网关汇总三笔费用，再在同一个会话中去掉其中一笔；后一次请求不重新发送明细，使用原生会话历史继续计算。

实际第一轮返回3笔、51.30，第二轮去掉火车费用后返回2笔、36.30。CLI、完整 SDK 和直接 HTTP 分别完成了这个两轮流程，结果字段由独立算术核对。可以查看这次实际结果的[结构化摘要](./expense-result.json)。

## 配置平台、模型和网关认证

本例使用极速版默认源码配方、OpenClaw2026.10.4、Node24.16.0、CLI0.5.7 和 client/server0.4.0a6。按[平台配置指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)准备沙箱 API Key、连接地址、地域、Docker、构建权限和镜像仓库。

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export OPENCLAW_GATEWAY_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export OPENCLAW_MODEL_API_KEY='<YOUR_MODEL_API_KEY>'
export OPENCLAW_MODEL_BASE_URL='<YOUR_CHAT_COMPLETIONS_API_BASE>'
export OPENCLAW_MODEL='<YOUR_AUTHORIZED_MODEL_ID>'
export ABX_HTTP_TIMEOUT=420
abx template launch Alibaba-Agent-Sandbox/awesome-templates//openclaw --sandbox-timeout 1800 --yes
export SANDBOX_ID='<launch 返回的沙箱 ID>'
```

三个模型变量要一起配置，API base 按服务要求包含 `/v1`，不要追加 `/chat/completions`。使用自己有权限的模型 ID，模型需支持模板声明的上下文/输出限制。模型 Key、网关 token、应用 token 和平台凭据各有用途，不互相替代。此 API Key 流程无需厂商 OAuth 登录，也不从旧的 OPENAI_API_KEY/ANTHROPIC_API_KEY 猜测服务。

## 发起第一轮费用汇总

```bash
abx run "$SANDBOX_ID" gateway_start --json-args '{"bind":"loopback","command_timeout":60}'
abx run "$SANDBOX_ID" gateway_health
abx run "$SANDBOX_ID" gateway_status
abx run "$SANDBOX_ID" gateway_chat --json-args '{"prompt":"Summarize taxi 12.50, lunch 23.80 and train 15.00. Return only JSON with integer count and two-decimal string total."}'
```

返回对象包含 `session_id` 和 `text`。实际业务文本解析后为：

```json
{"count":3,"total":"51.30"}
```

## 在同一会话继续追问

把上一次返回的 session_id 填入下面的占位符：

```bash
abx run "$SANDBOX_ID" gateway_chat --json-args '{"prompt":"Remove the train from the previous expenses. Return the same JSON fields.","session_id":"<returned-session-id>"}'
```

这次不发送原始金额。原生会话继续使用先前明细，实际文本解析后为：

```json
{"count":2,"total":"36.30"}
```

使用相同 ID 延续一个业务线程，省略或更换 ID 开始独立对话。模型文字格式可能变化，应用应解析 JSON、检查字段并独立核算。本例复杂度有限，不把一次费用汇总当成财务系统的准确性保证。

## SDK、HTTP 和二次开发

下载 [quickstart.py](./quickstart.py)，保留上述环境，执行 `python quickstart.py`。完整脚本连接同一个实例，执行健康检查与两轮实际消息，最后停止自己启动的网关并关闭连接。

HTTP 用户按[直接调用指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)解析9000端口，保留网关头、路径、查询和应用认证。`POST /commands/gateway_chat` 的 body 就是上述直接参数对象。封装内部调用 [OpenClaw 原生 Chat Completions](https://docs.openclaw.ai/gateway/openai-http-api)，不绕过网关直连模型，也无需把18789端口暴露到公网。CLI、SDK、HTTP 是替代入口，按自己的应用选择一种。

本例原生流程使用 qwen3.8-flash，完整文档流程使用 qwen3.8-max。更换模型、Key 或 endpoint 时修改三个 OPENCLAW_MODEL 变量并启动新实例；旧实例保留原启动环境。可将费用文本换成自己的发票 CSV，明确输出 schema，并在应用侧做独立计算与异常处理。

当前是文本模型对话 slice，禁用模型工具、渠道、浏览器/control UI 和嵌套 Docker；不会自动完成 Slack 等消息渠道接入。需要这些功能时应基于自己的模板副本补充配置，并单独验证实际使用流程。

## 会话生命周期与结束

`gateway_stop` 删除网关私有临时配置、工作区及对话历史。停止后重启，即使复用旧 session ID，也会从新会话开始。客户端超时或断开不保证已经接受的原生任务取消；需要结束剩余工作时停止当前拥有的网关或删除沙箱。生命周期与对话串行执行，stop 可能等待当前有期限的请求结束。

```bash
abx run "$SANDBOX_ID" gateway_stop
abx kill "$SANDBOX_ID"
```

源码、全部五个命名命令与参数见[模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/openclaw/README.zh-CN.md)。SDK close 只关闭连接；预备模板与镜像按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)仅删除自己的资源。本例的实例、预备模板、本地与远端镜像均独立确认不存在。

## 在 OpenSandbox 中使用同一工作流

这个案例也可以在 OpenSandbox 中完成。先按[OpenSandbox 提供方指南](https://github.com/Alibaba-Agent-Sandbox/awesome-providers/blob/main/opensandbox/docs/README.md)准备服务地址、服务 API Key 和镜像仓库，然后在创建实例前选择平台：

```bash
export ABX_PROVIDER=opensandbox
export ABX_OPENSANDBOX_USE_SERVER_PROXY=true
```

接着执行上面的 launch、业务命令和 SDK 示例；后续终端与 Python 继续使用同一个平台和实例 ID。沙箱 API Key 与应用令牌分别配置，原有业务输入、返回结果和结束实例的方法相同。

这里使用 OpenSandbox1.1.1 的服务代理模式；CLI、完整 SDK 示例和直接 HTTP 都能完成文中的实际任务。代理模式要求客户端能访问服务地址。若部署环境改为直连模式，客户端还必须能访问提供方解析出的端点；更换配置后重新创建自己的实例，不复用另一平台的 ID。
