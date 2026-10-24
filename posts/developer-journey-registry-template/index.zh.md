---
title: 用 Registry 的 Python 模板搭一个远程脚本工作台
summary: 从 python-hello 模板创建沙箱，上传并运行 Python 文件，通过 CLI、SDK 和 HTTP 调用它，再用终端和系统工具处理日常开发工作。
date: 2026-10-24
category: case
tags: [python, templates, registry, cli]
authors: [Alibaba-Agent-Sandbox]
cover: ./cover.svg
draft: false
---

有一个 Python 脚本要临时跑一下，如果每次都从安装环境、启动服务开始，准备工作会比脚本本身更长。Registry 中的模板可以作为起点：先用现成的运行环境和应用命令，再上传自己的文件。

这篇选择 [python-hello](https://registry.agent-sandbox.cn/templates/python-hello/)，把它部署到 Alibaba Cloud Express，做一个可以从终端和程序中调用的 Python 工作台。我们会运行一段代码、上传文件、下载结果，并连接交互终端。

这里采用云端 steps 构建，所以本机无需 Docker。示例使用 CLI `0.4.12` 和 Python client `0.3.1a2`，后者是显式选择的 alpha 版本。

## 先看看模板提供了什么

`python-hello` 不只是一个装好 Python 的镜像。它还包含应用命令，例如问候、运行代码字符串、运行文件和执行测试。创建沙箱后，可以发现这些命令，再按名称调用。

模板的主要文件各有职责：

| 文件 | 用途 |
| --- | --- |
| `template.yaml` | 描述模板和运行配置 |
| `Dockerfile` | 定义基础环境与依赖 |
| `commands.py` | 提供可从 CLI、SDK、HTTP 调用的命令 |

Registry 帮助我们找到模板，实际部署使用 Git 仓库中的源码。本文固定源码提交，避免以后分支更新时，安装步骤跟着变化。

![从模板源码准备云端构建，再创建和使用 Python 工作台](./flow.svg)

## 准备本机工具和账户配置

先按[安装案例](/blog/developer-journey-cli-install/)准备 CLI，然后为模板准备工具安装 Python 依赖：

```bash
mkdir registry-lab
cd registry-lab
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple \
  'agent-sandbox-client==0.3.1a2' 'PyYAML==6.0.3'
```

除了运行沙箱所需的连接配置，创建模板还需要有权限的阿里云 AK/SK：

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SANDBOX_API_KEY='<YOUR_SANDBOX_API_KEY>'
export ABX_SANDBOX_BASE_URL='<YOUR_EXPRESS_API_BASE_URL>'
export ABX_SANDBOX_DOMAIN='<YOUR_EXPRESS_SANDBOX_DOMAIN>'
export ALICLOUD_ACCESS_KEY_ID='<YOUR_ACCESS_KEY_ID>'
export ALICLOUD_ACCESS_KEY_SECRET='<YOUR_ACCESS_KEY_SECRET>'
export ALIBABA_CLOUD_REGION_ID='<YOUR_REGION_ID>'
```

这些配置应对应同一账户和目标地域。如果当前 shell 还保留了另一套 `E2B_API_KEY`、`E2B_API_URL`、`E2B_DOMAIN`，先处理配置冲突。这个流程不使用模型服务，不需要 LLM API key。

## 把模板准备成云端构建配方

```bash
git clone https://github.com/Alibaba-Agent-Sandbox/awesome-templates.git
cd awesome-templates
git checkout 565e546a3e1d814e840062cbdd5da4ba295e16a6
python scripts/prepare_steps.py python-hello --output ./python-hello-steps
abx --json template deploy ./python-hello-steps --build steps \
  --alias "python-hello-$(date +%s)" -y
```

`prepare_steps.py` 会生成一个新的模板目录，把模板所需的源码和配置放进 steps 配方。它支持[指南中说明的 Dockerfile 范围](https://registry.agent-sandbox.cn/source/awesome-templates/docs/platform-steps.zh-CN.md/)，不是任意 Dockerfile 的通用转换器。

部署输出中的 `TemplateID` 就是接下来要使用的模板 ID。先保存它并查看构建状态：

```bash
export TEMPLATE_ID='<DEPLOY_RETURNED_TEMPLATE_ID>'
abx --json template info "$TEMPLATE_ID"
```

看到 `submitted` 或 `building` 时，云端还在准备环境。等状态变为 `ready` 后，再创建沙箱。如果仍在构建，稍后重复查询；若失败，先处理构建错误，不要反复创建实例。

这个模板内的 server 固定为源码版本 `e2cb27e24fde0a67112f82b8d44af463445a5d1a`，包版本为 `0.3.0`。本机 client 的安装不会自动升级它。

## 创建工作台，运行第一段 Python

```bash
abx create "$TEMPLATE_ID" --detach --timeout 1200
export SANDBOX_ID='<CREATE_RETURNED_SANDBOX_ID>'
abx --json sandbox command list "$SANDBOX_ID"
```

这里创建了一个生命周期为 1200 秒的实例。命令列表可以帮助我们了解模板提供的接口。先调用 `hello`，再把一段 Python 交给 `run_script`：

```bash
abx --json run "$SANDBOX_ID" hello --arg name=Ada
abx --json run "$SANDBOX_ID" run_script \
  --json-args '{"code":"print(21 * 2)"}'
```

两次调用分别得到：

```json
{"result": "Hello, Ada!"}
```

```json
{"result": "42\n"}
```

命名命令适合复用模板已经封装好的操作。如果只是想直接执行沙箱进程，则使用 `abx exec`：

```bash
abx exec "$SANDBOX_ID" -- python3 -c 'print(6 * 7)'
```

## 上传自己的文件，再取回文件

代码变长后，把它存成文件会更方便：

```bash
printf 'print(6 * 7)\n' > main.py
abx upload "$SANDBOX_ID" main.py /home/user/app/main.py
abx --json run "$SANDBOX_ID" run --arg file=main.py
```

模板的 `run` 命令从应用工作目录运行这个文件，输出同样是 `42`。如果要查看远端文件或取回本地副本：

```bash
abx --json sandbox files list "$SANDBOX_ID" --path /home/user/app
abx download "$SANDBOX_ID" /home/user/app/main.py download.py
```

模板还提供 `test` 命令。可以上传项目的测试文件，然后用 `abx run ... test --arg path=...` 指定执行路径；示例脚本中包含一个最小 pytest 文件的完整操作。

## 从自己的 Python 程序里调用

CLI 方便人工操作，SDK 适合接入已有程序。下面连接刚刚创建的实例，并调用它的应用服务：

```python
import asyncio
import os
from agent_sandbox import ProviderSandbox

async def main():
    sandbox = await ProviderSandbox.connect(os.environ["SANDBOX_ID"])
    try:
        async with await sandbox.application_client(9000) as client:
            result = await client.commands.run("hello", name="Python")
            print(result)
    finally:
        await sandbox.close()

asyncio.run(main())
```

这会输出 `Hello, Python!`。`ProviderSandbox` 管理沙箱连接，`application_client(9000)` 则连接模板在 9000 端口提供的应用。

也可以用普通 HTTP 客户端发送 POST。以下调用放在已经取得 `client` 的异步上下文中，并先 `import httpx`：

```python
async with httpx.AsyncClient(timeout=30) as http:
    response = await http.post(
        client.base_url.rstrip("/") + "/commands/hello",
        headers=client.auth_headers(),
        json={"name": "Ada"},
    )
    response.raise_for_status()
    print(response.json())
```

响应为 `{"result": "Hello, Ada!"}`。认证头由应用绑定提供。本文的模板未设置业务访问令牌；接入自己的业务前，应配置适当的应用认证。网关认证与应用令牌是不同的层次，控制面 API key 不能直接当作业务令牌使用。

## 需要排查时，直接进入终端

脚本行为与预想不一致时，可以先看系统状态，或直接进入同一个沙箱：

```bash
abx --json sandbox system metrics "$SANDBOX_ID"
abx --json sandbox system ports "$SANDBOX_ID"
abx --json sandbox process list "$SANDBOX_ID"
abx connect "$SANDBOX_ID"
```

进入终端后，可以切换到应用目录，查看文件，手动运行 Python：

```bash
cd /home/user/app
python3 main.py
exit
```

`exit` 离开这次终端会话，沙箱仍然存在。文件操作、应用调用和交互终端都针对同一个实例，适合把“上传—运行—查看结果”的过程连起来。

## 结束任务，保留想复用的模板

用完工作台后删除实例：

```bash
abx kill "$SANDBOX_ID"
```

模板和实例是两个资源。保留模板，下次就可以再次使用它的 ID 创建实例；如果这个模板也只是临时试用，可以一并删除：

```bash
abx template delete "$TEMPLATE_ID" -y
```

想一次体验完整流程，可以下载[配套脚本](./lab/03_registry_end_to_end.py)，在前面创建的 `registry-lab` 中运行：

```bash
python 03_registry_end_to_end.py \
  --abx "$(command -v abx)" \
  --source-ref 565e546a3e1d814e840062cbdd5da4ba295e16a6 \
  --build-timeout 900 --output ./registry-run
```

输出目录需要是新目录。这个脚本会自行创建模板和实例，运行示例后释放它们；前面手动创建的资源仍由你自己管理。要做更持久的开发工作，可以沿用手动步骤，保留模板并按任务创建新实例。
