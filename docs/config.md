---
layout: default
title: TOML 配置参考
---

# TOML 配置参考

配置文件为博客仓库根目录的 `config.toml`（完整样例见 [`config.sample.toml`](https://github.com/interset-wq/InterNote/blob/main/config.sample.toml)）。

## 校验规则

- 全部配置段使用 pydantic `ConfigDict(extra="forbid")`：**任何未知键都是硬错误**，构建失败——包括历史遗留键（如已移除的 `language` / `utc`）
- 站点语言固定为简体中文，时区固定为 UTC+8，均无配置键
- 站内搜索无配置段：始终开启，构建时生成 `dist/search-index.json`

## `[site]`

| 键 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `title` | string | 必填 | 站点标题 |
| `sub_title` | string | — | 副标题 |
| `avatar_url` | URL | — | 头像图地址 |
| `about` | string | `"issue"` | 关于页来源，见下表 |
| `favicon` | string | `""` | `""` = 自动下载博客仓库 owner 的 GitHub 头像作为站点图标；URL = 下载该图；`"none"` = 无 favicon |
| `home_url` | URL | 自动推导 | 留空则按 GitHub Pages 地址推导 |

`about` 四种模式：

| 值 | 行为 |
| --- | --- |
| `"issue"`（默认） | 用 `slug = "about"` 的文章作为关于页（含 slug 别名重定向） |
| `"readme"` | GitHub 用户名仓库（`<owner>/<owner>`）的 README；无 README 时警告且无页面 |
| `"mixed"` | 该文章正文 + README 同页拼接；无文章时退化为纯 README；无 README 时完全等同 `"issue"` |
| `"none"` | 无关于页，导航无入口，slug 别名一并抑制 |

`readme` / `mixed`（有 README 时）模式下配置拥有 `about.html`，文章只保留规范页 `post/<id>.html`、slug 别名被抑制，导航标题取文章标题；README 渲染走共享缓存，增量构建不重取，README 变更在下次全局构建拾取。

> 注意：README 渲染**只支持普通的 GitHub README**——其中的相对路径静态资源（如 `./img/a.png`）不会被改写，会按站点自身地址解析而 404；绝对 URL 资源不受影响。

## `[layout]`

| 键 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `posts_per_page` | int | `10` | 首页每页文章数（客户端分页 `#p=N`，无 `pageN.html` 文件） |
| `start_date` | string | — | 建站日期（如 `"2026-01-01"`），页脚展示 |
| `icp` | string | — | ICP 备案号，页脚展示 |
| `footer_text` | string | — | 文章页底部附加文字 |

## `[comments]`

| 键 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `enabled` | bool | `true` | 关闭后所有页面不渲染评论区 |

评论系统为 [giscus](https://giscus.app)（基于 GitHub Discussions）。`[giscus]` 四个键未填时对应页面不渲染评论区。

## `[giscus]`

| 键 | 说明 |
| --- | --- |
| `repo` | 评论存储的仓库，如 `"your-name/your-blog"`（需开启 Discussions） |
| `repo_id` | giscus.app 提供 |
| `category` | Discussions 分类，如 `"Announcements"` |
| `category_id` | giscus.app 提供 |

## `[[social]]`（可选，可多个）

页脚社交图标。RSS 与 GitHub 两个按钮始终内置。

| 键 | 说明 |
| --- | --- |
| `id` | [Simple Icons](https://simpleicons.org) 图标 slug，构建时下载 SVG 内联进页面 |
| `title` | 悬停 / 无障碍文案，缺省用 `id` |
| `action` | 点击行为：`link`（跳转，默认）/ `copy`（复制 `username`）/ `qrcode`（弹出二维码浮层） |

`action` 决定必填字段（模型校验器强制，缺失即构建失败）：

| action | 必填 |
| --- | --- |
| `link` | `url` |
| `copy` | `username` |
| `qrcode` | `qrcode`（二维码图片地址，配合 `static/` 目录使用） |

单个图标下载失败只警告并丢弃该图标，不会导致构建失败。

## 环境与产物

- 博客仓库的 `static/` 目录原样拷贝到站点根目录，供配置引用二进制资源
- 构建产物 `dist/`、`sources/`、`internote.json`、`README.md` 由博客仓库提交（见[快速开始](quickstart.md)）
- workflow 配置见 `examples/blog-workflow.yml`；`INTERNOTE_REF` 固定生成器版本（见[快速开始 · 版本固定](quickstart.md#版本固定)）
