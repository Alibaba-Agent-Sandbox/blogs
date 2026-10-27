---
title: 用原生 OpenSandbox 上下文处理一份报销数据
summary: 原生提供方实例、SDK、业务扩展和资源清理的实践草稿；实际业务条件仍未满足。
date: 2026-10-27
category: case
tags: [templates, opensandbox-code-interpreter, python]
authors: [Alibaba-Agent-Sandbox]
draft: true
---

目标是在持久 Python 上下文中读入开销数据、计算汇总并导出图表。本文为未发布草稿：原生 SDK 已按锁文件安装；原生镜像实际拉取触发本机磁盘下限，尚未创建原生解释器实例。暂无真实业务输出，不把预期效果当作已完成的效果。

## 平台和实例准备

使用此模板声明的原生提供方，不能把其他提供方的模板 ID 或 API Key 当作同一个资源。安装 CLI0.5.7 与 Python client0.4.0a6，并保留 Node.js22+ 和对应提供方插件。模型 API Key、model 或 LLM endpoint 不参与下面的基础解释器/桌面操作。

```bash
export ABX_OPENSANDBOX_BASE_URL='http://127.0.0.1:8080'
export ABX_OPENSANDBOX_API_KEY='<server-api-key>'
```

```bash
abx provider install Alibaba-Agent-Sandbox/awesome-providers//opensandbox --allow-unpinned --yes
abx provider doctor opensandbox
abx --provider opensandbox template launch opensandbox-code-interpreter --sandbox-timeout 180 --yes
export ABX_SANDBOX_ID="<returned-sandbox-id>"
abx --provider opensandbox exec "$ABX_SANDBOX_ID" -- python3 -c 'print(6*7)'
abx --provider opensandbox kill "$ABX_SANDBOX_ID" -y
```

```bash
python3 -m pip install 'uv==0.9.5'
git clone https://github.com/opensandbox-group/OpenSandbox.git opensandbox-sdk
git -C opensandbox-sdk checkout 30348cbdfe4b9cfd49e0963617aed357a8f1ac4c
uv sync --project opensandbox-sdk/sdks/code-interpreter/python --frozen --no-dev --python 3.12
uv pip install --python opensandbox-sdk/sdks/code-interpreter/python/.venv/bin/python 'agent-sandbox-client==0.4.0a6'
```

## 用 SDK 操作同一个实例

[quickstart.py](./quickstart.py) 是当前模板的 SDK 示例草稿，演示进程返回42与文件写入、读取、删除。提供方的 kill 删除实例，close 仅关闭连接。该原生镜像没有项目的 /commands/* 应用服务器。

[native_example.py](./native_example.py) 使用原版解释器 SDK 连接同一个 Agent Sandbox 实例。目标是先保存 value=37，再在相同上下文计算 value+5 得到42；随后可以读入报销 CSV，保存汇总文件与图表，再用文件接口取回。通用 ProviderSandbox.run_code 在这个提供方上仍明确返回不支持，应使用原版 interpreter.codes。当前尚无该原生镜像的实际执行、错误、隔离或图表产物可以展示。

服务端需有足够磁盘拉取和解包原生镜像；本机容量不足时使用容量更大的 Docker 主机或已配置的远程 OpenSandbox。不要用缩减后的不同镜像冒充目录中的原生镜像。

## 二次开发与保存结果

把自己的输入副本上传到实例，保留明确的输出路径与需要保存的文件。解释器保留原生上下文与错误语义；桌面业务保留真实截图与实际界面结果。完成后先取回产物，再删除自己创建的实例。镜像和模板标记仍由对应提供方拥有，不做跨提供方 ID 转换。[完整模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/managed/opensandbox-code-interpreter/README.zh-CN.md)。本篇仍为草稿，模板仍保留 Beta。
