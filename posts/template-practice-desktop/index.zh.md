---
title: 把文件处理与原生桌面操作放在同一个实例
summary: 原生提供方实例、SDK、业务扩展和资源清理的实践草稿；实际业务条件仍未满足。
date: 2026-10-27
category: case
tags: [templates, desktop, python]
authors: [Alibaba-Agent-Sandbox]
draft: true
---

目标是用平台文件接口准备数据，再通过原版 Desktop SDK 在同一个实例完成截图与键鼠操作。本文为未发布草稿：缺少有权使用 E2B desktop 的账号凭据，原生桌面业务尚未运行。暂无真实业务输出，不把预期效果当作已完成的效果。

## 平台和实例准备

使用此模板声明的原生提供方，不能把其他提供方的模板 ID 或 API Key 当作同一个资源。安装 CLI0.5.7 与 Python client0.4.0a6，并保留 Node.js22+ 和对应提供方插件。模型 API Key、model 或 LLM endpoint 不参与下面的基础解释器/桌面操作。

```bash
export ABX_E2B_API_KEY='<e2b-api-key>'
```

```bash
abx provider install Alibaba-Agent-Sandbox/awesome-providers//e2b --allow-unpinned --yes
abx provider doctor e2b
abx --provider e2b template launch desktop --sandbox-timeout 180 --yes
export ABX_SANDBOX_ID="<returned-sandbox-id>"
abx --provider e2b exec "$ABX_SANDBOX_ID" -- python3 -c 'print(6*7)'
abx --provider e2b kill "$ABX_SANDBOX_ID" -y
```

## 用 SDK 操作同一个实例

[quickstart.py](./quickstart.py) 是当前模板的 SDK 示例草稿，演示进程返回42与文件写入、读取、删除。提供方的 kill 删除实例，close 仅关闭连接。该原生镜像没有项目的 /commands/* 应用服务器。

桌面截图与输入需要按[原版 Desktop SDK](https://github.com/e2b-dev/desktop/tree/9fe5f55fabe3bd9f0277661a830e1d228b463b44)连接同一个实例。当前缺少账号，原生截图、输入和同实例接入尚未完成，不提供假定已经可用的示例截图。可以先准备自己的网页表单与输入文件；取得账号后补齐原生截图与实际表单结果，再发布完整案例。极速版 E2B 兼容 API Key 不能由工具自行认定可用于这个 E2B 账号模板。

## 二次开发与保存结果

把自己的输入副本上传到实例，保留明确的输出路径与需要保存的文件。解释器保留原生上下文与错误语义；桌面业务保留真实截图与实际界面结果。完成后先取回产物，再删除自己创建的实例。镜像和模板标记仍由对应提供方拥有，不做跨提供方 ID 转换。[完整模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/managed/desktop/README.zh-CN.md)。本篇仍为草稿，模板仍保留 Beta。
