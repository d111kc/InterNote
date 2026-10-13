---
layout: default
title: Front matter 参考
---

# Front matter 参考

文章与系列子帖的正文都可以用 `+++` 围栏开头携带 TOML 元数据，构建时在渲染前剥离：

```markdown
+++
date = 2026-10-13
draft = false
+++
正文从这里开始。
```

## 设计规则

- **TOML 而非 YAML**：解析器走标准库 `tomllib`，零额外依赖
- **`+++` 而非 `---`**：`---` 与 Markdown 分隔线（thematic break）同形，置于正文开头有歧义
- **未知键直接报错**：拼错的字段名让构建失败，而不是被静默忽略——作者没有任何其他信号能发现手误
- **容忍 CRLF**：GitHub 存储 Issue 正文用 CRLF 行尾，解析器会剥离行尾 `\r`
- **幂等**：已剥离过 front matter 的正文再次解析是无操作（fixture 构建依赖这一点）

## 文章字段（Issue 正文）

| 字段 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `date` | TOML 日期时间 / Unix 时间戳 / ISO 字符串 | Issue 创建时间 | 发布日期与排序键。无时区时按 UTC+8（站点固定时区）解释 |
| `draft` | bool | `false` | `true` = 草稿：不发布；增量构建会同步下线该篇（清页面、列表、RSS、搜索索引） |
| `comments` | bool | `true` | `false` = 该页不渲染 giscus 评论区。系列文章中**父级 `false` 令整个系列关闭评论** |
| `pinned` | bool | — | 置顶：覆盖 GitHub 的 pin 时间线事件，直接驱动列表的 `top` 排序键——无需仓库维护权限也能置顶 |
| `slug` | string | — | 生成根目录**别名页**（如 `slug = "about"` → `about.html`），meta refresh + `location.replace` 重定向到规范页 `post/<编号>.html`，便于分享短链 |
| `refs` | 表数组 `[{name, url}]` | — | 「参考资料」链接列表，渲染在页面元信息区。系列子帖继承父级 |
| `repo` | URL 字符串 | — | 「源码」链接，渲染在页面元信息区。系列子帖继承父级 |

`url` 类字段必须是 `http://` 或 `https://` 开头的非空字符串，否则构建失败。

### 不可覆盖项（写了就报错）

- `title`：标题永远是 Issue 标题
- `description`：摘要永远从正文派生
- `labels`：标签永远由 GitHub Issue labels 驱动（标签页与标签颜色都来自它；无标签的文章归入 `default`）

### `slug` 约束

- 规范地址永远是 `post/<issue编号>.html`，slug **只添加**别名页，改名不断链
- 保留名被拒绝：`index`、`post`、`tag`、`rss`、`page<数字>` 等站点保留路径（见 `frontmatter.py` 的 `RESERVED_SLUGS`）

## 系列子帖字段（协作者评论）

一条**协作者评论**（OWNER / COLLABORATOR / MEMBER）在以下任一条件成立时成为系列子页：

- 正文以 `+++` front matter 块开头
- 正文以裸 `# ` 一级标题开头（标题被消费为页面标题，不重复渲染）

`##` 开头或纯文本的评论是普通评论，不生成页面。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `title` | string | 页面标题；缺省取正文首个 `# ` 一级标题（该标题随即从正文移除）。两者皆无则构建失败——避免系列列表出现空行 |
| `order` | int | 系列内排序键 |
| `refs` / `repo` | 同文章 | 自己的值优先，缺省继承父级 Issue |

```markdown
+++
order = 1
+++
# 第一章 标题

本章内容。
```

> 只有当父级 Issue `comments > 0` 时全量构建才会拉取评论列表；编辑评论不会改变评论数，因此对已评论 Issue 的刷新依靠编辑事件触发增量构建。

## URL 结构

| 页面 | 地址 | 说明 |
| --- | --- | --- |
| 文章 | `post/<issue编号>.html` | 规范地址，永不变化 |
| slug 别名 | `<slug>.html` | 根目录重定向页（noindex + canonical 指向规范页） |
| 系列子帖 | `post/<issue编号>_<评论ID>.html` | 评论删除即下线；父级关闭/撤稿整个系列下线 |
| 标签页 | `tag.html` | 客户端渲染，数据来自 `search-index.json` |
| 关于页 | `about.html` | slug 别名或合成页（见[配置参考 · about](config.md#site)） |
