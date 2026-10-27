---
title: 用浏览器读取发票页面，连接截图与表单流程
summary: 通过 Playwright 提取页面金额，了解独立浏览器与原生 MCP 会话的使用边界。
date: 2026-10-27
category: case
tags: [templates, browser-automation]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

浏览器页面里的业务信息可以直接变成结构化结果。这里让远端 Chromium 打开一段发票页面，取回标题和金额；同一个模板还可以连接截图、链接、表单和 PDF 工作。

真实浏览器返回 title: Invoice，正文含 Total: 51.30。三个入口分别导航并提取了这个页面；金额来自本例提供的 HTML。 

## 准备独立工作区

本例使用极速版、CLI `0.5.7`、Python client/server `0.4.0a6` 和模板的默认 Docker 配方。
先按[平台配置](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)
准备极速版沙箱 API Key、地域、连接地址、Docker、构建权限和镜像仓库。
应用的 `ABX_SERVER_TOKEN` 独立于平台认证；这个模板不需要模型 endpoint、模型 Key 或产品登录。

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export ABX_HTTP_TIMEOUT=450
abx template launch Alibaba-Agent-Sandbox/awesome-templates//browser-automation --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
abx sandbox command list "$SANDBOX_ID"
```

## 提交任务，取回业务结果

```bash
abx run "$SANDBOX_ID" browse --json-args '{"url":"data:text/html,<title>Invoice</title><h1>Total: 51.30</h1>","action":"extract"}'
```

真实浏览器返回 title: Invoice，正文含 Total: 51.30。三个入口分别导航并提取了这个页面；金额来自本例提供的 HTML。

截图、链接和 CSS 提取、无匹配结果、表单填值核对、Python 文件执行以及横竖版 PDF 都已实际调用；远端 PNG/PDF 文件也被下载检查。原生 MCP 启动、工具列表、计数器操作、截图、停止和状态入口均已调用。

## 用 Python 或 HTTP 连接自己的程序

附件 [quickstart.py](./quickstart.py) 是实际执行的完整模板 SDK 示例。
保留以上环境和实例 ID，运行 `python quickstart.py`。它连接同一个实例，通过
`application_client` 调用业务方法，并关闭本机连接。文件型结果在脚本中下载到本机。
这是 CLI、Python、HTTP 中的一种替代方式，选择适合自己程序的入口即可。

HTTP 用户按[直接 HTTP 指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)
解析当前实例的 9000 端口，保留网关头、URL 路径与查询参数，再添加独立应用认证。
向上方命令对应的 `POST /commands/<命令名>` 发送 `--json-args` 中的直接 JSON 对象，
不增加 `args` 包装层。结果放在 `result` 内；具体字段和全部命令见
[模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/browser-automation/README.zh-CN.md)。

本例分别执行了三种方式，并在文件型结果的前后调用间删除自己上一次的输出，
分别取回新产物。自己的工作流可以使用新的输出名或新实例，避免旧文件影响判断。

## 接到自己的业务并二次开发

browse、scrape、fill_form 每次拥有独立浏览器，不共享登录 cookie；fill_form 只填值并内部核对，不提交表单。需要在同一浏览器连续操作时使用 mcp_start、mcp_call、mcp_status、mcp_stop，在自己的会话内处理网站登录，并显式结束会话。此模板不需要模型 Key，页面提取与固定浏览器操作可直接接入自己的业务。

该模板的业务处理不调用大模型；若应用需要模型推理，由上层应用另外配置自己的
授权服务，把这里取回的文本、文件或编译结果作为输入。修改模板依赖、字体、语言包
或编译器时，在自己的版本中固定它们，并重新运行实际业务流程。

## 导出与清理

先下载需要保留的文件，再执行：

```bash
abx kill "$SANDBOX_ID"
```

SDK 的 `close()` 只关闭连接，不删除云实例。1800 秒实例寿命与 450 秒客户端等待
分别控制不同阶段。可复用的预备模板和镜像按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)
仅删除自己的资源。本例结束后，所用沙箱、预备模板和本次镜像均已独立确认不存在。
