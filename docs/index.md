---
layout: default
title: InterNote 文档
---

# InterNote 文档

InterNote 是一个超轻量级的个人博客生成器，完全基于 GitHub Pages、GitHub Issues 和 GitHub Actions：**写作流程就是提 Issue**，写完自动构建、自动发布，无需本地部署。

## 核心特性

- 文章外观与 GitHub Issues 一致：内置 Primer CSS（随包分发，无外部 CDN）
- TOML 配置 + TOML front matter，pydantic / 解析器双向严格校验（未知键直接报错）
- 系列文章：一条协作者评论就是一个子页面，按 `order` 排序成系列
- 评论系统 [giscus](https://giscus.app)（基于 GitHub Discussions，懒加载）
- 本地站内搜索：构建时生成 `search-index.json`，浏览器端按标题 / 标签 / 日期匹配，无第三方服务
- 文章 URL 恒为 `post/<issue编号>.html`，改标题永不断链；`slug` 可生成短链别名页
- 明暗主题三态切换、文章目录、悬浮工具栏、RSS、自定义 404
- 明暗主题、目录、代码复制等全部零依赖插件，图标服务端渲染

## 文档目录

| 文档 | 内容 |
| --- | --- |
| [快速开始](quickstart.md) | 建站五步走：博客仓库、配置、workflow、Pages、写作 |
| [TOML 配置参考](config.md) | `config.toml` 全部配置段与字段语义 |
| [Front matter 参考](frontmatter.md) | 文章与系列子帖的 front matter 字段、校验规则 |
| [架构说明](architecture.md) | 模块划分、渲染缓存、测试体系、发布流 |
| [开发计划](plan.md) | 已完成里程碑、设计定论、候选方向 |

## 最小可用示例

文章就是一个 Issue（标题 = 文章标题，正文 = Markdown）：

```markdown
+++
date = 2026-10-13
+++

正文 Markdown，与在 GitHub 上书写完全一致。
```

一条带 `order` 的协作者评论自动成为系列子页：

```markdown
+++
order = 1
+++
# 第一章 标题

本章内容。
```

配置与 workflow 各复制一份到博客仓库即可建站，见[快速开始](quickstart.md)。
