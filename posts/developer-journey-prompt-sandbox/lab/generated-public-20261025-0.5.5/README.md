# Python Add Sandboxed Application

这是一个Python沙箱应用，提供一个add命令用于计算两个整数的和。

## 功能说明

- 提供`add`命令，接收两个整数参数并返回它们的和

## 环境变量

- `ABX_SERVER_TOKEN`: 应用访问令牌（由平台自动注入）

## 调用示例

### CLI方式

列出可用命令：
```bash
abx --json sandbox command list <sandbox_id>
```

调用add命令：
```bash
abx --json sandbox command run <sandbox_id> add --json-args '{"a": 5, "b": 3}'
```

### HTTP方式

使用curl调用（需要替换APPLICATION_URL为实际地址）：
```bash
curl -X POST APPLICATION_URL/commands/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ABX_SERVER_TOKEN" \
  -d '{"a": 5, "b": 3}'
```

响应格式：
```json
{"result": 8}
```