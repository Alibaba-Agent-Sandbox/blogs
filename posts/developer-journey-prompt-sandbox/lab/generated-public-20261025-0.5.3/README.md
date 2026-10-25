# abx-nl-python-add-68cccd

一个提供加法运算的Python沙箱模板。

## 功能说明

该模板提供了一个 `add` 命令，可以接收两个整数参数并返回它们的和。

## 使用方法

### CLI 调用示例

```bash
# 列出可用命令
abx --json sandbox command list <sandbox_id>

# 调用 add 命令
abx --json sandbox command run <sandbox_id> add --json-args '{"a": 5, "b": 3}'
```

### HTTP 调用示例

```bash
# 调用 add 命令
curl -X POST APPLICATION_URL/commands/add \
  -H "Authorization: Bearer $ABX_SERVER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"a": 5, "b": 3}'
```

## 环境变量

- `ABX_SERVER_TOKEN`: 应用访问令牌，由运行环境提供

## 参数说明

- `a` (integer): 第一个整数
- `b` (integer): 第二个整数

## 返回值

- 返回两个整数的和