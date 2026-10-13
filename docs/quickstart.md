---
layout: default
title: 快速开始
---

# 快速开始

博客与生成器分两处存放：**生成器仓库**（本仓库）只放代码；**博客仓库**存放 Issue（文章）、`config.toml` 和 workflow。每次构建时 CI 克隆生成器、叠加博客文件、渲染并发布。

## 建站步骤

1. **创建博客仓库**：任意名称均可。`XXX.github.io` 形式 Pages 挂根路径，其他名称挂在 `/仓库名/` 子路径——生成器自动适配，无需关心 base 路径
2. **添加配置**：复制生成器的 [`config.sample.toml`](https://github.com/interset-wq/InterNote/blob/main/config.sample.toml) 为博客仓库根目录的 `config.toml` 并修改（字段见 [TOML 配置参考](config.md)）
3. **添加 workflow**：复制 `examples/blog-workflow.yml` 到博客仓库的 `.github/workflows/internote.yml`
4. **启用 Pages**：博客仓库 `Settings → Pages → Build and deployment → Source` 选择 **GitHub Actions**
5. **首次全局生成**：Actions 页面手动运行 `build InterNote → Run workflow`
6. **开始写作**：新建 Issue，保存后自动构建，片刻后通过 Pages 地址访问。不加 Label 也可以，文章会归入 `default` 标签

## 构建触发

| 触发 | 行为 |
| --- | --- |
| Issue `opened` / `edited` | 增量重建该篇文章及列表页 |
| Issue `closed` | 取消发布：从页面、列表、RSS、状态文件与搜索索引中移除 |
| Issue comment `created` / `edited` / `deleted` | 增量重建该 issue（系列子文章即评论，编辑/删除后重建生效） |
| `workflow_dispatch` | 手动全局重建（修改 `config.toml` 后执行一次） |

> 关闭 Issue 即取消发布。没有每日定时构建，因此没有事后清扫，`closed` 触发是唯一能让撤稿及时生效的方式。Pull Request 不会作为文章发布。

## 版本固定

workflow 模板通过 `INTERNOTE_REF` 环境变量固定检出 InterNote 的 release（当前 `v0.1.0`），生成器 `main` 分支的开发提交**不会**进入线上构建。发布新版本 = 打 tag 发 release 后，把 `INTERNOTE_REF` 提到新 tag，并同步推送模板与博客仓库两份 workflow。

## 生成产物

博客仓库会提交构建产物（`.gitignore` 不要忽略这些路径）：

| 路径 | 内容 |
| --- | --- |
| `dist/` | 站点 HTML、CSS、插件、搜索索引 |
| `sources/` | Issue 源码备份 |
| `internote.json` | 构建状态（含渲染缓存） |
| `README.md` | 自动更新的文章数 / 评论数 / 字数 / 时间统计 |

## 可选：静态资源目录

博客仓库的 `static/` 目录会被原样拷贝到站点根目录，用来存放配置需要引用的图片（如社交图标的二维码），按 `https://…/仓库名/文件名` 引用。

## 本地构建与预览

```bash
uv sync                                         # 安装依赖（Python >= 3.14）

# 全局构建（需要 token）
uv run internote <token> <owner/repo>

# 单篇增量重建
uv run internote <token> <owner/repo> --issue-number 42

# 离线构建：先抓取 fixture，再从 fixture 构建（无需 token、不写 GitHub）
uv run python scripts/fetch_fixtures.py <owner/repo> -o tests/fixtures/<owner>__<name>.json
uv run internote - <owner/repo> --fixtures tests/fixtures/<owner>__<name>.json
```
