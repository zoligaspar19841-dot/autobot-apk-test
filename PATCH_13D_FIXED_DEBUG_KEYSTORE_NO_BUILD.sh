#!/bin/bash
set -e

echo "=== PATCH 13D: FIX DEBUG KEYSTORE FOR STABLE APK UPDATE - APK BUILD NÉLKÜL ==="
echo "Cél: minden GitHub debug APK ugyanazzal a kulccsal készüljön."
echo "Nem indít APK buildet."

TS=$(date +%Y%m%d_%H%M%S)

mkdir -p logs keystore

echo "=== 1) Mentés ==="
cp .github/workflows/android.yml ".github/workflows/android.yml.bak_patch13d_$TS"

echo "=== 2) Fix debug keystore előkészítés ==="

if [ ! -f keystore/autobot-debug.keystore ]; then
  if command -v keytool >/dev/null 2>&1; then
    keytool -genkeypair \
      -v \
      -keystore keystore/autobot-debug.keystore \
      -storepass android \
      -alias androiddebugkey \
      -keypass android \
      -keyalg RSA \
      -keysize 2048 \
      -validity 10000 \
      -dname "CN=Android Debug,O=Android,C=US"
    echo "OK: új fix debug keystore létrehozva"
  else
    echo "HIBA: keytool nincs Termuxban."
    echo "Telepítés Termuxban általában: pkg install openjdk-17"
    exit 1
  fi
else
  echo "OK: keystore/autobot-debug.keystore már létezik"
fi

echo "=== 3) Workflow patch: fix debug keystore bemásolása build előtt ==="

python - <<'PY'
from pathlib import Path

p = Path(".github/workflows/android.yml")
s = p.read_text(encoding="utf-8", errors="replace")

marker = "# PATCH 13D FIXED DEBUG KEYSTORE"

block = r'''
      - name: Prepare fixed debug keystore
        run: |
          mkdir -p ~/.android
          cp keystore/autobot-debug.keystore ~/.android/debug.keystore
          chmod 600 ~/.android/debug.keystore
          keytool -list -keystore ~/.android/debug.keystore -storepass android -alias androiddebugkey || true
        # PATCH 13D FIXED DEBUG KEYSTORE
'''

if marker in s:
    print("OK: workflow már tartalmazza PATCH 13D blokkot")
else:
    lines = s.splitlines()
    out = []
    inserted = False

    for line in lines:
        # buildozer android debug lépés ELÉ szúrjuk be
        if (not inserted) and ("buildozer" in line and "android" in line and "debug" in line):
            out.append(block.rstrip("\n"))
            inserted = True
        out.append(line)

    if not inserted:
        raise SystemExit("HIBA: nem találtam buildozer android debug sort a workflow-ban")

    p.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("OK: workflow patch beszúrva")
PY

echo "=== 4) Ellenőrzés ==="
grep -nE "Prepare fixed debug keystore|autobot-debug.keystore|debug.keystore|buildozer.*android.*debug|PATCH 13D" .github/workflows/android.yml

echo "=== 5) Keystore fingerprint ==="
keytool -list -v -keystore keystore/autobot-debug.keystore -storepass android -alias androiddebugkey | grep -E "Alias name|SHA1|SHA256" || true

echo "=== 6) Git állapot - commit nincs, push nincs ==="
git status --short

echo ""
echo "=== PATCH 13D KÉSZ ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Ha ez jó, írd: jó"
