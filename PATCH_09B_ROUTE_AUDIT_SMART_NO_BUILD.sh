#!/bin/bash
set -e

echo "=== PATCH 09B: SMART ROUTE AUDIT - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, fő kódot nem módosít."

mkdir -p logs
REPORT="logs/PATCH_09B_ROUTE_AUDIT_SMART_REPORT.txt"

python - <<'PY' | tee "$REPORT"
import re
from pathlib import Path
from collections import Counter

FILES = [Path("main.py"), Path("apk_stage/main.py")]

# Ezek a Master listás / jövőbeli menüpontok, amik lehetnek még félkész modulok.
PLANNED_ROUTES = {
    "admin",
    "ai_advisor",
    "apk_build_gate",
    "approval_executor",
    "backtest",
    "binance_account",
    "binance_live",
    "binance_readonly_real",
    "binance_signed",
    "demo_core",
    "demo_settings",
    "firstrun_readiness",
    "healthcheck",
    "home",
    "integration_tests",
    "integrations",
    "live_gate",
    "master_status",
    "patch_manager",
    "pre_apk_safe",
    "release_candidate",
    "scanner",
    "secrets",
    "spot_portfolio",
    "sync",
    "trade_logic",
    "trend_history",
    "ui_route_check",
}

def read(p):
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def extract_registered(txt):
    names = []

    patterns = [
        r'add_widget\s*\(\s*[A-Za-z_][A-Za-z0-9_]*\s*\(\s*name\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'safe_add_screen\s*\(\s*[^,]+,\s*[A-Za-z_][A-Za-z0-9_]*\s*\(\s*name\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'\bScreen\s*\(\s*name\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'\bScreenName\s*\(\s*name\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'\bname\s*=\s*[\'"]([^\'"]+)[\'"]',
    ]

    for pat in patterns:
        names += re.findall(pat, txt)

    # Szűrés: csak route-szerű nevek
    names = [
        n for n in names
        if re.match(r'^[a-zA-Z0-9_\-]+$', n)
        and len(n) <= 40
        and n not in {"left", "right", "center", "top", "bottom"}
    ]

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
        r'current\s*=\s*[\'"]([^\'"]+)[\'"]',
    ]
    for pat in patterns:
        routes += re.findall(pat, txt)

    routes = [
        r for r in routes
        if re.match(r'^[a-zA-Z0-9_\-]+$', r)
        and len(r) <= 40
    ]
    return routes

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

    registered = extract_registered(txt)
    routes = extract_routes(txt)

    reg_count = Counter(registered)
    route_count = Counter(routes)

    registered_set = set(registered)
    routes_set = set(routes)

    duplicate_registered = {k: v for k, v in reg_count.items() if v > 1 and k in routes_set}

    real_missing = sorted([
        r for r in routes_set
        if r not in registered_set and r not in PLANNED_ROUTES
    ])

    planned_missing = sorted([
        r for r in routes_set
        if r not in registered_set and r in PLANNED_ROUTES
    ])

    has_main_or_home = bool({"main", "home", "demo_core"} & registered_set)

    print("Registered count:", len(registered_set))
    print("Routes count:", len(routes_set))
    print("Registered screens/routes:")
    for x in sorted(registered_set):
        print("  -", x)

    print("")
    print("Duplicate registered used routes:", duplicate_registered if duplicate_registered else "nincs")
    print("Real missing routes:", real_missing if real_missing else "nincs")
    print("Planned / placeholder missing routes:", planned_missing if planned_missing else "nincs")
    print("Main/Home/DemoCore exists:", has_main_or_home)

    if duplicate_registered:
        print("HARD ERROR: duplikált aktív screen route van.")
        overall_hard_error = True

    if real_missing:
        print("HARD ERROR: nem tervezett, valóban hiányzó route van.")
        overall_hard_error = True

    if not has_main_or_home:
        print("HARD ERROR: nincs main/home/demo_core jellegű főképernyő.")
        overall_hard_error = True

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
echo "=== PATCH 09B KÉSZ ==="
echo "Jelentés: $REPORT"
echo "APK build NEM indult."
echo "Commit NEM történt."
