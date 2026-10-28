---
title: 用 Prime Agent 的 Python REPL 修复现有函数
summary: 配置原生 Prime Agent 的模型、工作区和调用入口，完成实际源代码修改，取回可运行脚本与说明，并接入自己的开发流程。
date: 2026-10-27
category: case
tags: [templates, models, prime-agent]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

Prime Agent 的原生 Python REPL 工具可以用于小范围代码修复。这个案例让它纠正已有计算函数、保留原有检查，再生成脚本和说明，最后把文件带回本机。

本例使用 Prime Agent `0.10.0`、CLI `0.5.7`、Python client/server
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
export PRIME_MODEL_API_KEY='<YOUR_MODEL_API_KEY>'
export PRIME_MODEL_BASE_URL='<YOUR_CHAT_COMPLETIONS_BASE_URL>'
export PRIME_MODEL='<YOUR_AUTHORIZED_MODEL_ID>'
abx template launch Alibaba-Agent-Sandbox/awesome-templates//prime-agent --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
```

这是显式模型 API Key 配置，不启动浏览器 OAuth，也不继承本机已有登录态。
沙箱 API Key 用于平台，模型 Key 用于对应模型服务，`ABX_SERVER_TOKEN` 独立保护
应用命令。使用自己账号支持 Chat Completions 和工具调用的确切模型 ID。

## 确认原生工具与工作方式

```bash
abx run "$SANDBOX_ID" prime_agent_version
abx run "$SANDBOX_ID" prime_agent_kernel_check
abx run "$SANDBOX_ID" prime_agent_setup_check
```

这里使用未修改的稳定版原生 Rust CLI，以及工具名为 ipython 的原版 CPython REPL 后端。prime_agent_kernel_check 检查固定的本地 kernel 环境；任务返回原生缓冲输出。该入口围绕单次 headless 编码工作组织。

这些预检帮助确认安装和配置状态，实际交付仍要看任务返回与生成文件。
Prime Agent 的主任务命令是 `prime_agent`；这个案例使用工作目录 `/home/user/workspace`。

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
ABX_HTTP_TIMEOUT=420 abx run "$SANDBOX_ID" prime_agent --json-args '{"prompt":"Create generated_hello.py that prints exactly Hello from the sandbox, and GENERATED_REPORT.md explaining the program. Preserve unrelated existing files.","cwd":"/home/user/workspace","command_timeout":300}'
abx download "$SANDBOX_ID" /home/user/workspace/generated_hello.py ./generated_hello.py
abx download "$SANDBOX_ID" /home/user/workspace/GENERATED_REPORT.md ./GENERATED_REPORT.md
python generated_hello.py
```

输出为 `Hello from the sandbox`。该任务允许原生工具操作所选工作区，请使用自己
可丢弃的实例。任务返回对象若有 `exit_code`，先确认它为零；随后检查实际文件和
程序输出。遇到非零退出或缺失文件时，先处理错误及可能的部分产物，再决定下一步。

Python 用户下载 [quickstart.py](./quickstart.py)，保持以上环境变量与实例 ID，
执行 `python quickstart.py`。附件是实际执行过的完整 SDK 程序，通过
`ProviderSandbox.connect` 和带独立应用令牌的 `application_client` 调用 `prime_agent`，
结束后关闭连接。它不删除外层沙箱；生成文件仍可用 `abx download` 取回。

HTTP 用户按[直接 HTTP 说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)
解析同一实例端口 9000，保留网关头、路径、查询参数，再添加应用认证。
向 `POST /commands/prime_agent` 发送上面 `--json-args` 的直接 JSON 对象，不加
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

可以把数据处理或项目修改步骤交给同一个本地 REPL 后端，并在任务返回后独立运行自己的程序。需要额外 Python 依赖时在 Dockerfile 中固定安装；改变 kernel 环境、daemon 会话或递归代理等能力需要自己的模板设计和重新验证。

文件不会自动更新模板或本机项目。把需要保留的源文件、说明和差异下载到自己的
受控目录，审阅后再应用。任务结束显式删除实例：

```bash
abx kill "$SANDBOX_ID"
```

`close()` 只关闭本机连接。复用的预备模板和镜像按照
[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)
只删除自己的资源。修改原生程序、依赖或工具权限时，保留各自许可证与版本记录；
具体配置和上游授权见[此模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/prime-agent/README.zh-CN.md)。

## 在 OpenSandbox 中使用同一工作流

先按[OpenSandbox 提供方指南](https://github.com/Alibaba-Agent-Sandbox/awesome-providers/blob/main/opensandbox/docs/README.md)准备服务地址、服务 API Key 和镜像仓库。在创建前保留上面的模型 Key 与 endpoint，并选择平台、直连模式和模型：

```bash
export ABX_PROVIDER=opensandbox
export ABX_OPENSANDBOX_USE_SERVER_PROXY=false
export PRIME_MODEL='qwen3.8-flash'
```

这里的模型 ID 来自本例的模型服务，需与自己的 Key、endpoint 和授权匹配。接着执行前面的 launch、业务命令和完整 SDK 示例，后续调用继续使用同一平台和新实例 ID。CLI、SDK 与直接 HTTP 已分别完成本文的实际任务，并独立读取产物。

直连要求客户端能访问提供方解析出的端点；保留网关头、URL 路径/查询和独立应用令牌。服务代理与直连是不同的部署配置，客户端的等待时间不会改变上游代理期限，也不会延长远端任务或实例寿命。更换平台或启动模型配置后重新创建实例，先导出旧实例中的文件。
