#!/bin/bash
set -e

echo "=== PATCH 06C: safe_add_screen route védelem - APK BUILD NÉLKÜL ==="

TS=$(date +%Y%m%d_%H%M%S)

echo "=== 1) Biztonsági mentés ==="
cp main.py "main.py.bak_patch06c_safe_screen_$TS"
cp apk_stage/main.py "apk_stage/main.py.bak_patch06c_safe_screen_$TS"

echo "=== 2) safe_add_screen beépítése ==="
python - <<'PY'
from pathlib import Path
import re

FILES = [Path("main.py"), Path("apk_stage/main.py")]

HELPER = r'''

# === PATCH 06C SAFE SCREEN ADD ===
def safe_add_screen(sm, screen):
    try:
        name = getattr(screen, "name", None)
        if not name:
            sm.add_widget(screen)
            return True
        try:
            if sm.has_screen(name):
                return False
        except Exception:
            pass
        sm.add_widget(screen)
        return True
    except Exception:
        return False
# === END PATCH 06C SAFE SCREEN ADD ===

'''

for p in FILES:
    s = p.read_text(encoding="utf-8", errors="replace")

    if "PATCH 06C SAFE SCREEN ADD" not in s:
        if "def safe_go_back" in s:
            s = s.replace("def safe_go_back", HELPER + "\ndef safe_go_back", 1)
        else:
            s = HELPER + "\n" + s

    s = re.sub(
        r'(\s*)sm\.add_widget\((\w+\(name=["\'][^"\']+["\']\))\)',
        r'\1safe_add_screen(sm, \2)',
        s
    )

    p.write_text(s, encoding="utf-8")
    print("OK patched:", p)
PY

echo "=== 3) Python compile teszt ==="
python -m py_compile main.py demo_core_engine.py
python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py

echo "=== 4) Ellenőrzés ==="
python - <<'PY'
from pathlib import Path
from collections import Counter
import re

for f in [Path("main.py"), Path("apk_stage/main.py")]:
    text = f.read_text(encoding="utf-8", errors="replace")

    raw_add = re.findall(r'sm\.add_widget\((\w+)\(name=["\']([^"\']+)["\']', text)
    safe_add = re.findall(r'safe_add_screen\(sm,\s*(\w+)\(name=["\']([^"\']+)["\']', text)

    raw_names = [name for _, name in raw_add]
    safe_names = [name for _, name in safe_add]

    raw_dup = {k:v for k,v in Counter(raw_names).items() if v > 1}

    print("")
    print("FILE:", f)
    print("Direkt sm.add_widget duplikáció:", raw_dup if raw_dup else "nincs")
    print("safe_add_screen helper:", "OK" if "def safe_add_screen" in text else "HIÁNYZIK")
    print("safe_add_screen screenek:", Counter(safe_names))
PY

echo "=== 5) Git állapot ==="
git status --short

echo "=== PATCH 06C KÉSZ ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
