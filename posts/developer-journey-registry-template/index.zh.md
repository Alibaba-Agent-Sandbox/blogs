---
title: 从 Registry 到可调用 API：完整验证一个 Python Sandbox 模板
summary: 从公开 python-hello 模板出发，用官方工具准备云端构建步骤，验证 CLI、Python SDK、外部 HTTP、文件和真实终端，并保留可重跑脚本与清理证据。
date: 2026-10-24
category: case
tags: [python, templates, registry, cli, testing]
authors: [Alibaba-Agent-Sandbox]
cover: ./cover.svg
draft: false
---

本文从 [Registry 的 python-hello 页面](https://registry.agent-sandbox.cn/templates/python-hello/)开始，把公开模板部署到阿里云 Express，创建 sandbox，再分别通过 CLI、Python SDK 和外部 HTTP 调用同一组命令。最后验证文件往返、后台进程和真实交互终端，并删除本次创建的资源。

这条路径适合没有本地 Docker 的开发者：使用模板仓库提供的 `prepare_steps.py`，把已有模板准备为云端 steps 配方。本文的成功记录针对这一条路径，未执行本地 Docker 镜像构建，也不代表其他 provider 已通过。

2026 年 10 月 24 日，我们使用**正式发布的 CLI 0.4.12 和 PyPI client SDK 0.3.1a2**，原样运行本文附件，完成 **29/29 项断言、40 条捕获的命令**，总耗时 52.826 秒。sandbox 与 template 都已删除，并按精确 ID 回读不存在。[最终结果](./lab/evidence/release-0412-a2/result.json)、[版本与清理摘要](./lab/evidence/release-0412-a2/summary.json)和[附件执行哈希](./lab/evidence/release-0412-a2/execution.json)随文章提供。

此前 CLI 0.4.11 / client SDK 0.3.1a1 的实验也已通过，历史记录保存在独立目录，未被新版结果覆盖。两次使用相同模板源码与远程 server；新版本实验直接执行当前附件，不借用历史结果。

## 1. 先弄清楚本次部署的是什么

![公开模板经官方 steps 准备、等待 READY、三种入口验证和精确清理的完整流程](./flow.svg)

Registry 是发现模板和阅读文档的入口。这个案例实际使用的是 Git 仓库中的模板目录：`template.yaml` 描述运行配置，`Dockerfile` 固定基础环境，`commands.py` 定义命名命令和 HTTP 路由。为重现相同输入，我们记录源码提交，而不只记录一个可随时间变化的分支名。

| 层次 | 本次已验证的值 | 用途 |
| --- | --- | --- |
| 本机 CLI | `abx 0.4.12` | 部署模板、创建 sandbox、操作文件和进程 |
| 本机 Python | `3.12.13` | 运行测试脚本 |
| 本机 client SDK | `agent-sandbox-client 0.3.1a2` | 连接已有 sandbox 和调用应用客户端 |
| 本机 YAML 解析器 | `PyYAML 6.0.3` | 运行官方 steps 准备脚本 |
| 模板源码 | `565e546a3e1d814e840062cbdd5da4ba295e16a6` | 固定模板、转换器及文档输入 |
| 远程基础镜像 | `runtime/base:v0.0.49` | Express steps 的基础运行环境 |
| sandbox 内 Python | `3.13.13` | 执行模板命令 |
| sandbox 内 server | 包版本 `0.3.0`，源码固定为 `e2cb27e24fde0a67112f82b8d44af463445a5d1a` | 提供模板命令与 HTTP 服务 |

本机 SDK 与 sandbox 内 server 是不同的安装位置。本次没有用 `--server-commit` 改写模板的固定依赖；准备工具保留 Dockerfile 中的 server 源码 pin。升级本机 client 不会自动升级模板里的 server。模板来源见[固定提交目录](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/tree/565e546a3e1d814e840062cbdd5da4ba295e16a6/python-hello)，运行配方和文件哈希见 [steps-provenance.json](./lab/evidence/release-0412-a2/steps-provenance.json)。

## 2. 准备 CLI、Python 环境和两类凭据

先按[官网开始使用](https://www.agent-sandbox.cn/start/)安装 CLI，并执行 `abx --version`。以下最终配方固定 `0.4.12`；下载其他版本时，应单独保存其验证结果。脚本需要 Linux 或 macOS 的 POSIX PTY、Git、Python 3.10+，本次实际控制机是 Linux。

创建独立工作目录，然后准备本机依赖：

```bash
mkdir registry-lab
cd registry-lab
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple \
  "agent-sandbox-client==0.3.1a2" "PyYAML==6.0.3"
abx --version
```

这里固定 alpha 版本，并显式使用官方 PyPI。模板中的远程 server 仍按上一节的源码安装。

Express API 负责运行已有模板的 sandbox；模板构建还需要阿里云控制面凭据。按自己账户已授权的配置提供以下环境变量，不把真实值写进 `template.yaml` 或文章附件：

```bash
export ABX_PROVIDER=alicloud-express
export ABX_SANDBOX_API_KEY="<YOUR_API_KEY>"
export ABX_SANDBOX_BASE_URL="<YOUR_EXPRESS_API_BASE_URL>"
export ABX_SANDBOX_DOMAIN="<YOUR_EXPRESS_SANDBOX_DOMAIN>"
export ALICLOUD_ACCESS_KEY_ID="<YOUR_ACCESS_KEY_ID>"
export ALICLOUD_ACCESS_KEY_SECRET="<YOUR_ACCESS_KEY_SECRET>"
export ALIBABA_CLOUD_REGION_ID="<YOUR_REGION_ID>"
# 只有账户配置要求指定团队时才设置：
# export ABX_ALICLOUD_EXPRESS_TEAM_ID="<YOUR_TEAM_ID>"
```

如果当前 shell 还留有另一套 E2B 配置，先移除冲突的 `E2B_API_KEY`、`E2B_API_URL`、`E2B_DOMAIN`，再运行本实验。本文 steps 路径不需要本地 Docker、ACR 上传配置或模型 API Key。创建模板和 sandbox 会使用真实云资源；脚本仅清理自己记录的精确 ID。

## 3. 从公开源码准备 steps，再等模板真正就绪

[公开 steps 指南](https://registry.agent-sandbox.cn/source/awesome-templates/docs/platform-steps.zh-CN.md/)给出的路径是先准备输出目录，再部署该目录。为固定本次实验，增加一次精确 Git checkout：

```bash
git clone https://github.com/Alibaba-Agent-Sandbox/awesome-templates.git
cd awesome-templates
git checkout 565e546a3e1d814e840062cbdd5da4ba295e16a6
python scripts/prepare_steps.py python-hello --output ./python-hello-steps
abx --json template deploy ./python-hello-steps --build steps \
  --alias "python-hello-$(date +%s)" -y
```

输出目录必须是新的。部署前可查看其中的 `template.yaml` 和 `steps-provenance.json`。本次准备结果包含 4,605 字节的 steps JSON；原始 `commands.py` 的 SHA256 为 `819dd5d91a67edc9d681b01dc44caac479c6d693d947f1818d5a1253cc9b9ceb`。

官方准备工具负责把模板所需的公共源文件纳入步骤，并保留受支持的用户、工作目录、环境和启动约定。它支持文档限定的 Dockerfile profile，不是任意 Dockerfile 的通用转换器。仅给原模板加 `--build steps` 不会自动补出所需配方，也不会自动上传 `COPY` 的本地上下文。

将部署输出的 `TemplateID` 私下保存。**`submitted` 只说明请求已受理。** 此时不能把构建记为成功，也不应马上创建 sandbox：

```bash
export TEMPLATE_ID="<DEPLOY_RETURNED_TEMPLATE_ID>"
abx --json template info "$TEMPLATE_ID"
```

本次 CLI 0.4.12 的 `status` 可能是 `"{'state': 'ready'}"` 这样的字符串；不能直接假设它是嵌套 JSON 对象。附件脚本先解析外层 JSON，再以 `ast.literal_eval` 解析该字符串，按 10 秒间隔轮询，默认最多等待 900 秒。失败状态或超时都让实验失败，随后执行清理。

只有精确模板的状态为 `ready`，才创建实例：

```bash
abx create "$TEMPLATE_ID" --detach --timeout 1200
export SANDBOX_ID="<CREATE_RETURNED_SANDBOX_ID>"
abx info "$SANDBOX_ID" --format json
abx exec "$SANDBOX_ID" -- python3 -c 'print(6 * 7)'
```

这里 `1200` 是 sandbox 生命周期，`900` 是附件中等待模板构建的时限，两者用途不同。标准 `info` 命令使用 `--format json`；扩展命令按各自帮助使用 `--json`。本次 `exec` 的预期输出为 `42`。

## 4. 用 CLI 调用模板命令

先发现可用能力和命令，再调用具体业务：

```bash
abx --json sandbox capabilities "$SANDBOX_ID"
abx --json sandbox command list "$SANDBOX_ID"
abx --json run "$SANDBOX_ID" hello --arg name=Ada
abx --json run "$SANDBOX_ID" run_script \
  --json-args '{"code":"print(21 * 2)"}'
```

后两条在本次实验中分别返回：

```json
{"result": "Hello, Ada!"}
```

```json
{"result": "42\n"}
```

命名命令用于复用模板提供的业务接口；`exec` 则用于执行沙箱里的进程。下面把本地脚本和测试文件传入模板预期的工作目录，再经命名命令运行：

```bash
printf 'print(6 * 7)\n' > main.py
printf 'def test_answer():\n    assert 6 * 7 == 42\n' > test_main.py
abx upload "$SANDBOX_ID" main.py /home/user/app/main.py
abx upload "$SANDBOX_ID" test_main.py /home/user/app/test_main.py
abx --json run "$SANDBOX_ID" run --arg file=main.py
abx --json run "$SANDBOX_ID" test --arg path=test_main.py
```

实测得到 `42` 和 `1 passed`。这一步同时检查上传路径、运行用户对工作目录的访问，以及模板命令是否真正执行了刚上传的文件。

## 5. 同一命令，用 Python SDK 和外部 HTTP 再调用

这里使用公开的 `ProviderSandbox` 类型，因为 `application_client` 属于这一路 SDK API。连接的是已经创建的 sandbox，`close()` 负责释放本地客户端连接；资源销毁留到统一清理步骤。

```python
import asyncio
import os
from agent_sandbox import ProviderSandbox

async def main():
    sandbox = await ProviderSandbox.connect(os.environ["SANDBOX_ID"])
    try:
        async with await sandbox.application_client(9000) as client:
            result = await client.commands.run("hello", name="Python")
            assert result == "Hello, Python!"
        # 保存到当前进程变量或本机私有记录，不公开真实访问地址。
        application_url = sandbox.network.get_url(9000)
        return application_url
    finally:
        await sandbox.close()

asyncio.run(main())
```

除了 SDK，本次还从控制机直接向 `network.get_url(9000)` 返回的公网应用地址发送 POST，未用 sandbox 内的 localhost 冒充外部调用：

```python
import asyncio
import os
import httpx
from agent_sandbox import ProviderSandbox

async def main():
    sandbox = await ProviderSandbox.connect(os.environ["SANDBOX_ID"])
    try:
        url = sandbox.network.get_url(9000)
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url + "/commands/hello", json={"name": "Ada"})
            assert response.status_code == 200
            assert response.json() == {"result": "Hello, Ada!"}
    finally:
        await sandbox.close()

asyncio.run(main())
```

本文固定的 `python-hello` 配置是匿名演示应用；本次实际使用的 Express 应用绑定也无需额外网关认证，因此该 POST 没有添加应用 Bearer 或网关头。**应用匿名不等于网关匿名**：其他绑定应使用 `application_client.auth_headers()` 解析得到的实际认证头，并按模板配置应用令牌，不要将控制面 API Key 当作应用令牌转发。这个匿名示例也不构成生产认证方案。[SDK 应用客户端指南](https://registry.agent-sandbox.cn/source/python-sdk/docs/zh/guide/template-server-api.md/)说明了这些区别。

为了验证接口边界，实验还检查了失败响应，而不只测试成功路径：

| 请求 | 输入 | 本次预期及结果 |
| --- | --- | --- |
| `POST /commands/hello` | `{"name":"Ada"}` | `200`，`Hello, Ada!` |
| `POST /commands/run_script` | `{"code":"print(21 * 2)"}` | `200`，`42\n` |
| `POST /commands/run_script` | `{}` | `400`，缺少 `code` |
| `POST /commands/unknown` | `{}` | `404`，未知命令 |
| `GET /commands` | 无 | 发现列表不包含 `_debug_info` |
| `GET /hello/Ada` | 无 | `200`，`{"greeting":"Hello, Ada!"}` |

最后两项说明发现列表和自定义路由都按模板工作。命令隐藏仅表示不出现在发现列表中，本实验没有把它当作授权边界。四条 POST 的脱敏状态与响应保存在 [http.json](./lab/evidence/release-0412-a2/http.json)。

## 6. 文件、进程、系统状态和真实终端

完整实验并不在 `hello` 成功后结束。文件部分读取目录、查询元数据、按模式搜索，下载原文件并比较字节，然后移动、删除文件并回读空目录：

```bash
abx --json sandbox files list "$SANDBOX_ID" --path /home/user/app
abx --json sandbox files stat "$SANDBOX_ID" --path /home/user/app/main.py
abx --json sandbox files search "$SANDBOX_ID" --path /home/user/app --pattern '*.py'
abx download "$SANDBOX_ID" /home/user/app/main.py download.py
python -c 'from pathlib import Path; assert Path("main.py").read_bytes() == Path("download.py").read_bytes()'
abx sandbox files mkdir "$SANDBOX_ID" --path /home/user/app/proof
abx sandbox files mv "$SANDBOX_ID" \
  --source /home/user/app/main.py --dest /home/user/app/proof/moved.py
abx sandbox files rm "$SANDBOX_ID" --path /home/user/app/proof/moved.py -y
abx --json sandbox files list "$SANDBOX_ID" --path /home/user/app/proof
```

`rm -y` 是明确确认删除，适合本实验已知路径的自动化操作。系统检查覆盖 `info`、`metrics`、`ports`、`packages`，环境变量只读取 `PATH,HOME`，不导出全部环境：

```bash
abx --json sandbox system info "$SANDBOX_ID"
abx --json sandbox system metrics "$SANDBOX_ID"
abx --json sandbox system ports "$SANDBOX_ID"
abx --json sandbox system packages "$SANDBOX_ID"
abx --json sandbox system env "$SANDBOX_ID" --filter PATH,HOME
```

进程实验启动自己的 `sleep 77`，在列表中找到它的 PID，查询信息、发送 SIGTERM，再检查这个 PID 已消失。附件会自动定位这个唯一测试进程，避免误杀其他进程：

```bash
abx exec --background "$SANDBOX_ID" -- sleep 77
abx --json sandbox process list "$SANDBOX_ID"
export TEST_PID="<PID_OF_THIS_SLEEP_77>"
abx --json sandbox process info "$SANDBOX_ID" "$TEST_PID"
abx sandbox process signal "$SANDBOX_ID" "$TEST_PID" --signal 15
abx --json sandbox process list "$SANDBOX_ID"
```

真实终端测试使用 `abx connect`。在同一个会话中切换目录、设置环境变量，再读取二者：

```bash
abx connect "$SANDBOX_ID"
# 在交互终端内依次输入：
cd /tmp
export JOURNEY_PTY_FLAG=held
printf 'PTY_CHECK_%s:%s:%s\n' PASS "$PWD" "$JOURNEY_PTY_FLAG"
exit
```

本次实际输出包含 `PTY_CHECK_PASS:/tmp:held`。附件通过本机 PTY 启动 CLI 并读取返回流，所以验证的是交互会话里的状态保留，未用几次独立 `exec` 替代。公开[终端记录](./lab/evidence/release-0412-a2/terminal.txt)已移除 ANSI 控制序列。

## 7. 清理要回读精确资源

实验结束后先销毁 sandbox，再删除模板，并对各自精确 ID 进行回读：

```bash
abx kill "$SANDBOX_ID"
abx info "$SANDBOX_ID"
abx template delete "$TEMPLATE_ID" -y
abx --json template info "$TEMPLATE_ID"
```

这里两个 `info` 的预期是失败：sandbox 报不存在，template 返回 `TemplateNotFound/404`。不能把“命令全部退出 0”当作清理验收，也不能仅凭 `list` 为空断言已删除。

附件把清理放在 `finally` 中，部署成功返回 ID 后立即写入私有恢复状态。成功条件同时要求所有业务步骤完成且已创建资源的不存在回读成立。中途异常或 Ctrl-C 不会因为清理成功就变成实验成功。若进程被强制终止、网络中断导致创建结果未知，应保留终端提示的私有恢复目录人工核对，不能把不确定资源状态发布为 PASS。

## 8. 下载附件，一次跑完并保留自己的证据

[独立实验脚本](./lab/03_registry_end_to_end.py)不读取项目 workspace、`.env` 或内部测试 harness。它只使用当前环境的凭据、公开 Git 源码、已安装 CLI 和公开 Python SDK。

把脚本下载到前面创建的 `registry-lab`，保持虚拟环境激活、凭据已设置，然后从该工作目录运行：

```bash
python 03_registry_end_to_end.py \
  --abx "$(command -v abx)" \
  --source-ref 565e546a3e1d814e840062cbdd5da4ba295e16a6 \
  --build-timeout 900 \
  --output ./registry-proof-0412-a2
```

输出目录必须不存在。每次重跑选择新的目录，不覆盖上一次结果。脚本会自行创建唯一模板别名、准备源码、等待 READY、创建 sandbox、完成所有检查并清理。手动操作章节与自动脚本二选一；不要在已经手动创建的资源上再套用自动脚本的清理预期。

| 输出 | 应当检查的内容 |
| --- | --- |
| `result.json` | `passed: true`、`completed: true`、所有已创建资源 `absent: true` |
| `checks.json` | 每项断言的名称和真假 |
| `commands.json` | 操作顺序、退出码、脱敏输出 |
| `http.json` | 外部 HTTP 的精确状态与响应 |
| `source.json`、`steps-provenance.json` | 源码提交、输入和生成配方哈希 |
| `versions.json` | 实际本机 Python/SDK 版本 |
| `terminal.txt` | 真实 PTY 输出，发布前需去除终端控制序列 |

CLI 版本在 `commands.json` 中记录。模板 READY 的轮询次数取决于云端耗时，因此重跑的命令总数可能与本次 40 条或历史 50 条不同；固定功能断言仍是 29 项。脚本日志已做基础脱敏，分享前仍要检查本机可执行路径、资源标识和访问地址；私有恢复目录不要上传。

当前附件已用正式公共版本完整实跑，执行前后字节未变，SHA256 为 `871e2d60fcabeb91c3974607edd898a1b55efce6e313875d407fa691956fc73e`。它保留了清理、中断保护和可选本机 server 包探测：本机仅安装 client 也能使用；本次控制机还安装了 server 0.3.1a2，因此 `versions.json` 会记录该本机包。远程 server 的实测版本则来自 sandbox 内 `system packages`，仍是 0.3.0。两者不要混淆。

## 9. 这次实测发现并修正了什么

第一轮直接走默认部署时，本机缺少 Docker，CLI 返回 `E7020`。这是缺少该路径前置条件，不能据此说模板坏了。随后直接给未准备的模板加 `--build steps`，又因缺少对应构建块失败。正确动作是使用官方准备工具，明确选择云端 steps 路径。

文档审阅还发现了过期的 server 来源展示、旧参数，以及 `submitted` 容易被误当成 READY 的说明缺口；SDK 示例未充分说明 `ProviderSandbox` 类型与应用认证边界。相关修改通过[模板文档 PR #202](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/202)和[SDK 文档 PR #93](https://github.com/Alibaba-Agent-Sandbox/python-sdk/pull/93)合并后，先读回 13 个已发布页面，再按新公开的 `prepare_steps.py` 路径重跑本实验。[页面读回证据](./lab/evidence/historical-0411-a1/public-docs-readback.json)记录实际 URL、内容哈希与检查结果。

本文同时保留[历史 0.4.11/a1 摘要](./lab/evidence/historical-0411-a1/summary.json)与[最终 0.4.12/a2 摘要](./lab/evidence/release-0412-a2/summary.json)，原始失败记录没有覆盖。公开证据采用明确文件清单，命令副本只规范化本机可执行路径，终端副本去除 ANSI，原文件与发布副本的 SHA256 在[最终 manifest](./lab/evidence/release-0412-a2/manifest.json)中分别保存。它证明这个固定模板输入在 Express steps 路径上的创建、调用和清理结果，不延伸为所有模板、所有 provider 或生产认证配置的验收。
