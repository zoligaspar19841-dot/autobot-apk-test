#!/bin/bash
set -e

echo "=== PATCH 10A: SETTINGS LAYOUT AUDIT - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, fő kódot nem módosít."

mkdir -p logs
REPORT="logs/PATCH_10A_SETTINGS_LAYOUT_AUDIT_REPORT.txt"

python - <<'PY' | tee "$REPORT"
from pathlib import Path
import re

FILES = [Path("main.py"), Path("apk_stage/main.py")]

KEYWORDS = [
    "Settings",
    "settings",
    "demo_settings",
    "security",
    "secrets",
    "api",
    "email",
    "TextInput",
    "GridLayout",
    "ScrollView",
    "BoxLayout",
]

def read(p):
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def find_classes(txt):
    pattern = re.compile(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\):", re.M)
    matches = list(pattern.finditer(txt))
    blocks = []

    for i, m in enumerate(matches):
        name = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(txt)
        block = txt[start:end]
        if any(k.lower() in name.lower() for k in ["setting", "security", "secret", "api", "email"]):
            blocks.append((name, block))
        elif any(k in block for k in ["demo_settings", "TextInput", "API", "E-mail", "Email"]):
            if any(k.lower() in block.lower() for k in ["setting", "security", "secret", "email", "api"]):
                blocks.append((name, block))

    return blocks

print("PATCH 10A SETTINGS LAYOUT AUDIT")
print("=" * 70)
print("APK build: NEM indult")
print("Commit: NEM történt")
print("")

for f in FILES:
    txt = read(f)
    print("")
    print("=" * 70)
    print("FILE:", f)
    print("=" * 70)

    if not txt:
        print("HIBA: fájl hiányzik vagy üres")
        continue

    blocks = find_classes(txt)
    print("Settings/Security/API related classes:", [name for name, _ in blocks])

    print("")
    print("Gyors kulcsszó számláló:")
    for k in KEYWORDS:
        print(f"  {k}: {txt.count(k)}")

    print("")
    print("Talált Settings blokkok:")
    for name, block in blocks:
        print("")
        print("-" * 70)
        print("CLASS:", name)
        print("-" * 70)
        lines = block.splitlines()
        for idx, line in enumerate(lines[:220], 1):
            print(f"{idx:04d}: {line}")

print("")
print("=" * 70)
print("PATCH 10A AUDIT VÉGE")
print("=" * 70)
PY

echo ""
echo "=== PATCH 10A KÉSZ ==="
echo "Jelentés: $REPORT"
echo "APK build NEM indult."
echo "Commit NEM történt."
echo ""
echo "Most küldd el a report fontos részét ezzel:"
echo "grep -nE 'CLASS:|TextInput|GridLayout|ScrollView|BoxLayout|demo_settings|settings|security|api|email' $REPORT | head -160"
