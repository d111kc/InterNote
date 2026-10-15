---
name: creating-a-blog-with-internote
description: Use when setting up a new blog with the InterNote generator from scratch — creating the blog repo, writing config.toml, installing the GitHub Actions workflow, enabling Pages, running the first build, publishing the first posts as issues, or previewing the site locally — and when troubleshooting a fresh blog whose posts or pages are not showing.
---

# Creating a Blog with InterNote

## Overview

InterNote is a two-repo system. **This repo is the generator** (code only, never stores posts). **The blog repo** holds the articles (GitHub Issues), `config.toml`, and one workflow; its CI clones the generator, overlays the blog files, renders, commits artifacts back, and deploys GitHub Pages. Writing a post = opening an Issue. No local toolchain is needed to publish — only to preview.

## Hard Facts

| Fact | Value |
| --- | --- |
| Canonical post URL | `post/<issue#>.html` — renaming an issue never breaks links |
| Config schema | `config.sample.toml` is the complete schema; unknown keys are hard build errors (`extra="forbid"`); language fixed zh-CN, timezone UTC+8 |
| Front matter (issue body) | `date draft comments pinned slug refs repo` — `title`/`labels`/`description` rejected (issue title/labels are authoritative) |
| Front matter (series chapter = collaborator comment) | `title order refs repo` only |
| Build triggers | issue `opened/edited/closed/reopened`, comment `created/edited/deleted`, manual dispatch; **no cron** — closing the issue is the only way a post goes offline |
| Serial builds | one concurrency group; runs queued within ~30s are cancelled, only the newest executes — batch edits, then dispatch a full rebuild if something was skipped |
| Artifacts | the blog repo commits `dist/`, `sources/`, `internote.json`, `README.md` (stats) — these must NOT be gitignored |
| Version pin | the workflow template pins the generator via `INTERNOTE_REF` (a release tag, currently `v0.1.0`); generator `main` commits do NOT reach live builds until a release + bump |

## Setup Workflow

1. **Create the blog repo** (any name). `XXX.github.io` serves at the domain root; any other name serves at `/repo-name/` — the generator auto-derives `home_url`, never hardcode it.
2. **Config**: copy `config.sample.toml` → `config.toml` in the blog repo, edit values (labels/colors, giscus, social). Full field reference: the docs site `https://interset-wq.github.io/InterNote/` (config.md, frontmatter.md).
3. **Workflow**: copy `examples/blog-workflow.yml` → `.github/workflows/internote.yml` in the blog repo. Keep the `INTERNOTE_REF` pin unless intentionally tracking a release you made.
4. **Pages**: blog repo Settings → Pages → Build and deployment → Source: **GitHub Actions** (not the branch/pages-legacy option).
5. **First build**: Actions tab → run the workflow manually (dispatch). Verify the run is green and Pages serves the index.
6. **Write**: open an Issue (title = post title, body = markdown, optional `+++` front matter). Labels drive tag pages; no label publishes under `default`. A series = one issue + collaborator comments whose bodies start with `+++` or a bare `# ` h1 (chapter `order` sorts them).
7. **Local preview (optional, before pushing)**: in the generator repo, `uv run python scripts/fetch_fixtures.py <owner/repo> -o temp/fixture.json` (uses `gh` login), then `uv run internote - <owner/repo> --fixtures temp/fixture.json` (the `-` is the token placeholder — omitting it mis-parses args), then serve: `python -m http.server 8000 --directory dist`. Never open `dist/index.html` via `file://` — the index fetches `search-index.json` at runtime and browsers block file-URL fetches. Note the default preview loads CSS/JS from the absolute Pages URLs; to verify local template changes set `[site] home_url = "http://localhost:8000"` and rebuild.

## Maintenance Rules

- Changing `config.py` schema requires syncing the blog repo's `config.toml` in the same change; changing the workflow requires syncing both the template and the blog repo's copy (contents-API PUT 404s on workflow paths — clone and push instead).
- Closing an issue unpublishes it; deleting a chapter comment removes that sub page; both need a build to take effect (the events trigger one).
- Release flow: tag → `gh release create` → bump `INTERNOTE_REF` in both workflow copies.

## Common Mistakes

| Mistake | Consequence |
| --- | --- |
| Gitignoring `dist/`/`sources/`/`internote.json` in the blog repo | incremental builds lose state; posts vanish or rebuild from scratch |
| A closed issue expected to stay hidden after reopen | reopening now rebuilds — if it resurfaced, close it again (or use `draft = true` front matter) |
| `date` in a chapter comment body | build failure (sub-post whitelist) |
| Editing the blog's workflow through the API | 404; clone the repo and push the file |
| Previewing with `file://` | blank index — serve over HTTP |
| Pushing generator `main` and expecting the live blog to change | nothing happens: live builds are pinned to `INTERNOTE_REF` |
| Stale keys in `config.toml` after a generator update | hard build failure naming the unknown key |
