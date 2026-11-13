#!/usr/bin/env bash
# Copies this skill pack into ~/.claude/skills so it works in every project,
# not only when this repo is open. Usage: bash .claude/install-skills.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="${HOME}/.claude/skills"
mkdir -p "$DEST" "${HOME}/.claude/agents" "${HOME}/.claude/references"
for d in "$HERE"/skills/*/; do
  name="$(basename "$d")"
  rm -rf "${DEST:?}/$name"
  cp -rL "$d" "$DEST/$name"
done
cp "$HERE"/agents/*.md "${HOME}/.claude/agents/"
cp "$HERE"/references/*.md "${HOME}/.claude/references/"
echo "Installed $(ls "$HERE/skills" | wc -l) skills into $DEST"
