#!/bin/zsh

# 自動 commit 並 push 到 GitHub
# 使用方式：./push.sh "修改說明（可省略）"

MSG=${1:-"update: $(date '+%Y-%m-%d %H:%M')"}

cd "$(dirname "$0")"

git add .

# 確認有變動才 commit
if git diff --cached --quiet; then
  echo "沒有偵測到任何變動，略過 push。"
  exit 0
fi

git commit -m "$MSG"
git push origin main

echo "完成：已上傳至 GitHub。"
