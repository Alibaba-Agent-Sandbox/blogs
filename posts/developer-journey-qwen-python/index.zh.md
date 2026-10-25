---
title: 给 Qwen Code 一个沙箱，再把常用操作变成 API
summary: 用 Python SDK 创建临时代码工作区，让 Qwen Code 修复一个计算函数，并把订单金额计算封装成可由 Python、CLI 和 HTTP 调用的命令。
date: 2026-10-24
category: case
tags: [python, qwen-code, api, sandbox]
authors: [Alibaba-Agent-Sandbox]
cover: ./cover.svg
draft: false
---

让代码助手修改文件时，一个独立的临时工作区很实用：源文件和工具装在沙箱里，任务完成后把需要的产物取回，再释放环境。

这篇用 Python SDK 自己搭一个 Qwen Code 沙箱。让它修复计算器里的错误，并给同一个应用增加 `invoice_total` 命令。这样，代码助手负责修改程序，普通业务计算则可以直接通过 Python、CLI 或 HTTP 调用。

## 准备沙箱账户和模型服务

先按[CLI 上手案例](/blog/developer-journey-cli-install/)安装 `abx 0.5.3`，配置自己的 Express 沙箱账户。使用 Python 3.10 或更新版本，把依赖放在独立环境中：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple \
  'agent-sandbox-client==0.4.0a2'
```

这里选用的是 SDK alpha 版本。除沙箱连接配置外，还需要 Qwen 使用的模型服务：

```bash
export OPENAI_API_KEY='<YOUR_MODEL_API_KEY>'
export OPENAI_BASE_URL='<YOUR_OPENAI_COMPATIBLE_BASE_URL>'
export QWEN_MODEL='qwen3-coder-flash'
```

模型名称应是你的服务实际提供的名称。本例用单独的 `QWEN_MODEL`，避免沿用其他项目留下的模型配置。

取得示例代码后，可以先读一下三个主要文件：

```bash
git clone --depth 1 https://github.com/Alibaba-Agent-Sandbox/blogs.git agent-sandbox-cases
cd agent-sandbox-cases/posts/developer-journey-qwen-python
```

| 文件 | 负责什么 |
| --- | --- |
| [bootstrap.sh](./lab/bootstrap.sh) | 安装 Node.js、Qwen Code 和沙箱内的 Python 服务 |
| [commands.py](./lab/commands.py) | 定义查询版本、修复代码、计算金额三个应用命令 |
| [run.py](./lab/run.py) | 创建沙箱、上传文件、启动应用、调用命令和取回产物 |

## 创建工作区，把工具装进去

程序通过 `ProviderSandbox.create(template="base", timeout=900)` 创建环境，再把 bootstrap 和应用代码写入 `/home/user/journey-qwen/`。项目文件放在其中的 `project/` 目录。

Qwen Code `0.23.0` 要求 Node.js 22 或更新版本，基础镜像实测自带的是 Node.js `20.20.2`，因此这里需要升级。示例固定 Node.js `24.16.0` 和 Qwen Code `0.23.0`。开发者机器需要能访问官方 Node.js 下载站、npm 和 PyPI；沙箱还需要访问 npm 元数据、PyPI 和模型服务。

`run.py` 先查询沙箱的 CPU 架构，在本机下载对应的官方 Node.js 安装包和 Qwen npm 包，分别校验官方 SHA256、固定 SHA512 完整性值，再通过 SDK 的 `files.write` 上传。bootstrap 再次校验文件，解压 Node.js，用标准 `npm install` 安装本地 Qwen 包，并从官方 PyPI 安装远端 `agent-sandbox-server==0.4.0a2`。这样不必让沙箱重复下载这两个较大的工具包。

本例只用 Qwen 的非交互式文件工具，因此安装时使用 `--omit=optional`；音频、剪贴板、图像和原生 PTY 扩展没有在这个案例中验证。三个远端安装阶段有日志和带强制终止宽限的时间限制，外层 SDK 的整段安装预算为 300 秒。首次准备仍需要网络下载；反复执行同类任务时，应把这些固定工具放进自己的模板镜像，避免每个任务重新安装。

本地 client 和远端 server 是两个安装位置，本例两处均明确安装 `0.4.0a2`。修改本地版本不会自动升级 bootstrap 中指定的远端服务。

工具准备好后，程序启动监听 9008 端口的应用服务。下面是完整程序中的关键调用，其中 `sb` 是已创建的沙箱，`env` 提供工具路径和模型配置：

```python
server = await sb.start_server(
    port=9008,
    command="python3 -m agent_sandbox.server serve --port 9008 "
            "--commands /home/user/journey-qwen/commands.py",
    token=app_token,
    env=env,
    timeout=60,
)
```

`app_token` 是程序为这次应用生成的随机令牌。它保护应用接口，与创建沙箱时使用的控制面 API key 分开。

## 让 Qwen 真正修改文件

示例先写入一个有意出错的计算函数：

```python
def add(a, b):
    return a - b
