---
title: 把季度简报从 Markdown 交付为 Word 文档
summary: 用 Pandoc 和 LibreOffice 在临时工作区转换报告，取回真实 DOCX，并扩展到 HTML、演示文稿与 PDF。
date: 2026-10-27
category: case
tags: [templates, document-tools]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

季度简报往往从 Markdown 开始，交付时却需要 Word。这里把一份包含标题和收入金额的简报上传到独立工作区，用固定版本的转换程序生成 DOCX，再把可编辑文档交回本机。

下载的 DOCX 是真实 ZIP 文档，word/document.xml 中保留 Quarterly report 与 51.30。CLI、Python 和 HTTP 分别生成了新文件。 实际附件：[report.docx](./report.docx)。输入附件：[report-input.txt](./report-input.txt)。

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
abx template launch Alibaba-Agent-Sandbox/awesome-templates//document-tools --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
abx sandbox command list "$SANDBOX_ID"
```

## 提交任务，取回业务结果

```bash
printf '# Quarterly report\n\nRevenue: 51.30.\n' > report.md
abx upload "$SANDBOX_ID" ./report.md /home/user/app/report.md
abx run "$SANDBOX_ID" convert --json-args '{"input_path":"report.md","output_name":"report.docx","output_format":"docx"}'
abx download "$SANDBOX_ID" /home/user/app/report.docx ./report.docx
```

下载的 DOCX 是真实 ZIP 文档，word/document.xml 中保留 Quarterly report 与 51.30。CLI、Python 和 HTTP 分别生成了新文件。

转换入口还实际完成了 Markdown/HTML 到 TXT、PPTX 与 Writer PDF：检查了实际文本、压缩包中的幻灯片和 PDF 内容，原始输入保持原样。图片与任意原生选项不在此配置范围。

## 用 Python 或 HTTP 连接自己的程序

附件 [quickstart.py](./quickstart.py) 是实际执行的完整模板 SDK 示例。
保留以上环境和实例 ID，运行 `python quickstart.py`。它连接同一个实例，通过
`application_client` 调用业务方法，并关闭本机连接。文件型结果在脚本中下载到本机。
这是 CLI、Python、HTTP 中的一种替代方式，选择适合自己程序的入口即可。

HTTP 用户按[直接 HTTP 指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)
解析当前实例的 9000 端口，保留网关头、URL 路径与查询参数，再添加独立应用认证。
向上方命令对应的 `POST /commands/<命令名>` 发送 `--json-args` 中的直接 JSON 对象，
不增加 `args` 包装层。结果放在 `result` 内；具体字段和全部命令见
[模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/document-tools/README.zh-CN.md)。

本例分别执行了三种方式，并在文件型结果的前后调用间删除自己上一次的输出，
分别取回新产物。自己的工作流可以使用新的输出名或新实例，避免旧文件影响判断。

## 接到自己的业务并二次开发

需要增加公司样式时，从自己的模板副本固定参考文档、字体和转换配置开始。先保留本例的纯文本输入，逐步引入版式；用实际生成的 Office/PDF 文件确认排版。异步业务系统可以保存任务输入、返回路径和 sha256，再通过文件 API 导出自己的产物。

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
