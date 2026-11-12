---
title: 让 Coding Agent 在一次性沙箱里跑它自己写的代码
summary: Agent 写完脚本就想执行，但你不想让它碰你的电脑。这篇用一个很小的例子，走一遍"建沙箱、传数据、跑代码、取结果、销毁"，命令行和 Python 各一份。
date: 2026-10-14
category: case
tags: [python, cli, security]
authors: [Alibaba-Agent-Sandbox]
featured: true
---

示例基础模板：[base](https://registry.agent-sandbox.cn/templates/base/) · [使用说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/managed/base/README.zh-CN.md)。

Coding Agent 的日常是：读需求，写一段脚本，然后立刻想执行它。

脚本是模型刚生成的，你没有逐行看过。它可能读了不该读的目录，装了一个不认识的依赖，或者只是写了一个死循环。放在自己的机器上跑，出问题时要收拾的是你的环境。

这篇文章用一个很小的案例，演示怎么把"执行"这一步交给一次性沙箱：用完即销毁，机器上什么都不留。

## 场景

你让 Agent 分析一份销售数据：按地区汇总金额，从高到低排序。Agent 写好了 Python 脚本。我们要做的是：

1. 创建一个沙箱。
2. 把数据文件放进去。
3. 在沙箱里执行 Agent 写的脚本。
4. 拿回结果。
5. 销毁沙箱。

整个过程不需要在本机装任何 Agent 写的依赖，也不会让脚本接触本机文件。

## 准备

默认提供方是阿里云智能体沙箱极速版（`alicloud-express`），需要一个 API Key。

```bash
git clone https://github.com/Alibaba-Agent-Sandbox/agent-sandbox.git
cd agent-sandbox
npm ci
npm run build
npm link
cd ..
export ABX_SANDBOX_API_KEY="<YOUR_API_KEY>"
```

上述 CLI 构建需要 Node.js 20+，以下命令对应当前源码版本。其他平台的安装见[安装指南](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox#installation)，继续前运行 `abx --version`。

PowerShell 中请使用 `abx config set sandbox_api_key <YOUR_API_KEY>` 配置密钥，替代上面的 Bash `export` 命令。

Python 客户端发行名是 `agent-sandbox-client`，导入为 `agent_sandbox`。在独立 Python 环境中安装已发布的 alpha 版本；客户端会安装同版本的服务端依赖：

```bash
python -m pip install --index-url https://pypi.org/simple "agent-sandbox-client==0.3.1a5"
```

## 用 Python SDK

下面是完整的脚本。`AGENT_CODE` 是 Agent 生成的那一段，我们把它原样交给沙箱。

```python
import asyncio
from agent_sandbox import AsyncSandbox

CSV = """region,amount
hangzhou,120
beijing,80
hangzhou,45
shanghai,200
beijing,30
"""

AGENT_CODE = '''
import csv

totals = {}
with open("/home/user/sales.csv", newline="") as f:
    for row in csv.DictReader(f):
        totals[row["region"]] = totals.get(row["region"], 0) + int(row["amount"])

for region, amount in sorted(totals.items(), key=lambda kv: -kv[1]):
    print(f"{region:<8}{amount:>6}")
'''


async def main():
    sandbox = await AsyncSandbox.create(template="base")
    try:
        await sandbox.files.write("/home/user/sales.csv", CSV)
        await sandbox.files.write("/home/user/analyze.py", AGENT_CODE)
        result = await sandbox.commands.run("python /home/user/analyze.py")
        print(result.stdout)
        print("exit code:", result.exit_code)
    finally:
        await sandbox.kill()


asyncio.run(main())
```

几个要点：

- `finally` 在执行或读取结果失败时也会尝试销毁本次创建的沙箱。
- `commands.run` 在 `base` 中启动 Python 进程执行文件；这里不依赖持久解释器会话。
- 检查 `result.exit_code` 和 `result.stderr`，把错误信息交还给 Agent，让它自己修脚本，这就是一个完整的"写、跑、改"循环。

脚本的输出是：

```text
shanghai   200
hangzhou   165
beijing    110
```

## 用命令行

同样的流程，用 `abx` 手动走一遍：

```bash
abx deploy --template-id base --name analysis
abx sandbox upload analysis ./sales.csv /home/user/sales.csv
abx sandbox upload analysis ./analyze.py /home/user/analyze.py
abx sandbox exec analysis -- python /home/user/analyze.py
abx delete analysis --yes
```

`analyze.py` 就是上面 `AGENT_CODE` 中的脚本。本机部署名 `analysis` 在上传、执行与清理时指向同一个沙箱；结果打印在终端。取回文件使用 `abx sandbox download analysis REMOTE LOCAL`，使用后运行 `abx delete analysis --yes`；`abx list` 可查询部署与可见沙箱。

## 让 Agent 自己调用

不想写这段胶水代码，可以让 IDE 里的 Agent 通过 MCP 直接使用沙箱：

```bash
abx mcp install --target cursor   # 或 claude、vscode
```

之后 Agent 创建沙箱、传文件、执行、销毁，都是工具调用。

## 这样做换来了什么

- **隔离**：Agent 生成的代码在远端的一次性环境里运行，不读也不改你的本机文件。
- **可丢弃**：沙箱用完销毁，错误的依赖和临时文件不会留下来。
- **可重复**：每次都从同一个模板开始，同样的输入得到同样的环境。

它不是万能的。沙箱里的代码仍然能用你交给它的东西：传进去的文件、注入的环境变量。**不要把不需要的密钥放进沙箱。**

## 接着做

- 需要预装依赖？写一个[模板](https://registry.agent-sandbox.cn/templates/)，或者在 Registry 里找一个现成的。
- 想换别的后端？看[提供方](https://registry.agent-sandbox.cn/providers/)，按该平台说明安装、配置插件，再使用公开的 `ProviderSandbox` 入口；完整代码见 [Python 提供方指南](https://github.com/Alibaba-Agent-Sandbox/python-sdk/blob/main/docs/zh/guide/providers.md)。
- 完整的上手步骤见[开始使用](/start/)。
