#!/bin/bash
set -e

echo "=== PATCH 06B: Duplikált screen name javítás - APK BUILD NÉLKÜL ==="

TS=$(date +%Y%m%d_%H%M%S)

echo "=== 1) Biztonsági mentés ==="
cp main.py "main.py.bak_patch06b_routes_$TS"
cp apk_stage/main.py "apk_stage/main.py.bak_patch06b_routes_$TS"

echo "=== 2) Duplikált add_widget screen nevek javítása ==="
python - <<'PY'
from pathlib import Path
import re

FILES = [Path("main.py"), Path("apk_stage/main.py")]

def patch_file(p: Path):
    s = p.read_text(encoding="utf-8", errors="replace")

    # Csak az ismert duplikációkat kezeljük: main és scanner.
    # Az első példány marad, a továbbiakat kommenteljük.
    lines = s.splitlines()
    seen_names = {}
    out = []

    pattern = re.compile(r'(\s*)sm\.add_widget\((\w+)\(name=["\']([^"\']+)["\']\)\)')

    for line in lines:
        m = pattern.search(line)
        if m:
            indent, cls, name = m.groups()
            if name in ("main", "scanner"):
                seen_names[name] = seen_names.get(name, 0) + 1
                if seen_names[name] > 1:
                    out.append(indent + "# PATCH 06B: duplikált screen eltávolítva: " + line.strip())
                    continue
        out.append(line)

    s2 = "\n".join(out) + "\n"

    p.write_text(s2, encoding="utf-8")
    print("OK patched:", p)

for p in FILES:
    patch_file(p)
PY

echo "=== 3) Python compile teszt - build nélkül ==="
python -m py_compile main.py demo_core_engine.py
python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py

echo "=== 4) Új screen name ellenőrzés ==="
python - <<'PY'
from pathlib import Path
from collections import Counter
import re

for f in [Path("main.py"), Path("apk_stage/main.py")]:
    text = f.read_text(encoding="utf-8", errors="replace")
    add_widgets = re.findall(r'add_widget\((\w+)\(name=["\']([^"\']+)["\']', text)
    names = [name for _, name in add_widgets]
    dup = {k:v for k,v in Counter(names).items() if v > 1}
    print(f, "Duplikált screen name:", dup if dup else "nincs")
PY

echo "=== 5) Git állapot - commit nincs, push nincs ==="
git status --short

echo "=== PATCH 06B KÉSZ ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Ha ez jó, utána mentjük Patch 06 + 06B checkpointként."
