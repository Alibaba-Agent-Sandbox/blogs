# abx-nl-python-add-dcd7e0

Python 沙箱模板：镜像内常驻 `agent-sandbox-server` HTTP 服务（端口 9000），对外提供 `add` 命令，
接收两个整数 `a`、`b`，返回它们的和。

## 命令

| 名字 | 参数 | 返回 |
| --- | --- | --- |
| `add` | `a: int`（必填）、`b: int`（必填） | `int`，两数之和 |

命令通过 `POST /commands/add` 调用，body 为扁平 JSON，响应形如 `{"result": <返回值>}`。
内置接口始终可用：`GET /health`、`GET /capabilities`、`GET /commands`。
本模板未开启任何可选能力组（DEV_TOOLS / BROWSER / AGENTS 保持关闭）。

## 环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `LANG` | `C.UTF-8` | 运行环境编码，`template.yaml` 的 `env` 已声明 |
| `ABX_SERVER_PORT` | `9000` | `commands.py` 直接作为主程序运行时的监听端口；平台 start_cmd 已显式传 `--port 9000` |
| `ABX_SERVER_TOKEN` | 空（不设置） | 设置后，应用请求需带 `Authorization: Bearer <ABX_SERVER_TOKEN>`；仅 `/health` 免应用鉴权 |

`add` 命令本身不需要任何业务环境变量或密钥。

## 调用示例

### CLI

先查看沙箱内实际注册的命令：

```bash
abx sandbox command list <sandbox_id>
```

调用 `add`（JSON 模式返回 `{"result": <返回值>}`）：

```bash
abx --json sandbox command run <sandbox_id> add --json-args '{"a": 17, "b": 25}'
# {"result": 42}
```

省略 `--json` 时只输出返回值：

```bash
abx sandbox command run <sandbox_id> add --json-args '{"a": 17, "b": 25}'
# 42
```

### HTTP（curl）

`APPLICATION_URL` 必须是实际部署后 provider 返回的应用绑定地址，不要手工拼接 sandbox 域名或猜测网关 URL：

```bash
curl -sS -X POST "$APPLICATION_URL/commands/add" \
  -H 'Content-Type: application/json' \
  -d '{"a": 17, "b": 25}'
# {"result": 42}
```

该绑定的网关认证与应用认证相互独立，需按实际情况分别传递：

- 网关侧：若绑定要求 `X-Access-Token`，加上 `-H "X-Access-Token: $ACCESS_TOKEN"`；
- 应用侧：若镜像设置了 `ABX_SERVER_TOKEN`，加上 `-H "Authorization: Bearer $ABX_SERVER_TOKEN"`（`GET /health` 除外）。

未携带绑定所要求的凭据时请求会被拒绝，上面的无认证示例只在绑定确实不要求认证时可用。

## 构建方式

本次发布使用平台 `build.mode: steps`：`template.yaml` 里内联了类型化构建步骤
（`USER root` → 安装依赖 → 写入 `/home/user/app/commands.py` → 语法检查并 `chown` → `WORKDIR` → `USER user`），
源码以 base64 形式写入镜像。**无需本地 Docker，也无需推送 ACR**；仓库中的 `Dockerfile` 仅供审阅和以后本地构建。

- 基础镜像：`fc-e2b-registry.cn-hangzhou.cr.aliyuncs.com/runtime/base:v0.0.49`（逐字固定，区域需与沙箱区域一致）。
- 依赖解析策略：基础镜像已带 `python3`，不重复 apt 安装 Python，也不假定其具体版本；
  本模板没有第三方业务依赖，唯一的安装项是 `agent-sandbox-server==0.3.1a1`（**alpha 预发布版**），
  并强制使用 `--index-url https://pypi.org/simple`，避免镜像源尚未同步该 alpha 版本。
  如后续新增依赖，应由目标解释器上的 pip 自行解析兼容版本；有官方 wheel 的库用 `--only-binary=:all:` 安装。
- 启动由平台执行，不写 `CMD` / `ENTRYPOINT`：
  - `start_cmd`: `agent-sandbox-server serve --port 9000 --commands /home/user/app/commands.py`
  - `ready_cmd`: `agent-sandbox-server healthcheck --port 9000`
- 资源：`cpu: 2`、`memory: 4096`（MB）；端口：`9000`；运行用户 `user`，工作目录 `/home/user/app`。

验收时请记录实际使用的 Python 版本与 `agent-sandbox-server` 版本。

## 文件

- `Dockerfile` — 本地构建用的等价镜像定义
- `commands.py` — `agent_sandbox.server` 服务入口，注册 `add` 命令
- `template.yaml` — 模板清单（JSON 格式的合法 YAML），含 `build.steps`
- `README.md` — 本文档
