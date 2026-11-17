---
title: Choosing an Agent API Harness with a shared business interface
summary: Understand the shared HTTP interface, the relationship between Gateway, Session and Sandbox, and the native authentication and customization boundaries of each Harness.
date: 2026-11-17
category: tutorial
tags: [agents-api, harness, sandbox, http]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

Quick links: [Agent API template collection](https://registry.agent-sandbox.cn/en/topics/agents-api/) · [Topic guides](https://www.agent-sandbox.cn/en/blog/topics/agents-api/) · [Development template source](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/feat/agentsapi-harness-20261117)

The six new hosted templates remain under development and validation. This article explains their shared interface and selection criteria; it does not establish complete real-model or cloud acceptance for every Harness. Read the selected template's installation requirements, credential sources and supported scope before deployment. Released CLI 0.5.10 cannot execute the new YAML v1 recipes.

## Why give a business application one Agent API?

An application that asks an Agent to modify code, process files or continue a task otherwise has to discover Sandbox addresses, maintain workspaces and reclaim instances itself. A hosted Agent API moves that work to the server. Clients keep one Gateway URL and business key, then upload inputs, create a Session, submit follow-up tasks and download results over HTTP.

Each Session owns a Sandbox. Model calls, the native Agent and its tool loop run inside it; later tasks can reuse the workspace. Sessions have independent workspaces. Releasing session compute and deleting saved public results are separate operations.

The deployer still prepares FC, Sandbox, image storage, an existing PostgreSQL database and the required model or native Agent credentials. Browsing the collection and source creates none of those resources.

## Choose a template

The business protocol is shared. Choose a Harness according to your existing accounts, model service and required native behavior.

| Template | Native Harness | Check before choosing |
| --- | --- | --- |
| [agents-api-codex](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/feat/agentsapi-harness-20261117/agents-api-codex) | Codex | Responses model endpoint, tool rounds and native Session continuation |
| [agents-api-qwen-code](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/feat/agentsapi-harness-20261117/agents-api-qwen-code) | Qwen Code | Chat Completions tool calls and native Session continuation |
| [agents-api-claude-code](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/feat/agentsapi-harness-20261117/agents-api-claude-code) | Claude Code | Supported native authentication, model endpoint and tool permissions |
| [agents-api-qoder](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/feat/agentsapi-harness-20261117/agents-api-qoder) | Qoder | Native authentication and noninteractive execution; a model key is not a Qoder login credential |
| [agents-api-opencode](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/feat/agentsapi-harness-20261117/agents-api-opencode) | OpenCode | The selected model Provider, native configuration and noninteractive invocation |
| [agents-api-deepseek-harness](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/feat/agentsapi-harness-20261117/agents-api-deepseek-harness) | DeepSeek Harness | Native headless mode, model configuration and actual event granularity |

These links identify development source. Once a template enters the Registry catalog, its detail page becomes the configuration entry point; the collection follows actual catalog membership. Regular Sandbox templates such as `codex` and `qoder` have separate uses and do not automatically include the hosted Gateway.

## Use the shared HTTP interface

After deployment, use `curl` from a terminal, `httpx` from Python or your language's HTTP client. There is currently no dedicated Gateway client SDK. The Sandbox management SDK is a different client.

| Task | Interface |
| --- | --- |
| Discover allowed models | `GET /v1/models` |
| Create a Session with an initial task | `POST /v1/agents/sessions` |
| Submit follow-up input | `POST /v1/agents/sessions/{id}/events` |
| Read session events | `GET /v1/agents/sessions/{id}/events` |
| Inspect work and download output | Session `turns`, `items` and `artifacts` routes |
| Explicitly queue or inspect a submission | `/v1/agent-sandbox/sessions/{id}/submissions` extension |
| Release compute while retaining results | `POST /v1/agent-sandbox/sessions/{id}/close`, then poll the returned Operation |

Session creation accepts initial `input`; use the returned Session ID for follow-up work. Set `Idempotency-Key` when a submission must be retried safely, and keep the request body identical when reusing that key. HTTP acceptance does not mean the task completed: inspect its submission, specific Turn and actual artifacts.

OpenCode v1 JSON output reports tools after completion, so `maxToolSeconds` cannot be guaranteed from the actual tool start. Turn-level `maxRunSeconds`, cancellation and process cleanup still apply. The older DeepSeek practice article used a compatible Harness; the new hosted template uses official DSH. Results from one do not establish behavior of the other.

A shared protocol does not make native Agent capabilities identical. The managed profile currently does not support active steering, external functions/MCP or subagents. Use the explicit submissions extension to queue work during an active turn. A rejected active input has not steered the current task. Event gaps are explicit; an absence of events does not confirm execution stopped.

## Relationship to OpenAI Agents API

The project exposes a subset of similar session, event and file resources, plus its own submission, compute-close and cleanup operations. OpenAI's hosted Harness and this project's full native Agent loop inside Sandbox use different topologies. Similar URLs do not establish complete protocol equivalence or compatibility with every OpenAI SDK.

Read the deployment's `GET /v1/agent-sandbox/capabilities` and template API reference before integration. Native CLI support for MCP, subagents or other features does not mean the Gateway exposes those features.

## Customize an application

Start with the template that matches your accounts and native tools. Configure model or native authentication using its README. Put business files, initial tools and default instructions in the application or image; edit Sandbox resources and FC's native configuration in `template.yaml`. Keep credentials in private configuration sources, outside images, version control and sample output.

After building and publishing, clients continue to use the stable Gateway address. Updates must retain the Worker and workspace belonging to existing Sessions. Switching Harnesses must not silently move an active Session to another Agent. Follow the selected template's upgrade, cleanup and retention instructions.

The [single-endpoint practice article](https://www.agent-sandbox.cn/en/blog/managed-agents-one-endpoint/) records an earlier real two-turn CSV task. Its stated versions and fixed source define that result; it is not acceptance evidence for all six new templates.
