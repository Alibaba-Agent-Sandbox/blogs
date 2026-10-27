---
title: 在 SWE 工作区修复 Flask 空名称问题，交付可独立评估的补丁
summary: 用原生 mini-SWE-agent 修复一个真实 Flask 问题，从已知失败基线出发，在新工作副本中评估补丁，取回完整报告与源代码差异。
date: 2026-10-27
category: case
tags: [swe, flask, coding, models]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

给已有项目修复缺陷时，交付的不只是代理的一句“完成了”，还需要源代码差异和能复查的
结果。这个案例处理 Flask Blueprint 的空名称问题：先复现原来的失败，再让原生
mini-SWE-agent 修改代码，最后在另一个工作副本中应用补丁并运行原有检查。

实际交付物是 [repair.patch](./repair.patch) 和 [report.json](./report.json)。
补丁在 `src/flask/blueprints.py` 中加入以下判断：

```diff
+        if not name:
+            raise ValueError("'name' may not be empty.")
+
         if "." in name:
```

结果从 1 项失败、59 项通过变成了全部 60 项通过，零错误、零跳过。
它们对应固定的 `pallets__flask-5014` 实例，报告包含每一个原有检查的结果。
这是当前环境中的单实例可移植切片，报告明确记录 `official_benchmark_score: false`，
不等同于完整官方 SWE-bench Docker 评测，也不能代表其他实例的成绩。

## 准备客户端、工作区和模型

本例使用 `swe` 模板 `1.2.0`、mini-SWE-agent `2.4.6`、CLI `0.5.7` 和 Python
client/server `0.4.0a6`。代理和服务使用模板的 Python 环境；独立 Flask 评估固定
Python `3.11.10`，以保持原有检查的行为。

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
```

先按[平台与镜像构建配置](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)
准备极速版账号连接、Docker、镜像仓库与相应权限。然后填写独立的模型配置：

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export SWE_API_KEY='<YOUR_MODEL_API_KEY>'
export SWE_BASE_URL='<YOUR_CHAT_COMPLETIONS_BASE_URL>'
export SWE_MODEL='<YOUR_AUTHORIZED_MODEL_ID>'
export ABX_HTTP_TIMEOUT=1200
abx template launch Alibaba-Agent-Sandbox/awesome-templates//swe --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
abx run "$SANDBOX_ID" swe_version
abx run "$SANDBOX_ID" swe_setup_check
```

Key、API base 和模型 ID 必须属于匹配的模型服务和地域。base 包含供应商规定的前缀，
通常是 `/v1`，不追加 `/chat/completions`；模型填裸 ID，封装会添加 LiteLLM 的
`openai/` 前缀。这是模型 API Key 模式，不启动浏览器 OAuth，也不继承本机登录态。
沙箱 API Key 和 `ABX_SERVER_TOKEN` 分别用于平台与应用认证。

`1.2.0` 默认使用原生 bash 工具调用，要求模型支持 Chat Completions tool calling。
本例的修复分别使用过 `qwen3.8-flash` 和 `qwen3.8-max`。`swe_setup_check` 返回的
`native_tool_calls` 应为 `true`，其他配置标志也应满足运行条件。

## 从一个确实失败的基线开始

```bash
abx run "$SANDBOX_ID" swe_prepare --json-args '{}'
```

返回本次工作目录的 `run_id` 和基线。模板使用固定 Flask 源快照以及原有检查补丁，
要求恰好复现 1 失败、59 通过，才允许继续；不会用其他错误或缺失依赖替代预期失败。
其中 `tests/test_blueprints.py::test_empty_name_not_allowed` 是本次需要修复的项目。

把返回的 ID 填到下面的 `RUN_ID`。`allow_execution: true` 明确允许代理运行它生成的
shell 命令；这些命令拥有沙箱用户的文件和网络权限，使用自己可丢弃的实例。

```bash
export RUN_ID='<本次返回的 run_id>'
abx run "$SANDBOX_ID" swe_run_agent --json-args "{\"run_id\":\"$RUN_ID\",\"allow_execution\":true,\"max_steps\":30,\"command_timeout\":600}"
abx run "$SANDBOX_ID" swe_evaluate --arg run_id="$RUN_ID"
abx run "$SANDBOX_ID" swe_report --arg run_id="$RUN_ID"
```

