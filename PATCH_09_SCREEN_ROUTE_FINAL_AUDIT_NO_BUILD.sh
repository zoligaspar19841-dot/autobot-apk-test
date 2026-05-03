#!/bin/bash
set -e

echo "=== PATCH 09: SCREEN / ROUTE FINAL AUDIT - APK BUILD NÉLKÜL ==="
echo "Ez csak ellenőrzés. Nem buildel, nem pushol, nem küld Binance ordert."

mkdir -p logs

echo
echo "=== 1) Python compile ellenőrzés ==="
python -m py_compile main.py demo_core_engine.py
echo "OK: root compile jó"

if [ -f apk_stage/main.py ] && [ -f apk_stage/demo_core_engine.py ]; then
  python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py
  echo "OK: apk_stage compile jó"
else
  echo "FIGYELEM: apk_stage/main.py vagy apk_stage/demo_core_engine.py hiányzik"
fi

echo
echo "=== 2) Screen / route audit ==="

python - <<'PY'
import re, json, time
from pathlib import Path
from collections import Counter

REPORT_JSON = Path("logs/PATCH_09_SCREEN_ROUTE_FINAL_AUDIT_REPORT.json")
REPORT_TXT = Path("logs/PATCH_09_SCREEN_ROUTE_FINAL_AUDIT_REPORT.txt")

FILES = [
    Path("main.py"),
    Path("apk_stage/main.py"),
]

def read(p):
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def extract_screen_names(txt):
    names = []

    # Klasszikus: sm.add_widget(XScreen(name="demo"))
    for m in re.finditer(r'add_widget\s*\(\s*[A-Za-z_][A-Za-z0-9_]*\s*\(\s*name\s*=\s*[\'"]([^\'"]+)[\'"]', txt):
        names.append(m.group(1))

    # ScreenName(name="main") minták
    for m in re.finditer(r'ScreenName\s*\(\s*name\s*=\s*[\'"]([^\'"]+)[\'"]', txt):
        names.append(m.group(1))

    # Screen(name="main") minták
    for m in re.finditer(r'\bScreen\s*\(\s*name\s*=\s*[\'"]([^\'"]+)[\'"]', txt):
        names.append(m.group(1))

    return names

def extract_routes(txt):
    routes = []

    patterns = [
        r'go_to\s*\(\s*[\'"]([^\'"]+)[\'"]',
        r'manager\.current\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'self\.current\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'current\s*=\s*[\'"]([^\'"]+)[\'"]',
    ]

    for pat in patterns:
        for m in re.finditer(pat, txt):
            routes.append(m.group(1))

    return routes

def extract_classes(txt):
    return re.findall(r'^class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', txt, flags=re.M)

def audit_file(p):
    txt = read(p)
    if not txt:
        return {
            "file": str(p),
            "exists": p.exists(),
            "ok": False,
            "error": "file missing or empty",
        }

    screen_names = extract_screen_names(txt)
    routes = extract_routes(txt)
    classes = extract_classes(txt)

    c = Counter(screen_names)
    duplicates = {k: v for k, v in c.items() if v > 1}

    registered = set(screen_names)

    # Ezek lehetnek különleges / dinamikus útvonalak, nem hiba önmagukban
    allowed_dynamic = {
        "",
        "None",
    }

    missing_routes = sorted(set(
        r for r in routes
        if r not in registered and r not in allowed_dynamic
    ))

    # Ha home/main közül csak az egyik van, ezt külön jelezzük, mert gyakori navigációs hiba
    has_home = "home" in registered
    has_main = "main" in registered

    warnings = []
    if has_home and has_main:
        warnings.append("home és main is létezik; ez lehet szándékos, de ellenőrizni kell a főmenü logikát.")
    if not has_home and not has_main:
        warnings.append("Nincs home vagy main screen regisztrálva.")

    return {
        "file": str(p),
        "exists": True,
        "ok": not duplicates and not missing_routes,
        "screen_count": len(screen_names),
        "registered_screens": sorted(registered),
        "duplicates": duplicates,
        "routes_count": len(routes),
        "routes": sorted(set(routes)),
        "missing_routes": missing_routes,
        "class_count": len(classes),
        "classes_sample": classes[:80],
        "warnings": warnings,
    }

reports = [audit_file(p) for p in FILES]

overall_ok = all(r.get("ok") for r in reports if r.get("exists"))

summary = {
    "ts": int(time.time()),
    "no_build": True,
    "apk_build_touched": False,
    "order_endpoint_used": False,
    "ok": overall_ok,
    "reports": reports,
}

REPORT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

lines = []
lines.append("PATCH 09 SCREEN / ROUTE FINAL AUDIT")
lines.append("=" * 70)
lines.append(f"OK: {overall_ok}")
lines.append("APK build: NEM indult")
lines.append("Commit: NEM történt")
lines.append("")

for r in reports:
    lines.append("-" * 70)
    lines.append(f"FILE: {r.get('file')}")
    lines.append(f"EXISTS: {r.get('exists')}")
    lines.append(f"OK: {r.get('ok')}")
    if not r.get("exists"):
        lines.append(f"ERROR: {r.get('error')}")
        continue

    lines.append(f"SCREEN COUNT: {r.get('screen_count')}")
    lines.append("REGISTERED SCREENS:")
    for x in r.get("registered_screens", []):
        lines.append(f"  - {x}")

    lines.append("")
    lines.append(f"DUPLICATES: {r.get('duplicates')}")
    lines.append(f"MISSING ROUTES: {r.get('missing_routes')}")
    lines.append(f"WARNINGS: {r.get('warnings')}")

REPORT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "ok": overall_ok,
    "json": str(REPORT_JSON),
    "txt": str(REPORT_TXT),
    "files_checked": [str(p) for p in FILES],
}, ensure_ascii=False, indent=2))

if not overall_ok:
    print("")
    print("HIBA: van még screen/route probléma.")
    print("Nézd meg:")
    print(REPORT_TXT)
    raise SystemExit(2)

print("")
print("OK: screen/route audit tiszta.")
PY

echo
echo "=== 3) Android target / ikon gyors ellenőrzés ==="

echo "--- buildozer.spec ---"
grep -nE "title|package.name|package.domain|version|android.api|android.minapi|android.archs|icon.filename|source.include_exts" buildozer.spec || true

echo
echo "--- apk_stage/buildozer.spec ---"
grep -nE "title|package.name|package.domain|version|android.api|android.minapi|android.archs|icon.filename|source.include_exts" apk_stage/buildozer.spec || true

echo
echo "--- ikon fájlok ---"
ls -lah icon.png apk_stage/icon.png 2>/dev/null || true

echo
echo "=== PATCH 09 KÉSZ ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Jelentés:"
echo "logs/PATCH_09_SCREEN_ROUTE_FINAL_AUDIT_REPORT.txt"
echo
echo "Ha OK és nincs HIBA, írd: jó"
