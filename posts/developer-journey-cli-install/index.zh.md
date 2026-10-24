---
title: 从官网开始安装 abx，再完整跑一次沙箱生命周期
summary: 从官网安装入口出发，验证下载校验、CLI 版本、真实创建与执行，并用精确 ID 确认资源已删除。附可独立运行的复现实验。
date: 2026-10-24
category: case
tags: [cli, sandbox, getting-started]
authors: [Alibaba-Agent-Sandbox]
cover: ./cover.svg
draft: false
---

安装成功，不只是终端里出现一个版本号。这篇案例从 [Agent Sandbox 官网](/start/) 的安装入口开始，继续完成真实沙箱的创建、信息查询、命令执行、列表查询和删除。最终要回答两个问题：工具是否真的能连接你的提供方，以及实验结束后资源是否真的不存在了。

这是五个开发者实践的第一篇。测试环境为 Linux x86_64，后端为 Alibaba Cloud Express。其他系统的安装入口虽然存在，本文没有把它们记作实测通过。

## 安装 CLI，并固定实验版本

官网提供独立二进制和 npm 两条入口。独立二进制的基础 CLI 操作不要求先安装 Python；如果使用 npm，需要满足包声明的 Node.js 版本要求（Node.js 20 或更新版本）。

为便于复现，把安装脚本先保存下来，再明确选择实验版本和安装目录：

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh -o install-abx.sh
ABX_VERSION=0.4.12 ABX_INSTALL_DIR="$PWD/bin" sh install-abx.sh
export PATH="$PWD/bin:$PATH"
abx --version
abx --help
```

安装器会下载对应平台的发行文件并校验 checksum。不要绕过校验，也不要把“下载到一个同名文件”当成版本核验。若选择 npm 路线，可以使用独立目录，避免覆盖已有安装：

```bash
npm install --global --prefix "$PWD/abx-npm" @agent-sandbox/cli@0.4.12
"$PWD/abx-npm/bin/abx" --version
```

网站更新后，还在新目录中不设置 `ABX_VERSION` 运行了官网默认安装器：它从官网镜像下载 `0.4.12`，校验与版本检查同样通过。

两条安装路线应分别核对版本。切换后可用 `type -P abx` 确认当前 shell 实际调用哪个文件。

本轮最终使用公开发行的 `0.4.12` 完成两条安装路线：独立二进制通过发行校验和检查，npm 包通过 registry integrity 检查；隔离目录中的 npm 全局安装也报告相同版本。[安装证据](./proof/installation.json)保留版本、制品摘要和发行工作流结果。

## 配置自己的沙箱账户

按照官网的提供方配置指南，使用你自己的同一账户、地域和接入地址。下面的变量是占位符，不是可用凭据：

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SANDBOX_API_KEY='<YOUR_SANDBOX_API_KEY>'
export ABX_SANDBOX_BASE_URL='<YOUR_SANDBOX_API_URL>'
export ABX_SANDBOX_DOMAIN='<YOUR_SANDBOX_DOMAIN>'
```

沙箱 API 凭据与模型 API 凭据是两回事。本篇只验证沙箱生命周期，不需要 LLM API key。若电脑上还配置了其他提供方的 `E2B_*` 变量，请先核对它们是否会影响本次账户选择；不要把不同账户的 key、base URL 和 domain 混用。

## 手动走完一次生命周期

使用 `--detach` 让创建命令返回本次 sandbox ID，而不是直接进入交互终端：

```bash
SID=$(abx create base --detach --timeout 300)
abx info "$SID" --format json
abx exec "$SID" -- echo hello
abx list
abx kill "$SID"
abx info "$SID"
```

执行结果应包含 `hello`。最后一次 `info` 应报告该精确 ID 不存在，并以非零状态退出；这是预期的清理结果，不是脚本中的成功业务调用。

这里有两个容易混淆的细节：

- 标准 `info` 使用 `--format json`。扩展命令的全局 `--json` 并不意味着所有标准命令都采用同一参数接口；以各自 `--help` 为准。
- 列表可能有短暂可见性延迟。创建后能按精确 ID 查询并执行命令，比立即在列表中找到它更直接；但列表功能本身仍应单独有界重试验证。

手动步骤便于理解。正式实验使用下面的程序，把执行与清理放进 `try/finally`，失败也保留证据。

## 运行完整复现实验

附件 [run.py](./lab/run.py) 和 [support.py](./lab/support.py) 只使用 Python 标准库来驱动已安装的 CLI，不需要安装 Python SDK。可以从博客仓库取得完整目录：

```bash
git clone --depth 1 https://github.com/Alibaba-Agent-Sandbox/blogs.git agent-sandbox-cases
cd agent-sandbox-cases/posts/developer-journey-cli-install
python3 lab/run.py
```

程序依次检查：

| 检查 | 通过依据 |
| --- | --- |
| 创建 | 退出码为零，取得单个 sandbox ID |
| 信息 | 精确 ID 的 JSON 查询成功 |
| 执行 | 远端输出严格等于 `hello` |
| 列表 | 在有限次数查询内包含本次 ID |
| 删除 | `kill` 成功，再按相同 ID 查询确认 NotFound |

成功时会输出 `status: PASS` 和 `cleanup_verified: true`。完整命令、退出码和输出写入 `lab/evidence/result.json`；用于故障恢复的真实 ID 放在 `lab/.private/`。后者不应提交或公开。

程序不会因为“列表里没看到”就认定资源已删除，也不会把一次删除请求等同于清理完成。若进程被强制终止，无法保证 `finally` 执行；应使用自己保存的 ID 做恢复清理。

## 本次验证的边界

这篇验证的是 Linux 上的安装与一个真实 Express 沙箱生命周期。它没有执行所有提供方、所有平台，也没有修改团队、配额、卷或 API key 等管理资源。

最初实验中，曾把列表延迟和 NotFound 文案识别错误归为失败；这些是测试程序的判断问题，原始失败记录保留，修正后按精确 ID 重跑。最终 `0.4.12` 复验耗时约 9.5 秒，生命周期与精确清理均通过。[结果附件](./proof/result.json)保留命令、退出码和关键业务输出，省略账户元数据及列表中的其他资源。附件源码与最终执行的文件字节一致。

接下来可以阅读 [用 Python SDK 自建 Qwen Code 沙箱](/blog/developer-journey-qwen-python/)，把同一个应用命令通过 SDK、CLI 和 HTTP POST 三条路径调用起来。

附件的[源码 SHA256 清单](./lab/source-sha256.json)用于确认复现文件的字节。它与运行结果一起使用，单有哈希清单并不证明实验通过。
