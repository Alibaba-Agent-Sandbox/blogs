# Agent Sandbox Blog

**English** | [中文](README.zh-CN.md)

Tutorials, practical cases and engineering articles about building AI agents with Agent Sandbox. This repository owns article source files and assets; the official website publishes them.

[Read the blog](https://www.agent-sandbox.cn/en/blog/) · [Browse source posts](posts/) · [Get started with Agent Sandbox](https://www.agent-sandbox.cn/en/start/)

> **Preview release:** Agent Sandbox is currently in preview and may introduce breaking changes. The stable **1.0.0** release is expected on **November 15, 2026**. Stay tuned!

## Find an article

Each article lives in `posts/<slug>/`, with `index.en.md`, `index.zh.md`, or both. Images, runnable examples and other attachments stay alongside the article. Follow each post's stated versions and provider requirements when reproducing an example.

## Write a post

Start from the template:

```bash
cp -r _template posts/my-first-post
```

Edit `index.en.md` or `index.zh.md` and validate:

```bash
python -m pip install pyyaml
python scripts/validate.py
```

Open a pull request when ready. Set `draft: true` while the article is unfinished. See [CONTRIBUTING.md](CONTRIBUTING.md) for front matter, language rules, assets and local preview.

## Publication

The [website repository](https://github.com/Alibaba-Agent-Sandbox/website) imports posts during its build. Non-draft articles are published after the website deploys. A post may be written in one language; the site identifies when only the original language is available.

## Community

Join the **Agent Sandbox 开发者工具交流群** on DingTalk to discuss usage and share feedback. [Join the group](https://qr.dingtalk.com/action/joingroup?code=v1,k1,kIZr4Ai7sYm4U0xoz1p1QSlgoBHeoi/kE5TkIXeFCR4=&_dt_no_comment=1&origin=11) or search for group number **213605001586**.

Scan the QR code with DingTalk:

<a href="https://qr.dingtalk.com/action/joingroup?code=v1,k1,kIZr4Ai7sYm4U0xoz1p1QSlgoBHeoi/kE5TkIXeFCR4=&amp;_dt_no_comment=1&amp;origin=11"><img src="assets/dingtalk-group.png" alt="DingTalk group QR code" width="235" /></a>

## Contributing

Article corrections and new posts belong here. Website rendering and layout changes belong in [website](https://github.com/Alibaba-Agent-Sandbox/website). Follow the [contributor guide](CONTRIBUTING.md) for writing and review; report article problems in [Issues](https://github.com/Alibaba-Agent-Sandbox/blogs/issues).
