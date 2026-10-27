---
title: 在独立工作区用 Crush 修复计算函数并交付说明文档
summary: 为原生 Crush 配置兼容模型，让它修复已有代码、保留原检查并生成说明，再通过 CLI、Python 或 HTTP 取回结果。
date: 2026-10-27
category: case
tags: [crush, coding, models, templates]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

接手一段有问题的代码时，交付物应该包含能运行的源文件和说明。这个案例把任务放到
Crush 工作区：修复一个把加法写成减法的函数，保留已有检查，再取回修改结果。
另一个从零生成的小程序给出了可以直接下载运行的交付物：
[generated_hello.py](./generated_hello.py) 和
[GENERATED_REPORT.md 原文副本](./report.txt)。

本例使用原生 Crush `0.98.1`、CLI `0.5.7`、Python client/server `0.4.0a6`，
运行在极速版。修复任务使用 `qwen3.8-flash`，另一实例使用 `qwen3.8-max` 完成
CLI、完整 Python 示例和 HTTP 的生成任务。这里记录的是这些具体配置的结果。

## 安装并分开配置平台和模型

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
abx --version
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
```

先按[平台安装与镜像仓库配置](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)
准备极速版 API Key、地域、API 地址及镜像构建所需的权限和仓库。源码模板通过 Docker
构建，平台账号负责创建实例，模型账号负责调用模型。

然后在自己的终端填写以下三个模型设置。端点必须支持 Chat Completions 和工具调用，
Key 与模型 ID 必须在该服务和地域中有权限；`<YOUR_CHAT_COMPLETIONS_BASE_URL>`
是 API base，例如供应商提供的 `/v1` 地址，不是网页聊天地址，也不包含
`/chat/completions` 后缀。

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export CRUSH_API_KEY='<YOUR_MODEL_API_KEY>'
export CRUSH_BASE_URL='<YOUR_CHAT_COMPLETIONS_BASE_URL>'
export CRUSH_MODEL='<YOUR_AUTHORIZED_MODEL_ID>'
abx template launch Alibaba-Agent-Sandbox/awesome-templates//crush --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
abx run "$SANDBOX_ID" crush_version
abx run "$SANDBOX_ID" crush_setup_check
```

这是 API Key 模式，无需浏览器 OAuth 登录，也不导入本机 Crush 登录态。
`crush_setup_check` 只返回安装和配置是否存在的标志，不进行登录或修改配置。
`ABX_SERVER_TOKEN` 是独立的应用令牌，不要把模型 Key 当作应用令牌。

## 修复已有函数，保留原有约束

已有 `calculator.py` 中的问题很小，却会影响调用它的其他程序：

```python
def add(a, b):
    return a - b
```

修复任务要求 Crush 改正函数、保持 `test_calculator.py` 不变，并生成 `REPORT.md`
说明原因。调用时传入工作目录，并显式设置 `allow_tools: true`；默认任务不开放工具。
使用自己可丢弃的工作区，编辑权限会赋予代理沙箱用户本身的文件和进程权限。

这次修复后，原有三个检查文件未被修改并全部通过。独立进程还核对了额外输入：

| 输入 | 实际结果 |
| --- | --- |
| `add(127, 83)` | `210` |
| `add(-91, 13)` | `-78` |
| `add(0.5, 1.25)` | `1.75` |

说明文档和新生成的文件也从工作区实际取回。自己的项目应沿用同样的交付方式：保留
已有约束，在代理返回后独立运行自己的程序和检查，再查看源文件差异。

## 从一个生成任务开始使用三个入口

可以先让 Crush 生成一个小程序和解释文档。这个任务在 CLI 中这样调用：

```bash
ABX_HTTP_TIMEOUT=420 abx run "$SANDBOX_ID" crush --json-args '{"prompt":"Create generated_hello.py that prints exactly Hello from the sandbox, and GENERATED_REPORT.md explaining the program. Preserve unrelated existing files.","allow_tools":true,"cwd":"/home/user/app","command_timeout":300}'
abx download "$SANDBOX_ID" /home/user/app/generated_hello.py ./generated_hello.py
abx download "$SANDBOX_ID" /home/user/app/GENERATED_REPORT.md ./GENERATED_REPORT.md
python generated_hello.py
```

实际输出为 `Hello from the sandbox`。命令返回对象还包含 `exit_code`、`stdout`
和 `stderr`；先确认退出码为零，再检查下载文件。模型的自然语言描述不能代替文件。

Python 用户可以下载 [quickstart.py](./quickstart.py)，保持相同环境变量和实例 ID，
执行 `python quickstart.py`。它通过 `ProviderSandbox.connect` 连接本次实例，
用 `application_client(9000, token=..., timeout=420)` 调用同一个 `crush` 命令，
最后关闭客户端连接。该附件不会删除外层沙箱。

HTTP 用户按[直接 HTTP 调用说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)
解析同一实例的端口地址，保留网关认证、路径和查询参数，再添加应用令牌。
向 `POST /commands/crush` 发送上面 `--json-args` 中的直接 JSON 对象，不加 `args`
包装层。HTTP 等待设为至少 420 秒；请求是缓冲响应，不是流式事件。

三个入口是替代方式，选择一个即可。需要分别尝试时，使用新实例或先移走自己上次
生成的两个文件，避免旧文件掩盖当前任务未完成的问题。

## 更换模型、Key 或 endpoint

Crush 模板的 `CRUSH_API_KEY`、`CRUSH_BASE_URL`、`CRUSH_MODEL` 是启动时设置。
要换模型，先保存产物，再 export 新的模型 ID，并从同一公开模板创建新实例；后续
调用使用新返回的实例 ID。更换服务时同时替换匹配的 Key、base 和模型 ID。
在旧实例启动后改变本机 export，不会重配旧进程。

本例的 `qwen3.8-flash` 和 `qwen3.8-max` 就通过两个分别配置的新实例完成实际任务。
这不意味着任意兼容端点或任意模型都具有相同能力；使用自己账号支持工具调用的配置。

## 扩展为自己的代码交付流程

把生成任务的 prompt 换成具体的现有模块、允许修改的文件及交付要求即可。把输入和
自己的检查放到明确的工作目录，使用 `cwd` 定位。默认不开放工具；需要编辑时才打开
`allow_tools`，并在模型返回后运行自己的验证。该封装关闭了上游子代理、MCP、网络
抓取、后台任务和 LSP 工具；不要把此模板当作所有 Crush 集成的完整替代。

模型生成的文件不会自动更新模板或本机项目。下载、审阅并保存所需文件后释放实例：

```bash
abx kill "$SANDBOX_ID"
```

`close()` 只关闭本机连接；镜像和预备模板可能留在自己的启动日志中用于复用，按
[清理说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)
只删除自己创建的资源。

Crush `0.98.1` 使用 **FSL-1.1-MIT**，当前不是 MIT 或 OSI 批准的开源发行版。
二次开发和分发前查看[上游许可证](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/crush/upstream-LICENSE.md)；
模板封装的 Apache-2.0 许可证不会改变原生二进制的授权条件。
