---
title: 官网和 Registry 改版：同一套设计，一个博客
summary: 官网和 Registry 现在用同一套设计系统、都有中英文，内容来自仓库里的真实数据。官网多了这个博客，用来放案例、教程和发布说明。
date: 2026-10-14
category: announcement
tags: [website, registry, blog]
authors: [Alibaba-Agent-Sandbox]
---

官网（www.agent-sandbox.cn）和 Registry（registry.agent-sandbox.cn）这次一起改版。

## 变化

- **同一套设计。** 两个站共用一个 `ui/` 目录：颜色、字体、卡片、页头页脚、深浅色主题和脚本。页头的"官网 | Registry"开关可以在两边来回切换。
- **中英文。** 中文在 `/`，英文在 `/en/`，同一页可以一键切换。
- **内容来自真实数据。** Registry 从各仓库生成模板、提供方和文档页，并发布 SDK 读取的 `providers/index.json`。官网的提供方对比页取自 Registry 的目录，不是手写的。
- **Astro 静态站点。** 两个站都是 Astro 构建出来的静态文件。

## 博客

这个博客本身的内容放在 [blogs](https://github.com/Alibaba-Agent-Sandbox/blogs) 仓库：一篇文章一个目录，Markdown 加一段头部信息。合并到 `main` 之后，官网重新构建就会出现新文章。

想投稿案例或教程，看仓库 README 里的目录结构和写作规范，按模板新建一个目录，提 PR 即可。