```

随后调用 `repair_calculator`，要求 Qwen 修改磁盘上的 `calculator.py`，让 `add` 返回两数之和，并生成说明修改内容的 `REPORT.md`。

这个命令内部启动 Qwen Code 子进程，把工作目录设为刚创建的项目。它限制最多 8 轮、120 秒运行预算，外层子进程另有 150 秒超时保护。工作目录只是任务起点，并不是访问控制边界；示例中的 `--yolo` 用在这个可丢弃沙箱里。

完成后，程序取回修改后的源码和报告。修改后的核心逻辑是：

```python
def add(a, b):
    return a + b
```

本例还用几组输入运行修改后的函数，例如 `add(2, 3)` 得到 `5`，`add(123, 456)` 得到 `579`。实际执行修改后的文件，可以及时发现模型只解释了方案、却没有把修改写入磁盘的情况。

## 加一个不需要模型参与的业务命令

同一个服务还可以提供普通 Python 函数。例如，对一笔订单按数量和折扣计算总额：

```python
from decimal import Decimal, ROUND_HALF_UP
from agent_sandbox.server import command

@command(description="Calculate an exact invoice total with a bounded discount")
def invoice_total(unit_price: str, quantity: int, discount_percent: int = 0) -> dict:
    price = Decimal(unit_price)
    if not price.is_finite() or price < 0:
        raise ValueError("unit_price must be finite and nonnegative")
    if quantity < 0 or not 0 <= discount_percent <= 100:
        raise ValueError("invalid quantity or discount")
    total = (price * quantity * (Decimal(100) - discount_percent) / 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return {"total": str(total), "quantity": quantity,
            "discount_percent": discount_percent}
```

`@command` 把函数注册成应用命令。价格使用字符串传入，再由 `Decimal` 计算，结果按两位小数返回。

### 在 Python 中调用

服务启动后，直接使用返回的应用客户端：

```python
answer = await server.commands.run(
    "invoice_total", unit_price="19.00", quantity=3, discount_percent=10
)
print(answer)
```

单价 `19.00`、数量 `3`、打九折，得到：

```json
{"total": "51.30", "quantity": 3, "discount_percent": 10}
```

### 在终端中调用

应用运行期间，也可以让 CLI 调用同一个命令。`SID` 和 `APP_TOKEN` 分别是这个沙箱的 ID 和启动服务时的令牌：

```bash
ABX_SERVER_TOKEN="$APP_TOKEN" abx run "$SID" invoice_total \
  --server-port 9008 \
  --json-args '{"unit_price":"19.00","quantity":3,"discount_percent":10}'
```

这适合临时调试，或者把现成的业务命令放进 shell 流程。

### 从 HTTP 客户端调用

其他程序不必通过 CLI，可以向应用发送 POST：

```python
async with httpx.AsyncClient(timeout=30, follow_redirects=False) as http:
    response = await http.post(
        server.base_url.rstrip("/") + "/commands/invoice_total",
        headers=server.auth_headers(),
        json={"unit_price": "19.00", "quantity": 3, "discount_percent": 10},
    )
    response.raise_for_status()
    print(response.json()["result"])
```

这段代码使用 `httpx`，与前面的 `server` 处在同一个异步流程里。URL 和认证头由应用客户端提供，不需要自己拼接沙箱域名。缺少必要参数时接口返回 `400`；缺少或使用错误的应用令牌时返回 `401`。

## 跑完示例，拿走产物

配置完成后，在示例目录运行：

```bash
python lab/run.py
```

程序会在一次运行中完成以上操作，包括三种调用方式，然后自动删除自己创建的沙箱。它不是一个常驻服务；如果需要手动用 CLI 调试，应在应用仍运行时调用，而不是等脚本结束后复用已经删除的 ID。

运行后可以查看 `lab/calculator.generated.py` 和 `lab/REPORT.generated.md`。需要保留的业务结果应在释放沙箱前下载到本地；应用客户端的 `aclose()` 只是关闭连接，真正释放云资源需要 `sb.kill()`。

这个例子把两类工作放进了同一个临时环境：Qwen 处理需要读写代码的任务，注册好的 Python 命令提供稳定的调用入口。沿用这个结构，可以继续设计自己的项目操作；新增命令时，把参数、返回值和允许执行的操作写清楚。
