---
title: 在临时工作区启动 Node HTTP 服务，完成构建与发布前预览
summary: 让代码工作区拥有实际 HTTP 服务、构建、日志和进程管理入口，再把它接到自己的开发流程。
date: 2026-10-27
category: case
tags: [templates, node-web]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

一个 Node 项目的交付需要安装后的程序真正监听并回应请求。这里从自带应用开始，启动 HTTP 服务，读取实际响应，再用三种入口管理同一个工作区。

实际返回 HTTP 200，正文为 node-web ready。CLI、完整 Python 程序和直接 HTTP 都启动了真实服务并读取响应，随后独立确认服务已停止。

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
export ABX_HTTP_TIMEOUT=450
abx template launch Alibaba-Agent-Sandbox/awesome-templates//node-web --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
abx sandbox command list "$SANDBOX_ID"
```

这个模板的业务操作不需要模型 endpoint、模型 Key 或产品登录；应用令牌独立于平台认证。

## 完成一次实际业务流程

```bash
abx run "$SANDBOX_ID" serve --json-args '{"entry":"index.js","port":3000}'
abx run "$SANDBOX_ID" request --json-args '{"path":"/"}'
```

实际返回 HTTP 200，正文为 node-web ready。CLI、完整 Python 程序和直接 HTTP 都启动了真实服务并读取响应，随后独立确认服务已停止。

全部九个入口还完成了 serve、npm start、npm run dev、状态、停止、日志、请求、构建和固定 smoke。独立上传的程序、构建文件、就绪探测、超时与子进程清理均已运行。

命令参数、返回字段与期限见[此模板完整说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/node-web/README.zh-CN.md)。
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

先停止当前服务，再上传自己的 index.js、package.json 和锁文件。用 serve 运行明确入口，或使用 start/dev 运行已有 npm 脚本；build 读取项目的构建脚本。request 通过沙箱内部访问本次服务。需要浏览器预览时解析3000端口并使用 SDK 预览代理，保留网关认证；本例的业务响应通过命令接口读取。

修改模板时从自己的源码副本开始，固定依赖和项目配置，保留上游许可证。
自己的代码、数据和页面保存在沙箱工作区，先导出需要的结果再结束实例。

## 导出并结束

业务完成后，按完整说明停止自己启动的服务，下载需要的文件，再执行：

```bash
abx run "$SANDBOX_ID" stop
abx kill "$SANDBOX_ID"
```

SDK close 只关闭连接。预备模板和镜像按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)
仅删除自己的资源。本例的沙箱、预备模板、本次本地与远端镜像均独立确认不存在。
