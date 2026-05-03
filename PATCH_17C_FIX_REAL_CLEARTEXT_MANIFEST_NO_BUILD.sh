#!/usr/bin/env bash
set -e

echo "=== PATCH 17C: REAL ANDROID CLEARTEXT MANIFEST FIX - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, nem küld Binance ordert."

mkdir -p backups logs
TS=$(date +%Y%m%d_%H%M%S)

SPEC="apk_stage/buildozer.spec"

if [ ! -f "$SPEC" ]; then
  echo "HIBA: nincs $SPEC"
  exit 1
fi

cp "$SPEC" "backups/buildozer.spec.bak_patch17c_$TS"

python3 - <<'PY'
from pathlib import Path
import re

p = Path("apk_stage/buildozer.spec")
s = p.read_text(encoding="utf-8", errors="ignore")

# régi / rossz kulcs kikommentezése, ha van
s = re.sub(
    r'(?m)^android\.manifest\.application_arguments\s*=.*$',
    '# disabled by PATCH 17C: android.manifest.application_arguments was not effective',
    s
)

def set_line(key, value):
    global s
    lines = s.splitlines()
    out = []
    done = False
    for line in lines:
        if line.strip().startswith(key):
            out.append(value)
            done = True
        else:
            out.append(line)
    if not done:
        out.append(value)
    s = "\n".join(out) + "\n"

set_line("android.permissions", "android.permissions = INTERNET")
set_line("android.extra_manifest_application_arguments", 'android.extra_manifest_application_arguments = android:usesCleartextTraffic="true"')
set_line("source.include_exts", "source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,csv,html,css,js,svg,ico,xml")

p.write_text(s, encoding="utf-8")
print("OK patched:", p)
PY

echo "=== Ellenőrzés ==="
grep -nE "cleartext|Cleartext|extra_manifest|manifest.application|android.permissions|source.include_exts" "$SPEC" || true

python3 -m py_compile apk_stage/main.py

cat > logs/PATCH_17C_FIX_REAL_CLEARTEXT_MANIFEST_REPORT.txt <<EOF
PATCH 17C OK
Date: $(date)

Javítás:
- rossz / nem hatásos android.manifest.application_arguments kikapcsolva
- helyette android.extra_manifest_application_arguments beállítva
- android:usesCleartextTraffic="true"
- INTERNET permission ellenőrizve
- APK build NEM indult
- Commit NEM történt
- Binance order NEM történt

Cél:
- WebView engedje a helyi http://127.0.0.1:8080 betöltést.
EOF

echo "=== PATCH 17C KÉSZ ==="
echo "Jelentés: logs/PATCH_17C_FIX_REAL_CLEARTEXT_MANIFEST_REPORT.txt"
echo "APK build NEM indult. Commit NEM történt."
