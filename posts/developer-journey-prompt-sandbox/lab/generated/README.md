# abx-nl-python-add-a2d900

Python 沙箱模板，提供 `add` 命令：接收两个整数 `a`、`b`，返回它们的和。

## 模板用途

镜像内常驻 `agent-sandbox-server` HTTP 服务（端口 9000），业务命令通过平台返回的应用绑定访问：

- `add`：`POST /commands/add`，请求体为扁平 JSON `{"a": <int>, "b": <int>}`，返回 `{"result": <int>}`。

服务入口是 `/home/user/app/commands.py`，由平台 start_cmd 加载：

- start_cmd: `agent-sandbox-server serve --port 9000 --commands /home/user/app/commands.py`
- ready_cmd: `agent-sandbox-server healthcheck --port 9000`

## 构建方式（本次发布）

本次 `template.yaml` 使用 `build.mode: steps`：平台只接收 `base.image` 与类型化 steps，
**不需要本地 Docker、构建上下文或 ACR 镜像推送**。`commands.py` 的源码在 RUN 步骤中以
base64 解码写入绝对路径 `/home/user/app/commands.py`，最后一步用 `python3 -m py_compile` 校验语法，
并 `chown -R user:user /home/user/app` 保证运行用户 `user` 可写工作目录。

仓库中的 `Dockerfile` 保留供审阅与以后本地 `docker build`，本次发布不参与构建。

依赖解析策略：

- 无第三方业务依赖，Python 需求为标准库即可；不安装额外系统包，不重新安装 Python。
- `agent-sandbox-server==0.3.1a1` 是**已发布的 alpha 测试版**，用固定命令从官方索引安装：
  `python3 -m pip install --index-url https://pypi.org/simple --no-cache-dir "agent-sandbox-server==0.3.1a1"`。
- 未指定版本的用户依赖交由目标解释器上的 pip 解析兼容版本，不硬编码镜像源、不复制历史 pin。
- 验收时请记录容器内实际 `python3 --version` 与 `pip show agent-sandbox-server` 的版本；
  若用户指定版本与目标解释器不兼容，应报错而不是静默换版本。

## 环境变量

| 名称 | 说明 | 默认值 |
| --- | --- | --- |
| `LANG` | 容器区域设置，避免非 UTF-8 输出问题 | `C.UTF-8` |
| `ABX_SERVER_PORT` | 服务监听端口，须与 `ports` 中的 9000 一致 | `9000` |
| `ABX_SERVER_TOKEN` | 可选。设置后应用请求需 `Authorization: Bearer <token>`；仅 `/health` 免应用鉴权 | 空（不启用应用鉴权） |

密钥类变量只在 `template.yaml` 的 `env` 中列名字，不写入镜像。

## 调用示例

### CLI

先查看实际注册了哪些命令：

```bash
abx sandbox command list <sandbox_id>
```

JSON 模式（返回 `{"result": <返回值>}`）：

```bash
abx --json sandbox command run <sandbox_id> add --json-args '{"a": 3, "b": 4}'
# {"result": 7}
```

省略 `--json` 时只输出返回值：

```bash
abx sandbox command run <sandbox_id> add --json-args '{"a": 3, "b": 4}'
# 7
```

### HTTP（curl）

`APPLICATION_URL` 必须取自 provider 返回的**实际应用绑定**，不要手拼沙箱域名或猜测网关 URL：

```bash
curl -sS -X POST "$APPLICATION_URL/commands/add" \
  -H 'Content-Type: application/json' \
  -d '{"a": 3, "b": 4}'
# {"result": 7}
```

健康检查与能力查询：

```bash
curl -sS "$APPLICATION_URL/health"
curl -sS "$APPLICATION_URL/commands"
```

认证说明：绑定网关要求的凭据（如 `X-Access-Token`）与应用自身的 `Authorization: Bearer <ABX_SERVER_TOKEN>`
是两套**相互独立**的机制，请按实际绑定分别传递。设置了 `ABX_SERVER_TOKEN` 时，
`/capabilities`、`/commands`、`/commands/add` 都需要应用 token；只有 `/health` 免应用鉴权。
如果绑定本身启用了网关认证，未带凭据的请求会被网关拒绝，上面的 URL 示例不构成通用可用的免认证路径。
