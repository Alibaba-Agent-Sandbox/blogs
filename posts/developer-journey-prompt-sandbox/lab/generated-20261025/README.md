# Python Add 沙箱模板

这是一个用于执行两个整数相加操作的Python沙箱模板。

## 功能

提供一个 `add` 命令，接收两个整数参数并返回它们的和。

## 使用方式

### CLI 调用示例

```bash
# 列出可用命令
abx --json sandbox command list <sandbox_id>

# 调用 add 命令
abx --json sandbox command run <sandbox_id> add --json-args '{"a": 5, "b": 3}'
```

### HTTP 调用示例

```bash
# 使用 curl 调用
curl -X POST APPLICATION_URL/commands/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ABX_SERVER_TOKEN" \
  -d '{"a": 5, "b": 3}'
```

## 环境变量

- `ABX_SERVER_TOKEN` (可选): 应用访问令牌，用于API鉴权

## 响应格式

成功时返回 JSON 对象：
```json
{"result": 8}
```

## 部署说明

此模板使用 `agent-sandbox-server` 协议，通过 HTTP 接口提供服务。部署后可通过平台提供的 URL 访问。