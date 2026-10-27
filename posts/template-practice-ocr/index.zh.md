---
title: 把扫描图片变成可检索的英文文本
summary: 用 Tesseract 识别图片，导出 TXT 与 TSV，再把文字接入检索和结构化处理。
date: 2026-10-27
category: case
tags: [templates, ocr]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

扫描件进入检索系统之前，需要先从像素中提取文字。这里从模板附带的英文图片开始，取得正文和位置数据，再说明如何替换成自己的扫描文件。

下载的识别文本包含 SANDBOX、OCR、314159、ALPHA 和 BETA。CLI、完整 Python 程序和 HTTP 都从实际图片得到这些词句。 实际附件：[recognized.txt](./recognized.txt)。

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
abx template launch Alibaba-Agent-Sandbox/awesome-templates//ocr --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
abx sandbox command list "$SANDBOX_ID"
```

## 提交任务，取回业务结果

```bash
abx run "$SANDBOX_ID" ocr --json-args '{"image_path":"fixtures/sample.png"}'
abx download "$SANDBOX_ID" /home/user/app/recognized.txt ./recognized.txt
```

下载的识别文本包含 SANDBOX、OCR、314159、ALPHA 和 BETA。CLI、完整 Python 程序和 HTTP 都从实际图片得到这些词句。

固定 Tesseract 5.5.0、Pillow 11.3.0 和 eng 数据完成了额外随机数字图片识别；独立下载的 TXT/TSV 内容与识别结果一致，空白图片返回空文字。

## 用 Python 或 HTTP 连接自己的程序

附件 [quickstart.py](./quickstart.py) 是实际执行的完整模板 SDK 示例。
保留以上环境和实例 ID，运行 `python quickstart.py`。它连接同一个实例，通过
`application_client` 调用业务方法，并关闭本机连接。文件型结果在脚本中下载到本机。
这是 CLI、Python、HTTP 中的一种替代方式，选择适合自己程序的入口即可。

HTTP 用户按[直接 HTTP 指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)
解析当前实例的 9000 端口，保留网关头、URL 路径与查询参数，再添加独立应用认证。
向上方命令对应的 `POST /commands/<命令名>` 发送 `--json-args` 中的直接 JSON 对象，
不增加 `args` 包装层。结果放在 `result` 内；具体字段和全部命令见
[模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/ocr/README.zh-CN.md)。

本例分别执行了三种方式，并在文件型结果的前后调用间删除自己上一次的输出，
分别取回新产物。自己的工作流可以使用新的输出名或新实例，避免旧文件影响判断。

## 接到自己的业务并二次开发

上传自己的 scan.png 后，把 image_path 换成 scan.png。对正文可按段落建立检索索引；对 TSV 可按边界框和置信度筛选。当前只带英文 eng 数据，若要中文或其他语言，在自己的 Dockerfile 固定相应语言包，并用真实扫描件重新确认准确率。

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
