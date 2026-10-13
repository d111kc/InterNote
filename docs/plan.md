---
layout: default
title: 开发计划
---

# 开发计划

## 已完成里程碑

| 里程碑 | 内容 |
| --- | --- |
| 测试离线化 | pytest 全离线：conftest autouse 打桩网络调用；FixtureRepo 镜像 PyGithub 表面 |
| 友链与申请流 | `links.html` 友链页 + 页内申请表单 + giscus 承接申请评论 |
| 代码复制 | `code-copy.js` 代码块一键复制（复制后反馈态） |
| 品牌 | 统一品牌拼写 `InterNote`（小写标识符不动） |
| Release v0.1.0 | 首个 release；workflow 模板以 `INTERNOTE_REF` 固定版本 |
| `refs` / `repo` | front matter 参考资料与源码链接，元信息区渲染，系列子帖继承 |
| UI 重设计 | 站点视觉重构：设计令牌、导航、页脚、列表布局 |
| 系列子帖 | 协作者评论即子页面（`order` 排序、面包屑、上一篇/下一篇、系列折叠列表） |
| about 多模式 | `[site].about` 四模式：`issue`（默认）/ `readme` / `mixed` / `none`；README 渲染走共享缓存 |
| 本地搜索 | 第三方搜索替换为本地方案：构建时生成 `search-index.json`，浏览器端标题/标签/日期匹配，无第三方服务、无配置段 |
| 文档站 | 本站点：GitHub Pages + Jekyll 默认主题，从 `docs/` 部署 |

## 设计定论（不再讨论）

- **效率模型**：纯事件驱动构建（无 cron 定时）+ 单 issue 增量 + 两层渲染缓存。编辑一篇恰好一次 `/markdown` 调用，未变内容零调用。启发式子帖刷新与「不回提交产物」方案均已评估并否决
- **README 渲染**：只支持普通的 GitHub README，不做相对路径静态资源改写（方案已实现后回退）；README 内相对资源按站点自身地址解析
- **搜索**：本地、始终开启，刻意不设配置段；唯一的客户端数据文件是 `search-index.json`，记录由生成器预排序
- **校验哲学**：所有配置与 front matter 未知键都是硬错误；宁可构建失败也不静默忽略
- **URL 稳定**：规范地址恒为 `post/<issue编号>.html`，`slug` 只添加别名页

## 候选方向（未排期）

- 补齐 `cli.py` 与 `renderer.py` 的测试覆盖
- RSS 能力增强（全文输出、分类订阅）
- 插件系统的可配置化（现有 7 个插件零依赖、固定行为）
- 主题自定义机制（当前仅 `[layout]` 注入点，无完整主题包概念）
- 图片懒加载、文章目录的多级折叠等阅读体验项
