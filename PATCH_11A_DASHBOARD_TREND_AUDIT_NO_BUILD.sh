#!/bin/bash
set -e

echo "=== PATCH 11A: DASHBOARD / TREND AUDIT - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, fő kódot nem módosít."

mkdir -p logs
REPORT="logs/PATCH_11A_DASHBOARD_TREND_AUDIT_REPORT.txt"

python - <<'PY' | tee "$REPORT"
from pathlib import Path
import re

FILES = [Path("main.py"), Path("apk_stage/main.py")]

KEYWORDS = [
    "Dashboard",
    "dashboard",
    "modern_dashboard",
    "Trend",
    "trend",
    "sparkline",
    "Canvas",
    "canvas",
    "Line",
    "Color",
    "Rectangle",
    "Balance",
    "Equity",
    "PnL",
    "Realized",
    "Open Positions",
    "USDC",
    "USDT",
    "Profit",
    "SMA",
    "RSI",
]

def read(p):
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def find_relevant_classes(txt):
    pattern = re.compile(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\):", re.M)
    matches = list(pattern.finditer(txt))
    blocks = []

    for i, m in enumerate(matches):
        name = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(txt)
        block = txt[start:end]

        lname = name.lower()
        b = block.lower()

        if (
            "dashboard" in lname
            or "trend" in lname
            or "core" in lname
            or "chart" in lname
            or "kpi" in lname
            or "dashboard" in b
            or "trend" in b
            or "sparkline" in b
            or "canvas" in b
            or "balance" in b
            or "equity" in b
            or "open positions" in b
        ):
            blocks.append((name, block))

    return blocks

print("PATCH 11A DASHBOARD / TREND AUDIT")
print("=" * 70)
print("APK build: NEM indult")
print("Commit: NEM történt")
print("")

hard_error = False

for f in FILES:
    txt = read(f)

    print("")
    print("=" * 70)
    print("FILE:", f)
    print("=" * 70)

    if not txt:
        print("HIBA: fájl hiányzik vagy üres")
        hard_error = True
        continue

    print("Gyors kulcsszó számláló:")
    for k in KEYWORDS:
        print(f"  {k}: {txt.count(k)}")

    blocks = find_relevant_classes(txt)
    print("")
    print("Dashboard/Trend/KPI related classes:")
    for name, _ in blocks:
        print("  -", name)

    print("")
    print("Fontos blokkok első része:")
    for name, block in blocks[:12]:
        print("")
        print("-" * 70)
        print("CLASS:", name)
        print("-" * 70)
        lines = block.splitlines()
        for idx, line in enumerate(lines[:180], 1):
            print(f"{idx:04d}: {line}")

    required_any = ["Balance", "Equity", "PnL", "Open Positions"]
    missing = [x for x in required_any if x not in txt]

    if missing:
        print("")
        print("FIGYELEM: hiányzó KPI szöveg:", missing)
    else:
        print("")
        print("OK: alap KPI szövegek megtalálhatók.")

print("")
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("Hard error:", hard_error)
print("APK build NEM indult.")
print("Commit NEM történt.")

if hard_error:
    raise SystemExit(2)
PY

echo ""
echo "=== Python compile ellenőrzés ==="
python -m py_compile main.py demo_core_engine.py
python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py
echo "OK: compile jó"

echo ""
echo "=== PATCH 11A KÉSZ ==="
echo "Jelentés: $REPORT"
echo "APK build NEM indult."
echo "Commit NEM történt."
echo ""
echo "Küldd el a fontos részt ezzel:"
echo "grep -nE 'CLASS:|Dashboard|dashboard|Trend|trend|sparkline|Canvas|Line|Balance|Equity|PnL|Open Positions|SUMMARY|Hard error' $REPORT | head -200"
