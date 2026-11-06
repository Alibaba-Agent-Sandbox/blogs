---
title: 用一个 Gateway 部署和调用 Sandbox Agent：两轮文件任务实践
summary: 用正式CLI部署Server侧Gateway，让Agent在独占Sandbox内完成两轮CSV代码修改。涵盖凭据配置、构建部署、统一入口调用、结果检查与临时资源清理。
date: 2026-11-06
category: engineering
tags: [agents, sandbox, python, serverless, best-practice]
authors: [Alibaba-Agent-Sandbox]
draft: false
---

业务调用方希望配置一个 URL 和一把业务 Key，然后创建会话、上传文件、运行 Agent、
下载结果。每个 Sandbox 的地址、创建凭据、工作区和回收流程，应由服务端管理。
本文围绕这一目标，记录 `agents-api` 模板从本地验证到真实阿里云 FC 部署的操作。

本文使用正式CLI0.5.10、公开SDK0.4.0a7和recipe0.1.4，实际完成正常部署、
Sandbox内Qwen Agent两轮文件任务、下载断言及会话关闭删除。以下按读者操作顺序展开，
每一步区分配置示例、实际返回脱敏节选和实际断言摘要；本次已知临时资源均已释放并独立确认。

所有结果都有明确的范围。命令中的本机路径、应用名称、账号及资源标识使用占位符；
密钥和完整私有日志不公开。代码块标为“实际返回脱敏节选”的内容，只保留真实返回中的
允许字段；标为“实际断言摘要”的内容来自执行后的检查，不是伪造的 API 原始响应。

## 1. 先把部署者与业务调用方的入口分开

![统一 Gateway、Server 控制面与每个 Session 的独占 Sandbox](./architecture.svg)

[打开架构图](./architecture.svg) · [下载原 Mermaid 源码](./architecture.mmd)

Server 维护稳定的业务入口，首次输入才按需分配 Sandbox。同一个 Session 的后续轮次
继续使用原有工作区；不同 Session 各自独占 Sandbox。CLI 部署应用时配置云访问、镜像
仓库、数据库、模型及 Sandbox 管理凭据，普通业务客户端只拿 Gateway URL 和业务 Key。

会话关闭与删除分开：Close 释放计算，保留已保存的历史和产物；Delete 删除公开资源。
Close 请求返回一项 Operation，需要继续查询最终状态，不能只看到 HTTP202 就认为
远端进程已停止。客户端请求超时也不能据此自动重发一次任务。

这个模板参考 OpenAI Agents 的 Session/Turn 组织方式，支持一部分接口并提供明确的托管
扩展。它把完整 Agent CLI、模型调用和工具循环放在 Sandbox，能力边界以 Gateway 的
`/v1/agent-sandbox/capabilities` 为准。路径相似不构成任意 OpenAI SDK 或完整托管
harness 的兼容声明。

## 2. 安装正式CLI，固定镜像中的公开SDK版本

普通部署主机需要Node.js20+、Docker、可访问的镜像仓库，以及Python虚拟环境中的
`httpx==0.28.1`。使用npm分发的正式CLI0.5.10；业务HTTP客户端只需httpx、Gateway和业务Key，
不要求安装Sandbox管理SDK。常规准备命令如下：

```bash
npm install --global @agent-sandbox/cli@0.5.10
git clone https://github.com/Alibaba-Agent-Sandbox/awesome-templates.git
cd awesome-templates
git checkout 4971598a5b14b62207076dd2da4264c139423628
cd agents-api
python3 -m venv .abx/venv
. .abx/venv/bin/activate
python -m pip install httpx==0.28.1
abx --version
```

本次为独立验证公开发行物，实际使用fresh安装目录下载、核对npm公开tarball后安装，
没有用源码目录覆盖同名包。以上checkout固定到本次实际运行的提交，
其14个recipe文件已经逐字核对。已安装正式CLI的实际版本输出为：

```text
abx, version 0.5.10
```

两个Dockerfile固定使用公开PyPI0.4.0a7，分别提供Sandbox的guest bridge与Server侧托管服务。

本次使用公开发行的npm CLI0.5.10与PyPI client/server0.4.0a7，没有本地wheel替换。

本轮核心闭环使用的模板recipe版本0.1.4，Sandbox镜像固定Node.js24.16.0、Codex0.162.1和Qwen Code0.23.0。
Host与Sandbox的Node版本是不同配置。模型实际可用性必须另测，CLI能查版本不代表工具回合可用。

