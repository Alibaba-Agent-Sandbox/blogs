---
title: 在沙箱里完成 AppWorld 训练任务，保存结果并复核原生评分
summary: 让模型调用原版 AppWorld API，保留加密结果，再用无模型的原生 evaluator 重新评分。
date: 2026-10-27
category: case
tags: [templates, appworld]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

AppWorld 的任务涉及应用 API 和数据库状态。这里把原版训练世界、API 和 evaluator 放入一次性极速版沙箱，由明确配置的模型通过工具调用完成一个训练任务，再下载加密结果并从保存的数据库独立复核评分。

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
export APPWORLD_MODEL_API_KEY='<YOUR_MODEL_API_KEY>'
export APPWORLD_MODEL_BASE_URL='<YOUR_CHAT_COMPLETIONS_API_BASE>'
export APPWORLD_MODEL='<YOUR_AUTHORIZED_MODEL_ID>'
export ABX_HTTP_TIMEOUT=750
abx template launch Alibaba-Agent-Sandbox/awesome-templates//appworld --sandbox-timeout 1800 --yes
export SANDBOX_ID='<launch 返回的沙箱 ID>'
abx sandbox command list "$SANDBOX_ID"
```

所有尖括号内容替换为自己的配置；密钥仅放在终端或自己的凭据管理器中。launch 已启动应用，后续调用连接这个实例。

## 完成实际任务

```bash
abx run "$SANDBOX_ID" appworld_run --json-args '{"max_steps":30,"command_timeout":600}'
# 将实际返回的 artifact_path 填入以下两处。
abx download "$SANDBOX_ID" '<artifact_path>' ./appworld-result.zip
abx run "$SANDBOX_ID" appworld_verify_artifact --json-args '{"path":"<artifact_path>"}'
```

不填写 task 时，入口选择原版首个训练任务。模型读取原版 API 文档并发起真实 API 调用，原版引擎执行数据库变更，由原版 evaluator 给出 score、success 与原生测试数量。模型不保证完成任务，检查返回字段而不是只看自然语言答复。

这次实际业务结果如下，三个入口分别运行新的任务：

| 入口 | 原生 score | 下载字节数 | 保存结果的无模型复核 score |
| --- | ---: | ---: | ---: |
| CLI | 1.0 | 11278 | 1.0 |
| 完整 Python SDK | 1.0 | 12522 | 1.0 |
| 直接 HTTP | 1.0 | 11646 | 1.0 |

每份下载文件都与返回的字节数和 SHA256 一致。`appworld_verify_artifact` 重新载入那一次保存的数据库，使用原版 evaluator 再计算，且不调用模型。这样可以在首次运行后复核状态是否满足原生规则。

结果包保持上游加密格式。本文不分发受保护的源码、训练任务细节、数据库或原始对话；自己运行后，按上游许可保管自己的结果包。

## 接入 Python 与 HTTP

[quickstart.py](./quickstart.py) 是实际执行过的完整模板 SDK 示例。保留上面的环境与实例 ID 后运行 `python quickstart.py`；它连接同一实例并关闭连接。它会把本次实际产物下载到本机。

直接 HTTP 按[调用指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)解析9000端口并保留网关头、路径、查询与应用认证。对应方法是 `POST /commands/appworld_run`，body 使用上述 CLI `--json-args` 内的直接对象，不套 args。返回外层为 `result`。完整参数、返回值与各方法见[模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/appworld/README.zh-CN.md)。

CLI、Python、HTTP 是替代入口，选择一种即可；本文的三种入口分别实际运行。命令执行期限、客户端等待与实例1800秒寿命分别控制不同阶段，客户端断开不表示远端工作已取消。

## 二次开发与使用边界

此入口通过自编兼容模型连接层接入原版 AppWorld0.1.3.post1 引擎，保留原版 API、数据库和评分器，不声称复现论文基线或完整排行榜。API Key 模式无需浏览器 OAuth 登录；上游须支持 Chat Completions 工具调用。模型、endpoint 和 Key 属于同一服务，base 不追加 `/chat/completions`。本例核心任务使用 qwen3.8-flash，三种文档调用使用 qwen3.8-max。更换配置后启动新实例，主机新 export 不会更新旧服务。

二次开发时可在当前原版训练任务集合内选择合法 task ID，调整1..40范围的 max_steps，并保持原版评分器作为业务验收依据。不要把模型生成的可执行 Python 直接替换这个受限 API 连接层。模型 HTTP 可能超时，原生任务也可能失败；保存实际错误和结果，再判断是否需要重试，不能将未完成任务标为成功。返回的独占结果目录由调用方负责导出和清理，删除实例也会删除其中数据。

## 导出与结束

需要的文件先取回，再停止服务并结束实例：

```bash
abx kill "$SANDBOX_ID"
```

SDK close 只关闭连接。预备模板与镜像可用于复用，按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)只删除本次拥有的精确资源。本例的实例、预备模板、本地与远端镜像均已独立确认不存在。
