#!/usr/bin/env python3
"""Prepare an InterNote article payload from a local markdown note.

Strips the UTF-8 BOM, splits the TOML front matter, rebuilds it against the
InterNote whitelist (post fields for an issue body, sub-post fields for a
series chapter comment), validates the result with tomllib, and writes the
upload-ready payload. Purely local: posting is done with `gh` afterwards.

Usage (run from this skill's directory):
  python prepare_payload.py ARTICLE.md --mode article -o payload-body.md
  python prepare_payload.py CHAPTER.md --mode sub --order 2 -o payload-comment.md
"""
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

DELIM = "+++"
POST_FIELDS = {"date", "draft", "comments", "pinned", "slug", "refs", "repo"}
SUB_FIELDS = {"title", "order", "refs", "repo"}
KEY_START = re.compile(r"^(\w+)\s*=")


def split_front_matter(text: str) -> tuple[list[str], str]:
    """Return (front matter lines, body). Empty list when there is none."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != DELIM:
        return [], text
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == DELIM), None)
    if end is None:
        raise SystemExit("error: front matter opened with +++ but never closed")
    return lines[1:end], "\n".join(lines[end + 1:])


def keep_whitelisted(fm_lines: list[str], allowed: set[str]) -> list[str]:
    """Drop every top-level key outside *allowed*, keeping multi-line tables."""
    kept: list[str] = []
    in_key: str | None = None
    for line in fm_lines:
        stripped = line.strip()
        if KEY_START.match(line):
            in_key = KEY_START.match(line).group(1)  # type: ignore[union-attr]
            if in_key in allowed:
                kept.append(line)
        elif in_key is not None:
            # continuation of a multi-line value (array of tables etc.)
            if in_key in allowed:
                kept.append(line)
            if stripped.endswith("]"):
                in_key = None
    return kept


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="local markdown note (any encoding/BOM)")
    parser.add_argument("--mode", choices=("article", "sub"), required=True)
    parser.add_argument("--order", type=int, help="series order (mode=sub only)")
    parser.add_argument("-o", "--out", required=True, help="payload file to write")
    args = parser.parse_args()
    if args.mode == "sub" and args.order is None:
        parser.error("--order is required with --mode sub")

    raw = Path(args.source).read_text(encoding="utf-8-sig")
    fm_lines, body = split_front_matter(raw)

    allowed = POST_FIELDS if args.mode == "article" else SUB_FIELDS
    kept = keep_whitelisted(fm_lines, allowed)

    if args.mode == "sub":
        h1 = next(
            (l[2:].strip() for l in body.split("\n") if l.strip().startswith("# ")),
            None,
        )
        if h1 is None and not any(re.match(r"^title\s*=", l) for l in kept):
            raise SystemExit(
                "error: sub-post has neither a 'title' key nor a leading '# ' h1; "
                "the build would fail with an empty series row"
            )
        new_fm = ["order = %d" % args.order] + kept
    else:
        new_fm = kept

    payload = DELIM + "\n" + "\n".join(new_fm) + "\n" + DELIM + "\n\n" + body

    # validate exactly what will be uploaded
    end = next(i for i, l in enumerate(payload.split("\n")[1:], 1)
               if l.strip() == DELIM)
    meta = tomllib.loads("\n".join(payload.split("\n")[1:end]))
    unknown = sorted(set(meta) - allowed)
    if unknown:
        raise SystemExit("error: whitelist violation, keys %s" % unknown)

    Path(args.out).write_text(payload, encoding="utf-8", newline="\n")
    print("payload: %s (%d bytes, keys=%s)" % (args.out, len(payload), sorted(meta)))


if __name__ == "__main__":
    main()
