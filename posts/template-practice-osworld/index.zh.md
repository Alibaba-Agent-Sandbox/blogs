---
title: 让原生桌面完成一次报销表单填写
summary: 用真实桌面、输入事件、截图与原生任务配置完成表单的实践草稿；完整结果尚未通过。
date: 2026-10-27
category: case
tags: [templates, osworld, desktop]
authors: [Alibaba-Agent-Sandbox]
draft: true
---

目标是在浏览器里填写月度开销51.30并保存结果，通过真实鼠标、键盘、截图与原生状态完成业务流程。本篇为未发布草稿：当前仍有可访问性状态和原生外部操作检查失败，暂无成功结果图，不将界面能打开视为流程已经可用。

## 准备应用与表单

按[平台配置](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/docs/using-templates.zh-CN.md#安装)安装 CLI0.5.7/client0.4.0a6，配置极速版 API Key、连接地址、地域、Docker 与镜像仓库。导出独立 ABX_SERVER_TOKEN 后启动 osworld 模板。它是 Linux 浏览器切片，没有内置模型账号或其他桌面平台能力。

[expense.html](./expense.html) 与 [task.json](./task.json) 是实际使用过的输入文件，不是成功业务产物。把它们上传到本次实例的 /home/user/app/owned-desktop-expense.html 与 /home/user/app/owned-desktop-expense.json，保留 JSON 中的实际对应路径。

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
abx template launch Alibaba-Agent-Sandbox/awesome-templates//osworld --sandbox-timeout 1800 --yes
export SANDBOX_ID='<launch 返回的沙箱 ID>'
abx upload "$SANDBOX_ID" ./expense.html /home/user/app/owned-desktop-expense.html
abx upload "$SANDBOX_ID" ./task.json /home/user/app/owned-desktop-expense.json
abx run "$SANDBOX_ID" desktop_start --json-args '{}'
abx run "$SANDBOX_ID" a11y_tree --json-args '{}'
abx run "$SANDBOX_ID" run_task_config --json-args '{"task_path":"/home/user/app/owned-desktop-expense.json"}'
abx run "$SANDBOX_ID" evaluate --json-args '{"task_path":"/home/user/app/owned-desktop-expense.json"}'
```

## 填写与保存的业务路径

读取 run_task_config 返回的实际 browser_geometry；屏幕和网页视口不应被假定相等。通过 click 聚焦输入框、type 输入51.30、hotkey 修改选中内容，再 click 保存。目标结果为界面显示 Completed 51.30，原生 evaluate 得分从0变为1，并且实际可访问性树包含保存后的内容。当前这些完整条件尚未一起通过，本文不会展示不存在的成功截图。

[quickstart.py](./quickstart.py) 来自模板 SDK 示例，演示同实例启动、读取可访问性 XML 与停止的接入方式；它不代表本篇表单已经完成。HTTP 使用9000端口的命名命令，保留网关和应用认证，参数与模板说明一致。

## 二次开发与结束

可以替换为自己拥有的网页、输入数据和支持范围内的任务配置，保留实际界面结果、原生状态与输出文件。[模板说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/main/osworld/README.zh-CN.md)列出支持的任务配置、评分与命令参数，不把这个切片当作完整 OSWorld 基准或 Office 环境。

先保存需要的文件，执行 desktop_stop 后独立确认停止，再用 abx kill 删除本次实例。该模板继续保留 Beta；完整界面业务完成后再补充实际结果与发布本文。
