#!/bin/bash
set -e

echo "=== PATCH 07: APK stage előkészítés - APK BUILD NÉLKÜL ==="

TS=$(date +%Y%m%d_%H%M%S)

echo "=== 1) Biztonsági mentés ==="
cp buildozer.spec "buildozer.spec.bak_patch07_$TS" 2>/dev/null || true
cp apk_stage/buildozer.spec "apk_stage/buildozer.spec.bak_patch07_$TS" 2>/dev/null || true
cp .github/workflows/android.yml ".github/workflows/android.yml.bak_patch07_$TS" 2>/dev/null || true

echo "=== 2) apk_stage alap fájlok ellenőrzése ==="
test -f apk_stage/main.py
test -f apk_stage/demo_core_engine.py
test -f apk_stage/buildozer.spec
test -f apk_stage/icon.png

echo "OK: apk_stage alap fájlok megvannak."

echo "=== 3) buildozer.spec frissíthető APK beállítás ellenőrzés/javítás ==="
python - <<'PY'
from pathlib import Path
import re

SPECS = [Path("buildozer.spec"), Path("apk_stage/buildozer.spec")]

def set_key(text, key, value):
    lines = text.splitlines()
    out = []
    in_app = False
    done = False

    for line in lines:
        st = line.strip()
        if st.startswith("[") and st.endswith("]"):
            if in_app and not done:
                out.append(f"{key} = {value}")
                done = True
            in_app = st == "[app]"

        if in_app and re.match(rf"\s*#?\s*{re.escape(key)}\s*=", line):
            if not done:
                out.append(f"{key} = {value}")
                done = True
            continue

        out.append(line)

    if in_app and not done:
        out.append(f"{key} = {value}")

    return "\n".join(out) + "\n"

for spec in SPECS:
    s = spec.read_text(encoding="utf-8", errors="replace")

    # Stabil package: ez kell, hogy később frissítés legyen, ne új app.
    s = set_key(s, "title", "Binance Autobot")
    s = set_key(s, "package.name", "binanceautobot")
    s = set_key(s, "package.domain", "org.autobot")

    # Újabb Android kompatibilitás.
    s = set_key(s, "android.api", "35")
    s = set_key(s, "android.minapi", "23")
    s = set_key(s, "android.archs", "arm64-v8a")
    s = set_key(s, "android.accept_sdk_license", "True")

    # Saját ikon.
    s = set_key(s, "icon.filename", "icon.png")

    # Csak szükséges fájlokat csomagoljon.
    s = set_key(s, "source.include_exts", "py,png,jpg,jpeg,kv,atlas,json,txt,csv")
    s = set_key(s, "source.exclude_dirs", ".git,.github,__pycache__,.pytest_cache,.mypy_cache,.buildozer,bin,logs,packages,backups,_chatgpt_export")
    s = set_key(s, "source.exclude_exts", "pyc,pyo,enc,key,keystore,apk,aab,zip,tar,gz,bak,sh")
    s = set_key(s, "source.exclude_patterns", "*.bak,*.bak_*,*.BROKEN_*,*secret*,*secrets*,*.enc,*.key,.env,logs/*,packages/*,_chatgpt_export/*")

    # Verziót óvatosan emeljük, hogy frissítésként települjön.
    # Package marad ugyanaz, version nő.
    s = set_key(s, "version", "0.7.2")

    spec.write_text(s, encoding="utf-8")
    print("OK spec prepared:", spec)
PY

echo "=== 4) GitHub workflow artifact útvonal ellenőrzés/javítás ==="
python - <<'PY'
from pathlib import Path

wf = Path(".github/workflows/android.yml")
if not wf.exists():
    wf.parent.mkdir(parents=True, exist_ok=True)
    wf.write_text("""name: Build APK

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Placeholder
        run: echo "Workflow prepared"
""", encoding="utf-8")

s = wf.read_text(encoding="utf-8", errors="replace")

# Csak minimális védelem: legyen upload-artifact és APK path, ne csak log.
if "actions/upload-artifact" in s and "apk_stage/bin/*.apk" not in s and "bin/*.apk" not in s:
    s = s.replace("path: buildozer_full.log", "path: |\n          buildozer_full.log\n          bin/*.apk\n          apk_stage/bin/*.apk")

# Ha teljesen nincs APK path, a végére írunk megjegyzést, de nem építünk.
if "apk_stage/bin/*.apk" not in s and "bin/*.apk" not in s:
    s += """

# PATCH 07 NOTE:
# APK artifact path should include:
#   bin/*.apk
#   apk_stage/bin/*.apk
"""

wf.write_text(s, encoding="utf-8")
print("OK workflow checked:", wf)
PY

echo "=== 5) Prebuild ellenőrzés ==="
python - <<'PY'
from pathlib import Path
import configparser, py_compile

files = [
    "main.py",
    "demo_core_engine.py",
    "apk_stage/main.py",
    "apk_stage/demo_core_engine.py",
]
for f in files:
    py_compile.compile(f, doraise=True)
    print("OK compile:", f)

for spec in ["buildozer.spec", "apk_stage/buildozer.spec"]:
    txt = Path(spec).read_text(encoding="utf-8", errors="replace")
    cp = configparser.ConfigParser()
    cp.optionxform = str
    cp.read_string(txt)
    app = cp["app"]

    print("")
    print("SPEC:", spec)
    print("title =", app.get("title"))
    print("package =", app.get("package.domain") + "." + app.get("package.name"))
    print("version =", app.get("version"))
    print("android.api =", app.get("android.api"))
    print("android.minapi =", app.get("android.minapi"))
    print("icon =", app.get("icon.filename"))

    assert app.get("android.api") == "35"
    assert app.get("android.minapi") == "23"
    assert app.get("package.domain") == "org.autobot"
    assert app.get("package.name") == "binanceautobot"

print("")
print("OK: prebuild stage ready check passed")
PY

echo "=== 6) Git állapot - commit nincs, push nincs ==="
git status --short

echo "=== PATCH 07 KÉSZ ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Ha ez jó, írd: jó"
