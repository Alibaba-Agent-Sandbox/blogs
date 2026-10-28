---
title: 用 Codex 修复现有函数，再取回程序与说明
summary: 配置 Codex CLI 0.162.1 的独立模型，操作现有代码，取回真实程序，并把命令或会话入口接入自己的应用。
date: 2026-10-27
category: case
tags: [templates, models, codex]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

案例先修复现有 Fibonacci 实现，要求负数输入抛出 ValueError，保留原有检查，并补写 REPORT.md 与新的检查。原始检查、实际修改后的源文件和独立的额外输入均在任务返回后核对；随后在另一实例生成可下载脚本。

本例使用 Codex CLI 0.162.1、极速版、CLI `0.5.7`、Python client/server `0.4.0a6`。
代码修复配置 `qwen3.8-flash`，完整文档流程在另一实例配置 `qwen3.8-max`。
下载的 [generated_hello.py](./generated_hello.py) 独立运行后输出 `Hello from the sandbox`。

## 准备平台和独立模型服务

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
```

按[平台配置](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)
准备极速版 API Key、地域、连接地址、Docker、构建权限和镜像仓库。再设置独立模型：

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export ABX_LLM_API_KEY='<YOUR_MODEL_API_KEY>'
export ABX_LLM_BASE_URL='<YOUR_RESPONSES_BASE_URL>'
export CODEX_MODEL='<YOUR_AUTHORIZED_MODEL_ID>'
abx template launch Alibaba-Agent-Sandbox/awesome-templates//codex --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
abx run "$SANDBOX_ID" codex_version
abx run "$SANDBOX_ID" codex_setup_check
```

endpoint、Key、确切模型 ID 必须属于同一授权服务，并支持 **Responses**。
API base 使用服务提供的前缀，通常为 `/v1`，不追加具体 API 路径。
平台 API Key、模型 Key、应用令牌分别配置。codex_setup_check 读取目标实例里的安装与 Key 是否存在，只返回状态。codex_exec 按平台探测选择其支持的隔离方式；嵌套隔离不可用时，bypass 以自己拥有的外层沙箱作为边界。任务返回缓冲事件和最终消息；resume 参数可续接已有线程。

## 从代码任务到实际文件

上面的现有代码案例保留已有约束，实际改源文件并取回报告。
自己的项目可以先上传明确的工作目录，约定允许修改的文件和交付要求，
在任务返回后独立运行自己的检查并审阅差异。

再用完整的小任务生成一个程序：

```bash
ABX_HTTP_TIMEOUT=420 abx run "$SANDBOX_ID" codex_exec --json-args '{"prompt":"Create generated_hello.py that prints exactly Hello from the sandbox, and GENERATED_REPORT.md explaining the program. Preserve unrelated existing files.","sandbox":"auto","cwd":"/home/user/workspace","timeout_s":300}'
abx download "$SANDBOX_ID" /home/user/workspace/generated_hello.py ./generated_hello.py
python generated_hello.py
```

实际输出为 `Hello from the sandbox`。配套的 [report.txt](./report.txt) 是原生任务生成的说明原文。
任务返回若包含 exit_code，先确认其为零，再查看真实文件。
模型输出与任务期限分别受模型服务和 command_timeout/timeout_s 影响；
HTTP 客户端等待与 1800 秒实例寿命独立，断开客户端不保证远端任务取消。

## Python、HTTP 与项目扩展

[quickstart.py](./quickstart.py) 是实际执行的完整 SDK 示例：保留实例 ID 与环境，
运行 `python quickstart.py`。它连接当前实例，用独立应用令牌调用 `codex_exec`。
需要的结果通过文件 API 或 abx download 导出，再交给自己的程序。

HTTP 用户按[直接 HTTP 指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)
解析 9000 端口，保留网关头、路径、查询，再添加应用认证。向
`POST /commands/codex_exec` 发送上面的直接 JSON 对象，不加 args 包装层。
三个调用入口分别完成了新任务；每次先删除自己的上一轮输出，再下载并独立运行当前程序。

配置文件入口 codex_config_write 可以显式写入 provider、base_url、env_key、model 与 wire_api；Key 保留在环境中，不写入 TOML。codex_agents_write 接收 content 和 cwd，把自己的项目规则写到对应 AGENTS.md。实际云端调用过这两个入口并读回配置与规则；自己的项目先下载备份，再按命令参考选择目标目录。

二次开发可以从自己的模板副本固定额外依赖，上传项目、提交任务、运行已有检查、下载差异。
保留原生程序的版本和授权。扩展权限或接入其他工具时，按自己的业务验证实际行为。
全部参数、返回类型与上游边界见[模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/codex/README.zh-CN.md)。

## 更换模型与结束任务

保存产物后 export 新的模型 ID，重新 launch 同一模板，使用新实例 ID；更换服务时同步更换
Key 与 base。已运行的应用不会因本机再次 export 而重新配置。本例确实用两种分别配置的模型
完成了实际工作，没有推断其他服务或订阅的可用性。

```bash
abx kill "$SANDBOX_ID"
```

SDK close 只关闭连接。预备模板和镜像按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)
只删除自己的资源。本例所用云实例、预备模板及本次镜像均独立确认不存在。

## 在 OpenSandbox 中使用同一工作流

这个案例也可以在 OpenSandbox 中完成。先按[OpenSandbox 提供方指南](https://github.com/Alibaba-Agent-Sandbox/awesome-providers/blob/main/opensandbox/docs/README.md)准备服务地址、服务 API Key 和镜像仓库，然后在创建实例前选择平台：

```bash
export ABX_PROVIDER=opensandbox
export ABX_OPENSANDBOX_USE_SERVER_PROXY=true
```

接着执行上面的 launch、业务命令和 SDK 示例；后续终端与 Python 继续使用同一个平台和实例 ID。沙箱 API Key 与应用令牌分别配置，原有业务输入、返回结果和结束实例的方法相同。

这里使用 OpenSandbox1.1.1 的服务代理模式；CLI、完整 SDK 示例和直接 HTTP 都能完成文中的实际任务。代理模式要求客户端能访问服务地址。若部署环境改为直连模式，客户端还必须能访问提供方解析出的端点；更换配置后重新创建自己的实例，不复用另一平台的 ID。
