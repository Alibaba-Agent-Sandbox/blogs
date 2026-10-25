# Python Add A B Sandboxed Template

这是一个用于计算两个整数之和的Python沙箱模板。

## 功能

提供一个`add`命令，接收两个整数参数`a`和`b`并返回它们的和。

## 使用方法

### CLI调用示例

```bash
# 列出所有可用命令
abx --json sandbox command list <sandbox_id>

# 调用add命令
abx --json sandbox command run <sandbox_id> add --json-args '{"a": 5, "b": 3}'
```

### HTTP调用示例

```bash
# 使用curl调用（需要替换APPLICATION_URL为实际URL）
curl -X POST APPLICATION_URL/commands/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ABX_SERVER_TOKEN" \
  -d '{"a": 5, "b": 3}'
```

## 环境变量

- `ABX_SERVER_TOKEN`: 应用访问令牌，由平台自动注入

## 响应格式

成功时返回JSON格式：
```json
{"result": 8}
```

## 部署要求

- CPU: 2核
- 内存: 4096MB
- 端口: 9000