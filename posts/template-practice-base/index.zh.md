---
title: 不构建镜像，用托管 base 把 CSV 费用汇总成 JSON
summary: 直接创建极速版托管工作区，上传 CSV 和 Python 脚本，使用 Decimal 计算金额并取回 JSON，任务结束后释放实例。
date: 2026-10-27
category: case
tags: [python, csv, files, templates]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

只是处理一份 CSV 时，可以直接使用托管 `base`。这里把三笔费用上传到临时工作区，
运行 Python 汇总脚本，再把 JSON 交给后续程序。不需要自己构建镜像，也不需要先启动
模板应用服务。

实际得到的 [summary.json](./summary.json) 是：

```json
{"count": 3, "total": "51.30"}
```

本例使用极速版托管 `base`、CLI `0.5.7` 和 Python client `0.4.0a6`。
工作区中读取到 Python `3.13.13`。托管镜像由平台维护，后续可能更新，依赖具体版本
的程序应在启动后查询环境。

## 安装客户端，填写连接配置

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
abx --version
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
```

准备属于同一地域的极速版连接配置：

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SANDBOX_API_KEY='<YOUR_SANDBOX_API_KEY>'
export ABX_SANDBOX_BASE_URL='<YOUR_SANDBOX_API_URL>'
export ABX_SANDBOX_DOMAIN='<YOUR_SANDBOX_DOMAIN>'
```

`BASE_URL` 是 API 地址，`DOMAIN` 是主机名。使用自己账号对应的值，见
[配置参考](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/blob/main/docs/zh/reference/configuration.md)。
这个案例不需要 Docker、ACR、镜像构建 AK/SK、应用令牌或模型账号；已有托管模板直接
创建实例。也没有模型登录、换模型或模型 endpoint 的设置。

想先熟悉 CLI，可以创建一个实例，执行进程，再删除它：

```bash
abx --provider alicloud-express template launch base --sandbox-timeout 180 --yes
export ABX_SANDBOX_ID='<返回的沙箱 ID>'
abx --provider alicloud-express exec "$ABX_SANDBOX_ID" -- python3 -c 'print(6*7)'
abx --provider alicloud-express kill "$ABX_SANDBOX_ID"
```

进程的计算结果为 `42`。下面的完整业务脚本会创建并清理自己的实例，不复用已经删除
的 CLI 实例。

## 上传 CSV 和脚本

输入只有一个金额字段：

```csv
amount
12.50
18.80
20.00
```

[summarize.py](./summarize.py) 使用 `csv.DictReader` 读取数据，再以 `Decimal`
求和。输出的金额是两位小数的字符串，避免让 JSON 浮点数表示金额精度。
脚本以自身文件所在目录定位数据，不依赖进程启动时的当前目录。

把 [run_case.py](./run_case.py) 和 `summarize.py` 保存到同一个本机目录，执行：

```bash
python run_case.py
```

程序通过 `ProviderSandbox.create(provider="alicloud-express", template="base")`
创建实例；`files.write` 上传 CSV 和源文件；`commands.run` 执行上传的脚本；
`files.read` 取回生成的 `summary.json` 并保存到本机。完成后，`finally` 删除实例并
关闭客户端。运行期限为 180 秒，单次进程等待 30 秒。

三个字段在流程中各有用途：`exit_code` 决定任务是否成功，`stdout` 适合反馈进度或
短结果，文件 API 用于持久保存业务产物。进程退出码非零时，不应继续消费上次留下
的结果文件。

## 接入自己的数据处理流程

把示例内联 CSV 换成本机文件内容，就可以接收上游导出的费用清单。保留随机任务目录，
让多个任务的输入和结果分开。还可以在汇总脚本中校验金额格式、币种、空行和最大行数，
把拒绝的行单独输出成错误文件；这些属于你自己的业务规则。

需要固定额外依赖或重复运行较大的环境时，可以基于源码模板准备镜像，把业务函数
封装成命名命令，参考[费用文件案例](/blog/template-practice-python-hello/)。
这时才会涉及模板构建和应用服务配置。

托管 `base` 没有项目的 `/commands/*` HTTP 服务，也不提供该 provider 的持久
`run_code` 解释器接口。这里通过进程执行 Python，不把它当作跨请求保留变量的 kernel。
需要后者时，应选择支持对应协议的解释器模板和平台。

## 保存本机结果，结束远端任务

脚本退出后，本机 `summary.json` 仍然保留，远端临时工作区随实例删除。任务中途失败
也会进入清理逻辑；宿主程序被直接终止时，有限的实例寿命提供额外回收上限。
本例没有创建镜像或模板，因此没有额外的构建产物需要清理。

完整接口与平台边界见 [base 模板说明](https://registry.agent-sandbox.cn/templates/base/)。
