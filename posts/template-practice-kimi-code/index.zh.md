---
title: 用 Kimi Code 完成一次无交互的脚本交付
summary: 配置原生 Kimi Code 的模型、工作区和调用入口，完成实际源代码修改，取回可运行脚本与说明，并接入自己的开发流程。
date: 2026-10-27
category: case
tags: [templates, models, kimi-code]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

一次性代码工作可以用 Kimi Code 的 headless prompt 模式完成：把任务、工作目录和交付要求一起提交，让原生 CLI 改文件，随后导出程序与说明。这里同时经历了已有函数修复和从零生成脚本两个步骤。

本例使用 Kimi Code `2.2.0`、CLI `0.5.7`、Python client/server
`0.4.0a6`，运行在极速版。已有代码的修复使用 `qwen3.8-flash`；另一实例配置
`qwen3.8-max` 完成 CLI、完整 Python 示例和 HTTP 的生成任务。
实际取回的 [generated_hello.py](./generated_hello.py) 运行后打印
`Hello from the sandbox`，配套 [report.txt](./report.txt) 保留了生成说明的原文。

## 准备平台与独立模型配置

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
```

先按[平台与镜像仓库配置](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)
准备极速版 API Key、地域、连接地址、Docker、构建权限和镜像仓库。然后配置独立的
模型服务。三个值须在同一授权服务与地域中匹配；API base 使用服务提供的前缀，
通常是 `/v1`，不追加 `/chat/completions`。

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export KIMI_MODEL_API_KEY='<YOUR_MODEL_API_KEY>'
export KIMI_MODEL_BASE_URL='<YOUR_CHAT_COMPLETIONS_BASE_URL>'
export KIMI_MODEL_NAME='<YOUR_AUTHORIZED_MODEL_ID>'
abx template launch Alibaba-Agent-Sandbox/awesome-templates//kimi-code --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
```

这是显式模型 API Key 配置，不启动浏览器 OAuth，也不继承本机已有登录态。
沙箱 API Key 用于平台，模型 Key 用于对应模型服务，`ABX_SERVER_TOKEN` 独立保护
应用命令。使用自己账号支持 Chat Completions 和工具调用的确切模型 ID。

## 确认原生工具与工作方式

```bash
abx run "$SANDBOX_ID" kimi_version
abx run "$SANDBOX_ID" kimi_setup_check
```

上游 prompt 模式会允许工具，因此包装层要求显式 allow_tools=true。每次调用使用独立的临时 Kimi 设置并清理自己的进程组，返回缓冲 stream-JSON 文本；当前接口没有可续接的会话 ID。

这些预检帮助确认安装和配置状态，实际交付仍要看任务返回与生成文件。
Kimi Code 的主任务命令是 `kimi`；这个案例使用工作目录 `/home/user/app`。

## 从现有函数修复开始

任务中的 `calculator.py` 把 `add(a, b)` 写成了 `a - b`。要求代理纠正函数、保持
`test_calculator.py` 不变，并写出 `REPORT.md` 说明原因。修改完成后，原有三个检查
全部通过，原检查文件保持不变；独立进程还核对了额外输入：

| 输入 | 实际结果 |
| --- | --- |
| `add(127, 83)` | `210` |
| `add(-91, 13)` | `-78` |
| `add(0.5, 1.25)` | `1.75` |

自己的项目可以采用同样的交付约束：指定要改的模块、保留现有检查，在代理返回后
独立运行自己的构建和检查，并审阅实际文件差异。

## 生成脚本与说明，通过三个入口取回结果

先从一个完整的小任务开始：生成 `generated_hello.py` 和 `GENERATED_REPORT.md`。
下面是实际文档中的 CLI 请求，包含当前入口所需的参数：

```bash
ABX_HTTP_TIMEOUT=420 abx run "$SANDBOX_ID" kimi --json-args '{"prompt":"Create generated_hello.py that prints exactly Hello from the sandbox, and GENERATED_REPORT.md explaining the program. Preserve unrelated existing files.","allow_tools":true,"cwd":"/home/user/app","command_timeout":300}'
abx download "$SANDBOX_ID" /home/user/app/generated_hello.py ./generated_hello.py
abx download "$SANDBOX_ID" /home/user/app/GENERATED_REPORT.md ./GENERATED_REPORT.md
python generated_hello.py
```

