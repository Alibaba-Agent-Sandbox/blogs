---
title: 让原生 QM 工具通过 SDK 写入并取回工作区文件
summary: 使用原版 QM 工具上下文与真实 Node HTTP SDK，在一个极速版实例内完成文件和进程任务。
date: 2026-10-27
category: case
tags: [templates, qm-sandbox]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

QM 工具可以连接已有沙箱工作区，避免为每个文件操作创建新的云实例。这里通过原生工具写入 note.txt，再用独立文件接口取回精确内容。

CLI、完整 SDK 和 HTTP 分别写入新文件，下载后均为 Hello from QM tools 加一个换行。每次替代调用前，自己的旧文件均独立确认不存在。
实际附件：[note.txt](./note.txt)。

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
abx template launch Alibaba-Agent-Sandbox/awesome-templates//qm-sandbox --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
abx sandbox command list "$SANDBOX_ID"
```

这个模板的业务操作不需要模型 endpoint、模型 Key 或产品登录；应用令牌独立于平台认证。

## 完成一次实际业务流程

```bash
abx run "$SANDBOX_ID" qm_sandbox_file --json-args '{"action":"write","path":"note.txt","text":"Hello from QM tools\n"}'
```

CLI、完整 SDK 和 HTTP 分别写入新文件，下载后均为 Hello from QM tools 加一个换行。每次替代调用前，自己的旧文件均独立确认不存在。

全部六个命名入口实际执行：原生版本与工具上下文检查、只读设置、真实 SDK 往返、执行命令与文件操作。这里使用原版 QM0.1.0 的库与工具上下文，Node SDK0.1.0 在镜像内由固定源码和锁文件构建，没有宣称它已发布到 npm。

命令参数、返回字段与期限见[此模板完整说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/qm-sandbox/README.zh-CN.md)。
任务的执行期限、客户端等待和1800秒实例寿命分别控制不同阶段。

用文件接口导出精确结果：

```bash
abx download "$SANDBOX_ID" /home/user/app/note.txt ./note.txt
```

## 通过 Python 或 HTTP 接入

下载 [quickstart.py](./quickstart.py)，保留上面的环境变量与实例 ID，执行
`python quickstart.py`。它是实际运行的完整模板 SDK 示例，通过 `ProviderSandbox.connect`
连接同一实例，使用应用令牌调用业务方法，最后关闭本机连接。
脚本会把实际产物下载到本机。

HTTP 用户按[直接 HTTP 指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)
解析9000端口，保留网关头、路径、查询，再添加独立应用认证。
按模板 HTTP 章节给定的顺序调用 `POST /commands/<命令名>`，发送直接 JSON 参数对象，
不加 args 包装。多步服务先启动再调用，结束后显式停止；具体请求与完整返回合同见上面的模板说明。

CLI、Python、HTTP是替代入口，选择适合自己程序的一种即可。本例分别执行了三种方式；
服务在替代调用之间停止，文件或数据使用自己的新状态，生成的产物独立取回确认。

## 二次开发与业务边界

qm_sandbox_exec 用于有期限的工作区进程，qm_sandbox_file 提供命令参考列出的文件操作。把输入上传到自己的项目目录，调用原生工具后下载需要的文件。这个入口不调用模型；需要模型代理时使用另一个 qm 模板并单独配置模型。当前集成不启动原版多人协作、Slack、Postgres 持久化或订阅系统，也不使用原版 Docker 后端。

修改模板时从自己的源码副本开始，固定依赖和项目配置，保留上游许可证。
自己的代码、数据和页面保存在沙箱工作区，先导出需要的结果再结束实例。

## 在 OpenSandbox 中使用同一工作流

这个案例也可以在 OpenSandbox 中完成。先按[OpenSandbox 提供方指南](https://github.com/Alibaba-Agent-Sandbox/awesome-providers/blob/main/opensandbox/docs/README.md)准备服务地址、服务 API Key 和镜像仓库，然后在创建实例前选择平台：

```bash
export ABX_PROVIDER=opensandbox
export ABX_OPENSANDBOX_USE_SERVER_PROXY=true
```

接着执行上面的 launch、业务命令和 SDK 示例；后续终端与 Python 继续使用同一个平台和实例 ID。沙箱 API Key 与应用令牌分别配置，原有业务输入、返回结果和结束实例的方法相同。

这里使用 OpenSandbox1.1.1 的服务代理模式；CLI、完整 SDK 示例和直接 HTTP 都能完成文中的实际任务。代理模式要求客户端能访问服务地址。若部署环境改为直连模式，客户端还必须能访问提供方解析出的端点；更换配置后重新创建自己的实例，不复用另一平台的 ID。

## 导出并结束

业务完成后，按完整说明停止自己启动的服务，下载需要的文件，再执行：

```bash
abx kill "$SANDBOX_ID"
```

SDK close 只关闭连接。预备模板和镜像按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)
仅删除自己的资源。本例的沙箱、预备模板、本次本地与远端镜像均独立确认不存在。
