# Agent Sandbox 博客

**中文** | [English](README.md)

围绕 Agent Sandbox 构建 AI Agent 的教程、实践案例与工程文章。本仓库维护文章源文件和资产，由官网构建并发布。

[阅读博客](https://www.agent-sandbox.cn/blog/) · [浏览文章源码](posts/) · [开始使用 Agent Sandbox](https://www.agent-sandbox.cn/start/)

> **预览版说明：** Agent Sandbox 目前处于预览阶段，可能会有不兼容变更。预计于 **2026 年 11 月 15 日**发布 **1.0.0 正式版**，敬请期待！

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

## 交流与反馈

欢迎加入 **Agent Sandbox 开发者工具交流群**，交流使用经验、分享建议与反馈。[点击加入钉钉群](https://qr.dingtalk.com/action/joingroup?code=v1,k1,LSusypYdoGm4U0xoz1p1QSlgoBHeoi/kgpsl4uQ8qus=&_dt_no_comment=1&origin=1)，或搜索钉钉群号 **213605001586**。

也可以使用钉钉扫描二维码加入：

<a href="https://qr.dingtalk.com/action/joingroup?code=v1,k1,LSusypYdoGm4U0xoz1p1QSlgoBHeoi/kgpsl4uQ8qus=&amp;_dt_no_comment=1&amp;origin=1"><img src="assets/dingtalk-group.jpg" alt="钉钉交流群二维码" width="235" /></a>

## 参与贡献

文章纠正与新文章在这里提交，网站渲染和布局修改在 [website](https://github.com/Alibaba-Agent-Sandbox/website)提交。写作和评审要求见[贡献指南](CONTRIBUTING.md)，文章问题请提交到 [Issues](https://github.com/Alibaba-Agent-Sandbox/blogs/issues)。
