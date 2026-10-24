---
title: 一句话创建 add 沙箱：从模型生成到真实 CLI 与 HTTP 验收
summary: 用一句中文需求生成完整模板，通过云端 steps 构建并运行整数相加 API。保留模型失败、构建超时和权限观察，附自动验收与精确清理脚本。
date: 2026-10-24
category: case
tags: [cli, ai-generation, sandbox, testing]
authors: [Alibaba-Agent-Sandbox]
cover: ./cover.svg
draft: false
---

给 CLI 一句需求，得到一个能通过命令行和 HTTP 调用的沙箱：这是本文要验证的完整链路。需求很小，但验收不只检查“创建成功”，还检查业务结果、生成源码是否真的进入云端、文件操作、后台进程、交互终端和资源清理。

本文已使用官方下载并校验 checksum 的 **CLI 0.4.12** 和从官方 PyPI 安装的 **Python client 0.3.1a2**，原样执行随文脚本：重新生成、构建、创建、50 项验收以及精确清理全部通过。[脱敏结果](./lab/proof.json)、[逐项断言](./lab/assertions.json)及[公开证据选择说明与摘要](./lab/proof-provenance.json)随文保存；这不代表文末列出的限制已经解决。

这是五个开发者实践中的第四篇。环境为 Linux x86_64、Alibaba Cloud Express、杭州地域。成功案例使用的原句是：

```text
创建一个 Python 沙箱，提供 add 命令接收两个整数并返回相加结果
```

## 先明确：这次究竟测试了什么

