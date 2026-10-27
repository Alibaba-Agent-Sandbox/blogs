---
title: 在沙箱里建立 PostgreSQL 与 Redis 的开发数据服务
summary: 初始化独立数据库，写入季度金额，查询汇总，并使用实际 Redis 与重启持久化能力。
date: 2026-10-27
category: case
tags: [templates, dev-services]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

开发应用时，可以把数据库和业务程序一起放在可丢弃的工作区。这里启动固定版本 PostgreSQL 和 Redis，写入一笔5130分的金额，查询总额，再由已有接口管理状态与停止。

三种调用方式都执行真实 PostgreSQL SQL，返回总额5130分，对应51.30。每种方式使用自己的新表状态，上一轮表在下一轮之前移除。

## 准备平台与工作区

本例使用极速版、默认 Docker 配方、CLI `0.5.7` 和 Python client/server `0.4.0a6`。
按[平台配置](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)
准备沙箱 API Key、地域、连接地址、Docker、构建权限和镜像仓库，再运行：

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export DEV_SERVICES_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
export ABX_HTTP_TIMEOUT=450
abx template launch Alibaba-Agent-Sandbox/awesome-templates//dev-services --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
abx sandbox command list "$SANDBOX_ID"
```

这个模板的业务操作不需要模型 endpoint、模型 Key 或产品登录；应用令牌独立于平台认证。

## 完成一次实际业务流程

```bash
abx run "$SANDBOX_ID" services_start --json-args '{}'
abx run "$SANDBOX_ID" services_sql --json-args '{"sql":"CREATE TABLE usage_demo (amount integer); INSERT INTO usage_demo VALUES (5130); SELECT sum(amount) AS total_cents FROM usage_demo;"}'
```

三种调用方式都执行真实 PostgreSQL SQL，返回总额5130分，对应51.30。每种方式使用自己的新表状态，上一轮表在下一轮之前移除。

全部八个入口实际调用；SQL 和 Redis 的读写、停止后再启动的数据保持、状态、版本和私有数据清理均已完成。数据库数据目录在停止后保留，便于同一沙箱内再次启动。

命令参数、返回字段与期限见[此模板完整说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/dev-services/README.zh-CN.md)。
任务的执行期限、客户端等待和1800秒实例寿命分别控制不同阶段。

## 通过 Python 或 HTTP 接入

下载 [quickstart.py](./quickstart.py)，保留上面的环境变量与实例 ID，执行
`python quickstart.py`。它是实际运行的完整模板 SDK 示例，通过 `ProviderSandbox.connect`
连接同一实例，使用应用令牌调用业务方法，最后关闭本机连接。
脚本会输出实际业务返回值，并停止自己启动的服务。

HTTP 用户按[直接 HTTP 指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)
解析9000端口，保留网关头、路径、查询，再添加独立应用认证。
按模板 HTTP 章节给定的顺序调用 `POST /commands/<命令名>`，发送直接 JSON 参数对象，
不加 args 包装。多步服务先启动再调用，结束后显式停止；具体请求与完整返回合同见上面的模板说明。

CLI、Python、HTTP是替代入口，选择适合自己程序的一种即可。本例分别执行了三种方式；
服务在替代调用之间停止，文件或数据使用自己的新状态，生成的产物独立取回确认。

## 二次开发与业务边界

DEV_SERVICES_PASSWORD 是独立数据库密码，16–128个 URL-safe ASCII 字符，与应用令牌分开。services_sql/services_redis 处理数据库认证，无需本机数据库登录。默认数据库只监听沙箱回环地址；应用可以在沙箱内连接，外部程序也可通过9000端口的命令 API 使用。原生外部 TCP 客户端需要平台另行支持的转发，本例没有把 HTTP 预览代理当作数据库隧道。依赖数据要先备份再删除实例。

修改模板时从自己的源码副本开始，固定依赖和项目配置，保留上游许可证。
自己的代码、数据和页面保存在沙箱工作区，先导出需要的结果再结束实例。

## 导出并结束

业务完成后，按完整说明停止自己启动的服务，下载需要的文件，再执行：

```bash
abx run "$SANDBOX_ID" services_stop
abx kill "$SANDBOX_ID"
```

SDK close 只关闭连接。预备模板和镜像按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)
仅删除自己的资源。本例的沙箱、预备模板、本次本地与远端镜像均独立确认不存在。
