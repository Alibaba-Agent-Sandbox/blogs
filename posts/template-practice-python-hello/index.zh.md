---
title: 用 python-hello 把一组费用变成可下载的汇总文件
summary: 启动一个 Python 工作区，通过 CLI、Python SDK 或 HTTP 计算费用、取回文件，再把内联脚本扩展成自己的任务接口。
date: 2026-10-27
category: case
tags: [python, templates, files, cli]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

有一个小任务：把 `12.50`、`18.80` 和 `20.00` 三笔费用合计，并把结果交给后续流程。
`python-hello` 可以把这段 Python 放到独立工作区执行，返回标准输出，同时留下可下载的文件。
不需要先搭 Web 框架，也不需要模型账号。

这里使用 CLI `0.5.7`、Python client/server `0.4.0a6`，模板源码固定到
`961959470411c3375a8346eb43755fa183129c22`，运行平台为极速版。
本例得到的文件是 [summary.txt](./summary.txt)，内容为 `total=51.30`。

## 安装工具，准备运行平台

安装官网提供的独立 CLI，并把它加入当前终端路径：

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
abx --version
```

源码构建需要本机 Docker。准备自己的极速版兼容 API Key、ACR namespace 和具备
所需权限的构建账号，再填写下面的变量。AK/SK 本身不代表已经获得授权；先按
[权限指南](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/blob/main/docs/zh/guide/permissions.md)
为实际执行身份授予相应权限。

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SANDBOX_API_KEY='<YOUR_SANDBOX_API_KEY>'
export ALIBABA_CLOUD_REGION_ID=cn-hangzhou
export ALICLOUD_ACCESS_KEY_ID='<YOUR_BUILD_ACCESS_KEY_ID>'
export ALICLOUD_ACCESS_KEY_SECRET='<YOUR_BUILD_ACCESS_KEY_SECRET>'
export ACR_NAMESPACE='<YOUR_ACR_NAMESPACE>'
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export ABX_HTTP_TIMEOUT=450
```

平台如要求自定义 API 地址或网关域名，再按[平台配置参考](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/blob/main/docs/zh/reference/configuration.md)
设置 `ABX_SANDBOX_BASE_URL`、`ABX_SANDBOX_DOMAIN`。应用令牌 `ABX_SERVER_TOKEN`
用于访问模板内服务；它与创建沙箱的 API Key 分开。这个模板不需要模型登录、模型
endpoint 或模型 API Key。

## 启动一次，把费用交给 Python

```bash
abx template launch Alibaba-Agent-Sandbox/awesome-templates//python-hello@961959470411c3375a8346eb43755fa183129c22 --sandbox-timeout 1800 --yes
export SANDBOX_ID='<上一步返回的沙箱 ID>'
abx sandbox command list "$SANDBOX_ID"
abx run "$SANDBOX_ID" run_script --json-args '{"code":"from pathlib import Path\nrows = [12.50, 18.80, 20.00]\ntotal = sum(rows)\nPath(\"summary.txt\").write_text(f\"total={total:.2f}\\n\")\nprint(f\"total={total:.2f}\")"}'
abx download "$SANDBOX_ID" /home/user/app/summary.txt ./summary.txt
```

命令的标准输出和下载文件都得到 `total=51.30`。`run_script` 在
`/home/user/app` 执行，因此相对路径 `summary.txt` 与下载时的绝对路径对应。
不要把文件留到释放实例之后再取。

`--sandbox-timeout 1800` 给实例 30 分钟寿命；`ABX_HTTP_TIMEOUT` 控制本机等待。
它们都不会把 `run_script` 的 30 秒子进程期限变长。

## 接到自己的 Python 程序或 HTTP 流程

想把这一步放到已有 Python 程序中，可以连接上面同一个实例：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
```

下载并运行完整的 [quickstart.py](./quickstart.py)。它读取 `SANDBOX_ID`、
`ABX_PROVIDER` 和 `ABX_SERVER_TOKEN`，调用相同的 `run_script`，再用文件 API
把结果写到本机 `summary.txt`。关闭 SDK 连接不会删除实例。

HTTP 调用使用 `POST /commands/run_script`，请求体直接传参数对象：

```json
{"code":"from pathlib import Path\nrows = [12.50, 18.80, 20.00]\ntotal = sum(rows)\nPath(\"summary.txt\").write_text(f\"total={total:.2f}\\n\")\nprint(f\"total={total:.2f}\")"}
```

按[完整 HTTP 示例](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/961959470411c3375a8346eb43755fa183129c22/docs/using-templates.zh-CN.md#http-post)
解析 9000 端口并保留 provider 返回的路径、查询和网关头，再添加应用 Bearer 令牌。
三种调用方式得到相同费用文件；实际接入时任选一种即可。

## 从一段代码扩展成自己的任务

费用来自 CSV 时，可以先上传脚本和数据，再调用 `run` 的 `file` 参数；
脚本的工作目录仍与文件上传路径保持一致。把回归用例上传后，用 `test` 的 `path`
参数运行 pytest。非零退出会成为命令错误，调用方应处理失败，而不是继续消费旧文件。
金额计算用于正式业务时，改用 `decimal.Decimal` 或整数分，并明确舍入规则。

要让调用方只提交业务参数，可以 fork 模板，在 `commands.py` 中增加
`@command("invoice_total")`，把计算封装为有类型的函数。保留现有启动方式、更新
模板版本，按[模板开发规范](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/template-spec.zh-CN.md)
构建并启动自己的目录。新增接口仍应校验输入，并让调用方能下载需要的产物。

现有模板还提供 `hello`、上传脚本执行、pytest、可调用但不列出的 `_debug_info`，
以及 `GET /hello/{name}`。这些能力适合学习命名命令、路由和文件传输的组合；
它们以工作区用户权限执行，不是任意代码的额外权限边界。

## 保存结果，释放资源

```bash
abx kill "$SANDBOX_ID"
```

实例删除后，已经下载的文件仍在本机。启动时准备的模板和镜像可能保留；不再复用时，
按启动回执中的准确引用清理本次自有资源。磁盘有限时，可在一个任务结束后删除对应
本地镜像及不再需要的构建缓存。不要清理共享基础镜像或别人的资源。

OpenSandbox 需要单独配置服务，并显式选择这个模板的 `portable` 构建方案；
本文的实际运行结果对应极速版。接口参数和其他平台的使用入口见
[模板说明](https://registry.agent-sandbox.cn/templates/python-hello/)。
