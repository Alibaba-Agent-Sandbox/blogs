---
title: 用原版 Devin CLI 完成一次工程文件交付
summary: 准备账号、提交工程任务、导出文件并独立运行的实践草稿；实际账号产物尚未补齐。
date: 2026-10-27
category: case
tags: [templates, devin, coding]
authors: [Alibaba-Agent-Sandbox]
draft: true
---

目标是把工程修改交付为代码文件和说明，从一个可以独立运行的小程序建立完整路径，再扩展到自己的项目。本篇为未发布草稿：目前缺少对应厂商账号的真实业务产物，不能把下面的目标结果当作已经完成的效果。

## 准备账号与应用

需要在可信机器执行原版 devin auth login 得到的 credentials.toml，并且账号角色允许 Enterprise CLI。没有通用 DEVIN_API_KEY 替代品。

先按[平台指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)安装 CLI0.5.7/client0.4.0a6，配置沙箱 API Key、连接地址、地域、Docker、构建权限与镜像仓库。账号凭据与独立应用 token 另行设置。以下来自当前模板的完整 CLI 路径：

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export DEVIN_CREDENTIALS_FILE='/home/user/devin-private/credentials.toml'
abx template launch Alibaba-Agent-Sandbox/awesome-templates//devin --sandbox-timeout 1800 --yes
export SANDBOX_ID='<sandbox-id-returned-by-launch>'
abx sandbox command list "$SANDBOX_ID"
```

```bash
abx exec "$SANDBOX_ID" -- mkdir -p /home/user/devin-private
abx exec "$SANDBOX_ID" -- chmod 700 /home/user/devin-private
abx upload "$SANDBOX_ID" "<local-credentials.toml>" /home/user/devin-private/credentials.toml
abx exec "$SANDBOX_ID" -- chmod 600 /home/user/devin-private/credentials.toml
```

```bash
ABX_HTTP_TIMEOUT=420 abx run "$SANDBOX_ID" devin --json-args '{"prompt":"Create generated_hello.py that prints exactly Hello from the sandbox, and GENERATED_REPORT.md explaining the program. Preserve unrelated existing files.","allow_unsafe_tools":true,"cwd":"/home/user/app","command_timeout":300}'
```

devin 参数中的 model 使用账号实际可用的模型 ID，空字符串保留原生默认。原生账号文件与自有兼容模型 Key 是两类凭据。

Devin 的本机账号文件需要上传到实例内 WORKSPACE 之外的私有目录，并设置目录700/文件600；本机路径不会自动传入远端。其他模板只使用各自声明的账号变量，不借用其他厂商或平台凭据。

## 通过 SDK 或 HTTP 提交同一个任务

保留前述实例 ID 与环境，用 [quickstart.py](./quickstart.py) 作为 SDK 接入草稿。它来自模板示例，当前尚未在该账号上完成业务运行；取得账号后应对同一实例选择 CLI、SDK 或 HTTP 中的一种方式提交，避免无意重复执行。

HTTP 解析9000端口时保留网关头、路径、查询和独立应用认证，使用 POST /commands/devin，发送直接参数对象，不加 args 包装：

```json
{
  "prompt": "Create generated_hello.py that prints exactly Hello from the sandbox, and GENERATED_REPORT.md explaining the program. Preserve unrelated existing files.",
  "allow_unsafe_tools": true,
  "cwd": "/home/user/app",
  "command_timeout": 300
}

```

检查实际命令结果、生成的 Python 文件与报告，下载后由调用方独立运行；需要的目标输出是 Hello from the sandbox。本文没有尚未取得的生成程序、截图或报告可供展示。

## 扩展为自己的业务工程

上传项目副本和锁文件，用 cwd 选择 WORKSPACE 内已有目录。描述具体修改、要保留的原始用例与交付文件，例如读取报销 CSV 并输出汇总。把源代码、报告与独立运行结果作为交付内容。涉及原生编辑/执行工具时，按模板提供的显式权限参数选择自己拥有的一次性沙箱。

## 保存文件并结束

先取回所需产物，然后执行 abx kill 删除本次实例；close 仅释放连接。按[清理指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#导出文件与清理)处理自己的预备模板和镜像。[完整模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/devin/README.zh-CN.md)保留账号、参数与权限边界。该模板当前仍保留 Beta，本篇不会作为通过凭据或业务流程的证据。
