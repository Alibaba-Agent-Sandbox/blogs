# Agent Sandbox 博客

**中文** | [English](README.md)

围绕 Agent Sandbox 构建 AI Agent 的教程、实践案例与工程文章。本仓库维护文章源文件和资产，由官网构建并发布。

[阅读博客](https://www.agent-sandbox.cn/blog/) · [浏览文章源码](posts/) · [开始使用 Agent Sandbox](https://www.agent-sandbox.cn/start/)

## 查找文章

每篇文章位于 `posts/<slug>/`，包含 `index.zh.md`、`index.en.md` 或两者。图片、可运行示例和其他附件与文章放在同一目录。复现案例时，请按文章说明使用对应版本并准备提供方环境。

## 写一篇文章

从模板开始：

```bash
cp -r _template posts/my-first-post
```

编辑 `index.zh.md` 或 `index.en.md`，然后校验：

```bash
python -m pip install pyyaml
python scripts/validate.py
```

文章就绪后提交 PR，尚未完成时设置 `draft: true`。头部字段、语言规则、资产和本地预览方法见[贡献指南](CONTRIBUTING.md)。

## 发布

[官网仓库](https://github.com/Alibaba-Agent-Sandbox/website)在构建时读取文章，非草稿文章在官网部署后发布。允许只写一种语言，网站会提示仅有原文的情况。

## 参与贡献

文章纠正与新文章在这里提交，网站渲染和布局修改在 [website](https://github.com/Alibaba-Agent-Sandbox/website)提交。写作和评审要求见[贡献指南](CONTRIBUTING.md)，文章问题请提交到 [Issues](https://github.com/Alibaba-Agent-Sandbox/blogs/issues)。
