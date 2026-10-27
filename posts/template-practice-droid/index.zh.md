---
title: 用 Factory Droid 原生 BYOK 接入自己的模型，交付可运行的小程序
summary: 在独立沙箱中配置 Droid 自定义模型，完成原生文件编码，通过 CLI、SDK 或 HTTP 导出代码和报告，再独立运行产物。
date: 2026-10-27
category: case
tags: [templates, droid, coding]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

有自己的 Chat Completions 模型服务时，可以使用 Factory Droid 的原生 BYOK 自定义模型。本例让原版 Droid0.241.1 在沙箱中生成 Python 程序与报告，再把文件取回独立运行。下载的 [generated_hello.py](./generated_hello.py) 输出 `Hello from the sandbox`，对应的 [生成报告](./generated-report.txt) 保留原始内容。

这里使用模板的 `droid_byok`，由原版 CLI 执行文件工具循环；它使用原生 `customModels` 配置，没有另写协议转换服务，也没有替换 Droid 二进制。实际运行这条链路不需要 Factory 账号或浏览器登录。另一个 `droid` 命令使用 Factory 账号，凭据与本文自己的模型 Key 分开。

## 配置沙箱与自己的模型

先按[平台指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)完成沙箱 API Key、连接地址、地域、Docker、构建权限和镜像仓库配置。本文使用极速版默认源码配方、CLI0.5.7/client-server0.4.0a6。

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export DROID_MODEL_API_KEY='<YOUR_COMPATIBLE_MODEL_API_KEY>'
export DROID_MODEL_BASE_URL='<YOUR_CHAT_COMPLETIONS_API_BASE>'
export DROID_MODEL='<YOUR_AUTHORIZED_MODEL_ID>'
export ABX_HTTP_TIMEOUT=420
abx template launch Alibaba-Agent-Sandbox/awesome-templates//droid --sandbox-timeout 1800 --yes
export SANDBOX_ID='<launch 返回的沙箱 ID>'
abx run "$SANDBOX_ID" droid_byok_setup_check --json-args '{}'
```

三项模型配置来自自己有权限的同一个服务。base 应包含实际 API 前缀，例如 `/v1`，不要再追加 `/chat/completions`。启动时传入这些值；要更换模型、endpoint 或 Key，修改对应环境变量并启动新实例，改变本机环境不会重配旧应用。本例核心编码使用 qwen3.8-flash，文档的三种替代入口使用 qwen3.8-max。

模板每次调用创建私有原生配置，使用 `generic-chat-completion-api` 自定义模型和环境变量形式的 Key 引用；真实 Key 不写入原生配置或 argv。固定使用原版0.241.1，关闭自动更新，临时原生 HOME 在结束后移除。工作区文件仍需自己审阅，避免把秘密写进任务或项目。

## 从明确的文件交付开始

```bash
abx run "$SANDBOX_ID" droid_byok --json-args '{"prompt":"Create generated_hello.py that prints exactly Hello from the sandbox, and GENERATED_REPORT.md explaining the program. Preserve unrelated existing files.","cwd":"/home/user/app","command_timeout":300}'
abx download "$SANDBOX_ID" /home/user/app/generated_hello.py ./generated_hello.py
abx download "$SANDBOX_ID" /home/user/app/GENERATED_REPORT.md ./GENERATED_REPORT.md
python generated_hello.py
```

实际结果为：

```text
Hello from the sandbox
```

Droid 原生允许的工具为 Read、Edit、Create、Grep、Glob、LS，可读取和编辑工程；该入口没有给原生代理 shell 执行工具。生成后由调用方独立运行程序。真实文件与运行输出能说明交付是否可用，单独的自然语言“已完成”不能代替它们。

本例的 CLI、完整 SDK 和直接 HTTP 三个替代入口分别在清理旧产物后生成新文件和报告，再分别下载并放入只读、无网络的有界容器执行。原生核心流程还修复了已有的错误函数，原始用例文件逐字保留，调用方独立执行原始和额外边界用例。

## 接入 SDK 或业务 HTTP 服务

保留上述环境与实例 ID，运行实际使用过的 [quickstart.py](./quickstart.py)。脚本连接同一应用，调用 `droid_byok`，检查返回结果后再通过文件接口导出产物。SDK 的 close 只关闭连接。

HTTP 按[直接调用指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)解析9000端口，保留网关头、路径、查询与独立应用认证。使用 `POST /commands/droid_byok`，body 就是 CLI 的直接参数对象，不加 args 包装。响应外层为 result，其中包含 stdout、stderr、exit_code 与 native_version。检查原生命令正常结束、实际文件和独立执行结果。

## 扩展为自己的工程修改任务

把项目副本与锁文件上传到 WORKSPACE 内已有目录，用 cwd 选择这个目录，描述要修改的文件、保留的原始用例和报告路径。模型可以读取、编辑这个工程；调用方再独立执行检查与取回文件。该 cwd 约束用于选择工程，不代表原生文件工具受到操作系统级目录隔离。

若要使用 Factory 账号路径，另按[模板账号说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/droid/README.zh-CN.md)准备真正的 FACTORY_API_KEY，再使用 `droid`。自己的兼容模型 Key 不能替代 Factory 账号 Key。本文没有使用该账号路径，模板完整方法验收仍保留 Beta；原生 BYOK 的实际效果不代表已验证另一个账号入口。

## 保存产物并结束

```bash
abx kill "$SANDBOX_ID"
```

先保存需要的源码和报告，再按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)删除本次创建的资源。本例实例、预备模板、本地和远端镜像均已独立确认不存在。
