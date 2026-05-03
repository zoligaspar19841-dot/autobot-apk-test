#!/bin/bash
set -e

echo "=== PATCH 06: PREBUILD AUDIT - APK BUILD NÉLKÜL ==="

REPORT="PATCH_06_PREBUILD_AUDIT_REPORT.txt"

python - <<'PY' | tee "$REPORT"
from pathlib import Path
from collections import Counter
import configparser, py_compile, re, sys, subprocess

FILES = [Path("main.py"), Path("apk_stage/main.py")]
SPECS = [Path("buildozer.spec"), Path("apk_stage/buildozer.spec")]

print("=== 1) Python compile ===")
for f in FILES + [Path("demo_core_engine.py"), Path("apk_stage/demo_core_engine.py")]:
    try:
        py_compile.compile(str(f), doraise=True)
        print("OK compile:", f)
    except Exception as e:
        print("FAIL compile:", f, e)

print("\n=== 2) buildozer.spec ellenőrzés ===")
for spec in SPECS:
    print("\nSPEC:", spec)
    if not spec.exists():
        print("FAIL: hiányzik")
        continue

    text = spec.read_text(encoding="utf-8", errors="replace")

    keys = []
    in_app = False
    for line in text.splitlines():
        st = line.strip()
        if st.startswith("[") and st.endswith("]"):
            in_app = st == "[app]"
            continue
        if in_app and "=" in line and not st.startswith("#"):
            keys.append(line.split("=", 1)[0].strip())

    dup = {k:v for k,v in Counter(keys).items() if v > 1}
    print("Duplikált app kulcsok:", dup if dup else "nincs")

    cp = configparser.ConfigParser()
    cp.optionxform = str
    try:
        cp.read_string(text)
        app = cp["app"]
        checks = {
            "title": app.get("title"),
            "package.name": app.get("package.name"),
            "package.domain": app.get("package.domain"),
            "version": app.get("version"),
            "android.api": app.get("android.api"),
            "android.minapi": app.get("android.minapi"),
            "android.archs": app.get("android.archs"),
            "icon.filename": app.get("icon.filename"),
        }
        for k, v in checks.items():
            print(k, "=", v)

        api = int(app.get("android.api", "0"))
        minapi = int(app.get("android.minapi", "0"))
        if api < 34:
            print("WARN: android.api alacsony, Play Protect régi Android figyelmeztetést okozhat")
        if minapi < 23:
            print("WARN: android.minapi alacsony")
        icon = app.get("icon.filename", "icon.png")
        icon_path = spec.parent / icon
        print("Ikon létezik:", icon_path, icon_path.exists())
    except Exception as e:
        print("FAIL spec parse:", e)

print("\n=== 3) UI class / screen ellenőrzés ===")
needed = [
    "class DemoCoreScreen",
    "class DemoCoreSettingsScreen",
    "class TrendMiniChart",
    "def safe_go_back",
    "def safe_go_to",
    "def _android_back_button",
    "PATCH 05 DARK/YELLOW",
]
for f in FILES:
    text = f.read_text(encoding="utf-8", errors="replace")
    print("\nFILE:", f)
    for n in needed:
        print(("OK " if n in text else "MISSING "), n)

    classes = re.findall(r"^class\s+(\w+)\(", text, re.M)
    dup_classes = {k:v for k,v in Counter(classes).items() if v > 1}
    print("Duplikált class:", dup_classes if dup_classes else "nincs")

    add_widgets = re.findall(r'add_widget\((\w+)\(name=["\']([^"\']+)["\']', text)
    names = [name for _, name in add_widgets]
    dup_routes = {k:v for k,v in Counter(names).items() if v > 1}
    print("Duplikált screen name:", dup_routes if dup_routes else "nincs")

print("\n=== 4) Git státusz ===")
try:
    out = subprocess.check_output("git status --short", shell=True, text=True, stderr=subprocess.STDOUT)
    print(out if out.strip() else "Git munkaterület tiszta vagy csak nincs listázott változás.")
except Exception as e:
    print("Git status hiba:", e)

print("\n=== AUDIT VÉGE ===")
PY

echo "=== Jelentés mentve: $REPORT ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Ha az audit jó, írd: jó"
