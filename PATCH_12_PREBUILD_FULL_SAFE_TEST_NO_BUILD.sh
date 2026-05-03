#!/bin/bash
set -e

echo "=== PATCH 12: PRE-BUILD FULL SAFE TEST - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, nem küld Binance ordert."

mkdir -p logs
REPORT="logs/PATCH_12_PREBUILD_FULL_SAFE_TEST_REPORT.txt"

{
echo "PATCH 12 PRE-BUILD FULL SAFE TEST"
echo "APK build: NEM indult"
echo "Commit: NEM történt"
echo "Idő: $(date)"
echo ""

echo "============================================================"
echo "1) Python compile teszt"
echo "============================================================"
python -m py_compile main.py demo_core_engine.py && echo "OK: root compile jó"
python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py && echo "OK: apk_stage compile jó"

echo ""
echo "============================================================"
echo "2) buildozer.spec gyors ellenőrzés"
echo "============================================================"
echo "--- root buildozer.spec ---"
grep -nE "^(title|package.name|package.domain|source.include_exts|version|android.api|android.minapi|android.archs|icon.filename)" buildozer.spec || true

echo ""
echo "--- apk_stage/buildozer.spec ---"
grep -nE "^(title|package.name|package.domain|source.include_exts|version|android.api|android.minapi|android.archs|icon.filename)" apk_stage/buildozer.spec || true

echo ""
echo "Duplikált buildozer kulcsok root:"
python - <<'PY'
from pathlib import Path
from collections import Counter

for f in ["buildozer.spec", "apk_stage/buildozer.spec"]:
    print("FILE:", f)
    p = Path(f)
    if not p.exists():
        print("HIBA: hiányzik")
        continue
    keys = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k = s.split("=", 1)[0].strip()
        keys.append(k)
    dup = {k:v for k,v in Counter(keys).items() if v > 1}
    print("DUP:", dup if dup else "nincs")
PY

echo ""
echo "============================================================"
echo "3) Ikon ellenőrzés"
echo "============================================================"
ls -lah icon.png apk_stage/icon.png 2>/dev/null || true
python - <<'PY'
from pathlib import Path
for f in ["icon.png", "apk_stage/icon.png"]:
    p = Path(f)
    print(f, "exists:", p.exists(), "size:", p.stat().st_size if p.exists() else "-")
PY

echo ""
echo "============================================================"
echo "4) main.py és apk_stage/main.py egyezés gyors diff"
echo "============================================================"
if cmp -s main.py apk_stage/main.py; then
    echo "OK: main.py és apk_stage/main.py azonos"
else
    echo "FIGYELEM: main.py és apk_stage/main.py eltér"
    diff -u main.py apk_stage/main.py | head -80 || true
fi

echo ""
echo "============================================================"
echo "5) Screen / route audit gyors"
echo "============================================================"
python - <<'PY'
import re
from pathlib import Path
from collections import Counter

FILES = [Path("main.py"), Path("apk_stage/main.py")]
hard = False

for f in FILES:
    txt = f.read_text(encoding="utf-8", errors="replace")
    names = re.findall(r'safe_add_screen\s*\(\s*[^,]+,\s*[A-Za-z_][A-Za-z0-9_]*\s*\(\s*name\s*=\s*[\'"]([^\'"]+)[\'"]', txt)
    names += re.findall(r'\.add_widget\s*\(\s*[A-Za-z_][A-Za-z0-9_]*\s*\(\s*name\s*=\s*[\'"]([^\'"]+)[\'"]', txt)
    c = Counter(names)
    d = {k:v for k,v in c.items() if v > 1}
    has_entry = bool({"main", "home", "demo_core"} & set(names))
    print("FILE:", f)
    print("  registered:", len(set(names)))
    print("  duplicates:", d if d else "nincs")
    print("  main/home/demo_core:", has_entry)
    print("  safe_add_screen:", "def safe_add_screen" in txt)
    if not has_entry:
        hard = True

print("Hard route error:", hard)
if hard:
    raise SystemExit(2)
PY

echo ""
echo "============================================================"
echo "6) Android target ellenőrzés"
echo "============================================================"
python - <<'PY'
from pathlib import Path

required = {
    "android.api": "35",
    "android.minapi": "23",
}

hard = False

for f in ["buildozer.spec", "apk_stage/buildozer.spec"]:
    print("FILE:", f)
    txt = Path(f).read_text(encoding="utf-8", errors="replace")
    data = {}
    for line in txt.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        data[k.strip()] = v.strip()

    for k, want in required.items():
        got = data.get(k)
        print(f"  {k}: {got}")
        if got != want:
            print(f"  HIBA: {k} nem {want}")
            hard = True

    icon = data.get("icon.filename")
    print("  icon.filename:", icon)
    if not icon:
        print("  HIBA: nincs icon.filename")
        hard = True

if hard:
    raise SystemExit(2)
else:
    print("OK: android target és ikon beállítás rendben")
PY

echo ""
echo "============================================================"
echo "7) Git rövid állapot"
echo "============================================================"
git status --short

echo ""
echo "============================================================"
echo "SUMMARY"
echo "============================================================"
echo "PREBUILD_SAFE_TEST: OK"
echo "APK build NEM indult."
echo "Commit NEM történt."

} | tee "$REPORT"

echo ""
echo "=== PATCH 12 KÉSZ ==="
echo "Jelentés: $REPORT"
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Ha minden OK, írd: jó"
