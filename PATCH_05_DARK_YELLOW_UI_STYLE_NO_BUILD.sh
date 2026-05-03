#!/bin/bash
set -e

echo "=== PATCH 05: Egységes sötét/sárga UI stílus - APK BUILD NÉLKÜL ==="

TS=$(date +%Y%m%d_%H%M%S)

echo "=== 1) Biztonsági mentés ==="
cp main.py "main.py.bak_patch05_style_$TS"
cp apk_stage/main.py "apk_stage/main.py.bak_patch05_style_$TS"

echo "=== 2) Globális Kivy stílus beszúrása ==="
python - <<'PY'
from pathlib import Path

FILES = [Path("main.py"), Path("apk_stage/main.py")]

STYLE_CODE = r'''

# === PATCH 05 DARK/YELLOW GLOBAL UI STYLE ===
try:
    from kivy.lang import Builder

    Builder.load_string("""
<Button>:
    background_normal: ''
    background_down: ''
    background_color: 0.30, 0.30, 0.30, 1
    color: 1, 1, 1, 1
    font_size: '18sp'

<TextInput>:
    background_normal: ''
    background_active: ''
    background_color: 0.08, 0.08, 0.08, 1
    foreground_color: 1, 1, 1, 1
    cursor_color: 1, 0.82, 0.18, 1
    hint_text_color: 0.62, 0.62, 0.62, 1
    font_size: '17sp'
    padding: [10, 10, 10, 10]

<Label>:
    color: 1, 1, 1, 1
""")
except Exception:
    pass


APP_BG = (0.0, 0.0, 0.0, 1)
APP_YELLOW = (1.0, 0.78, 0.10, 1)
APP_DARK_CARD = (0.08, 0.08, 0.08, 1)
APP_BUTTON = (0.30, 0.30, 0.30, 1)


def make_title(text, subtitle=""):
    try:
        if subtitle:
            return Label(
                text="[b]" + text + "[/b]\\n[size=13]" + subtitle + "[/size]",
                markup=True,
                color=APP_YELLOW,
                size_hint_y=None,
                height=64,
                halign="center",
                valign="middle"
            )
        return Label(
            text="[b]" + text + "[/b]",
            markup=True,
            color=APP_YELLOW,
            size_hint_y=None,
            height=48,
            halign="center",
            valign="middle"
        )
    except Exception:
        return Label(text=text)


def make_dark_input(default_text=""):
    try:
        return TextInput(
            text="",
            hint_text=str(default_text),
            multiline=False,
            size_hint_y=None,
            height=48,
            foreground_color=(1, 1, 1, 1),
            background_color=(0.08, 0.08, 0.08, 1),
            cursor_color=(1, 0.82, 0.18, 1),
            hint_text_color=(0.62, 0.62, 0.62, 1),
            padding=[10, 10, 10, 10]
        )
    except Exception:
        return TextInput(text=str(default_text))


def style_button(btn):
    try:
        btn.background_normal = ""
        btn.background_down = ""
        btn.background_color = APP_BUTTON
        btn.color = (1, 1, 1, 1)
        btn.font_size = "18sp"
    except Exception:
        pass
    return btn
# === END PATCH 05 DARK/YELLOW GLOBAL UI STYLE ===

'''

def patch_file(p: Path):
    s = p.read_text(encoding="utf-8", errors="replace")

    if "PATCH 05 DARK/YELLOW GLOBAL UI STYLE" not in s:
        # importok után próbáljuk beszúrni
        marker = "NAV_STACK"
        if marker in s:
            idx = s.find(marker)
            s = s[:idx] + STYLE_CODE + "\n" + s[idx:]
        else:
            s = STYLE_CODE + "\n" + s

    # A legdurvább fehér inputokat sötétre tereljük, ha explicit fehér background maradt.
    s = s.replace("background_color=(1, 1, 1, 1)", "background_color=(0.08, 0.08, 0.08, 1)")
    s = s.replace("background_color = (1, 1, 1, 1)", "background_color = (0.08, 0.08, 0.08, 1)")
    s = s.replace("foreground_color=(0, 0, 0, 1)", "foreground_color=(1, 1, 1, 1)")
    s = s.replace("foreground_color = (0, 0, 0, 1)", "foreground_color = (1, 1, 1, 1)")

    p.write_text(s, encoding="utf-8")
    print("OK patched:", p)

for p in FILES:
    patch_file(p)
PY

echo "=== 3) Python compile teszt - build nélkül ==="
python -m py_compile main.py demo_core_engine.py
python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py

echo "=== 4) Ellenőrzés ==="
grep -nE "PATCH 05 DARK|APP_YELLOW|make_dark_input|style_button|background_color|foreground_color|hint_text_color" main.py | head -100
echo "--- apk_stage ---"
grep -nE "PATCH 05 DARK|APP_YELLOW|make_dark_input|style_button|background_color|foreground_color|hint_text_color" apk_stage/main.py | head -100

echo "=== 5) Git állapot - commit nincs, push nincs ==="
git status --short

echo "=== PATCH 05 KÉSZ ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Ha ez jó, írd: jó"
