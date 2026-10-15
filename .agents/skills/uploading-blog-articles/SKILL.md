---
name: uploading-blog-articles
description: Use when publishing local markdown notes as posts or series chapters to the InterNote blog repo (interset-wq/blog) via the GitHub CLI — reopening issues, converting article front matter into issue-body or sub-post-comment form, posting chapter comments, or verifying the rendered Pages site — especially when the GitHub web UI is slow or unreachable (mainland China) and CLI upload is the efficient path.
---

# Uploading Blog Articles

## Overview

InterNote renders GitHub Issues into a GitHub Pages site. Uploading an article is therefore **repo surgery on `interset-wq/blog`**, not a push to this generator. Two correctness gates dominate everything: the front-matter whitelists (a wrong key fails the build) and the serial build queue (a cancelled run silently skips your issue).

## When to Use

- User asks to publish/upload local notes (any `E:/.blog-post/...` tree) to the blog
- Reopening an issue, retitle/relabel it, replacing its body, adding series chapter comments
- "The site doesn't show my article" triage

Not for: editing the generator itself, or pure content review with no upload.

## Hard Facts (verify nothing, rely on these)

| Fact | Value |
| --- | --- |
| Repo / Pages / workflow | `interset-wq/blog` / `https://interset-wq.github.io/blog/` / `internote.yml` |
| Post front matter (issue body) | `date draft comments pinned slug refs repo` |
| Sub-post front matter (comment) | `title order refs repo` — **`date` here fails the build** |
| Front matter format | TOML only, fenced with `+++` — never YAML `---`; `repo` = optional http(s) source-repo URL rendered as a 源码 link, NOT a label |
| Sub post trigger | collaborator comment whose body starts with `+++` or a bare `# ` h1 |
| Canonical URLs | `post/<issue#>.html`, subs at `post/<issue#>_<commentId>.html` |
| Search index | parent record only, carrying `subs: N`; sub pages NEVER appear in `search-index.json` |
| Encoding | files may be UTF-8 BOM + CRLF; strip BOM, keep CRLF or normalize — both parse |

## Workflow

1. **Transform payloads** — run from this skill's directory:
   `python prepare_payload.py <file.md> --mode article|sub --order N -o <out.md>`
   It strips BOM, rebuilds front matter against the whitelist, validates with tomllib, reports the h1 (sub-post title fallback). Never hand-edit payloads for CJK files.
2. **Never use bash text tools on Chinese-named files** (`head`, `wc`, `grep` mojibake the path on GBK Windows). Use Python for ALL read/transform steps.
3. **Issue-level ops** (one batch, back-to-back): `gh issue reopen <n> -R interset-wq/blog` → one `gh issue edit` with `--title` + `--body-file` + `--add-label` (fetch old labels first, remove stale ones in the same batch). Then post chapter comments in `order` sequence via `gh api repos/interset-wq/blog/issues/<n>/comments --input -` with a JSON body.
4. **Build queue**: every event fires the workflow; the serial concurrency group cancels queued runs, keeping only the newest — per issue AND across issues posted within ~30s. Batch per issue; the last run renders the final state. If any issue still didn't render, `gh workflow run internote.yml -R interset-wq/blog` (full rebuild) is the remedy.
5. **Verify**: poll `gh run list` until the newest run completes; then probe Pages with a **tag-stripped** Python fetch (raw HTML grep misses code content — highlight spans split literals): check `<title>`, `post/<n>_<id>.html` sub pages, breadcrumbs, and `search-index.json` — the parent record's `subs` count must equal the chapter count; sub pages never appear in the index (expecting them there is a bug in the check, not the site). Append `?cb=$RANDOM` to bust the 10-min CDN cache. Every `gh` command targets `-R interset-wq/blog` and every site URL sits under `https://interset-wq.github.io/blog/` — recheck `-R` and the URL prefix when switching steps.

## Common Mistakes

| Mistake | Consequence |
| --- | --- |
| `date` in a comment payload | build failure — sub whitelist rejects it |
| BOM left in payload | `+++` not detected → rendered as `<hr>`, or no sub page |
| grep probes on raw HTML | false MISS on code blocks; strip tags first |
| Reopen+edit+comments spread over minutes across issues | queued runs cancelled, article missing; batch, then dispatch if needed |
| Trusting a comment became a page | non-collaborator comments silently stay comments; check `author_association` |
| YAML front matter, or a label stuffed into `repo` | payloads are TOML inside `+++`; `repo` takes an http(s) URL only |
| Expecting sub pages in `search-index.json` | wrong check — only the parent record exists there, with `subs: N` |
| Switching repo/site mid-flow (dispatch or verify elsewhere) | every step stays on `-R interset-wq/blog` and `https://interset-wq.github.io/blog/` |
