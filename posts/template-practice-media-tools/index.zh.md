---
title: 把上传的 WAV 转成可下载的无损 FLAC
summary: 使用固定 FFmpeg 进行音频探测与转码，导出 FLAC，再接入自己的媒体处理流程。
date: 2026-10-27
category: case
tags: [templates, media-tools]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

录音处理可以先完成格式统一，再交给后续业务。这里准备一秒单声道 WAV，上传后调用 FFmpeg 转为 FLAC，下载到本机解码，确认音频内容完整。

实际 FLAC 下载后解码为 16000 个单声道、16 位零值采样，共 32000 字节；这是文档中一秒静音输入的精确结果。三个调用入口生成的 FLAC 字节一致。 实际附件：[sample.flac](./sample.flac)。输入附件：[sample.wav](./sample.wav)。

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
abx template launch Alibaba-Agent-Sandbox/awesome-templates//media-tools --sandbox-timeout 1800 --yes
export SANDBOX_ID='<返回的沙箱 ID>'
abx sandbox command list "$SANDBOX_ID"
```

## 提交任务，取回业务结果

先下载 [make_input.py](./make_input.py)，它是模板文档中实际运行过的 WAV 输入生成程序。

```bash
python make_input.py
abx upload "$SANDBOX_ID" ./sample.wav /home/user/app/sample.wav
abx run "$SANDBOX_ID" transcode --json-args '{"input_path":"sample.wav","output_name":"sample.flac","preset":"flac","max_seconds":5,"command_timeout":60}'
abx download "$SANDBOX_ID" /home/user/app/sample.flac ./sample.flac
```

实际 FLAC 下载后解码为 16000 个单声道、16 位零值采样，共 32000 字节；这是文档中一秒静音输入的精确结果。三个调用入口生成的 FLAC 字节一致。

原生能力还处理了独立生成的随机 PCM，转换后 WAV 的声道、采样率、帧数和 PCM 与输入一致；固定 FFmpeg 的 CPU H.264 视频入口和原生 argv 入口也已运行。

## 用 Python 或 HTTP 连接自己的程序

附件 [quickstart.py](./quickstart.py) 是实际执行的完整模板 SDK 示例。
保留以上环境和实例 ID，运行 `python quickstart.py`。它连接同一个实例，通过
`application_client` 调用业务方法，并关闭本机连接。文件型结果在脚本中下载到本机。
这是 CLI、Python、HTTP 中的一种替代方式，选择适合自己程序的入口即可。

HTTP 用户按[直接 HTTP 指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#http-post)
解析当前实例的 9000 端口，保留网关头、URL 路径与查询参数，再添加独立应用认证。
向上方命令对应的 `POST /commands/<命令名>` 发送 `--json-args` 中的直接 JSON 对象，
不增加 `args` 包装层。结果放在 `result` 内；具体字段和全部命令见
[模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/media-tools/README.zh-CN.md)。

本例分别执行了三种方式，并在文件型结果的前后调用间删除自己上一次的输出，
分别取回新产物。自己的工作流可以使用新的输出名或新实例，避免旧文件影响判断。

## 接到自己的业务并二次开发

可以把 media_probe 返回的流信息接到上传检查，再按业务选择 WAV、FLAC 或 MP4/H.264 输出。优先使用带明确输入输出的转码入口；需要受支持的原生 argv 时参考 transcode_args 的类型和参数限制。此配置只处理上传的工作区文件，不能把网络 URL 当作输入。

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
