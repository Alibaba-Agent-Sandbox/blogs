---
title: 选择 Agent API Harness：统一业务接入，保留原生 Agent 能力
summary: 用同一组 HTTP 接口接入不同原生 Agent，理解 Gateway、Session 与 Sandbox 的关系，以及 Harness 选择、凭据配置和应用定制的边界。
date: 2026-11-17
category: tutorial
tags: [agents-api, harness, sandbox, http]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

快速入口：[Agent API 模板专题](https://registry.agent-sandbox.cn/topics/agents-api/) · [专题文章](https://www.agent-sandbox.cn/blog/topics/agents-api/) · [开发中模板源码](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/048db39f5a865b07343ede2a93393ceab7f2df31)

六个新托管模板仍在开发与验证中。本文说明共同接口和选择方法，不表示每个 Harness 已完成真实模型与云端验收。需要部署时，先核对相应模板的安装要求、凭据来源与支持范围；旧 CLI 0.5.10 不能直接执行新的 YAML v1 配方。

## 业务方为什么需要一个 Agent API

如果业务系统要让 Agent 修改代码、处理文件或连续完成任务，直接为每次请求创建 Sandbox，会让业务方承担实例地址发现、工作区维护和资源回收。托管 Agent API 将这些操作放到服务端：业务方保存一个 Gateway URL 和业务 Key，通过 HTTP 上传输入、创建 Session、提交后续任务并下载结果。

同一个 Session 使用独占 Sandbox。模型调用、原生 Agent 和工具循环在其中执行，后续任务可以继续使用原工作区。不同 Session 的工作区彼此独立；关闭会话计算与删除已保存的公开结果是两个操作。

部署者仍需准备 FC、Sandbox、镜像仓库、已有 PostgreSQL 及相应模型或原生 Agent 凭据。浏览专题和读取源码不会创建这些资源。

## 六个模板怎么选择

统一的是业务协议；选择 Harness 仍要看团队已有账号、模型服务和需要保留的原生行为。

| 模板 | 原生 Harness | 选择时检查什么 |
| --- | --- | --- |
| [agents-api-codex](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/048db39f5a865b07343ede2a93393ceab7f2df31/agents-api-codex) | Codex | Responses 模型接口、工具回合及原生 Session 继续方式 |
| [agents-api-qwen-code](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/048db39f5a865b07343ede2a93393ceab7f2df31/agents-api-qwen-code) | Qwen Code | 对应模型服务的 Chat Completions 工具调用与原生会话继续 |
| [agents-api-claude-code](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/048db39f5a865b07343ede2a93393ceab7f2df31/agents-api-claude-code) | Claude Code | Claude Code 支持的认证和模型入口，以及所需工具权限 |
| [agents-api-qoder](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/048db39f5a865b07343ede2a93393ceab7f2df31/agents-api-qoder) | Qoder | Qoder 原生认证与非交互执行要求，不能把模型 Key 当作 Qoder 登录凭据 |
| [agents-api-opencode](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/048db39f5a865b07343ede2a93393ceab7f2df31/agents-api-opencode) | OpenCode | 所选模型 Provider、原生配置及非交互运行方式 |
| [agents-api-deepseek-harness](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/048db39f5a865b07343ede2a93393ceab7f2df31/agents-api-deepseek-harness) | DeepSeek Harness | 原生 headless 模式、模型配置和实际可提供的事件粒度 |

上表链接指向开发源码。模板在 Registry 上架后，以详情页为配置入口；专题页会根据实际目录提供详情链接。普通 `codex`、`qoder` 等 Sandbox 模板保留独立用途，不自动具备托管 Gateway。

## 共同的 HTTP 接入方式

部署后，终端用 `curl`，Python 应用用 `httpx`，其他语言使用各自 HTTP 客户端。当前没有专用的 Gateway 客户端 SDK；Sandbox 管理 SDK 也不是这个业务客户端。

| 任务 | 接口 |
| --- | --- |
| 查看部署允许的模型 | `GET /v1/models` |
| 创建会话并提交初始任务 | `POST /v1/agents/sessions` |
| 向同一会话发送后续输入 | `POST /v1/agents/sessions/{id}/events` |
| 读取会话事件 | `GET /v1/agents/sessions/{id}/events` |
| 查询任务与下载产物 | 会话下的 `turns`、`items` 与 `artifacts` 接口 |
| 明确排队或查询提交结果 | `/v1/agent-sandbox/sessions/{id}/submissions` 扩展 |
| 释放计算、保留结果 | `POST /v1/agent-sandbox/sessions/{id}/close`，随后查询返回的 Operation |

创建会话时可携带初始 `input`；后续输入继续使用返回的 Session ID。为需要安全重试的提交设置 `Idempotency-Key`，重复使用时请求内容必须相同。HTTP 接收成功与任务完成不同，应读取提交状态、具体 Turn 和实际产物。

OpenCode v1 的 JSON 输出只在工具完成后提供记录，无法从真实工具开始时刻保证 `maxToolSeconds`；整轮 `maxRunSeconds`、取消与进程清理仍适用。DeepSeek 旧实践文章使用当时的兼容 Harness；这里的新模板使用官方 DSH，两者的结果不能互相替代。

统一协议不等于六种原生 Agent 提供完全相同的能力。当前托管范围不支持 active steering、外部 functions/MCP 或 subagents。任务运行中需要排队时使用显式 submissions 扩展；不要把被拒绝的 active input 当作已引导当前任务。事件缺失会显式提示，不能根据没有新事件推断执行已经停止。

## 与 OpenAI Agents API 的关系

本项目采用部分相似的会话、事件和文件资源结构，并增加明确的提交、计算关闭与清理操作。OpenAI 官方托管 Harness 与这里在 Sandbox 内运行整个原生 Agent 的拓扑不同。相似的 URL 不构成完整的协议等价或任意 OpenAI SDK 兼容保证。

接入前读取部署的 `GET /v1/agent-sandbox/capabilities` 及模板 API 说明。不能把底层 CLI 支持的 MCP、子 Agent 或其他原生功能，直接当成 Gateway 已经开放的功能。

## 怎样定制自己的应用

从最符合账号和原生工具需求的模板开始，修改对应 README 指明的模型或原生认证配置。业务文件、初始工具和默认说明放在模板业务代码或镜像中；Sandbox 模板资源与 FC 原生配置在 `template.yaml` 修改。凭据使用私有配置来源，不写入镜像、版本库或示例输出。

构建发布后，让客户端继续使用稳定 Gateway 地址。更新需要保留已有会话的 Worker 与工作区归属；不能为了切换 Harness 将正在运行的会话静默转交给另一种 Agent。具体升级、清理与保留策略以模板说明为准。

旧版真实 CSV 两轮任务见[单入口实践](https://www.agent-sandbox.cn/blog/managed-agents-one-endpoint/)。那篇文章注明了原始版本和固定源码，其结果不能替代六个新模板的逐项验证。
