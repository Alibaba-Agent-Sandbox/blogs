---
title: 让原生 QM Agent 连接当前沙箱，生成文件并取回运行结果
summary: 配置模型服务，使用原版 QM Pi harness 与真实 SDK 工具完成工作区编码，再独立运行产物。
date: 2026-10-27
category: case
tags: [templates, qm]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

一个编码代理需要能把模型决策落实为真实文件和进程。这里使用原版 QM 的 Pi harness、工具上下文和 Node SDK 连接当前极速版沙箱，生成 hello.py 并实际运行，再从另一条文件接口取回代码。

## 准备平台与配置

本例使用极速版默认源码配方、CLI0.5.7 和 client/server0.4.0a6。按[平台配置指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)准备沙箱 API Key、连接地址、地域、Docker、构建权限和镜像仓库。API Key、模型服务密钥和应用令牌各有用途，不相互替代。

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export QM_MODEL_API_KEY='<YOUR_MODEL_API_KEY>'
export QM_MODEL_BASE_URL='<YOUR_CHAT_COMPLETIONS_API_BASE>'
export QM_MODEL='<YOUR_AUTHORIZED_MODEL_ID>'
export ABX_HTTP_TIMEOUT=450
abx template launch Alibaba-Agent-Sandbox/awesome-templates//qm --sandbox-timeout 1800 --yes
export SANDBOX_ID='<launch 返回的沙箱 ID>'
abx sandbox command list "$SANDBOX_ID"
```

所有尖括号内容替换为自己的配置；密钥仅放在终端或自己的凭据管理器中。launch 已启动应用，后续调用连接这个实例。

## 完成实际任务

```bash
abx run "$SANDBOX_ID" qm --json-args '{"prompt":"Create hello.py in the current project. It must print Hello from QM. Run it and report the output.","command_timeout":300}'
abx download "$SANDBOX_ID" /home/user/app/hello.py ./hello.py
```

原版工具通过真实 SDK 在当前工作区执行写文件与进程操作。生成的 [hello.py](./hello.py) 为：

```python
print("Hello from QM")
```

取回的文件在独立、只读、无网络的 Python 容器中再次执行，stdout 精确为 `Hello from QM` 加换行。CLI、完整 SDK 程序和直接 HTTP 三种替代入口都分别产生了新的文件，下载后独立执行；没有使用上一轮遗留文件。

编码任务还可以针对已有项目。该原生链路实际修复过一份带错误的 Python 计算程序，原始测试文件保持不变；原始测试和额外边界输入在返回后独立运行。模型结果对象中的 `exit_code:0` 只说明代理正常结束，仍需读取要求的文件并运行自己的检查；代理有可能结束而未创建指定文件。

## 接入 Python 与 HTTP

[quickstart.py](./quickstart.py) 是实际执行过的完整模板 SDK 示例。保留上面的环境与实例 ID 后运行 `python quickstart.py`；它连接同一实例并关闭连接。它会把本次实际产物下载到本机。

直接 HTTP 按[调用指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)解析9000端口并保留网关头、路径、查询与应用认证。对应方法是 `POST /commands/qm`，body 使用上述 CLI `--json-args` 内的直接对象，不套 args。返回外层为 `result`。完整参数、返回值与各方法见[模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/qm/README.zh-CN.md)。

CLI、Python、HTTP 是替代入口，选择一种即可；本文的三种入口分别实际运行。命令执行期限、客户端等待与实例1800秒寿命分别控制不同阶段，客户端断开不表示远端工作已取消。

## 二次开发与使用边界

模型配置使用 API Key，无需浏览器 OAuth 登录，也不会继承本机账号。上游需支持 Chat Completions 的工具调用。API base 包含服务要求的前缀，常见为 `/v1`，不要追加 `/chat/completions`；模型 ID 必须由同一个服务和账号提供。本例原生任务使用 qwen3.8-flash，文档中的三种替代流程使用 qwen3.8-max。更换模型、Key 或 endpoint 时重新 export 三项并启动新实例；运行中的旧应用保留启动配置。

上传自己的源码和保留的原始测试，使用 `cwd` 选择 WORKSPACE 内已有目录，再描述目标、不可修改的文件和所需产物。独立下载结果后运行原始及边界测试。当前为原版 QM0.1.0 库/工具与固定源码构建的 SDK0.1.0 集成，不代表 SDK 已发布到 npm，也不包含原版多人协作、Slack、订阅和持久化服务。工具可能修改工作区，应保留自己的输入副本。

## 在 OpenSandbox 中使用同一工作流

先按[OpenSandbox 提供方指南](https://github.com/Alibaba-Agent-Sandbox/awesome-providers/blob/main/opensandbox/docs/README.md)准备服务地址、服务 API Key 和镜像仓库。在创建前保留上面的模型 Key 与 endpoint，并选择平台、直连模式和模型：

```bash
export ABX_PROVIDER=opensandbox
export ABX_OPENSANDBOX_USE_SERVER_PROXY=false
export QM_MODEL='qwen3.8-flash'
```

这里的模型 ID 来自本例的模型服务，需与自己的 Key、endpoint 和授权匹配。接着执行前面的 launch、业务命令和完整 SDK 示例，后续调用继续使用同一平台和新实例 ID。CLI、SDK 与直接 HTTP 已分别完成本文的实际任务，并独立读取产物。

直连要求客户端能访问提供方解析出的端点；保留网关头、URL 路径/查询和独立应用令牌。服务代理与直连是不同的部署配置，客户端的等待时间不会改变上游代理期限，也不会延长远端任务或实例寿命。更换平台或启动模型配置后重新创建实例，先导出旧实例中的文件。

## 导出与结束

需要的文件先取回，再停止服务并结束实例：

```bash
abx kill "$SANDBOX_ID"
```

SDK close 只关闭连接。预备模板与镜像可用于复用，按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)只删除本次拥有的精确资源。本例的实例、预备模板、本地与远端镜像均已独立确认不存在。
