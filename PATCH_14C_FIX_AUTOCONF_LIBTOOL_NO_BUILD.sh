#!/usr/bin/env bash
set -e

echo "=== PATCH 14C: Autoconf / Libtool Buildozer fix - APK BUILD NÉLKÜL ==="

mkdir -p backups logs
TS=$(date +%Y%m%d_%H%M%S)

cp .github/workflows/android.yml "backups/android.yml.bak_patch14c_$TS"

python3 - <<'PY'
from pathlib import Path

p = Path(".github/workflows/android.yml")
s = p.read_text(encoding="utf-8", errors="replace")

old = s

# Biztonságos csomaglista bővítés Ubuntu noble + Buildozer/p4a miatt
repls = {
    "autoconf libtool pkg-config zlib1g-dev libncurses6 libstdc++6":
    "autoconf automake autotools-dev libtool libtool-bin pkg-config m4 gettext autopoint zlib1g-dev libncurses6 libstdc++6",

    "autoconf libtool pkg-config zlib1g-dev libncurses5 libstdc++6":
    "autoconf automake autotools-dev libtool libtool-bin pkg-config m4 gettext autopoint zlib1g-dev libncurses6 libstdc++6",

    "autoconf libtool pkg-config":
    "autoconf automake autotools-dev libtool libtool-bin pkg-config m4 gettext autopoint",
}

for a,b in repls.items():
    s = s.replace(a,b)

# Ha valamiért nem került bele, akkor az apt-get install sor végére tesszük
needed = ["automake", "autotools-dev", "libtool-bin", "m4", "gettext", "autopoint"]
if "sudo apt-get install -y" in s:
    lines = s.splitlines()
    out = []
    for line in lines:
        if "sudo apt-get install -y" in line:
            for n in needed:
                if n not in s:
                    line += " " + n
        out.append(line)
    s = "\n".join(out) + "\n"

p.write_text(s, encoding="utf-8")

print("Changed:", s != old)
PY

echo "=== Ellenőrzés ==="
grep -nE "apt-get install|autoconf|automake|libtool|libtool-bin|autopoint|gettext|m4|zlib|ncurses" .github/workflows/android.yml || true

cat > logs/PATCH_14C_FIX_AUTOCONF_LIBTOOL_REPORT.txt <<EOF
PATCH 14C OK
Date: $(date)
Fix:
- Buildozer / python-for-android autoreconf hiba javítás
- LT_SYS_SYMBOL_USCORE macro miatt libtool-bin, automake, autotools-dev, m4, gettext, autopoint hozzáadva
- APK build helyben nem indult
EOF

echo "=== PATCH 14C KÉSZ ==="
echo "Commit még nincs."
