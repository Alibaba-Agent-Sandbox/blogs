---
title: 把文件补丁接入工作流：在沙箱中新增、修改和移动文件
summary: 使用 apply-patch 模板执行原生补丁，通过 CLI、Python 或 HTTP 提交变更，检查真实退出码和文件内容，再扩展到自己的文件处理流程。
date: 2026-10-27
category: case
tags: [patch, files, automation, templates]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

流程已经生成了一份补丁，下一步是把它应用到工作区，并把变更后的文件交出去。
`apply-patch` 提供原生 Codex 补丁工具，支持新增、更新、移动和删除文件；执行补丁
本身不需要调用模型。

这里使用极速版、CLI `0.5.7`、Python client/server `0.4.0a6`，原生工具版本为
`codex-cli 0.162.1`。模板源码固定为 `50d7e38cd5837042acb756aad66d8f97050f11dd`。
本例实际下载的 [hello.txt](./hello.txt) 内容是 `Hello from a patch`。

## 准备平台，启动文件工作区

按[费用文件案例](/blog/template-practice-python-hello/#安装工具准备运行平台)
安装 CLI、准备 Docker，并配置极速版、ACR 和构建账号权限。然后设置独立应用令牌：

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SERVER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export ABX_HTTP_TIMEOUT=450
abx template launch Alibaba-Agent-Sandbox/awesome-templates//apply-patch@50d7e38cd5837042acb756aad66d8f97050f11dd --sandbox-timeout 1800 --yes
export SANDBOX_ID='<启动返回的沙箱 ID>'
abx sandbox command list "$SANDBOX_ID"
```

这里的登录配置只有沙箱平台凭据和应用令牌。补丁工具不需要模型账号、模型 endpoint
或模型 API Key，也没有需要切换的模型；使用它不要求在本机安装 Rust 或 Codex。

## 提交补丁，再检查文件

```bash
abx run "$SANDBOX_ID" apply_patch --json-args '{"patch_text":"*** Begin Patch\n*** Add File: hello.txt\n+Hello from a patch\n*** End Patch\n"}'
abx download "$SANDBOX_ID" /home/user/app/hello.txt ./hello.txt
```

结果对象包含 `stdout`、`stderr` 和 `exit_code`。先确认 `exit_code == 0`，再读取
下载文件。HTTP200 只表示命令调用完成：格式错误的补丁仍可能以非零 `exit_code`
返回，不能仅凭 HTTP 状态把任务标记为成功。

默认目录为 `/home/user/app`。想操作已有项目，可先上传文件，在 `cwd` 中选择已有
工作目录，再让补丁中的文件名相对它定位。

## 更新和移动文件

原生工具的实际能力包括 add、update、move、delete，模板的 `apply_patch_smoke`
会在自有临时目录中完成这些操作并核对字节，不改调用方项目。可以先调用：

```bash
abx run "$SANDBOX_ID" apply_patch_version
abx run "$SANDBOX_ID" apply_patch_smoke
```

版本返回 `codex-cli 0.162.1`；完整临时文件操作返回 `APPLY_PATCH_OK`。
在自己的项目里，接下来可以使用这种原生补丁形式更新并重命名文件：

```text
*** Begin Patch
*** Update File: hello.txt
*** Move to: greeting.txt
@@
-Hello from a patch
+Hello from the workflow
*** End Patch
```

调用方应保留提交的补丁、退出码和下载后的结果，便于展示差异或人工确认。
补丁不是事务；一个操作失败时，工作区内可能已经发生部分变更，应检查实际文件。

## 用 Python 或 HTTP 连接现有流程

安装 `agent-sandbox-client==0.4.0a6`，保存完整的
[quickstart.py](./quickstart.py)，保留 `SANDBOX_ID`、provider 和应用令牌后运行：

```bash
python quickstart.py
```

程序连接同一实例，调用 `apply_patch`，再通过文件 API 下载 `hello.txt`。
CLI、SDK、HTTP 是同一任务的替代入口；创建示例文件后，换入口运行整段示例前，先
清理自己的旧输出，或在新实例中执行。

HTTP 对应 `POST /commands/apply_patch`，JSON 请求体直接传参数：

```json
{"patch_text":"*** Begin Patch\n*** Add File: hello.txt\n+Hello from a patch\n*** End Patch\n"}
```

按[完整 HTTP 指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/50d7e38cd5837042acb756aad66d8f97050f11dd/docs/using-templates.zh-CN.md#http-post)
保留 provider 解析出的地址、路径、查询和网关头，再添加独立应用认证。参数缺失或
多传返回400，未知命令返回404；原生解析失败则查看结果中的退出码。

## 扩展成自己的文件变更步骤

可以让上游系统生成补丁，由这个模板负责执行，再由下游程序下载文件、运行用例和
展示差异。补丁文本通过原生 stdin 传入，不交给 shell 解释；它既可以来自模型，也
可以来自普通规则程序。

单次补丁最多256KiB，原生进程有30秒期限。路径必须相对工作目录，绝对路径、`..`、
反斜杠和已有符号链接会在执行前被拒绝。这些检查适合受控工作区，不替代操作系统
隔离，也不应与同一用户的并发重命名或符号链接操作竞争。

需要新增业务参数时，可以 fork 模板，在自己的 `commands.py` 中把业务输入转换成
补丁，再复用原生调用。保留上游许可证和归属说明，更新模板版本，并核对新增方法的
参数、返回值和实际文件效果。

## 下载成果，释放实例

```bash
abx kill "$SANDBOX_ID"
```

先取回需要保留的文件，再删除实例。准备的镜像和模板可能供复用；不再需要时，按
启动回执的准确引用清理本次资源。本文实际结果对应极速版；其他平台的配置入口见
[模板页面](https://registry.agent-sandbox.cn/templates/apply-patch/)。
