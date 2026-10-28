---
title: 给临时代码工作区准备 Go、Rust 和 Java
summary: 在同一非 root 沙箱中运行固定编译器，完成三个程序的编译、执行与临时文件清理。
date: 2026-10-27
category: case
tags: [templates, polyglot-toolchain]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

多语言项目常常需要为小任务临时准备编译器。这里用一个固定工具链工作区编译并运行 Go、Rust 和 Java 三个程序，再把同样的入口接到自己的代码流程。

三个调用入口均返回 go: GO_OK、rust: RUST_OK、java: JAVA_OK，以及 cleanup_verified: true。结果来自实际编译与执行，工作区里的本次临时源文件、二进制和 Go 缓存随后被移除。 

## 准备独立工作区

本例使用极速版、CLI `0.5.7`、Python client/server `0.4.0a6` 和模板的默认 Docker 配方。
先按[平台配置](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)
准备极速版沙箱 API Key、地域、连接地址、Docker、构建权限和镜像仓库。
应用的 `ABX_SERVER_TOKEN` 独立于平台认证；这个模板不需要模型 endpoint、模型 Key 或产品登录。

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh | ABX_VERSION=0.5.7 sh
export PATH="$HOME/.local/bin:$PATH"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple 'agent-sandbox-client==0.4.0a6'
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export ABX_HTTP_TIMEOUT=450
abx template launch Alibaba-Agent-Sandbox/awesome-templates//polyglot-toolchain --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
abx sandbox command list "$SANDBOX_ID"
```

## 提交任务，取回业务结果

```bash
abx run "$SANDBOX_ID" toolchain_smoke --json-args '{}'
```

三个调用入口均返回 go: GO_OK、rust: RUST_OK、java: JAVA_OK，以及 cleanup_verified: true。结果来自实际编译与执行，工作区里的本次临时源文件、二进制和 Go 缓存随后被移除。

版本入口实际读到了 Go 1.25.14、Rust/Cargo 1.90.0、Eclipse Temurin JDK 21.0.12.1。工具链来自固定校验和的官方归档；运行时不自动下载另一套 Go 工具链。

## 用 Python 或 HTTP 连接自己的程序

附件 [quickstart.py](./quickstart.py) 是实际执行的完整模板 SDK 示例。
保留以上环境和实例 ID，运行 `python quickstart.py`。它连接同一个实例，通过
`application_client` 调用业务方法，并关闭本机连接。文件型结果在脚本中下载到本机。
这是 CLI、Python、HTTP 中的一种替代方式，选择适合自己程序的入口即可。

HTTP 用户按[直接 HTTP 指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)
解析当前实例的 9000 端口，保留网关头、URL 路径与查询参数，再添加独立应用认证。
向上方命令对应的 `POST /commands/<命令名>` 发送 `--json-args` 中的直接 JSON 对象，
不增加 `args` 包装层。结果放在 `result` 内；具体字段和全部命令见
[模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/polyglot-toolchain/README.zh-CN.md)。

本例分别执行了三种方式，并在文件型结果的前后调用间删除自己上一次的输出，
分别取回新产物。自己的工作流可以使用新的输出名或新实例，避免旧文件影响判断。

## 接到自己的业务并二次开发

把自己的源码上传到独立项目目录，然后通过沙箱 process/exec 接口运行对应构建命令。toolchain_smoke 是固定的三语言预检任务，不接受任意项目参数；自己的工程需要自己声明依赖、构建命令和输出路径。需要保留二进制时在清理前下载，固定第三方依赖版本，并审阅项目自己的许可证。

该模板的业务处理不调用大模型；若应用需要模型推理，由上层应用另外配置自己的
授权服务，把这里取回的文本、文件或编译结果作为输入。修改模板依赖、字体、语言包
或编译器时，在自己的版本中固定它们，并重新运行实际业务流程。

## 导出与清理

先下载需要保留的文件，再执行：

```bash
abx kill "$SANDBOX_ID"
```

SDK 的 `close()` 只关闭连接，不删除云实例。1800 秒实例寿命与 450 秒客户端等待
分别控制不同阶段。可复用的预备模板和镜像按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)
仅删除自己的资源。本例结束后，所用沙箱、预备模板和本次镜像均已独立确认不存在。

## 在 OpenSandbox 中使用同一工作流

这个案例也可以在 OpenSandbox 中完成。先按[OpenSandbox 提供方指南](https://github.com/Alibaba-Agent-Sandbox/awesome-providers/blob/main/opensandbox/docs/README.md)准备服务地址、服务 API Key 和镜像仓库，然后在创建实例前选择平台：

```bash
export ABX_PROVIDER=opensandbox
export ABX_OPENSANDBOX_USE_SERVER_PROXY=true
```

接着执行上面的 launch、业务命令和 SDK 示例；后续终端与 Python 继续使用同一个平台和实例 ID。沙箱 API Key 与应用令牌分别配置，原有业务输入、返回结果和结束实例的方法相同。

这里使用 OpenSandbox1.1.1 的服务代理模式；CLI、完整 SDK 示例和直接 HTTP 都能完成文中的实际任务。代理模式要求客户端能访问服务地址。若部署环境改为直连模式，客户端还必须能访问提供方解析出的端点；更换配置后重新创建自己的实例，不复用另一平台的 ID。
