---
layout: default
title: 架构说明
---

# 架构说明

## 模块划分

```
src/internote/
├── cli.py           # typer 入口：token/repo/--issue-number/--fixtures
├── generator.py     # 编排器：构建状态、增量 run_one / 全量 run_all、README 统计
├── config.py        # pydantic 配置模型（extra="forbid"）
├── renderer.py      # Jinja2 环境（trim_blocks / lstrip_blocks / autoescape off）
├── github_client.py # PyGithub 封装 + /markdown 渲染 + profile README
├── feed.py          # RSS 生成
├── frontmatter.py   # TOML front matter 解析与严格校验
├── constants.py     # 固定文案（i18n）与图标 SVG path
├── fixtures.py      # 离线构建用 fixture 仓库（duck-typed PyGithub 表面）
├── templates/       # Jinja2 模板（随包分发，Path(__file__) 定位，与 cwd 无关）
├── plugins/         # 零依赖浏览器插件（原样拷贝，非 Jinja 渲染）
└── assets/          # main.css + Primer 21（随包分发，无外部 CDN）
```

## 模板与插件

- 模板 6 页：`post-list` / `post` / `tag` / `404` / `alias` + `base` 布局；共享 UI 全部在 `components/macros.j2.html`，`footer` / `comments` 为纯 include
- `base.j2.html` 拥有 `<style>` 包装：子模板用 `{% block style %}` 填充裸 CSS
- 渲染配置：`autoescape off`（正文是 GitHub API 预渲染的 HTML）、`StrictUndefined`（缺上下文键直接报错而非静默空白）
- 插件 7 个全部零依赖：`theme`（三态明暗）、`toc`（目录 + 滚动高亮）、`fab`（悬浮工具栏）、`lightbox`（图片查看）、`code-copy`（代码复制）、`giscus`（评论懒加载）、`search`（搜索弹窗）
- 插件原样拷贝到 `dist/plugins/`，**不经 Jinja**：配置通过服务端渲染的 `data-*` 属性传入，模板里不出现 `{{ }}` 占位符
- `window.icons` 只保留运行时需要的图标：静态图标全部由服务端 `icon()` 宏渲染

## 搜索与列表数据

`dist/search-index.json` 是站点唯一的客户端数据文件，同时供搜索弹窗、首页列表、标签页消费：

```json
{
  "label_colors": { "标签名": "#hex" },
  "posts": [{ "title": "...", "labels": [], "date": "...", "top": 0, "url": "post/1.html", "subs": 0 }]
}
```

记录由生成器**预排序**（置顶优先、日期倒序），所有客户端渲染天然同序。搜索支持标题/标签子串匹配与 `YYYY` 日期片段过滤。系列子帖不进索引，父级记录带 `subs` 计数供角标展示。

## 渲染缓存与增量构建

- `internote.json` 持久化两层状态：条目状态 + `render_cache`（`sha256(剥离后的正文)` → HTML）
- **编辑一篇 Issue 恰好消耗一次 `/markdown` 调用**；内容未变的重建零调用
- 缓存在 `Generator.__init__` 加载（`run_all` 不读条目状态）
- 增量 `run_one(<issue>)` 只处理该 issue：渲染页面、增删条目、重写列表与索引；草稿化 / 关闭 / 删评论走下线路径（`_drop_entry`）
- 全量 `run_all` 重建一切；只有 `comments > 0` 的 issue 支付一次 `get_comments()` 调用（编辑评论不改变评论数，全量重拉是可靠刷新的唯一途径）
- 构建必须串行（workflow `concurrency` 组保证），并发增量会互相覆盖产物

## 双仓库流

- **生成器仓库**（本仓库）：只放代码、模板、测试与 workflow 模板；不存任何文章
- **博客仓库**：Issue（文章）+ `config.toml` + workflow + 提交的构建产物
- 博客 CI 每次构建克隆生成器到 `/opt/InterNote`，叠加博客文件，运行 CLI，把产物提交回博客仓库并部署 Pages
- workflow 模板用 `INTERNOTE_REF` 环境变量固定检出 release（当前 `v0.1.0`）；博客仓库 workflow 不自动同步，需手工跟进
- **schema 同步纪律**：`config.py` 任何变更必须同步博客仓库的 `config.toml`（`extra="forbid"` 把过期键变成硬构建失败）；workflow 变更须同步模板与博客仓库两份
- 发布流程：打 tag → `gh release create` → 提升 `INTERNOTE_REF` → 同步 workflow

## CSS 体系

- `main.css` 是唯一全局样式表（含目录、lightbox、任务列表等 Primer 缺失的补丁段）；模板除用户注入点外不写内联 `<style>`
- 颜色与间距来自 `:root` 的 `--in-*` 设计令牌，别名 Primer 变量并带字面回退（`var(--color-fg-default, #1f2328)`），Primer 升级不至于全站崩坏
- 项目自有类一律 `in-` 前缀，与捆绑的 Primer 无作用域冲突：`in-site-` / `in-post-` / `in-nav-` / `in-toc-` / `in-search-` 等
- 断点：600px（移动端）、768px（lightbox 控件）、1249px（目录退出侧栏）

## 测试体系

- `uv run pytest -q`，全部离线：`tests/conftest.py` autouse 打桩任何真实网络调用，违例仅警告跳过
- `FixtureRepo`（`fixtures.py`）镜像生成器用到的 PyGithub 表面——优先用 fixture 而非 mock；`FixtureIssue` 必须带上 `generator.py` 触碰的每个属性（`state` 最易遗漏）
- fixture 由 `scripts/fetch_fixtures.py` 用 `gh api` 抓取（显式 `encoding="utf-8"`，规避中文 Windows 的 GBK 默认编码崩溃）
- 已知测试缺口：`cli.py` 与 `renderer.py` 未覆盖
- fixture 保持原始正文，`body_html` 由剥离后的正文渲染——`split()` 幂等性保证两者对得上

## 本地开发

```bash
uv sync                # 安装依赖
uv run pytest -q       # 全部测试（离线）
uv build               # 构建 wheel；templates/ 与 plugins/ 随包自动带上
```