输出为 `Hello from the sandbox`。该任务允许原生工具操作所选工作区，请使用自己
可丢弃的实例。任务返回对象若有 `exit_code`，先确认它为零；随后检查实际文件和
程序输出。遇到非零退出或缺失文件时，先处理错误及可能的部分产物，再决定下一步。

Python 用户下载 [quickstart.py](./quickstart.py)，保持以上环境变量与实例 ID，
执行 `python quickstart.py`。附件是实际执行过的完整 SDK 程序，通过
`ProviderSandbox.connect` 和带独立应用令牌的 `application_client` 调用 `kimi`，
结束后关闭连接。它不删除外层沙箱；生成文件仍可用 `abx download` 取回。

HTTP 用户按[直接 HTTP 说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)
解析同一实例端口 9000，保留网关头、路径、查询参数，再添加应用认证。
向 `POST /commands/kimi` 发送上面 `--json-args` 的直接 JSON 对象，不加
`args` 包装层。设置至少 420 秒客户端等待；任务的 300 秒执行期限与实例的
1800 秒寿命分别控制不同阶段，返回值是缓冲结果。

三个入口是替代方式，选一个即可。本例分别完成了三次生成，取回了三个说明文档，
并独立运行下载的程序。分别尝试时使用新实例，或先移走自己上一轮的两个输出，
让当前任务的产物与旧文件区分清楚。

## 切换模型、密钥或 endpoint

模型的三个变量在启动时读取。要换模型，保存产物后 export 新的授权模型 ID，再从
同一个公开模板创建新实例，后续操作使用新返回的实例 ID。换服务时同步更换 Key、
base 和模型 ID；在旧进程启动后修改本机 export 不会重配旧进程。

本例通过两个分别配置的实例使用了 `qwen3.8-flash` 和 `qwen3.8-max`。
其他模型或账号的工具能力取决于其服务配置，使用前按自己的授权条件确认。

## 接到自己的开发流程

把下一步任务所需的代码与上下文放进工作区文件，可以分阶段再次提交任务。需要长期保留结果时先下载；修改自己的模板时保留原生 CLI 身份、配置隔离和进程清理，不要依赖上一轮临时设置继续存在。

文件不会自动更新模板或本机项目。把需要保留的源文件、说明和差异下载到自己的
受控目录，审阅后再应用。任务结束显式删除实例：

```bash
abx kill "$SANDBOX_ID"
```

`close()` 只关闭本机连接。复用的预备模板和镜像按照
[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)
只删除自己的资源。修改原生程序、依赖或工具权限时，保留各自许可证与版本记录；
具体配置和上游授权见[此模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/kimi-code/README.zh-CN.md)。

## 在 OpenSandbox 中使用同一工作流

这个案例也可以在 OpenSandbox 中完成。先按[OpenSandbox 提供方指南](https://github.com/Alibaba-Agent-Sandbox/awesome-providers/blob/main/opensandbox/docs/README.md)准备服务地址、服务 API Key 和镜像仓库，然后在创建实例前选择平台：

```bash
export ABX_PROVIDER=opensandbox
export ABX_OPENSANDBOX_USE_SERVER_PROXY=true
```

接着执行上面的 launch、业务命令和 SDK 示例；后续终端与 Python 继续使用同一个平台和实例 ID。沙箱 API Key 与应用令牌分别配置，原有业务输入、返回结果和结束实例的方法相同。

这里使用 OpenSandbox1.1.1 的服务代理模式；CLI、完整 SDK 示例和直接 HTTP 都能完成文中的实际任务。代理模式要求客户端能访问服务地址。若部署环境改为直连模式，客户端还必须能访问提供方解析出的端点；更换配置后重新创建自己的实例，不复用另一平台的 ID。
