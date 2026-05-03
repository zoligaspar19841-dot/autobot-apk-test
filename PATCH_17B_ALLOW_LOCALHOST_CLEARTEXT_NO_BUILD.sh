#!/usr/bin/env bash
set -e

echo "=== PATCH 17B: ALLOW LOCALHOST CLEARTEXT WEBVIEW - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, nem küld Binance ordert."

mkdir -p backups logs
TS=$(date +%Y%m%d_%H%M%S)

SPEC="apk_stage/buildozer.spec"

if [ ! -f "$SPEC" ]; then
  echo "HIBA: nincs $SPEC"
  exit 1
fi

cp "$SPEC" "backups/buildozer.spec.bak_patch17b_$TS"

python3 - <<'PY'
from pathlib import Path

p = Path("apk_stage/buildozer.spec")
s = p.read_text(encoding="utf-8", errors="ignore")

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
set_line("android.manifest.application_arguments", 'android.manifest.application_arguments = android:usesCleartextTraffic="true"')
set_line("source.include_exts", "source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,csv,html,css,js,svg,ico,xml")

p.write_text(s, encoding="utf-8")
print("OK patched:", p)
PY

echo "=== Ellenőrzés ==="
grep -nE "android.permissions|android.manifest.application_arguments|source.include_exts" "$SPEC"

python3 -m py_compile apk_stage/main.py

cat > logs/PATCH_17B_ALLOW_LOCALHOST_CLEARTEXT_REPORT.txt <<EOF
PATCH 17B OK
Date: $(date)

Javítás:
- Android WebView localhost HTTP engedélyezés
- android:usesCleartextTraffic="true"
- INTERNET permission ellenőrizve
- webui fájltípusok engedélyezve
- APK build NEM indult
- Commit NEM történt
- Binance order NEM történt

Hiba oka:
net::ERR_CLEARTEXT_NOT_PERMITTED
EOF

echo "=== PATCH 17B KÉSZ ==="
echo "Jelentés: logs/PATCH_17B_ALLOW_LOCALHOST_CLEARTEXT_REPORT.txt"
echo "APK build NEM indult. Commit NEM történt."
