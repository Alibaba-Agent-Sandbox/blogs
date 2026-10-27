---
title: 通过显式兼容接入层，让原版 Gemini CLI 完成文件编码任务
summary: 配置自己的 Chat Completions 模型服务，通过原版 CLI 和显式协议接入层完成编码，独立运行下载的文件。
date: 2026-10-27
category: case
tags: [templates, gemini, coding]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

已有兼容模型服务时，可以通过模板明确提供的接入层使用原版编码 CLI。本例运行原版 Gemini CLI0.64.0，通过项目自编的 GenerateContent-to-Chat 文本/工具协议适配层接入 Chat Completions，生成一个 Python 程序和报告，再取回代码独立运行。

实际下载的 [generated_hello.py](./generated_hello.py) 输出 `Hello from the sandbox`。CLI、完整 SDK 与直接 HTTP 三种替代入口分别生成了新文件和报告；每份 Python 文件在独立、只读、无网络的有界容器中执行。模型结束不等于文件正确，业务结果以实际文件与运行输出为准。

## 平台与模型配置

本例使用极速版默认源码配方、CLI0.5.7/client-server0.4.0a6。先按[平台配置指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)准备沙箱 API Key、连接地址、地域、Docker、构建权限和镜像仓库。

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export GEMINI_BYOK_API_KEY='<YOUR_COMPATIBLE_MODEL_API_KEY>'
export GEMINI_BYOK_BASE_URL='<YOUR_CHAT_COMPLETIONS_API_BASE>'
export GEMINI_BYOK_MODEL='<YOUR_AUTHORIZED_MODEL_ID>'
export ABX_HTTP_TIMEOUT=450
abx template launch Alibaba-Agent-Sandbox/awesome-templates//gemini --sandbox-timeout 1800 --yes
export SANDBOX_ID='<launch 返回的沙箱 ID>'
```

模型、Key 和 endpoint 来自自己有权限的同一个服务。base 包含实际 API 前缀，常见 `/v1`，不要追加 `/chat/completions`。兼容服务需支持模板说明列出的文本与工具调用能力。该接入链路无需浏览器 OAuth 登录，不继承本机账号，也不会把兼容服务的 Key 发到默认厂商服务。

## 让原版 CLI 完成文件任务

```bash
abx run "$SANDBOX_ID" gemini_byok --json-args '{"prompt": "Create generated_hello.py that prints exactly Hello from the sandbox, and GENERATED_REPORT.md explaining the program. Preserve unrelated existing files.", "allow_unsafe_tools": true, "cwd": "/home/user/app", "command_timeout": 300}'
abx download "$SANDBOX_ID" /home/user/app/generated_hello.py ./generated_hello.py
abx download "$SANDBOX_ID" /home/user/app/GENERATED_REPORT.md ./GENERATED_REPORT.md
```

`allow_unsafe_tools:true` 是对自己拥有的一次性沙箱中原生工具权限的显式选择。代理可以编辑和执行工作区代码；使用自己的输入副本并独立检查产物。适配层使用每次调用的私有状态与临时原生协议地址，外部请求发送到明确配置的模型 endpoint，保留原版 CLI 的工具循环。

实际原生编码链路还修复过带错误的已有程序，原始测试保持不变，返回后独立执行原始和额外边界用例。本文的小程序用于展示一条完整的接入、生成、导出路径，不代表所有厂商扩展功能都已由兼容层覆盖。

## 用 SDK 或 HTTP 接入

下载 [quickstart.py](./quickstart.py)，保留上述环境和实例 ID，执行 `python quickstart.py`。这是实际运行过的完整模板 SDK 示例，连接同一实例，执行业务方法并下载生成文件。不要在未清理前对同一实例连续执行所有替代示例。

HTTP 按[直接调用指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)解析9000端口，保留网关头、路径、查询和独立应用认证，使用 `POST /commands/gemini_byok`。body 是上述 --json-args 中的直接对象，不加 args 包装；响应外层为 result。检查命令 exit_code、原生完成状态、实际代码和报告。

本例原生核心流程使用 qwen3.8-flash，文档的三种替代入口使用 qwen3.8-max。更换模型、Key 或 endpoint 时重新 export 对应三项并启动新实例，后续改变本机环境不会重配旧应用。

## 二次开发和账号边界

上传自己的项目与锁文件，使用 WORKSPACE 内已有 cwd，描述具体修改、需要保留的原始测试和交付文件。把模型输出视为待检查的代码，从独立接口取回后执行自己的测试。当前适配层的协议、工具范围、输入/输出与执行期限见[模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/gemini/README.zh-CN.md)。扩展适配层时保留上游版本和许可证，逐项确认实际协议行为。

本文使用的是 `gemini_byok` 显式兼容接入方法。模板另有原生厂商账号入口 `gemini`，需要它自己的厂商凭据或接入条件；本例未使用该账号链路，不表示已登录厂商账号或具有其订阅权益。该模板完整方法验收因此仍保留 Beta，本文的兼容接入效果不替代其他入口的验证。

## 保存结果并结束

```bash
abx kill "$SANDBOX_ID"
```

先保存需要的源码和报告，SDK close 只关闭连接。模板与镜像按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)只删除自己的资源。本例的实例、预备模板、本地和远端镜像均独立确认不存在。
