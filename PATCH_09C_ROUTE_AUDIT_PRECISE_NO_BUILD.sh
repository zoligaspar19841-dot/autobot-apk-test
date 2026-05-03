#!/bin/bash
set -e

echo "=== PATCH 09C: PRECISE SCREEN ROUTE AUDIT - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, fő kódot nem módosít."

mkdir -p logs
REPORT="logs/PATCH_09C_ROUTE_AUDIT_PRECISE_REPORT.txt"

python - <<'PY' | tee "$REPORT"
import re
from pathlib import Path
from collections import Counter

FILES = [Path("main.py"), Path("apk_stage/main.py")]

PLANNED_ROUTES = {
    "admin","ai_advisor","apk_build_gate","approval_executor","backtest",
    "binance_account","binance_live","binance_readonly_real","binance_signed",
    "demo_core","demo_settings","firstrun_readiness","healthcheck","home",
    "integration_tests","integrations","live_gate","master_status","patch_manager",
    "pre_apk_safe","release_candidate","scanner","secrets","spot_portfolio",
    "sync","trade_logic","trend_history","ui_route_check","settings",
    "trade_simple","trade_simple_advanced","strategy","strategy_advanced",
    "schedules","trades_export","security","startup_safety","safety_guards",
    "readonly_balance","profit_report","profit_hold_ai","ui_mockup"
}

def read(p):
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def extract_real_registered(txt):
    names = []

    # Csak valódi ScreenManager hozzáadás.
    patterns = [
        r'sm\.add_widget\s*\(\s*[A-Za-z_][A-Za-z0-9_]*\s*\(\s*name\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'self\.sm\.add_widget\s*\(\s*[A-Za-z_][A-Za-z0-9_]*\s*\(\s*name\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'safe_add_screen\s*\(\s*sm\s*,\s*[A-Za-z_][A-Za-z0-9_]*\s*\(\s*name\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'safe_add_screen\s*\(\s*self\.sm\s*,\s*[A-Za-z_][A-Za-z0-9_]*\s*\(\s*name\s*=\s*[\'"]([^\'"]+)[\'"]',
    ]

    for pat in patterns:
        names += re.findall(pat, txt)

    return names

def extract_routes(txt):
    routes = []
    patterns = [
        r'safe_go_to\s*\(\s*[\'"]([^\'"]+)[\'"]',
        r'go_to\s*\(\s*[\'"]([^\'"]+)[\'"]',
        r'go_screen\s*\(\s*[\'"]([^\'"]+)[\'"]',
        r'open_screen\s*\(\s*[\'"]([^\'"]+)[\'"]',
        r'manager\.current\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'self\.manager\.current\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'sm\.current\s*=\s*[\'"]([^\'"]+)[\'"]',
    ]

    for pat in patterns:
        routes += re.findall(pat, txt)

    return [
        r for r in routes
        if re.match(r'^[a-zA-Z0-9_\-]+$', r)
        and len(r) <= 50
    ]

overall_hard_error = False

for f in FILES:
    txt = read(f)

    print("")
    print("=" * 70)
    print("FILE:", f)
    print("=" * 70)

    if not txt:
        print("HARD ERROR: fájl hiányzik vagy üres")
        overall_hard_error = True
        continue

    registered = extract_real_registered(txt)
    routes = extract_routes(txt)

    reg_counter = Counter(registered)
    route_set = set(routes)
    registered_set = set(registered)

    # Csak az baj, ha valódi sm.add_widget ismétli ugyanazt.
    # safe_add_screen duplikáció runtime védett, de itt is megmutatjuk.
    true_duplicates = {k: v for k, v in reg_counter.items() if v > 1}

    missing_real = sorted([
        r for r in route_set
        if r not in registered_set and r not in PLANNED_ROUTES
    ])

    planned_missing = sorted([
        r for r in route_set
        if r not in registered_set and r in PLANNED_ROUTES
    ])

    has_entry = bool({"main", "home", "demo_core"} & registered_set)

    print("Real registered screens:", sorted(registered_set))
    print("Real registered count:", len(registered_set))
    print("Routes used count:", len(route_set))
    print("True duplicate registered screens:", true_duplicates if true_duplicates else "nincs")
    print("Real missing routes:", missing_real if missing_real else "nincs")
    print("Planned / placeholder missing routes:", planned_missing if planned_missing else "nincs")
    print("Main/Home/DemoCore exists:", has_entry)

    if missing_real:
        overall_hard_error = True
        print("HARD ERROR: valódi hiányzó route van.")

    if not has_entry:
        overall_hard_error = True
        print("HARD ERROR: nincs belépő főképernyő.")

    # Duplikált valódi screen csak akkor hard error, ha NINCS safe_add_screen védelem.
    if true_duplicates and "def safe_add_screen" not in txt:
        overall_hard_error = True
        print("HARD ERROR: duplikált screen van safe_add_screen védelem nélkül.")
    elif true_duplicates:
        print("INFO: duplikált regisztráció látszik, de safe_add_screen védelem jelen van.")

print("")
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("Hard error:", overall_hard_error)
print("APK build NEM indult.")
print("Commit NEM történt.")

if overall_hard_error:
    raise SystemExit(2)
PY

echo ""
echo "=== PATCH 09C KÉSZ ==="
echo "Jelentés: $REPORT"
echo "APK build NEM indult."
echo "Commit NEM történt."
