#!/bin/bash
set -e

echo "=== PATCH 13A: APK STAGE CONTENT AUDIT - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, nem módosít fő kódot."

mkdir -p logs
REPORT="logs/PATCH_13A_APK_STAGE_CONTENT_AUDIT_REPORT.txt"

{
echo "PATCH 13A APK STAGE CONTENT AUDIT"
echo "APK build: NEM indult"
echo "Commit: NEM történt"
echo "Idő: $(date)"
echo ""

echo "============================================================"
echo "1) apk_stage fájlok"
echo "============================================================"
find apk_stage -maxdepth 2 -type f | sort

echo ""
echo "============================================================"
echo "2) root fő fájlok"
echo "============================================================"
find . -maxdepth 1 -type f \( -name "*.py" -o -name "*.json" -o -name "*.png" -o -name "*.kv" \) | sort

echo ""
echo "============================================================"
echo "3) Import audit main.py / apk_stage/main.py"
echo "============================================================"
python - <<'PY'
from pathlib import Path
import ast

ROOT_PY = {p.stem for p in Path(".").glob("*.py")}
STAGE_PY = {p.stem for p in Path("apk_stage").glob("*.py")}

def imports_of(path):
    txt = Path(path).read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(txt)
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                mods.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module.split(".")[0])
    return mods

for f in ["main.py", "apk_stage/main.py"]:
    mods = imports_of(f)
    local_imports = sorted([m for m in mods if m in ROOT_PY or m in STAGE_PY])
    missing_in_stage = sorted([m for m in local_imports if m not in STAGE_PY])

    print("FILE:", f)
    print("Local imports:", local_imports)
    print("Missing in apk_stage:", missing_in_stage if missing_in_stage else "nincs")
    print("")

print("ROOT_PY:", sorted(ROOT_PY))
print("STAGE_PY:", sorted(STAGE_PY))
PY

echo ""
echo "============================================================"
echo "4) buildozer source.include_exts"
echo "============================================================"
grep -nE "source.include_exts|requirements|android.api|android.minapi|icon.filename|version|package.name|package.domain" buildozer.spec apk_stage/buildozer.spec || true

echo ""
echo "============================================================"
echo "5) Python compile"
echo "============================================================"
python -m py_compile main.py demo_core_engine.py
python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py
echo "OK: compile jó"

echo ""
echo "============================================================"
echo "SUMMARY"
echo "============================================================"
echo "APK_STAGE_AUDIT: kész"
echo "APK build NEM indult."
echo "Commit NEM történt."

} | tee "$REPORT"

echo ""
echo "=== PATCH 13A KÉSZ ==="
echo "Jelentés: $REPORT"
echo "APK build NEM indult."
echo "Commit NEM történt."
echo ""
echo "Küldd be ezt:"
echo "grep -nE 'Missing in apk_stage|ROOT_PY|STAGE_PY|source.include_exts|requirements|SUMMARY' $REPORT"
