---
title: 用一句话搭一个可以调用的 Python API
summary: 给 abx 一句需求，让 Qwen Code 生成 Python 应用与模板，在云端运行后分别从 CLI 和 HTTP 调用，理解从想法到接口的过程。
date: 2026-10-24
category: case
tags: [cli, ai-generation, python, sandbox]
authors: [Alibaba-Agent-Sandbox]
cover: ./cover.svg
draft: false
---

想试一个小接口时，业务逻辑往往只有几行，准备应用服务和运行环境却要做不少工作。`abx create --prompt` 可以把需求交给代码生成工具，让它一并生成应用代码和沙箱模板。

这篇从一个最小例子开始：提供 `add` 命令，接收两个整数，返回它们的和。完成后，它既能在终端里调用，也能作为 HTTP API 被其他程序使用。

这里使用 `abx 0.4.12`、Alibaba Cloud Express 杭州地域和服务端提供的 `qwen3.8-max` 模型。Qwen Code 在本机负责生成模板；应用代码随后运行在云端沙箱中。

## 准备连接信息与模型

先按照[CLI 安装案例](/blog/developer-journey-cli-install/)配置沙箱账户，包括该账户实际需要的接入地址与域名。接下来补上创建模板和调用模型所需的变量：

```bash
export ABX_PROVIDER=alicloud-express
export ALIBABA_CLOUD_REGION_ID=cn-hangzhou
export ALICLOUD_ACCESS_KEY_ID='<YOUR_ACCESS_KEY_ID>'
export ALICLOUD_ACCESS_KEY_SECRET='<YOUR_ACCESS_KEY_SECRET>'
export ABX_SANDBOX_API_KEY='<YOUR_SANDBOX_API_KEY>'

export ABX_LLM_BASE_URL='<YOUR_OPENAI_COMPATIBLE_BASE_URL>'
export ABX_LLM_API_KEY='<YOUR_MODEL_API_KEY>'
export ABX_LLM_MODEL=qwen3.8-max
export ABX_QWEN_CODEGEN_TIMEOUT=1200
```

模型名称要以自己的服务为准。这里给代码生成预留 1200 秒；它与沙箱存活时间、云端构建等待时间是三个不同的设置。

CLI 支持自动准备 Qwen Code；如果本机已经安装，也可以用 `qwen --version` 查看版本。本例使用的是本机 Qwen Code `0.19.3`。

## 描述需要的接口

```bash
abx --json create \
  --prompt '创建一个 Python 沙箱，提供 add 命令接收两个整数并返回相加结果' \
  --yes --detach --build steps \
  --dir ./generated \
  --timeout 900
```

这条命令把生成文件放进 `generated` 下的新目录，采用 Express 的云端 steps 构建路径，并在创建完成后返回沙箱信息。`--yes` 用于跳过交互确认，`--detach` 则让创建后不直接进入终端。

`--timeout 900` 设置的是沙箱的生命周期。生成与构建可能需要几分钟；本例从开始生成到返回运行中的沙箱约用了五分半钟。

运行过程中会看到生成文件、提交模板和等待构建的进度。命令等模板达到 `ready` 后创建实例。保存返回的沙箱 ID，后面调用接口会用到：

```bash
export SANDBOX_ID='<CREATE_RETURNED_SANDBOX_ID>'
```

同时保留进度中返回的模板 ID，便于后面复用或删除模板。

## 先读懂生成了什么

生成目录包含四类文件：

| 文件 | 作用 |
| --- | --- |
| `commands.py` | 业务函数与应用命令 |
| `Dockerfile` | 可阅读、可继续修改的构建说明 |
| `template.yaml` | 资源、启动配置和云端构建步骤 |
| `README.md` | 模型生成的使用说明 |

本例生成的业务代码很直接：

```python
from agent_sandbox.server import command, start

@command("add", description="Add two integers and return the sum.")
def add(a: int, b: int) -> int:
    return a + b
```

`@command` 把函数注册到应用服务中。完整文件还在 `__main__` 下提供启动逻辑；作为命令模块导入时，不会重复启动服务。

可以下载本例的 [commands.py](./lab/generated/commands.py)、[Dockerfile](./lab/generated/Dockerfile) 和 [template.yaml](./lab/generated/template.yaml) 对照阅读。重新生成时，模型可能采用不同的参数名或组织方式，调用前应先阅读自己的文件。

