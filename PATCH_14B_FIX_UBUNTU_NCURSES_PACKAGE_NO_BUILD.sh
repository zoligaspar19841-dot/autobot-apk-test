#!/usr/bin/env bash
set -e

echo "=== PATCH 14B: Ubuntu libncurses5 -> libncurses6 javítás ==="

mkdir -p backups logs
TS=$(date +%Y%m%d_%H%M%S)

cp .github/workflows/android.yml "backups/android.yml.bak_patch14b_$TS"

python3 - <<'PY'
from pathlib import Path

p = Path(".github/workflows/android.yml")
s = p.read_text(encoding="utf-8", errors="replace")

s2 = s.replace("libncurses5", "libncurses6")

p.write_text(s2, encoding="utf-8")

if s != s2:
    print("OK: libncurses5 cserélve libncurses6-ra")
else:
    print("INFO: libncurses5 nem volt benne")
PY

echo "=== Ellenőrzés ==="
grep -nE "apt-get install|libncurses|zlib|openjdk|buildozer" .github/workflows/android.yml || true

cat > logs/PATCH_14B_FIX_UBUNTU_NCURSES_PACKAGE_REPORT.txt <<EOF
PATCH 14B OK
Date: $(date)
Fix:
- GitHub Actions Ubuntu csomaghiba javítva
- libncurses5 -> libncurses6
- APK build helyben nem indult
EOF

echo "=== PATCH 14B KÉSZ ==="
