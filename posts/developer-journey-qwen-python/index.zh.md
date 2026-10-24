---
title: 用 Python SDK 自建 Qwen Code 沙箱，并把自定义命令交给 CLI 和 HTTP
summary: 自己编写沙箱应用，安装固定版本 Qwen Code，用 SDK、CLI 和真实 POST 调用自定义命令，再让模型实际修复文件并验证结果。
date: 2026-10-24
category: case
tags: [python, qwen-code, api, sandbox]
authors: [Alibaba-Agent-Sandbox]
cover: ./cover.svg
draft: false
---

这篇案例自己编写一个 Qwen Code 沙箱：Python SDK 负责创建和配置环境，沙箱里的 Python 服务注册业务命令，宿主机通过 SDK、CLI 和 HTTP 调用它。最后让 Qwen Code 真正修改一份有 bug 的程序，再用独立测试检查修改结果。

这里没有直接采用官方 Qwen 模板，因此结果也不能当作官方 Qwen Registry 镜像的验收。我们测试的是自己的应用、安装步骤和调用链。

## 准备两个独立账户上下文

先按 [CLI 安装实践](/blog/developer-journey-cli-install/) 安装并配置 `abx`。宿主 Python 使用独立环境：

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.3.1a2'
python -m pip check
```

`0.3.1a2` 是显式选择的 alpha。client 会安装同版本的宿主 server 依赖，但这不会自动升级远端沙箱里的服务。本例的远端 bootstrap 仍固定 `agent-sandbox-server==0.3.1a1`，需要把这两层版本区分开。

除沙箱账户的 `ABX_*` 配置外，还需要自己的模型服务：

```bash
export OPENAI_API_KEY='<YOUR_MODEL_API_KEY>'
export OPENAI_BASE_URL='<YOUR_OPENAI_COMPATIBLE_BASE_URL>'
export QWEN_MODEL='qwen3-coder-flash'
```

模型名称必须是该服务实际支持的名称。实验专用的 `QWEN_MODEL` 不继承宿主泛用的 `OPENAI_MODEL`，避免把另一个项目的模型配置误传给 Qwen。

## 编写特殊命令

[commands.py](./lab/commands.py) 注册三个命令：`qwen_version` 查询版本，`repair_calculator` 启动有时间和轮数限制的真实 Qwen 任务，`invoice_total` 演示类型化业务调用。

下面是业务命令的核心代码，完整附件还检查了非有限价格、负价格和无效折扣：

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

注册函数使它成为应用服务的命令，并不意味着把任意宿主 Python 函数直接传给 CLI。CLI 最终调用的是沙箱中已启动的 HTTP 服务。

## 创建环境并启动服务

[run.py](./lab/run.py) 使用公开的 `ProviderSandbox` 创建 `base` 沙箱，然后写入 bootstrap 和应用文件。它在创建回调中保存本次 ID，以便后续步骤失败时仍能恢复清理。

[bootstrap.sh](./lab/bootstrap.sh) 做了三件具体的事：下载 Node.js `24.16.0` 并校验官方 SHA256；安装 Qwen Code `0.23.0`；把远端 server alpha 安装到应用专属 Python 目录。最后一步明确使用官方 PyPI，因为首次实验使用的镜像源尚未同步该 alpha。

启动服务的关键调用如下，完整程序负责先构造 `sb`、`app_token` 和必要环境变量：

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

`app_token` 是每次实验随机生成的应用令牌。模型凭据只注入本次拥有的 sandbox；原始模型输出保留在私有恢复目录，不进入公开附件。

## 同一个命令，三条真实调用路径

SDK 调用使用启动后返回的应用客户端：

```python
answer = await server.commands.run(
    "invoice_total", unit_price="19.00", quantity=3, discount_percent=10
)
assert answer == {"total": "51.30", "quantity": 3, "discount_percent": 10}
```

CLI 则指定相同应用端口，并在调用环境中提供本次应用令牌：

```bash
ABX_SERVER_TOKEN="$APP_TOKEN" abx run "$SID" invoice_total \
  --server-port 9008 \
  --json-args '{"unit_price":"19.00","quantity":3,"discount_percent":10}'
```

这里的 `SID` 和 `APP_TOKEN` 来自你自己的创建过程；自动实验会管理它们，不会把真实值打印到公开日志。普通输出是业务对象；使用扩展全局 `--json` 时，外层格式另有 `result` 包装，不应混淆。

HTTP 路线是真实的宿主 POST：

```python
async with httpx.AsyncClient(timeout=30, follow_redirects=False) as http:
    response = await http.post(
        server.base_url.rstrip("/") + "/commands/invoice_total",
        headers=server.auth_headers(),
        json={"unit_price": "19.00", "quantity": 3, "discount_percent": 10},
    )
    assert response.status_code == 200
    assert response.json()["result"]["total"] == "51.30"
```

使用应用绑定返回的 URL 和 `auth_headers()`，不要自己拼域名，也不要把沙箱控制面 key 直接当成应用 Bearer token。平台网关认证和应用认证可能同时存在。

实验保留平台网关所需头，分别删除或替换应用令牌，确认两种情况都返回 `401`；缺少必要参数返回 `400`。这样测试的是应用鉴权边界，而不是误删所有认证后被前置网关拦截。

## 确认 Qwen 真的修改了文件

程序先写入一个有意错误的文件：

```python
def add(a, b):
    return a - b
```

随后调用 `repair_calculator`，要求 Qwen 使用文件工具修改 `calculator.py`，并在同一目录写出 `REPORT.md`。Qwen 的工作目录设为这个可丢弃项目，配置最大 8 轮、120 秒预算，外层子进程另有 150 秒超时保护。`--yolo` 仅用于本实验拥有的 sandbox；工作目录是起点，不是访问控制，不能据此宣称模型只能访问该目录。

通过条件不是模型回答“已修复”，也不是进程退出码为零。宿主会下载实际源码和报告，再在沙箱里检查四组独立输入：`(2, 3)`、`(-4, 9)`、`(0, 0)`、`(123, 456)`。结果必须分别为 `5`、`5`、`0`、`579`，报告还必须非空。

首次错误配置曾使模型服务返回“不支持该模型”的内容，而外层进程仍退出零。正是文件和独立断言阻止了误报成功。这个例子说明，模型任务应验收产物和业务行为，而不只验收模型进程。

## 一次运行完整实验

```bash
git clone --depth 1 https://github.com/Alibaba-Agent-Sandbox/blogs.git agent-sandbox-cases
cd agent-sandbox-cases/posts/developer-journey-qwen-python
python lab/run.py
```

完整程序会执行创建、安装、三路调用、`200/400/401` 边界、真实模型修复和清理。结果写到 `lab/evidence/result.json`；成功必须同时满足 `status: PASS` 和 `cleanup_verified: true`。关闭应用客户端只是释放连接，删除 sandbox 才会释放云资源，程序两者都做，并按精确 ID 复查。

最终复验使用公开 CLI `0.4.12`、从官方 PyPI 新安装的宿主 SDK `0.3.1a2`，运行的正是附件文件，耗时约 89 秒。三条业务调用、`400/401` 边界、真实文件修改、四组独立运算和精确清理全部通过；[结果附件](./proof/result.json)保留了相应证据。它是有界的开发实践，不是任意模型、任意代码任务或多租户服务的生产保证。

附件的[源码 SHA256 清单](./lab/source-sha256.json)用于确认复现文件的字节。它与运行结果一起使用，单有哈希清单并不证明实验通过。