## 从 CLI 调用 add

先看应用提供的命令，再传入两个整数：

```bash
abx sandbox command list "$SANDBOX_ID"
abx --json sandbox command run "$SANDBOX_ID" add \
  --json-args '{"a":17,"b":25}'
```

本例返回：

```json
{"result": 42}
```

这里使用 `--json-args` 传业务参数，使用全局 `--json` 输出包装后的 JSON。省略 `--json` 时，普通输出是 `42`。

## 从其他程序发送 HTTP 请求

如果想在自己的 Python 程序里调用这个 API，先安装本例使用的 client：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple \
  'agent-sandbox-client==0.3.1a2' httpx
```

下面的程序连接已创建的沙箱，从应用绑定中取得地址和认证头，再发送 POST：

```python
import asyncio
import os
import httpx
from agent_sandbox import ProviderSandbox

async def main():
    sandbox = await ProviderSandbox.connect(os.environ["SANDBOX_ID"])
    application = await sandbox.application_client(9000)
    try:
        async with httpx.AsyncClient(
            headers=application.auth_headers(), timeout=60
        ) as http:
            response = await http.post(
                application.base_url.rstrip("/") + "/commands/add",
                json={"a": 17, "b": 25},
            )
            response.raise_for_status()
            print(response.json())
    finally:
        await application.aclose()
        await sandbox.close()

asyncio.run(main())
```

返回结果仍是 `{"result": 42}`。应用参数缺失会返回 `400`，调用不存在的命令会返回 `404`。这两个响应可以帮助调用方区分参数问题和接口名称问题。

本例生成的模板没有设置业务访问令牌。自己的应用如果需要限制访问，应配置应用认证；平台网关的认证头与应用 Bearer token 需要分别处理。本地 SDK 的 `0.3.1a2` 与本例模板固定的远端 server `0.3.1a1` 也是两个独立版本。

## 在沙箱里继续探索

除了调用 API，还可以查看环境、文件和进程，或打开交互终端：

```bash
abx info "$SANDBOX_ID" --format json
abx --json sandbox files list "$SANDBOX_ID" --path /home/user/app
abx --json sandbox system metrics "$SANDBOX_ID"
abx --json sandbox process list "$SANDBOX_ID"
abx connect "$SANDBOX_ID"
```

这使生成出的应用仍然是一个可以检查、修改和理解的项目。发现接口行为不对时，先看业务源码和实际参数，不必只依赖模型生成的 README。

在这个示例环境里，`/home/user/app` 的目录权限不允许运行用户新建文件。需要输出数据时，应选择运行用户可写的位置；生成说明中的“工作目录可写”不能直接作为依据。加法接口只计算并返回值，不需要向该目录写数据。

## 留下代码，释放临时环境

生成文件保存在本机，因此删除沙箱不会把本地项目一并删除。用完当前实例后执行：

```bash
abx kill "$SANDBOX_ID"
abx template delete '<TEMPLATE_ID>' -y
```

模板还要复用时，可以只删除沙箱。若只想部署已有生成文件，使用显式模板部署流程，并等模板就绪后再创建实例，具体步骤见[模板使用指南](https://registry.agent-sandbox.cn/source/agent-sandbox/docs/zh/guide/using-templates.md/)。

随文的 [run.py](./lab/run.py) 与 [verify.py](./lab/verify.py) 可以自动完成生成、调用和清理。取得博客仓库后，在这篇文章的目录运行：

```bash
git clone --depth 1 https://github.com/Alibaba-Agent-Sandbox/blogs.git agent-sandbox-cases
cd agent-sandbox-cases/posts/developer-journey-prompt-sandbox
python lab/run.py --output ./my-add-project --generation-timeout 1200
```

`my-add-project` 必须是新目录，生成源码保存在其中的 `generated/`。自动流程会自己创建并删除资源，不会清理前面手动操作的实例；中途强制退出时，需要根据已返回的 ID 手动处理尚未释放的资源。

从小而明确的接口开始更容易理解生成结果。这个加法例子只有标准库依赖；加入 pandas、matplotlib 等大型依赖后，构建时间和可用镜像需要另外考虑。此前这类环境曾出现构建超时，当前原因尚未确定，不能照搬小接口的耗时预期。
