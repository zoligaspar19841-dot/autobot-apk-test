#!/bin/bash
set -e

echo "=== PATCH 13E: FIX WORKFLOW YAML SIGNING BLOCK - APK BUILD NÉLKÜL ==="
echo "Cél: android.yml YAML hiba javítása a fixed debug keystore blokk körül."

TS=$(date +%Y%m%d_%H%M%S)
cp .github/workflows/android.yml ".github/workflows/android.yml.bak_patch13e_$TS"

python - <<'PY'
from pathlib import Path
import re

p = Path(".github/workflows/android.yml")
s = p.read_text(encoding="utf-8", errors="replace")

# 1) Töröljük a hibás PATCH 13D blokkot, ha már benne van
s = re.sub(
    r"\n\s*-\s*name:\s*Prepare fixed debug keystore\s*\n\s*run:\s*\|\s*\n(?:\s{10,}.*\n)+\s*# PATCH 13D FIXED DEBUG KEYSTORE\s*\n?",
    "\n",
    s,
    flags=re.M
)

# 2) Ha maradt markeres blokk furcsa formában, tisztítás
s = re.sub(
    r"\n\s*-\s*name:\s*Prepare fixed debug keystore.*?# PATCH 13D FIXED DEBUG KEYSTORE\s*\n",
    "\n",
    s,
    flags=re.S
)

lines = s.splitlines()
out = []
inserted = False

block = [
"      - name: Prepare fixed debug keystore",
"        run: |",
"          mkdir -p ~/.android",
"          cp keystore/autobot-debug.keystore ~/.android/debug.keystore",
"          chmod 600 ~/.android/debug.keystore",
"          keytool -list -keystore ~/.android/debug.keystore -storepass android -alias androiddebugkey || true",
"        # PATCH 13D FIXED DEBUG KEYSTORE",
]

for line in lines:
    # A buildozer debug lépés ELÉ szúrjuk be, pontos GitHub Actions step behúzással
    if not inserted and ("buildozer" in line and "android" in line and "debug" in line):
        out.extend(block)
        inserted = True
    out.append(line)

if not inserted:
    raise SystemExit("HIBA: nem találtam buildozer android debug sort")

p.write_text("\n".join(out) + "\n", encoding="utf-8")
print("OK: workflow signing blokk javítva")
PY

echo "=== Ellenőrzés: hibás környék ==="
nl -ba .github/workflows/android.yml | sed -n '55,90p'

echo ""
echo "=== YAML gyors ellenőrzés Python-nal ==="
python - <<'PY'
from pathlib import Path
txt = Path(".github/workflows/android.yml").read_text(encoding="utf-8")
bad = False
for i, line in enumerate(txt.splitlines(), 1):
    if "\t" in line:
        print("TAB HIBA sor:", i)
        bad = True
if not bad:
    print("OK: nincs tab karakter")
print("OK: alap ellenőrzés kész")
PY

echo ""
echo "=== PATCH 13E KÉSZ ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Ha a 55-90 sorok jól néznek ki, commit + push következik."
