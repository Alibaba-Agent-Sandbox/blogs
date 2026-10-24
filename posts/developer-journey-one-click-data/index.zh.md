---
title: 用一次 Python 函数调用完成云端订单清洗、汇总与自动清理
summary: 用 declarative sandbox 把 Pandas 计算放到真实远端环境，独立核对 10 条订单的结果，并验证成功和异常两条路径都自动删除资源。
date: 2026-10-24
category: case
tags: [python, pandas, data-processing, sandbox]
authors: [Alibaba-Agent-Sandbox]
cover: ./cover.svg
draft: false
---

一个临时数据处理任务不一定要手工维护沙箱生命周期。这篇案例使用公开的 `@sandbox` 装饰器，让一次 Python 函数调用完成远端执行、结果返回和资源清理，再用独立的本地算法检查数据是否正确。

“一键”指账户、依赖和输入准备好之后的一次运行，不是省略账户配置。本次使用真实 Express 后端，宿主是 Python `3.12.13` 和从官方 PyPI 全新安装的 `agent-sandbox-client==0.3.1a2`。远端采用 `code-interpreter-v1` 模板，实测 Pandas 为 `3.0.3`；宿主安装的 server 包版本不等同于模板内部环境版本。

## 准备环境与固定输入

先按照 [官网上手指南](/start/) 配置自己的 Express 沙箱账户，再创建独立 Python 环境：

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.3.1a2'
python -m pip check
```

这个案例不调用语言模型，所以不需要 LLM API key，也不通过 CLI 执行数据函数。SDK alpha 是显式选择的测试版本。

[05-orders.csv](./lab/05-orders.csv) 是 10 条合成订单，包含重复订单、空地区、负数量和非数字数量，避免拿真实业务或个人数据做公开演示：

```csv
order_id,region,quantity,unit_price
A001, east ,2,19.95
A002,west,3,10.00
A003,EAST,1,99.90
A004,north,5,2.50
A002,west,3,10.00
A005,,4,8.00
A006,west,-1,20.00
A007,west,two,11.00
A008,North,2,5.25
A009,east,3,0.10
```

本例的输入合同是固定 CSV 字段、三个地区和最多两位小数的价格。它不是通用财务导入系统；扩展到任意 CSV 时，仍需要明确重复冲突规则、空值、非有限值、精度和规模上限。

## 把计算放进远端函数

[完整程序](./lab/05-data-processing.py) 使用公开的 declarative API：

```python
from agent_sandbox.declarative import sandbox

@sandbox(
    template="code-interpreter-v1",
    envs={"JOURNEY_REMOTE_MARKER": "orders-case-05-20261024"},
)
def summarize_orders(csv_text):
    import io
    from decimal import Decimal
    import pandas as pd
    # 完整附件执行清洗、按地区汇总并返回普通 Python 数据。
```

函数内部导入 Pandas，是因为计算发生在模板环境中。调用时传入 CSV 字符串，而不是假设远端可以直接读取宿主文件路径。

实际处理顺序明确且可复查：先按 `order_id` 保留第一条，统计重复数；再清理地区空白并转小写；剔除无效地区、非正整数数量和无效价格；以 `Decimal` 把固定两位小数价格换算为整数分，再按地区汇总。这里先去重再校验，是本例选择的规则，不应该在处理真实订单时无声改变。

函数返回汇总列表、CSV 文本、行数统计和远端身份标记。它不把远端任意对象或打开的文件句柄交回宿主。

## 一次命令完成计算

```bash
git clone --depth 1 https://github.com/Alibaba-Agent-Sandbox/blogs.git agent-sandbox-cases
cd agent-sandbox-cases/posts/developer-journey-one-click-data
python lab/05-data-processing.py
```

这会真正创建并使用一个远端 sandbox。成功后写出 `lab/05-summary.csv` 和 `lab/05-data-result.json`，同时执行结果断言。实际汇总如下：

| 地区 | 有效订单 | 商品数量 | 金额（分） | 金额 |
| --- | ---: | ---: | ---: | ---: |
| east | 3 | 6 | 14010 | 140.10 |
| north | 2 | 7 | 2300 | 23.00 |
| west | 1 | 3 | 3000 | 30.00 |
| 合计 | 6 | 16 | 19310 | 193.10 |

10 条输入减去 1 条重复，再剔除 3 条无效记录，得到 6 条有效记录。不是把无效行静默消失：各类数量都包含在结果中。

![本次合成订单的地区金额，单位为分](./revenue.svg)

## 用独立算法核对结果

如果把同一段 Pandas 代码在本地再运行一次，只能证明两次执行一致，较难发现同一个逻辑错误。附件里的 `expected_summary` 改用标准库 `csv`、`Decimal` 和字典累加，逐项核对远端返回的行数、地区明细和总额。

程序还重新解析返回的 CSV，对比它与结构化汇总；检查只在远端设置的 marker；确认远端 hostname 与宿主不同。公开结果仅保留“远端身份不同”的结论，不公开实际主机标识。

这些检查建立了真实执行和结果一致性的证据，但不等于对所有输入空间的证明。金额使用整数分也不自动解决任意精度、汇率或退款业务规则。

## 清理也要实际验证

我们额外运行了 [audit.py](./lab/audit.py)。它观察真实 HTTP 传输，不替换请求、不伪造返回，记录创建和删除操作，并对创建出来的精确 ID 再查询一次：

```bash
python lab/audit.py documentation 05-documentation-example.py
python lab/audit.py orders 05-data-processing.py
python lab/audit.py exception 05-failure-cleanup.py
```

第二个参数是与 `audit.py` 同目录的文件名，不要再重复附上 `lab/`。最初一次复验曾传入重复路径，程序在创建任何资源前就失败；纠正调用后重新运行，旧错误记录保留。

三条路径分别覆盖最小文档示例、完整订单处理和远端主动抛出 `ValueError`、宿主收到包装后的 `RuntimeError`。异常路径要确认异常确实回到调用方，同时资源仍被自动清理。

| 公开 PyPI 0.3.1a2 复验 | 计算/异常符合预期 | 装饰器自动 DELETE | 精确 GET 读回 |
| --- | --- | --- | --- |
| 文档示例 | 通过 | 1 次，204 | 404 |
| 订单处理 | 通过 | 1 次，204 | 404 |
| 异常传播 | 通过 | 1 次，204 | 404 |

每次都只观察到一个本次创建的 sandbox，没有靠兜底删除才达到通过。审计程序虽然具备失败后的恢复清理，但一旦需要它兜底，该次自动清理验收就会失败。

## 复现文件与适用范围

附件包含 [输入 CSV](./lab/05-orders.csv)、[数据处理程序](./lab/05-data-processing.py)、[最小示例](./lab/05-documentation-example.py)、[异常实验](./lab/05-failure-cleanup.py) 和 [审计程序](./lab/audit.py)。本次可查看[验收摘要](./proof/summary.json)、[真实数据结果](./proof/05-data-result.json)和[附件源码 SHA256](./lab/source-sha256.json)。审计命令会在自己的 `lab/evidence/` 下写入结果；直接运行数据程序则写入前述 CSV 和数据结果 JSON。真实资源恢复信息属于 `.private/`，不要公开。

本文验证了固定数据集上的真实远端计算、返回值和正常/异常清理。它没有测试强制杀死宿主进程、无限大的数据集或所有云提供方；这些需要按实际使用场景增加验收，而不是从一次成功自动推断。