原生 mini CLI 需要实际调用模型并提交工作。随后 `swe_evaluate` 创建新的源代码与评估
环境，只导入允许的源文件差异，再运行固定的 60 个原有检查。修改代理工作目录中的
检查文件或打印成功文字，都不能代替这份独立结果。

本例实际报告的关键字段为：

```json
{"passed": 60, "failed": 0, "errors": 0, "skipped": 0,
 "resolved_slice": true, "official_benchmark_score": false}
```

完整报告还保留 `fail_to_pass` 和 `pass_to_pass` 的逐项结果，见附件。

## 导出补丁并释放资源

使用评估或报告返回的实际文件路径，不要根据本机目录猜测远端路径：

```bash
abx download "$SANDBOX_ID" '<返回的 report_path>' ./report.json
abx download "$SANDBOX_ID" '<返回的 patch_path>' ./repair.patch
abx run "$SANDBOX_ID" swe_cleanup --arg run_id="$RUN_ID"
abx kill "$SANDBOX_ID"
```

`swe_cleanup` 删除这个 `run_id` 的工作目录；`abx kill` 删除外层实例，两者负责不同
资源。下载完成后审阅补丁，再在自己的项目版本和依赖环境中应用。已有镜像与预备模板
可能留作复用，按[清理说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)
只删除本次创建的资源。

## 用 Python 或 HTTP 接入交付流程

CLI、SDK 和 HTTP 是替代入口，选择一个完整运行即可。下载
[quickstart.py](./quickstart.py)，在已启动的实例上保持相同环境变量，执行
`python quickstart.py`。它会准备自己的 run、执行真实修复、评估、下载两个产物并在
`finally` 中清理 run。附件会关闭客户端连接，外层实例仍需由你显式删除。

HTTP 用户按[直接调用指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)
解析端口 9000，保留网关认证和独立应用令牌，依次调用：

1. `POST /commands/swe_prepare`，发送 `{}` 并保留返回的 `run_id`。
2. `POST /commands/swe_run_agent`，发送该 ID、`allow_execution: true`、`max_steps: 30` 和 `command_timeout: 600`。
3. `POST /commands/swe_evaluate`，发送 `{"run_id":"<本次 ID>"}`。
4. `POST /commands/swe_report` 读取结果，导出实际返回的文件。
5. `POST /commands/swe_cleanup` 清理同一个 run。

请求体是直接参数对象，不加 `args` 包装层。本例分别通过 CLI、完整 SDK 程序和 HTTP
独立完成了三次修复，每次报告都是相同的 60 项通过；三个 run 的工作目录都已删除。

## 切换模型与二次开发

`SWE_API_KEY`、`SWE_BASE_URL`、`SWE_MODEL` 在启动时读取。换模型时设置新的授权 ID，
重新从公开模板创建实例，并使用新返回的沙箱 ID；换供应商时同步替换 Key、base 和模型。
旧进程不会因为你修改本机 export 而重配。

`SWE_MODEL_PROTOCOL` 在当前清单中是非空 `toolcall`，主机 export 无法覆盖它。
需要旧版 `text` 协议时，复制并审阅自己的模板，显式设置该字段后按
[本地源码方式](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md)
启动，不要把旧协议与当前默认原生工具调用混用。

接入自己的修复流水线时，可以把准备、修复、评估、归档分成明确阶段，让调用方决定
是否接受补丁。当前模板只提供这个固定实例；扩展到其他实例需要增加相应的源快照、
依赖、原有检查和独立评估规则，不能仅替换一个 ID。Flask 源码及其 BSD-3-Clause
授权见[上游项目](https://github.com/pallets/flask)与[固定快照](https://github.com/pallets/flask/tree/7ee9ceb71e868944a46e1ff00b506772a53a4f1d)。

补丁随附固定源快照的 [Flask 许可证原文](./FLASK-LICENSE.txt)，保留版权及再分发条款。
