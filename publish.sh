#!/usr/bin/env bash
# normal push only (never force); idempotent — no commit if nothing changed
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
python3 "$ROOT/build.py"
if [[ -f "$ROOT/SCAN_REPORT.txt" ]]; then
  echo "----- SCAN_REPORT.txt -----"
  cat "$ROOT/SCAN_REPORT.txt"
  echo "---------------------------"
  if grep -q '^命中 ' "$ROOT/SCAN_REPORT.txt"; then
    echo "敏感字樣已從發布檔移除；請檢查 SCAN_REPORT.txt 後再決定是否推送。" >&2
    exit 2
  fi
fi
if [[ -f "$ROOT/ASSET_CHECK.txt" ]]; then
  echo "----- ASSET_CHECK.txt -----"
  cat "$ROOT/ASSET_CHECK.txt"
  echo "---------------------------"
fi
git config user.name grokbot
git config user.email bot@local
# never add credentials, shots, or the volatile scan log
git add index.html sources.html history.json style.css robots.txt README.md .nojekyll .gitignore
git add entries assets status status_history.json assets_manifest.json ASSET_CHECK.txt archive
git add build.py publish.sh assemble.py visuals.py
if git diff --cached --quiet; then
  echo "nothing to publish"
  exit 0
fi
git commit -m "update $(TZ=Asia/Taipei date +%Y-%m-%d_%H%M)"
# first run may have no remote yet
if git remote get-url origin >/dev/null 2>&1; then
  git push origin HEAD
else
  echo "no origin remote; skip push"
fi
git log --oneline -1
