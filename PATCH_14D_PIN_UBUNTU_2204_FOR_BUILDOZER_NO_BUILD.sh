#!/usr/bin/env bash
set -e

echo "=== PATCH 14D: GitHub runner pin ubuntu-22.04 Buildozerhez ==="

mkdir -p backups logs
TS=$(date +%Y%m%d_%H%M%S)

cp .github/workflows/android.yml "backups/android.yml.bak_patch14d_$TS"

python3 - <<'PY'
from pathlib import Path

p = Path(".github/workflows/android.yml")
s = p.read_text(encoding="utf-8", errors="replace")
old = s

# Buildozer/p4a stabilabb Ubuntu 22.04 alatt, ne noble/latest fusson
s = s.replace("runs-on: ubuntu-latest", "runs-on: ubuntu-22.04")
s = s.replace("runs-on: ubuntu-24.04", "runs-on: ubuntu-22.04")

# 22.04 alatt libncurses5 elérhetőbb, de a 6 is maradhat. Biztonságosan legyen libncurses5 is opcionálisan.
s = s.replace("libncurses6 libstdc++6", "libncurses5 libncurses6 libstdc++6")
s = s.replace("libncurses5 libncurses5", "libncurses5")

# Autoconf/libtool makrókhoz explicit env
if "ACLOCAL_PATH: /usr/share/aclocal" not in s:
    s = s.replace(
        "runs-on: ubuntu-22.04\n",
        "runs-on: ubuntu-22.04\n\n    env:\n      ACLOCAL_PATH: /usr/share/aclocal\n      LIBTOOLIZE: libtoolize\n"
    )

p.write_text(s, encoding="utf-8")
print("Changed:", s != old)
PY

echo "=== Ellenőrzés ==="
grep -nE "runs-on|ACLOCAL_PATH|LIBTOOLIZE|apt-get install|libncurses|autoconf|automake|libtool|buildozer" .github/workflows/android.yml || true

cat > logs/PATCH_14D_PIN_UBUNTU_2204_FOR_BUILDOZER_REPORT.txt <<EOF
PATCH 14D OK
Date: $(date)
Fix:
- GitHub Actions runner pin: ubuntu-22.04
- Buildozer/p4a autoreconf/libtool hibák ellen stabilabb környezet
- ACLOCAL_PATH és LIBTOOLIZE env beállítva
- APK build helyben nem indult
EOF

echo "=== PATCH 14D KÉSZ ==="
echo "Commit még nincs."
