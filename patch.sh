#!/bin/bash
set -e

MSG="${1:-patch update}"

echo "=== AUTOBOT PATCH ==="
echo "Üzenet: $MSG"

cp main.py main.py.bak_$(date +%Y%m%d_%H%M%S)

git add main.py buildozer.spec .gitignore patch.sh

if git diff --cached --quiet; then
  echo "Nincs kódváltozás. Rebuild trigger létrehozása."
  date +"%Y-%m-%d %H:%M:%S" > rebuild.trigger
  git add rebuild.trigger
fi

git commit -m "PATCH: $MSG"
git push

echo "Kész. GitHub Actions build indul."
