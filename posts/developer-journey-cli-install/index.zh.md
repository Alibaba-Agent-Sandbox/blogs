---
title: 用 abx 开一个临时云端开发环境
summary: 安装命令行工具，创建一个临时沙箱，在里面运行命令、查看环境，用完后释放资源。适合第一次上手 Agent Sandbox。
date: 2026-10-24
category: case
tags: [cli, sandbox, getting-started]
authors: [Alibaba-Agent-Sandbox]
cover: ./cover.svg
draft: false
---

想试运行一段代码，又不想把依赖装进日常使用的电脑，可以先开一个临时云端环境。任务结束后删除环境，下次需要时再创建。

这篇从安装 `abx` 开始，创建一个 `base` 沙箱，运行第一条命令，再介绍查看和释放这个环境的方法。后面的 [Qwen Code 案例](/blog/developer-journey-qwen-python/)和 [Python 模板案例](/blog/developer-journey-registry-template/)都会用到这些操作。

本文使用 Linux、Alibaba Cloud Express 和 `abx 0.5.6`。开始前需要有自己的沙箱账户；账户配置入口见[官网上手指南](/start/)。

## 把 CLI 装到自己的工作目录

独立二进制适合只想先用 CLI 的情况，不需要预先安装 Python。下面把工具放到当前目录的 `bin` 中：

```bash
curl -fsSL https://www.agent-sandbox.cn/install.sh -o install-abx.sh
ABX_VERSION=0.5.6 ABX_INSTALL_DIR="$PWD/bin" sh install-abx.sh
export PATH="$PWD/bin:$PATH"
abx --version
```

安装器会下载适合当前平台的文件并校验下载内容。这里固定版本，方便按文章操作；安装完成后应看到 `abx, version 0.5.6`。

如果你平时使用 Node.js，也可以选 npm 路线，要求 Node.js 20 或更新版本：

```bash
npm install --global --prefix "$PWD/abx-npm" @agent-sandbox/cli@0.5.6 --registry=https://registry.npmjs.org
export PATH="$PWD/abx-npm/bin:$PATH"
abx --version
```

两种方式选一种即可。如果电脑里已经有另一个 `abx`，用 `type -P abx` 查看当前 shell 使用的是哪个文件。

## 连接沙箱账户

将提供方和连接信息放进当前终端的环境变量。请把占位符换成自己账户的配置：

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SANDBOX_API_KEY='<YOUR_SANDBOX_API_KEY>'
export ABX_SANDBOX_BASE_URL='<YOUR_SANDBOX_API_URL>'
export ABX_SANDBOX_DOMAIN='<YOUR_SANDBOX_DOMAIN>'
```

API key、接入地址和域名应来自同一账户配置。若另一套 E2B 配置也在当前 shell 中，先确认它不会影响此次连接。本篇只运行沙箱，不调用模型，因此不需要 LLM API key。

## 创建第一个环境

```bash
SID=$(abx create base --detach --timeout 300)
```

`base` 是创建时使用的模板。`--detach` 让命令返回沙箱 ID，方便后续继续操作；`--timeout 300` 给这个临时环境设置 300 秒的生命周期。

把 ID 保存在 `SID` 变量后，就可以在同一个沙箱里执行命令：

```bash
abx exec "$SID" -- echo hello
```

终端会输出：

```text
hello
```

这里 `--` 后面的内容由沙箱执行。以后需要运行自己的程序时，可以沿用这个命令结构，把 `echo hello` 换成目标命令。

## 查看环境，也把它接进脚本

当终端里同时开着几个任务时，可以用列表查找沙箱；已经知道 ID 时，直接查它的信息更方便：

```bash
abx list
abx info "$SID" --format json
```

JSON 信息包含沙箱状态、使用的模板、资源配置和生命周期，适合由脚本读取。标准 `info` 的参数是 `--format json`；不同命令的输出选项可以通过各自的 `--help` 查看。

新建资源可能稍后才出现在列表中。刚创建时若列表还没显示，先用返回的 ID 查询，不必马上再创建一个。

## 用完就释放

临时任务结束后，主动删除沙箱：

```bash
abx kill "$SID"
abx info "$SID"
```

删除后的 `info` 会提示资源不存在，并返回非零退出码。对于刚刚删除的这个 ID，这是正常结果。

如果想把这套过程放进自动化任务，可以参考附件 [run.py](./lab/run.py) 和 [support.py](./lab/support.py)。它们把创建、执行和清理串在一起，正常结束或遇到普通异常时都会尝试释放本次创建的环境：

```bash
git clone --depth 1 https://github.com/Alibaba-Agent-Sandbox/blogs.git agent-sandbox-cases
cd agent-sandbox-cases/posts/developer-journey-cli-install
python3 lab/run.py
```

这个脚本会自己创建并删除另一个沙箱，不会接管前面手动创建的 `SID`。若进程被强制终止，保留的资源 ID 可用于手动清理。

现在已经有了一个可从终端管理的临时环境。接下来可以给它装入自己的程序：例如[运行 Qwen Code 并提供自定义接口](/blog/developer-journey-qwen-python/)，或者直接[从 Registry 选择 Python 模板](/blog/developer-journey-registry-template/)。
