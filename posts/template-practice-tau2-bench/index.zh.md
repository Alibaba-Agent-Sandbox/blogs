---
title: 用 Tau2 完成一次零售客服任务，再复核原生轨迹
summary: 配置原生客服代理和用户模拟器，运行实际零售任务，下载轨迹并独立回放原生评分。
date: 2026-10-27
category: case
tags: [templates, tau2-bench]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

一次客服工具任务是否完成，可以同时查看模型对话、实际领域工具调用和原生评估。这里运行 Tau2 的零售任务0，让原版代理和用户模拟器使用明确配置的模型，再复核保存轨迹。

CLI、完整 SDK 和 HTTP 的三次独立任务均完成，原生 reward 为1.0；各自下载的轨迹与返回的长度、SHA256一致，独立无模型回放再次得到1.0。

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
export TAU2_MODEL_API_KEY='<YOUR_MODEL_API_KEY>'
export TAU2_MODEL_BASE_URL='<YOUR_CHAT_COMPLETIONS_BASE_URL>'
export TAU2_MODEL='<YOUR_AUTHORIZED_MODEL_ID>'
export ABX_HTTP_TIMEOUT=750
abx template launch Alibaba-Agent-Sandbox/awesome-templates//tau2-bench --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
abx sandbox command list "$SANDBOX_ID"
```

本例原生任务使用 qwen3.8-flash，三种完整文档流程在另一实例使用 qwen3.8-max。更换模型、Key或endpoint时，保存产物后重新 export 三项匹配的配置并创建新实例；本机后来 export 不会更新旧应用。

## 完成一次实际业务流程

```bash
abx run "$SANDBOX_ID" tau2_run --json-args '{"domain":"retail","task_id":"0","max_steps":30,"command_timeout":600}'
```

CLI、完整 SDK 和 HTTP 的三次独立任务均完成，原生 reward 为1.0；各自下载的轨迹与返回的长度、SHA256一致，独立无模型回放再次得到1.0。

原生 Tau2 v1.0.1、固定源代码与原始零售数据在2核极速版实例中运行。四个命名入口全部调用；真实代理与用户对话包含领域工具调用，正常结束，随后用原版严格回放重算奖励。一次任务结果不代表完整 benchmark 成绩。

命令参数、返回字段与期限见[此模板完整说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/tau2-bench/README.zh-CN.md)。
任务的执行期限、客户端等待和1800秒实例寿命分别控制不同阶段。

返回中的 artifact_path 是这一次的轨迹路径，可直接下载并回放：

```bash
abx download "$SANDBOX_ID" '<artifact_path-from-result>' ./tau2-trajectory.json
abx run "$SANDBOX_ID" tau2_verify_artifact --json-args '{"path":"<artifact_path-from-result>","task_id":"0"}'
```

把占位路径换成刚才返回的实际值。回放使用原版评估器，不再次调用模型。

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

TAU2_MODEL_API_KEY、TAU2_MODEL_BASE_URL、TAU2_MODEL 同时配置到支持 Chat Completions 工具调用的服务；代理和用户模拟器都会调用它。API Key 模式无需浏览器登录。可在零售 slice 中选择存在的 task_id，调整合法 max_steps；其他领域、语音和需要自然语言裁判的任务不由该入口支持。把任务ID、固定源版本、模型和原生轨迹哈希放进自己的运行记录，用 tau2_verify_artifact 复核；轨迹数据按自己的业务要求保存。

修改模板时从自己的源码副本开始，固定依赖和项目配置，保留上游许可证。
本例没有发布原始对话轨迹；运行程序会为你保存自己那一次的轨迹。

## 导出并结束

业务完成后，按完整说明停止自己启动的服务，下载需要的文件，再执行：

```bash
abx kill "$SANDBOX_ID"
```

SDK close 只关闭连接。预备模板和镜像按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)
仅删除自己的资源。本例的沙箱、预备模板、本次本地与远端镜像均独立确认不存在。