模板在[PR296](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/296)维护；
上面的完整提交固定本次使用的recipe。更早版本的失败和发行字节核对保留在
[工程补充](https://github.com/Alibaba-Agent-Sandbox/blogs/blob/main/.agents/evidence/verify/2026-11-06-managed-agents-history-supplement.md)，不混作当前业务结果。

参考实现与实际发行来源：
[SDK PR156](https://github.com/Alibaba-Agent-Sandbox/python-sdk/pull/156)、
[CLI PR238](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/pull/238)、
[CLI0.5.10发行](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/releases/tag/v0.5.10)、
[模板PR296](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/pull/296)。
公开包安装、正常部署和两轮文件任务已经实际验证；本轮资源最终清理另在第11节记录。

## 3. 准备凭据与私有配置

先明确每项凭据的用途，避免把部署权限交给业务调用方。

| 配置 | 用途和来源 | 使用位置 |
| --- | --- | --- |
| 云 AK/SK 或已有 STS 凭据 | 来自已有云访问身份，部署 FC、构建或查询拥有的镜像 | 部署 CLI 子进程 |
| Sandbox 管理凭据 | 来自已有 Sandbox 账号配置，创建和回收 Session 的计算实例 | Server 的 Provider binding |
| 模型 Key、端点、模型 ID | 来自实际模型服务账号；先验证工具结果回合 | Sandbox 中所选 Agent 的模型配置 |
| PostgreSQL URL、密码、CA | 本轮临时私网数据库及其实际 CA | Server；启用 verify-full |
| Business Key | CLI 首次 Apply 生成并安全保存，后续部署复用 | 业务客户端 |
| Internal Token | CLI 生成的私有控制鉴权，独立于业务 Key | Server 内部控制调用 |
| Sandbox 应用令牌 | 运行时为应用连接单独准备，独立于云 Key 和模型 Key | Server 与 Sandbox 应用服务之间 |

应用令牌不是去云控制台申请的 API Key。普通用户使用模板时，应让 CLI 自动准备并
保存缺省应用认证；不需要先手工生成一串随机令牌才能开始。

Build前还要配置已经存在的ACR命名空间，确保部署身份能向其中推送镜像。正式CLI0.5.10
的`abx config set --help`实际列出`acr_namespace`，对应环境变量`ACR_NAMESPACE`。
下面是填写自己已有namespace的配置示例，不是本轮私有值：

```bash
abx config set acr_namespace YOUR_EXISTING_ACR_NAMESPACE
```

按[模板安装配置指南](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/a4d43370ff82e244c542412d0af0c68759d19fdb/docs/using-templates.md#installation)
准备Sandbox配置与镜像仓库。清单的`application.deployment.accessRef`选择已经配置好的
Serverless Devs access名称；模板默认是`default`，它不会把Sandbox Key当成云部署身份。
本轮显式选择`env`，由部署子进程提供已有的`ALIBABA_CLOUD_ACCESS_KEY_ID`和
`ALIBABA_CLOUD_ACCESS_KEY_SECRET`（使用STS时再提供对应Security Token），没有新建管理Key。
云AK/SK用于部署和镜像操作，与Server binding中的Sandbox管理Key用途不同。

从模板的受支持示例复制私有binding，保持它在被忽略的`.abx/`内：

```bash
cp bindings.example.json .abx/bindings.json
chmod 600 .abx/bindings.json
```

示例中的`{env: ...}`由Apply在部署host读取。普通配置需要提供
`ABX_MANAGED_DATABASE_URL`、`SANDBOX_API_KEY`、`SANDBOX_BASE_URL`、`SANDBOX_DOMAIN`、
`SANDBOX_REGION`、模型的`OPENAI_API_KEY/OPENAI_BASE_URL/OPENAI_MODEL`，以及已有
`AGENTS_FC_ROLE_ARN`。这些名称是公开示例的配置引用；本轮工程控制器使用自己私有的引用
名称，不需要把它们照搬进业务客户端。模型ID实际选择`qwen3.5-plus`，首个adapter为`qwen-code`。

本轮数据库只走私网，state binding包含`databaseUrl`、`databaseCa`及`vpcConfig`。
下面是可供部署者填写的形状示例，环境引用和host路径是占位配置，不冒充原私有JSON：

```json
{
  "agents-state": {
    "databaseUrl": {"env": "ABX_MANAGED_DATABASE_URL"},
    "databaseCa": {"file": "/absolute/private/database-ca.pem"},
    "vpcConfig": {
      "vpcId": {"env": "AGENTS_VPC_ID"},
      "vSwitchIds": [{"env": "AGENTS_VSWITCH_ID"}],
      "securityGroupId": {"env": "AGENTS_SECURITY_GROUP_ID"}
    }
  }
}
```

这是替换已有binding中的state对象，其余示例对象继续保留。数据库URL使用证书覆盖的
主机名及`sslmode=verify-full`，CA从数据库服务获得并核对有效链；不把密码或CA塞进Dockerfile。
清单的地域与已有网络、镜像仓库、Sandbox平台保持一致，accessRef选择已有的云访问配置。
本轮使用显式环境访问身份，已有网络和执行角色按借用处理，业务/内部Key由首次Apply新生成。


凭据保存在本机受保护的私有目录，文件权限应逐一确认；只传入所需子进程，不打印值，也不写入Docker context、公开仓库或文章素材。

数据库保持私网访问，没有为方便控制器而开启公网数据库或搭建隧道。已有 VPC、交换机、
安全组和执行角色按借用处理，不在清理时删除。

本轮另建的临时数据库只用于这次实践，已经独立删除确认，详情见第11节。
模板本身连接你显式配置的已有PostgreSQL，不负责自动创建数据库。

## 4. 先验证模型的工具回合

Agent 编码任务通常包含“模型要求调用工具→执行工具→把工具结果发回模型→继续生成”。
简单文本请求成功、`/models` 列出模型，以及 CLI 版本查询，都不足以证明这个流程可用。

本轮用当前账号实际可用的 `qwen3.5-plus`，分别检测 Chat Completions 和 Responses。
探针只做加法：模型调用 `add(a=2,b=3)`，控制器回传5，要求最终回答精确为5。
探针不执行模型生成的任意函数体。

本次另用工程辅助探针实际验证了Chat和Responses的工具结果回合。
这些探针不是模板部署依赖，也不要求业务客户端安装管理SDK。

实际断言摘要如下；这些只是独立模型协议回合，尚不证明Sandbox中的完整编码任务：

| 本轮协议回合 | 第一次HTTP | 工具结果第二次HTTP | 回合内耗时/秒 | 整条命令退出码/耗时秒 |
| --- | ---: | ---: | ---: | --- |
| Chat工具调用与结果返回 |200 |200 |3.940 |0 /4.496 |
| Responses function_call_output |200 |200 |14.363 |0 /14.441 |

两项只针对本轮兼容端点的`qwen3.5-plus`，均通过工具结果回合断言；
这不构成原生OpenAI账号或所有模型的资格。原始许可字段投影保存在[准备摘要](./public-verified-preparation.json)，
实际Agent修改源码、执行工具及生成产物仍由第7节另验。

## 5. 用有缺陷的现有工程作为业务练习

只让 Agent 新建一个包含固定文字的文件，很难判断真实代码修改能力。模板在
`/workspace/agents-api-demo` 预置一个 CSV 汇总程序和原始测试。程序故意把同月金额覆盖，
第一轮需要修改现有源码，使重复月份可以正确累加。

实际练习文件的内容如下，包含重复月份、带逗号的字段和中文：

```csv
month,amount,label
2026-01,19.90,"North, launch"
2026-01,10.10,中文客户
2026-02,2.50,Renewal
2026-02,7.50,Support
```

[原始练习源码](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/4971598a5b14b62207076dd2da4264c139423628/agents-api/fixtures/csv-analysis/aggregate.py)
中的缺陷是同一月份反复执行下面的覆盖赋值，Agent需要修改程序：

```python
totals[row["month"]] = Decimal(row["amount"])
```

输入文件通过 Gateway 上传，附件目标固定为 `/workspace/input/sales.csv`。程序源码和
测试放在练习工程目录，输出放到 `/workspace/outputs/`。这几个路径承担不同职责。

两轮任务的业务断言是：第一轮输出 `month,total`，两个月分别为30.00和10.00；第二轮
继续修改同一文件，加入 `--with-share`，输出占比分别为0.750000和0.250000，同时保留
默认模式及第一轮产物。这些数值是任务合同，第7至8节说明本轮实际断言。

维护者已执行20项smoke回归、52项规格检查、48个模板目录检查和232份文档检查，全部通过。
这是模板交付的本地验证记录，不是普通部署者的前置操作；你可以直接继续部署当前模板。

## 6. 使用公开安装包正常部署：获得稳定 Gateway

当前最终验证使用正式npm CLI0.5.10、公开PyPI client/server0.4.0a7，以及4971598a提交的
recipe0.1.4。仅按普通配置调整应用名称与accessRef，配置文件和CA保存在Docker context之外。
先等待数据库Running及TLS真正on/success，再准备verify-full的DSN和CA引用。

本轮直接使用正常CLI完成Build、Plan与Apply，没有手工驱动Dispatcher或改写收据。
常规命令为：

```bash
cd <TEMPLATES_CHECKOUT>/agents-api
abx app build template.yaml --out .abx/build.json --yes
abx app plan template.yaml --build-receipt .abx/build.json --out .abx/plan.json
abx app apply .abx/plan.json --bindings <PRIVATE_BINDINGS_FILE> --yes
```

本轮截至已收集证据的实际命令结果为：

| 步骤 | 实际退出码 | 耗时/秒 | 真实返回状态 |
| --- | ---: | ---: | --- |
| Build |0 |30.949 |built |
| Plan |0 |1.316 |planned |
| Apply |0 |372.713 |ready，phase=ready |

Build在17:20:16 UTC、Plan在17:22:26 UTC记录完成，[准备摘要](./public-verified-preparation.json)保留两项原结果哈希。
Apply实际在17:30:15.554 UTC记录ready，正常收据包含3个Server侧FC角色与1个Guest模板。
[本轮Apply与核心检查摘要](./public-verified-core-apply.json)记录实际退出码、耗时和检查边界；
ready来自真实候选业务检查及正常稳定入口发布，不是仅凭镜像构建成功推断。

新版host报告仍位于`.abx/agents-smoke-reports/`，每次有独立JSONL与latest快照。
报告只含受限阶段、检查码、HTTP状态和known-cleanup布尔值，不能替代最终Provider独立absence。

## 7. 一个 Gateway 完成两轮真实文件任务

普通业务调用方只需要`AGENTS_API_BASE_URL`和`AGENTS_API_KEY`。前者对应Apply返回的
`endpoint`，后者对应Apply返回的`credentials_file`内的`businessKey`。部署者只分发
businessKey，不分发internalToken、整个凭据文件或Provider管理权限。

正常Apply会自动执行下面的检查，因此完成部署后不需要再手工重复运行。若要在已有部署上
单独检查，可以安全配置这两个环境值后在模板目录运行`python scripts/smoke.py`。例如在部署主机
从私有文件读取业务Key，只传给检查子进程，不把它打印出来：

```bash
export AGENTS_API_BASE_URL='APPLY_RETURNED_ENDPOINT'
export AGENTS_CREDENTIALS_FILE='/absolute/private/APPLY_RETURNED_CREDENTIALS_FILE'
python - <<'PYTHON'
import json, os, subprocess, sys
from pathlib import Path
env = os.environ.copy()
env["AGENTS_API_KEY"] = json.loads(
    Path(env["AGENTS_CREDENTIALS_FILE"]).read_text()
)["businessKey"]
subprocess.run([sys.executable, "scripts/smoke.py"], env=env, check=True)
PYTHON
```

两轮具体HTTP步骤可以直接查看公开的[模板smoke脚本](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/4971598a5b14b62207076dd2da4264c139423628/agents-api/scripts/smoke.py)和
[中文托管API说明](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/4971598a5b14b62207076dd2da4264c139423628/docs/managed-agents-api.zh-CN.md)。

正常Apply的afterReady会执行模板自带的同一脚本：只经Gateway上传CSV、创建Session、
驱动两轮Agent、下载CSV与源码，然后Close/Delete。它通过`/v1/models`发现默认模型，
也可用`AGENTS_API_MODEL`指定已发布的模型ID。第二轮复用同一个Session工作区，修改第一轮已有程序，
加入占比计算并保留默认模式和第一轮产物。

本轮afterReady已经通过：两次真实Qwen Agent turn、输入与CSV下载校验、Close及Delete均完成。
部署验证使用候选Gateway的短期verification key，正常发布后业务调用方使用稳定Gateway与businessKey；
二者都走Server业务HTTP，未要求业务方连接各个Sandbox。

[17条实际host安全检查点](./public-verified-core-smoke-report.jsonl)逐步记录setup、health、输入、两轮任务、
结果下载与清理；最后一条实际报告为：

```json
{"schemaVersion":1,"status":"passed","phase":"complete","code":"passed","cleanup_attempted":true,"cleanup_confirmed":true}
```

## 8. 结果检查与会话释放分别确认

业务脚本已经独立解析下载的CSV，并通过任务合同中的汇总30.00/10.00与第二轮占比
0.750000/0.250000断言。这里提供的是实际断言摘要，不是重新拼接的原始CSV响应。
脚本也下载源码，且不在宿主执行模型生成程序；本轮hook未保留源码原件供文章附件，
所以文章提供当前实际断言摘要，不附未经保存的原始源码或CSV。历史原件仅在工程补充按真实版本展示。

Close与Delete含义不同：Close释放计算并保留历史，Delete删除公开资源。异步Close返回
Operation时，要查询最终状态，不能把一次HTTP202当作停止或资源消失。
模板host报告的cleanup_confirmed只涵盖脚本掌握的公开资源，最终云资源仍须独立核对。

这些断言证明本次两轮任务和下载结果，不把执行报告扩展为所有接口、模型或Provider的完整认证。
额外的私有工程检查不会变成业务客户端必须拥有的Provider凭据。

## 9. 业务客户端只保存统一入口和业务 Key

部署成功后，把收据中的稳定Gateway endpoint和安全保存的businessKey交给业务应用。
每次新建Session不需要再配置Sandbox URL；Server负责分配实例，并将同一Session的后续输入路由到原工作区。
客户端按返回的资源ID查询Session、Turn与Operation，下载所需产物，再Close并Delete。

模板保持Beta，支持范围以`/v1/agent-sandbox/capabilities`及双语README为准。
这篇实践只声明已经完成的正常部署、两轮真实文件任务与释放流程，不声称任意OpenAI SDK、所有模型或Provider均兼容。

## 10. 失败时保留结果与资源记录

不要重复提交结果不确定的创建或Apply。先保留原始收据与安全报告，再按已有记录检查
实际资源和状态；客户端没有收到结果，不等于远端没有执行。

0.1.4保留`.abx/agents-smoke-reports/`中的逐次JSONL与latest快照。运行中的最后检查点
不是完成证明；报告写入失败也不会返回成功。报告不保存模型正文、URL、资源ID或密钥，
未知异常只给受控错误码。

更早版本的失败及排查过程保存在[历史工程补充](https://github.com/Alibaba-Agent-Sandbox/blogs/blob/main/.agents/evidence/verify/2026-11-06-managed-agents-history-supplement.md)，不需要先阅读这些工程记录才能使用模板。

## 11. 清理应用与外置临时资源，并独立确认不存在

应用清理使用正常CLI销毁计划，不手工修改旧ready或失败收据：

```bash
abx app plan --destroy <CURRENT_RECEIPT> --out .abx/destroy.json
abx app destroy .abx/destroy.json --bindings <PRIVATE_BINDINGS_FILE> --yes
```

若drain未完成，保留失败和收据，正常Reconcile后使用新的销毁计划；不把一次ACK当成不存在。
`abx app destroy`不会自动创建或删除PostgreSQL。这里的临时RDS由独立工程流程释放；
自建临时数据库须另行清理，借用或共享数据库、VPC、交换机、安全组、执行角色不能随应用删除。
构建中保留的manual镜像仅按原journal中的本次精确tag处理；空仓库也要先证明本次所有权和无引用。

本轮实际普通Destroy退出0，耗时6.374秒，在17:37:26 UTC确认drain完成、retained为空，
3个FC角色、1个Guest模板及Server镜像的收据清理均confirmed。
随后独立原生查询在17:50:42 UTC确认3个Function和1个Template为受支持的NotFound；
Sandbox清单完整穷尽且匹配本轮范围的数量为0。hook未保留原生Sandbox ID，因此没有声称逐ID查询。

临时RDS在17:43:12.301 UTC通过严格原生零清单确认删除，操作耗时17.992秒，早于本轮绝对截止。
Guest构建的3个精确tag已在17:46:33 UTC完成回收，耗时54.656秒：1个原已不存在，另2个删除，
3个均独立确认absence；原receipt和journal未被改写。两个本轮独占空仓库也已按精确名称处理：Server仓库退出0/42.149秒，Guest仓库退出0/39.724秒，
分别在18:01:36和18:02:31 UTC记录完成。每个仅一次Delete，之后独立原生GET确认受支持的NotFound。
两个原journal均保留完整intent、ack和typedabsence，未按前缀删除其他仓库。

[本次实际部署、两轮任务与清理摘要](./public-verified-core-apply.json)包含各项边界和原件哈希。
这次已知临时云资源已经全部释放；借用的网络、角色与共享资源没有删除。
结束前分别确认业务Session、应用计算、数据库、构建镜像和空仓库，避免把一次脚本成功当成全部清理完成。
