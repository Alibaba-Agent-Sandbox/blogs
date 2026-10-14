---
title: The website and the Registry relaunch with one design and a blog
summary: The website and the Registry now share one design system, both come in English and Chinese, and their content comes from real repository data. The website also gains this blog for cases, tutorials and release notes.
date: 2026-10-14
category: announcement
tags: [website, registry, blog]
authors: [Alibaba-Agent-Sandbox]
---

The website (www.agent-sandbox.cn) and the Registry (registry.agent-sandbox.cn) were rebuilt together.

## What changed

- **One design.** Both sites share a single `ui/` directory: colors, type, cards, header and footer, light and dark themes, and scripts. The Website | Registry switch in the header moves you between them.
- **English and Chinese.** Chinese lives at `/`, English at `/en/`, and every page can be switched in one click.
- **Content from real data.** The Registry generates template, provider and docs pages from the repositories and publishes the `providers/index.json` the SDK reads. The website's provider comparison comes from the Registry catalog rather than being typed by hand.
- **Astro static sites.** Both sites are static files built by Astro.

## The blog

The content of this blog lives in the [blogs](https://github.com/Alibaba-Agent-Sandbox/blogs) repository: one directory per post, Markdown plus a block of front matter. After a merge to `main` the website rebuilds and the new post appears.

To contribute a case or a tutorial, read the directory layout and the writing rules in the repository README, create a directory from the template and open a pull request.
