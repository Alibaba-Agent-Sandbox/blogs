---
title: 用 Aider 沙箱先评审代码，再放行指定文件的修改
summary: 配置兼容模型服务，在独立 Git 工作区中调用 Aider，区分只读评审与显式写回，取回生成的代码，并通过新实例更换模型。
date: 2026-10-27
category: case
tags: [aider, coding, git, models]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

代码修改流程可以拆成两步：先让助手解释问题，再明确允许它修改哪些文件。
`aider` 模板默认使用只读 ask 模式；设置 `allow_write=true` 并列出文件后，才把
选定的修改写回项目。它不自动提交 Git。

本例使用极速版、CLI `0.5.7`、Python client/server `0.4.0a6` 和 Aider
`0.86.2`。模板源码固定为 `50d7e38cd5837042acb756aad66d8f97050f11dd`。
生成的 [generated_hello.py](./generated_hello.py) 下载后可以独立运行，输出
`Hello from the sandbox`。

## 准备账号和模型连接

先按[费用文件案例](/blog/template-practice-python-hello/#安装工具准备运行平台)
安装 CLI、准备 Docker，并配置自己的极速版连接、ACR 和构建账号权限。模型设置独立于
沙箱平台凭据：

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export AIDER_API_KEY='<YOUR_MODEL_API_KEY>'
export AIDER_BASE_URL='https://dashscope.aliyuncs.com/compatible-mode/v1'
export AIDER_MODEL='qwen3.8-flash'
export ABX_HTTP_TIMEOUT=660
```

公开 endpoint 只是配置示例。Key、地址和模型 ID 必须来自同一个可用服务；这个适配
需要 OpenAI 兼容 Chat Completions，且服务接受 `enable_thinking=false`。
这里使用 whole-file 文本编辑，不依赖模型原生工具调用。

这条路径用 API Key 认证，不启动浏览器或 OAuth 登录。`AIDER_API_KEY` 是模型凭据，
`ABX_SERVER_TOKEN` 是模板应用令牌，均不等于创建沙箱的 API Key。

## 启动 Git 工作区并生成脚本

```bash
abx template launch Alibaba-Agent-Sandbox/awesome-templates//aider@50d7e38cd5837042acb756aad66d8f97050f11dd --sandbox-timeout 1800 --yes
export SANDBOX_ID='<启动返回的沙箱 ID>'
abx exec "$SANDBOX_ID" -- git -C /home/user/app init -q
abx sandbox command list "$SANDBOX_ID"
abx run "$SANDBOX_ID" aider --json-args '{"prompt":"Create generated_hello.py that prints exactly Hello from the sandbox, and GENERATED_REPORT.md explaining the program. Preserve unrelated existing files.","files":"[\"generated_hello.py\",\"GENERATED_REPORT.md\"]","allow_write":true,"cwd":"/home/user/app","command_timeout":300}'
abx download "$SANDBOX_ID" /home/user/app/generated_hello.py ./generated_hello.py
python3 generated_hello.py
```

最后输出 `Hello from the sandbox`。返回对象中的 `changed_files` 列出实际写回的
文件；这里包括脚本和 `GENERATED_REPORT.md`。需要保留说明时，也在释放前下载它。

`files` 是一个 **JSON 编码的字符串**，不是外层参数对象中的数组。
`allow_write` 则必须是 JSON 布尔值。`cwd` 必须是已有 Git 工作树；尚未初始化的新
目录需要先执行上面的 `git init`。

## 先评审，再修改已有文件

对已有计算函数，可以先提交只读请求：

```bash
abx run "$SANDBOX_ID" aider --json-args '{"prompt":"Review generated_hello.py and explain what it does without editing files.","files":"[\"generated_hello.py\"]","cwd":"/home/user/app","command_timeout":300}'
```

不设置 `allow_write` 时，不把修改写回原工作区。针对已有 `calculator.py`，同一
工作方式可以先解释加法函数中的减法错误，再允许修改源码并新增 `REPORT.md`。
该流程实际完成了修复，保留了原来的三个用例，并通过额外的独立计算检查。

Aider 在这里负责修改文件；运行用例是调用方的工作。把用例放进项目后，通过进程
API 执行它们，查看真实退出码。不要把模型文字里的“已经通过”当作执行结果。

## 接入 Python 或 HTTP

安装 `agent-sandbox-client==0.4.0a6`，保存完整的
[quickstart.py](./quickstart.py)，保留 `SANDBOX_ID`、`ABX_PROVIDER` 和应用令牌：

```bash
python quickstart.py
abx download "$SANDBOX_ID" /home/user/app/generated_hello.py ./generated_hello.py
```

它连接已经启动的实例，初始化工作树后调用相同的命名命令。HTTP 对应
`POST /commands/aider`，直接发送 CLI `--json-args` 中的参数对象。按
[HTTP 指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/50d7e38cd5837042acb756aad66d8f97050f11dd/docs/using-templates.zh-CN.md#http-post)
解析服务地址、保留网关信息并添加应用令牌。三种方式均能生成可执行的脚本；实际
接入时任选一种，不要在未清理输出前反复提交整段创建示例。

## 更换模型、endpoint 或 API Key

这三个设置在应用启动时读取，没有单次调用的 `model` 参数。保存旧实例的成果并
删除它，再修改变量，启动新实例：

```bash
abx kill "$SANDBOX_ID"
export AIDER_MODEL='qwen3.8-max'
abx template launch Alibaba-Agent-Sandbox/awesome-templates//aider@50d7e38cd5837042acb756aad66d8f97050f11dd --sandbox-timeout 1800 --yes
export SANDBOX_ID='<新实例 ID>'
abx exec "$SANDBOX_ID" -- git -C /home/user/app init -q
```

新实例中再次执行上面的生成任务。本案例的修复流程使用 `qwen3.8-flash`，完整文档
任务也使用了 `qwen3.8-max`，实际下载的代码能够运行。自己的账号不支持这些 ID 时，
换成服务实际提供的模型。更换 endpoint 或 Key 也在新启动前修改对应变量；修改主机
环境不会重配运行中的应用。

## 扩展到自己的仓库

上传真实项目，先让只读请求说明修改范围，再显式选定源码、说明或补丁文件。
下载差异，由自己的流程运行原有用例和进行提交。需要自动批处理时，可以让外层程序
维护任务、文件清单和结果，不必把 GitHub 凭据交给这个模板。

接口还有 `aider_version` 和 `aider_setup_check`，可用于查询安装和配置存在性。
版本、Key 存在或返回 HTTP200 都不能替代检查 `changed_files`、实际文件及进程退出码。
写回文件清单也不是操作系统权限边界；只在自己控制的工作区处理相应任务。

完成后先下载代码与报告，再运行 `abx kill "$SANDBOX_ID"`。不再复用时，按启动回执
清理本次自有模板和镜像。本文的实际结果对应极速版；其他平台的独立配置见
[模板页面](https://registry.agent-sandbox.cn/templates/aider/)。