我们从 [公开的使用模板指南](https://registry.agent-sandbox.cn/source/agent-sandbox/docs/zh/guide/using-templates.md/) 中的自然语言创建入口开始。模型实际写出 `commands.py`、`Dockerfile`、`template.yaml` 和 `README.md`，CLI 校验产物并提交平台构建，等待模板 `READY`，随后创建沙箱。

实验没有先手写一个模板再声称它是模型生成的，也没有手动修好模型产物后把原命令改记为成功。

| 项目 | 本次公开发行版实验 |
| --- | --- |
| CLI | 官方公开发行版 `0.4.12`，下载与 checksum 校验见安装案例 |
| 宿主机 Python / SDK | Python 3.12.13 / `agent-sandbox-client==0.3.1a2` |
| 生成模型 | 实测服务提供的 `qwen3.8-max` |
| 宿主机 Qwen Code | `0.19.3` |
| 生成预算 | 显式配置 1200 秒 |
| 云构建等待预算 | 600 秒，未扩大默认值 |
| 生成的运行资源 | 2 CPU、4096 MB |
| 模板内服务端 | `agent-sandbox-server==0.3.1a1`，alpha 预发布版 |
| 随文脚本验收 | 50/50；脚本文件摘要与实际执行时一致 |
| 清理 | 精确 sandbox ID 和 template ID 均确认不存在 |

这里的 Qwen Code 跑在**宿主机上，负责生成模板**。它与[第二篇案例](/blog/developer-journey-qwen-python/)中安装在沙箱里的 Qwen Code 0.23.0 是两个位置、两种用途，不能混成一个版本结论。

## 准备 CLI、提供方与模型配置

先按[安装案例](/blog/developer-journey-cli-install/)安装 CLI，检查实际版本：

```bash
abx --version
```

本次实际安装和验证的版本是 `0.4.12`。CLI 支持自动准备 Qwen Code；这里不把 Node.js/npm 写成所有用户的硬性前置条件。若你已经有 Qwen Code，可额外记录 `qwen --version`，便于比较生成行为。

按[配置参考](https://registry.agent-sandbox.cn/source/agent-sandbox/docs/zh/reference/configuration.md/)设置本次进程的环境变量：

```bash
export ABX_PROVIDER=alicloud-express
export ALIBABA_CLOUD_REGION_ID=cn-hangzhou
export ALICLOUD_ACCESS_KEY_ID='<YOUR_ACCESS_KEY_ID>'
export ALICLOUD_ACCESS_KEY_SECRET='<YOUR_ACCESS_KEY_SECRET>'
export ABX_SANDBOX_API_KEY='<YOUR_SANDBOX_API_KEY>'

export ABX_LLM_BASE_URL='<YOUR_OPENAI_COMPATIBLE_BASE_URL>'
export ABX_LLM_API_KEY='<YOUR_MODEL_API_KEY>'
export ABX_LLM_MODEL=qwen3.8-max
export ABX_QWEN_CODEGEN_TIMEOUT=1200
```

本例沿用[第一篇](/blog/developer-journey-cli-install/)已验证的同一账户连接配置，包括 Sandbox API Key 以及该账户实际使用的 `ABX_SANDBOX_BASE_URL`、`ABX_SANDBOX_DOMAIN`（如需覆盖默认地址）。它们是已有连接配置的延续，不是要求所有用户新增自定义端点。

模板管理需要 AK/SK，沙箱访问需要 Sandbox API Key；它们不是互相替代的凭据。模型 ID 必须由你使用的服务实际提供。本实验先通过服务模型列表及真实工具调用确认 `qwen3.8-max` 可用，不能由这篇文章推断所有兼容端点都支持它。

## 执行一句话创建

```bash
abx --json create \
  --prompt '创建一个 Python 沙箱，提供 add 命令接收两个整数并返回相加结果' \
  --yes --detach --build steps \
  --dir ./generated \
  --timeout 900
```

几个选项解决的是不同问题：

- `--yes` 跳过交互确认，适合脚本执行。
- `--detach` 创建后返回；它不能替代 `--yes`。
- `--build steps` 选择本次已经验证的 Express 云构建路径，无需本地 Docker/ACR 推镜像。
- `--timeout 900` 是沙箱存活时间，不是模型生成时间，也不是构建等待时间。

公开发行版的真实进度如下，资源 ID 已替换为占位符：

```text
Generating template with Qwen Code ...
Template registration submitted: <owned-template>
Template <owned-template>: building (0s)
Template <owned-template>: building (16s)
Template <owned-template>: building (33s)
Template <owned-template>: building (50s)
Template <owned-template>: ready (60s)
```

整条命令耗时 **331.54 秒**，退出码为 0，最后返回 `Status: running` 的沙箱。这个耗时包括模型生成、构建与创建，不能只引用 60 秒声称整个流程只需一分钟。

## 阅读模型实际生成的接口，再调用

本次公开版本实际生成了这个业务函数：

```python
from agent_sandbox.server import command, start

@command("add", description="Add two integers and return the sum.")
def add(a: int, b: int) -> int:
    return a + b
```

完整文件还包含仅在 `__main__` 下执行的启动逻辑。平台通过 `--commands` 导入该文件时，不会因为导入而重复启动监听端口。

先看实际注册的命令，再传参数：

```bash
abx sandbox command list <SANDBOX_ID>

abx --json sandbox command run <SANDBOX_ID> add \
  --json-args '{"a": 17, "b": 25}'
```

实际结果：

```json
{"result": 42}
```

省略 `--json` 时，CLI 普通输出是 `42`，不能把普通模式示例写成 JSON 包装对象。参数选项是 `--json-args`，不是 `--input`。

本次也通过真正的 HTTP POST 测试了接口。URL 与认证头来自 SDK 的 `application_client(9000)` 应用绑定，没有手拼沙箱域名：

```python
import asyncio
import os
import httpx
from agent_sandbox import ProviderSandbox

async def main():
    sandbox = await ProviderSandbox.connect(os.environ["SANDBOX_ID"])
    application = await sandbox.application_client(9000)
    try:
        async with httpx.AsyncClient(
            headers=application.auth_headers(), timeout=60
        ) as client:
            response = await client.post(
                application.base_url.rstrip("/") + "/commands/add",
                json={"a": 17, "b": 25},
            )
            response.raise_for_status()
            assert response.json() == {"result": 42}
            print(response.json())
    finally:
        await application.aclose()
        await sandbox.close()

asyncio.run(main())
```

代码中的 `close()` 只结束客户端连接，资源删除见后文。网关凭据与可选的应用 Bearer token 是独立的。若设置了应用 `ABX_SERVER_TOKEN`，只有 `/health` 免应用鉴权，不能把 `/capabilities` 也宣传成匿名接口。本文模板没有设置业务 token；可移植验收脚本使用实际绑定返回的认证头。

## 把“成功”拆成可以复核的断言

独立脚本[verify.py](./lab/verify.py)通过实际 CLI 和 HTTP 调用完成了 50 个断言。它没有 mock 后端，也没有读取项目源码来代替调用结果。

| 验收面 | 实际检查 |
| --- | --- |
| 生命周期 | info、请求的约 900 秒租期、kill-on-timeout；时间精度允许 1 秒表示误差 |
| 列表 | 列表 JSON 中精确找到本次完整 sandbox ID；最多 3 次、间隔 10 秒 |
| 远程执行 | 真正执行 Python；实测 Python 3.13.13 |
| 应用 | capabilities 中命令端点允许调用，命令列表包含 add |
| 业务结果 | `(17,25)→42`、`(-15,7)→-8`、`(0,0)→0`、两个 `2147483648` 相加得到 `4294967296` |
| 错误结果 | 缺参数返回 400，不存在的命令返回 404 |
| 文件 | 上传下载字节 SHA256 一致；目录创建、移动后内容/源路径、删除后精确 stat 不存在 |
| 系统与进程 | info、metrics、ports、packages、限定环境查询；找到自建后台 PID，终止后确认消失 |
| 终端 | 真正连接 PTY，验证 `cd` 与环境变量在同一会话中保留 |
| 生成物真实性 | 从云端下载 commands.py，与模型最终磁盘文件逐字节比较 |

最后一项很容易漏掉：清单中内联的 base64 可能与磁盘上的 `commands.py` 不一致。我们先检查清单里的内容，再下载云端文件比较；本次三者一致，源码 SHA256 为：

```text
b5a8a47f8fa0e58841376ce9a88243c0c9ea7cb8aa9feb837c92d48250fefa33
```

文件实验在用户主目录下建立独占子目录。公开版本本轮的只读检查确认：应用源码目录 `/home/user/app` 为 root:root、0755，UID 1000 不可写；源码文件本身归 user 所有。此前候选直接向源码目录写数据曾失败，记录保留。

本轮生成 README 仍声称 `chown` “保证运行用户可写工作目录”，这句话与实测不符，已单独记录到 [Issue #132](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/issues/132)。清单确实先 chown，再 WORKDIR，最后切回 user，但现有证据不足以断言哪个步骤造成归属变化。加法业务不要求写源码目录，故这项限制不影响当前业务验收；我们没有修改快照、临时 chmod 或把 50 项通过写成“所有生成说明都准确”。

## 一次执行生成、验收与精确清理

随文提供的[run.py](./lab/run.py)调用真实的上述 create 命令，接着运行独立 verifier，并在 `finally` 中清理本次捕获到的精确 ID。将它和 [verify.py](./lab/verify.py)放在同一个目录：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple \
  'agent-sandbox-client==0.3.1a2' httpx

EXPERIMENT_ROOT="$(mktemp -d)"
python lab/run.py --output "$EXPERIMENT_ROOT/run" \
  --generation-timeout 1200
```

输出目录必须是新的，以免覆盖历史证据。`report.json` 保存运行报告，已替换已知凭据和资源 ID，但公开前仍需审查本机路径等信息；`verification/evidence/` 保存逐项调用与断言，`generated/` 保留本轮模型原始文件。`.private/` 保存精确恢复 ID 和原始输出，不能和公开报告一起发布。

本轮直接执行了上述两个附件的原始字节，wrapper 退出码为 0，50/50 断言通过。`proof.json` 记录它们的 SHA256、四个生成文件摘要、实测版本与清理结果。宿主机 client 是 0.3.1a2，生成模板固定的服务端是 0.3.1a1；应用 `/capabilities` 实测回报的服务端版本也为 0.3.1a1，没有把两者混写。

自动清理并不是“list 里没看见就算删除”。实际执行了对应 sandbox 的 kill，然后通过 SDK 精确查询得到 `SandboxNotFoundError`；模板删除后精确查询得到 `TemplateNotFound`。人工执行时也应保留同等证据：

```bash
abx kill <SANDBOX_ID>
abx info <SANDBOX_ID> --format json

abx template delete <TEMPLATE_ID> -y
abx --json template info <TEMPLATE_ID>
```

两次查询应该明确报告对应资源不存在。普通网络失败不能当作清理成功。

本轮验证了正常完成后的清理；此前受控失败的历史记录分别保留，这不代表任意中断都能被自动处理。尤其在生成期间按 Ctrl-C，子 CLI 可能仍在运行，不能把 `finally` 理解为所有中断都自动回收。应先停止本次子进程，依据这次终端进度中已提交的精确模板 ID，以及 `.private/owned.json` 中已捕获的 ID，逐个检查并删除；不要批量删除账号中的其他资源。尚未捕获 ID 的中断，需要从本次生成别名对应的模板精确确认归属后处理。

## 已冻结的产物，和重新生成是两个实验

本次成功模型产物保留在 [lab/generated](./lab/generated/README.md)：[commands.py](./lab/generated/commands.py)、[Dockerfile](./lab/generated/Dockerfile)、[template.yaml](./lab/generated/template.yaml)及[四文件摘要](./lab/generated/SHA256.json)。文件没有经过人工修复。CLI 的正常校验流程会把模型输出的 JSON 清单重新输出为 YAML；这是 CLI 正常处理，并非实验人工改写。快照中的 README 保留上述已发现的工作目录表述问题，阅读时应以实测结果为准。

之前源码候选 `7ef688b` 的四文件仍单独保留在 [generated-candidate12](./lab/generated-candidate12/README.md)：该轮创建耗时 256.15 秒、READY 52 秒、主验收 49/49、独立验收 50/50。它与本文公开安装版的 fresh generation 是两次不同实验；新的文件摘要、331.54 秒和 READY 60 秒属于本轮，不混用。

重新运行同一句话，模型可能生成不同参数名、额外命令或不同说明文档。应先读取新生成的文件与命令列表，再判断 verifier 是否适用于那个真实契约；不能为了符合脚本手工改造生成物。

如果只是想复用已冻结模板，可以另走显式部署路径：

```bash
abx --json template deploy ./lab/generated --build steps \
  --alias "add-snapshot-$(date +%s)" --yes
```

直接 template deploy 返回提交结果时，需要再查询模板，等到 `ready` 后才能创建沙箱。这条路径是在**复建已知模板**，没有重新调用模型，不能把它算作“一句话重新生成成功”。附带快照固定了杭州基础镜像引用；更换地域也不再是原字节快照实验。

## 哪些失败仍然重要

这次不是所有尝试都成功，成功的 add 案例也没有抹掉前面的失败：

- 原来的 0.4.11 自然语言路由不接受普通 create 帮助中出现的 `--detach`，并且生成后会撞上本地 Docker 缺失。修复接通了已有 steps 路径，保留默认 Docker 行为。
- 一些模型结果缺少文件、Dockerfile 漏 COPY、YAML 参数类型错误，或没有真实编码源码。校验器拒绝了它们，没有放松规则让失败通过。
- `qwen3-coder-flash` 的失败与改用 `qwen3.8-max` 是不同配置实验。一次 600 秒生成超时后，明确改用 1200 秒配置，不能声称默认配置已经通过。
- 较复杂的 pandas/matplotlib 环境多次停留在 building。一次原 600 秒预算耗尽后，另做了 296 秒有界观察，仍未 READY。平台接口未提供足够步骤日志，当前仍不能证明完整根因；后续工作单独记录在 [Issue #131](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/issues/131)。
- 简单 add 的一次候选选择了 1 CPU / 512 MB，被 FC 明确拒绝：内存 GB 与 CPU 核数之比必须在 1 到 4。provider 指导补充了已验证的 2 CPU / 4096 MB，随后 fresh 候选通过；这条说明不是模板 schema 的强制约束。
- 模型 README 曾给出错误 CLI 参数、输出形状及鉴权说明。相关生成指导已经纠正，并对最终产物重新审阅；本轮仍发现工作目录表述问题，已如上保留，不能默认模型说明文档天然可信。

因此，这篇案例证明的是：在明确版本、模型与预算配置下，一个真实生成的简单业务可以走完云构建、应用调用、CLI 验收和精确清理。复杂依赖构建的稳定性以及模型输出的一致性，仍应按各自实验的证据评价。
