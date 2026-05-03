#!/bin/bash
set -e

echo "=== PATCH 10B: SETTINGS / SECRETS MOBIL TEXTINPUT FIX - APK BUILD NÉLKÜL ==="

TS=$(date +%Y%m%d_%H%M%S)

echo "=== 1) Biztonsági mentés ==="
cp main.py "main.py.bak_patch10b_settings_mobile_$TS"
cp apk_stage/main.py "apk_stage/main.py.bak_patch10b_settings_mobile_$TS"

echo "=== 2) Mobilbarát TextInput/Button stílus helper beépítése ==="

python - <<'PY'
from pathlib import Path

FILES = [Path("main.py"), Path("apk_stage/main.py")]

HELPER = r'''

# === PATCH 10B SETTINGS MOBILE UI HELPERS ===
def ba_style_textinput(widget, height=46):
    """Mobilbarát sötét TextInput stílus."""
    try:
        widget.size_hint_y = None
        widget.height = height
        widget.multiline = False
        widget.font_size = 16
        widget.foreground_color = (1, 1, 1, 1)
        widget.background_color = (0.08, 0.08, 0.08, 1)
        widget.cursor_color = (1.0, 0.72, 0.12, 1)
        widget.padding = [10, 10, 10, 10]
    except Exception:
        pass
    return widget

def ba_style_button(widget, height=48):
    """Mobilbarát sötét/sárga gombstílus."""
    try:
        widget.size_hint_y = None
        widget.height = height
        widget.font_size = 15
        widget.background_color = (0.22, 0.22, 0.22, 1)
        widget.color = (1, 1, 1, 1)
    except Exception:
        pass
    return widget

def ba_bind_grid_height(grid):
    """GridLayout magasság fix ScrollView-hoz."""
    try:
        grid.size_hint_y = None
        grid.bind(minimum_height=grid.setter('height'))
    except Exception:
        pass
    return grid
# === END PATCH 10B SETTINGS MOBILE UI HELPERS ===

'''

def insert_helper(s: str) -> str:
    if "PATCH 10B SETTINGS MOBILE UI HELPERS" in s:
        return s

    if "def safe_add_screen" in s:
        return s.replace("def safe_add_screen", HELPER + "\ndef safe_add_screen", 1)

    if "class " in s:
        return s.replace("class ", HELPER + "\nclass ", 1)

    return HELPER + "\n" + s

def inject_after_assignments(s: str) -> str:
    lines = s.splitlines()
    out = []
    pending = None
    paren_depth = 0
    injected_markers = {
        "TextInput": "ba_style_textinput",
        "Button": "ba_style_button",
        "GridLayout": "ba_bind_grid_height",
    }

    for line in lines:
        out.append(line)

        stripped = line.strip()

        # Ne injektáljunk helper definíciókbe.
        if "def ba_style_textinput" in line or "def ba_style_button" in line or "def ba_bind_grid_height" in line:
            pending = None

        if pending is None:
            # változó = TextInput( / Button( / GridLayout(
            for typ, helper in injected_markers.items():
                if f"= {typ}(" in line or f"={typ}(" in line:
                    var = line.split("=")[0].strip()
                    if var and var.replace("_", "").replace(".", "").isalnum():
                        pending = (var, helper, line[:len(line)-len(line.lstrip())])
                        paren_depth = line.count("(") - line.count(")")
                        # egysoros hívás
                        if paren_depth <= 0:
                            var, helper, indent = pending
                            marker = f"{helper}({var})"
                            # ha a következő sorokban már van, nem baj; minimalista
                            out.append(f"{indent}{marker}")
                            pending = None
                    break
        else:
            paren_depth += line.count("(") - line.count(")")
            if paren_depth <= 0:
                var, helper, indent = pending
                marker = f"{helper}({var})"
                out.append(f"{indent}{marker}")
                pending = None

    return "\n".join(out) + "\n"

for p in FILES:
    s = p.read_text(encoding="utf-8", errors="replace")
    s = insert_helper(s)

    # Csak ha még nincs 10B injektált alkalmazás.
    if "ba_style_textinput(inp)" not in s and "ba_bind_grid_height(form)" not in s:
        s = inject_after_assignments(s)

    p.write_text(s, encoding="utf-8")
    print("OK patched:", p)
PY

echo "=== 3) Python compile teszt ==="
python -m py_compile main.py demo_core_engine.py
python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py

echo "=== 4) Ellenőrzés ==="
grep -n "PATCH 10B SETTINGS MOBILE UI HELPERS" main.py apk_stage/main.py
grep -n "ba_style_textinput" main.py apk_stage/main.py | head -30
grep -n "ba_bind_grid_height" main.py apk_stage/main.py | head -30

echo "=== 5) Git állapot - commit nincs, push nincs ==="
git status --short

echo "=== PATCH 10B KÉSZ ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Ha ez jó, írd: jó"
