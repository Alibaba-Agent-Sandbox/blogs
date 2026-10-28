# Agent Sandbox Blog

**English** | [中文](README.zh-CN.md)

Tutorials, practical cases and engineering articles about building AI agents with Agent Sandbox. This repository owns article source files and assets; the official website publishes them.

[Read the blog](https://www.agent-sandbox.cn/en/blog/) · [Browse source posts](posts/) · [Get started with Agent Sandbox](https://www.agent-sandbox.cn/en/start/)

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

## Contributing

Article corrections and new posts belong here. Website rendering and layout changes belong in [website](https://github.com/Alibaba-Agent-Sandbox/website). Follow the [contributor guide](CONTRIBUTING.md) for writing and review; report article problems in [Issues](https://github.com/Alibaba-Agent-Sandbox/blogs/issues).
