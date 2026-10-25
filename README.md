# Agent Sandbox 博客 · Blogs

[Agent Sandbox](https://www.agent-sandbox.cn) 的博客、案例和教程的源文件。文章在这里写，官网在构建时读取，发布到 [www.agent-sandbox.cn/blog/](https://www.agent-sandbox.cn/blog/)。

The source of the Agent Sandbox blog: cases, tutorials, announcements and engineering notes. Posts are written here; the website reads them at build time and publishes them at [www.agent-sandbox.cn/en/blog/](https://www.agent-sandbox.cn/en/blog/).

## 当前用法与历史案例 · Current guidance and reproducible cases

新项目从[开始使用](https://www.agent-sandbox.cn/start/)选择安装与调用入口。当前 CLI 为 [0.5.6](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/releases/tag/v0.5.6)，Python client/server 为 [0.4.0a6 alpha](https://github.com/Alibaba-Agent-Sandbox/python-sdk/releases/tag/v0.4.0a6)。默认 `base` 案例通过文件与进程 API 执行脚本；命名应用命令、持久解释器与 PTY 按各自的实际接口说明使用。

For new projects, follow [Get started](https://www.agent-sandbox.cn/en/start/). Current releases are CLI 0.5.6 and Python client/server 0.4.0a6 alpha. The default `base` walkthrough uses file and process APIs; named application commands, persistent interpreters and PTY have separate interfaces and prerequisites.

五篇 `developer-journey-*` 案例的当前步骤和可运行附件统一使用 CLI 0.5.6、Python 0.4.0a6。历史 `proof/` 与 `evidence/` 子目录保留各次实际运行的原始版本与范围；最新运行结果见各案例的新记录，不能把旧记录当作新发行版证明。

The five `developer-journey-*` cases use CLI 0.5.6 and Python 0.4.0a6 in their current instructions and runnable attachments. Historical `proof/` and `evidence/` directories retain their original executed versions and scope. New runs receive separate evidence; an old receipt does not prove a new release.

当前决策与验证入口见 [`.agents/README.md`](.agents/README.md)。维护文章时同步已有翻译，区分现行用法与固定版本复现，修改文章源文件后由官网构建同步。

See [`.agents/README.md`](.agents/README.md) for current decisions and verification. Keep existing translations aligned, distinguish current usage from pinned reproductions, and update article sources here before the website ingests them.

## 目录结构 · Layout

```text
blogs/
├── README.md
├── posts/                              每篇文章一个目录，目录名就是网址里的 slug
│   └── agent-runs-untrusted-code/         → /blog/agent-runs-untrusted-code/
│       ├── index.zh.md                       中文正文
│       ├── index.en.md                       英文正文（可以只写一种语言）
│       ├── cover.svg                         可选封面
│       └── pipeline.png                      文章用到的图片，放在同一目录
├── _template/                          复制它来开始一篇新文章
│   ├── index.zh.md
│   └── index.en.md
├── scripts/validate.py                 检查头部信息，PR 里会自动运行
└── .github/workflows/
    ├── validate.yml                    PR 上校验
    └── notify-website.yml              合并到 main 后通知官网重新构建
```

## 写一篇文章 · Write a post

```bash
cp -r _template posts/my-first-post     # 目录名用小写加连字符
$EDITOR posts/my-first-post/index.zh.md
python -m pip install pyyaml && python scripts/validate.py
```

然后提 PR。合并到 `main` 后官网会重新构建，新文章出现在博客列表里。

### 头部信息 · Front matter

| 字段 | 必填 | 说明 |
|---|---|---|
| `title` | 是 | 标题 |
| `summary` | 是 | 一到两句摘要，显示在卡片和搜索结果里，不超过 300 字 |
| `date` | 是 | `2026-10-14`。中英文两份要相同 |
| `category` | 是 | `case` 案例、`tutorial` 教程、`announcement` 发布、`engineering` 工程笔记 |
| `tags` | 是 | 1 到 5 个，小写加连字符，例如 `[python, security]` |
| `authors` | 是 | GitHub 用户名列表 |
| `cover` | 否 | `./cover.svg`。不写则按 slug 生成渐变封面 |
| `featured` | 否 | `true` 时作为博客首页的大卡片。多篇都设时取最新的一篇 |
| `draft` | 否 | `true` 时不会出现在网站上 |

### 语言 · Languages

- `index.zh.md` 和 `index.en.md` 至少写一个。只写一种时，另一种语言的博客列表里仍会显示这篇文章，打开后顶部提示"仅有原文语言"。
- 两种语言都有时，`date` 和 `category` 必须一致，校验脚本会检查。

### 写作规范 · Style

- 先说读者会得到什么，再讲步骤。一篇文章解决一件事。
- 用二级标题（`##`）分节，官网会据此生成目录。
- 代码块标注语言。命令必须能直接复制运行，密钥写成 `<YOUR_API_KEY>`，不要提交真实密钥。
- 写你验证过的事实。没有在真实后端上跑过的，要明说。
- 图片和文件放在文章目录里，用相对路径引用，例如 `![流程](./pipeline.png)`。
- 链接到官网或 Registry 的页面时，中文用不带语言前缀的路径（`/start/`），英文用 `/en/start/`。

### 案例

[`posts/agent-runs-untrusted-code`](posts/agent-runs-untrusted-code/index.zh.md) 是一篇完整的案例：有头部信息、分节、可运行的代码和限制说明。新文章可以照它的结构来。

## 官网怎么读取 · How the website reads this repo

官网的构建脚本 `npm run sync:blogs` 把 `posts/` 复制到 `src/content/blog/`，文章里的相对图片路径会改写成站内路径。官网只读取 `main`。合并到 `main` 后，`notify-website.yml` 会向官网仓库发送 `blogs-updated` 事件，官网的 Deploy 工作流随之重新构建。

这需要在本仓库设置 Actions secret `WEBSITE_DISPATCH_TOKEN`（对 `website` 仓库有 `contents:write` 权限的令牌）。没有设置时，手动运行官网的 Deploy 工作流即可发布。

## Related projects / 相关项目

| | |
|---|---|
| Official site / 官网 | https://www.agent-sandbox.cn |
| Registry / 模板与提供方目录 | https://registry.agent-sandbox.cn |
| CLI | https://github.com/Alibaba-Agent-Sandbox/agent-sandbox |
| Python SDK | https://github.com/Alibaba-Agent-Sandbox/python-sdk |
