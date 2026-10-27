---
title: 用 OpenCode 沙箱生成脚本、修复代码并切换模型
summary: 把 OpenCode 放进独立工作区，生成可下载的 Python 文件，修复已有计算函数，续接会话，并给同一接口选择第二个兼容模型。
date: 2026-10-27
category: case
tags: [opencode, coding, models, templates]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

让代码助手做完工作，需要拿到真正能运行的文件。这个案例先让 OpenCode 生成一个
Python 脚本并下载到本机，再把同一工作方式用于修复已有函数、保留原有用例和续接会话。
最后为下一次任务选择第二个模型，工作区和调用接口都可以继续使用。

这里使用极速版、CLI `0.5.7`、Python client/server `0.4.0a6` 和 OpenCode
`1.19.0`，模板源码固定为 `961959470411c3375a8346eb43755fa183129c22`。
生成并下载的 [hello.py](./hello.py) 可以在本机执行，输出 `Hello from OpenCode`。

## 把平台凭据与模型凭据分开配置

先按[Python 工作区案例](/blog/template-practice-python-hello/#安装工具准备运行平台)
安装 CLI、准备 Docker、配置极速版和 ACR。构建账号按
[权限指南](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/blob/main/docs/zh/guide/permissions.md)
授予权限；持有 AK/SK 不等于已经有构建、推送和管理资源的权限。

模型连接单独配置。下面的 endpoint 是公开兼容服务的示例；换成自己实际使用的
完整 OpenAI 兼容地址，并使用它接受的 Key 和模型名称。

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export ABX_LLM_API_KEY='<YOUR_MODEL_API_KEY>'
export ABX_LLM_BASE_URL='https://dashscope.aliyuncs.com/compatible-mode/v1'
export ABX_HTTP_TIMEOUT=660
```

这条路径通过 API Key 认证，不需要浏览器登录。模板的 `opencode.json` 已经把
自定义 provider `dashscope` 指向 `ABX_LLM_BASE_URL`、`ABX_LLM_API_KEY`。
`dashscope/` 是这里使用的配置名称；实际请求发到你填写的兼容 endpoint。
本机 OpenCode 的登录状态不会自动复制进沙箱。

## 启动后生成一个能运行的文件

```bash
abx template launch Alibaba-Agent-Sandbox/awesome-templates//opencode@961959470411c3375a8346eb43755fa183129c22 --sandbox-timeout 1800 --yes
export ABX_SANDBOX_ID='<启动返回的沙箱 ID>'
abx exec "$ABX_SANDBOX_ID" -- mkdir -p /home/user/workspace
abx run "$ABX_SANDBOX_ID" opencode_version
abx run "$ABX_SANDBOX_ID" opencode_setup_check
abx run "$ABX_SANDBOX_ID" opencode_run --json-args '{"prompt":"Create hello.py in the current directory that prints Hello from OpenCode, then run it.","model":"dashscope/qwen3.8-flash","cwd":"/home/user/workspace"}'
abx download "$ABX_SANDBOX_ID" /home/user/workspace/hello.py ./hello.py
python3 hello.py
```

最后一步输出 `Hello from OpenCode`。模型返回的说明文字可以变化，下载的文件能够
独立执行，才是交给后续流程的结果。`opencode_run` 还返回 `session_id`、`model`、
`cwd` 和 JSON 事件；保存会话 ID，可以继续处理同一项目。

Python 程序可以使用完整的 [quickstart.py](./quickstart.py)：安装
`agent-sandbox-client==0.4.0a6` 后，它读取上述环境变量，连接同一个实例，调用
`client.commands.run` 并下载 `hello.py`。HTTP 对应 `POST /commands/opencode_run`，
直接发送上面 `--json-args` 中的对象。按
[HTTP 调用指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/961959470411c3375a8346eb43755fa183129c22/docs/using-templates.zh-CN.md#http-post)
保留 provider 返回的路径、查询和网关头，再添加独立应用令牌；等待时间设为 660 秒。

## 在已有项目里修复函数，再续接会话

把已有项目上传到一个新的工作目录，让 `cwd` 指向它。一个小例子是
`calc.py` 的 `add(a, b)` 错写成减法：

```python
def add(a, b):
    return a - b
```

任务要求修复函数，保留 `test_calc.py`，运行其中正数、负数和零的三个用例，
再生成 `report.txt` 说明修改。这里实际完成了源码修改；原测试文件保持不变，
修复后的函数也能处理额外的整数和小数输入。

继续任务时，把返回的真实 ID 作为 `session` 参数传入 `opencode_run`，同时保留
同一个 `cwd`。例如让它读取已有 `report.txt`，计算文件 SHA-256，调用修复后的
`add`，把输入与结果写进新的 `resume.json`。这样续接建立在实际文件和前一段
工作上，而不只依赖聊天文字。需要复核时，下载报告和源文件，在模型调用之外
运行自己的用例。

## 为下一次任务选择第二个模型

先确认 endpoint 的账号支持另一个具备工具调用能力的模型。本例第二次选择
`qwen3.8-max`，让它新建一个文件，再独立下载内容：

```bash
abx run "$ABX_SANDBOX_ID" opencode_run --json-args '{"prompt":"Create model-switch.txt containing exactly MODEL_SWITCH_CONFIRMED followed by a newline. Read the file and reply with that text.","model":"dashscope/qwen3.8-max","cwd":"/home/user/workspace"}'
abx download "$ABX_SANDBOX_ID" /home/user/workspace/model-switch.txt ./model-switch.txt
```

得到的 [model-switch.txt](./model-switch.txt) 内容为 `MODEL_SWITCH_CONFIRMED`。
这次调用使用了另一个模型并完成文件操作。模型 ID 不在你账号的服务列表中时，
应换成实际可用的 ID；示例名称不代表账号拥有该模型的权限。

换 endpoint 或 Key 时，在启动前更改 `ABX_LLM_BASE_URL` 和 `ABX_LLM_API_KEY`，
创建新实例。运行中的应用不会因为本机重新 `export` 而自动改变配置。换单次任务
的模型使用 `model` 参数；清单的非空 `OPENCODE_MODEL` 默认值不会被主机同名变量覆盖。

## 可选服务与二次开发

普通任务使用 `opencode_run` 即可。需要 OpenCode 自己的 HTTP 服务时，可以调用
`opencode_serve_start`，用 `opencode_serve_status` 查看状态，再以
`opencode_serve_stop` 停止当前服务进程。端口默认 4096；通过 provider 解析其地址，
不要把沙箱内部 localhost 地址当作外部入口。需要原生服务密码时，启动模板前设置
`OPENCODE_SERVER_PASSWORD`，同时保留平台网关认证。

把本例接入自己的代码流程，可以上传真实仓库、指定工作目录、给出明确的文件修改
要求，再让外部程序运行原有用例和下载差异。要支持其他原生模型 provider，可 fork
模板并按[现有配置说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/961959470411c3375a8346eb43755fa183129c22/opencode/README.zh-CN.md#配置)
添加其配置，保留当前兼容 provider，选择对应的 `provider/model`。
原生认证文件需要在沙箱内准备，不能依赖主机登录态。

模板自动批准 OpenCode 工具执行，因此应使用独立工作区，只提供任务所需文件和
凭据。`cwd` 选择目录，不构成操作系统权限隔离；模型仍能修改运行用户可写的文件。
模型任务有 600 秒期限，HTTP 客户端断开也不保证模型进程立即取消。

## 取回成果后释放实例

```bash
abx kill "$ABX_SANDBOX_ID"
```

先下载需要保留的代码、报告和会话资料，再删除实例；不再复用时，按启动回执清理
本次自有模板与镜像。本案例的实际结果对应极速版；OpenSandbox 的独立配置和构建
方式见[模板页面](https://registry.agent-sandbox.cn/templates/opencode/)。
