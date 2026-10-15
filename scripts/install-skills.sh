#!/usr/bin/env bash
# Mirror .agents/skills/ into the project-level skill directories of agents
# that do not scan .agents/skills/ themselves.
#
# .agents/skills/ is the SOURCE OF TRUTH (Agent Skills standard). It is
# scanned natively at project level by AtomCode, OpenCode and pi. Claude Code
# only scans .claude/skills/, so the mirrors below are generated for it
# (OpenCode also reads .claude/skills/, which covers it twice over).
#
# Usage: scripts/install-skills.sh [skill-name ...]
#   With no arguments, installs every skill. Both mirror directories are
#   git-ignored; re-run after editing any SKILL.md.
set -euo pipefail
cd "$(dirname "$0")/.."

src=".agents/skills"
targets=(".claude/skills" ".opencode/skills")

if [ ! -d "$src" ]; then
  echo "error: $src not found (run from the generator repo)" >&2
  exit 1
fi

installed=0
for skill_dir in "$src"/*/; do
  name=$(basename "$skill_dir")
  if [ "$#" -gt 0 ]; then
    keep=false
    for want in "$@"; do
      [ "$want" = "$name" ] && keep=true
    done
    $keep || continue
  fi
  for target in "${targets[@]}"; do
    mkdir -p "$target"
    rm -rf "${target:?}/${name:?}"
    cp -r "$skill_dir" "$target/$name"
    echo "installed $name -> $target/$name"
  done
  installed=$((installed + 1))
done

[ "$installed" -gt 0 ] || { echo "no matching skill in $src" >&2; exit 1; }
