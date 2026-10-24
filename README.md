# Agent Sandbox 博客 · Blogs

[Agent Sandbox](https://www.agent-sandbox.cn) 的博客、案例和教程的源文件。文章在这里写，官网在构建时读取，发布到 [www.agent-sandbox.cn/blog/](https://www.agent-sandbox.cn/blog/)。

The source of the Agent Sandbox blog: cases, tutorials, announcements and engineering notes. Posts are written here; the website reads them at build time and publishes them at [www.agent-sandbox.cn/en/blog/](https://www.agent-sandbox.cn/en/blog/).

## 当前用法与历史案例 · Current guidance and reproducible cases

新项目从[开始使用](https://www.agent-sandbox.cn/start/)选择安装与调用入口。当前 CLI 为 [0.4.17](https://github.com/Alibaba-Agent-Sandbox/agent-sandbox/releases/tag/v0.4.17)，Python client/server 为 [0.3.1a5 alpha](https://github.com/Alibaba-Agent-Sandbox/python-sdk/releases/tag/v0.3.1a5)。默认 `base` 案例通过文件与进程 API 执行脚本；命名应用命令、持久解释器与 PTY 按各自的实际接口说明使用。

For new projects, follow [Get started](https://www.agent-sandbox.cn/en/start/). Current releases are CLI 0.4.17 and Python client/server 0.3.1a5 alpha. The default `base` walkthrough uses file and process APIs; named application commands, persistent interpreters and PTY have separate interfaces and prerequisites.

五篇 `developer-journey-*` 案例保留实际运行时使用的 CLI 0.4.12、Python 0.3.1a2 及各自固定的沙箱内依赖。升级当前安装指南不会改写旧脚本、生成结果或实验记录，也不表示它们已在新版重新运行。模板目录的后续默认启动矩阵另见 [46 个源码模板的双平台记录](https://github.com/Alibaba-Agent-Sandbox/awesome-templates/blob/78c30fbbd186cb59c3a0f0abd9fdf85b10c84b35/.agents/evidence/verify/2026-10-24-public-template-matrix.md)；不能替代案例中的具体模型或业务任务。

The five `developer-journey-*` cases retain their executed CLI 0.4.12, Python 0.3.1a2 and individually pinned in-sandbox dependencies. Updating current guidance does not change their runnable attachments or historical results, or claim that the cases ran again on newer releases. Later template smoke coverage is recorded by the template repository and does not establish the cases' model or business outcomes.

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
