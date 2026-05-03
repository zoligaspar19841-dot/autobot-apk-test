#!/bin/bash
set -e

echo "=== PATCH 02: Android vissza gomb + navigáció stabilizálás - APK BUILD NÉLKÜL ==="

TS=$(date +%Y%m%d_%H%M%S)

echo "=== 1) Biztonsági mentés ==="
cp main.py "main.py.bak_patch02_back_$TS"
cp apk_stage/main.py "apk_stage/main.py.bak_patch02_back_$TS"

echo "=== 2) main.py + apk_stage/main.py javítás ==="
python - <<'PY'
from pathlib import Path
import re

FILES = [Path("main.py"), Path("apk_stage/main.py")]

BACK_HELPERS = r'''

# === PATCH 02 BACK NAVIGATION HELPERS ===
def safe_go_back(sm, fallback="main"):
    """
    Egységes vissza navigáció.
    - Ha van NAV_STACK: oda megy vissza.
    - Ha nincs stack: fallback/main.
    - Nem engedi, hogy hibára kifusson.
    """
    try:
        if sm is None:
            return False
        if "NAV_STACK" in globals() and NAV_STACK:
            target = NAV_STACK.pop()
            if target and target != getattr(sm, "current", None):
                sm.current = target
                return True
        if getattr(sm, "current", None) != fallback:
            sm.current = fallback
            return True
        return False
    except Exception:
        try:
            sm.current = fallback
            return True
        except Exception:
            return False


def safe_go_to(sm, screen):
    """
    Egységes előre navigáció stack mentéssel.
    """
    try:
        if sm is None:
            return False
        cur = getattr(sm, "current", None)
        if cur and cur != screen and "NAV_STACK" in globals():
            NAV_STACK.append(cur)
        sm.current = screen
        return True
    except Exception:
        try:
            sm.current = screen
            return True
        except Exception:
            return False
# === END PATCH 02 BACK NAVIGATION HELPERS ===

'''

def patch_file(p: Path):
    s = p.read_text(encoding="utf-8", errors="replace")

    # Window import ellenőrzés
    if "from kivy.core.window import Window" not in s:
        s = "from kivy.core.window import Window\n" + s

    # Helper csak egyszer
    if "PATCH 02 BACK NAVIGATION HELPERS" not in s:
        marker = "def load_json("
        if marker in s:
            s = s.replace(marker, BACK_HELPERS + "\n" + marker, 1)
        else:
            s = BACK_HELPERS + "\n" + s

    # A régi go_back függvény belsejét biztonságosabbra cseréljük, ha van
    s = re.sub(
        r'def go_back\(sm,\s*fallback="main"\):\n(?:    .*\n)+?\n(?=def |class |\Z)',
        '''def go_back(sm, fallback="main"):
    return safe_go_back(sm, fallback)

''',
        s,
        count=1
    )

    # A régi go_to függvény belsejét biztonságosabbra cseréljük, ha van
    s = re.sub(
        r'def go_to\(sm,\s*screen\):\n(?:    .*\n)+?\n(?=def |class |\Z)',
        '''def go_to(sm, screen):
    return safe_go_to(sm, screen)

''',
        s,
        count=1
    )

    # AppMain osztályba hardveres Android back kezelő beszúrása.
    # Csak akkor, ha még nincs.
    if "def _android_back_button" not in s:
        pattern = r'(class AppMain\(App\):\n(?:    .*\n)*?    def build\(self\):)'
        m = re.search(pattern, s)
        if m:
            insert = '''class AppMain(App):
    title = "Binance Autobot"

    def _android_back_button(self, window, key, *args):
        # Android BACK gomb: 27 / 1001
        if key in (27, 1001):
            try:
                handled = safe_go_back(self.root, "main")
                return True if handled else False
            except Exception:
                return False
        return False

    def on_start(self):
        try:
            Window.bind(on_keyboard=self._android_back_button)
        except Exception:
            pass

    def on_stop(self):
        try:
            Window.unbind(on_keyboard=self._android_back_button)
        except Exception:
            pass

    def build(self):'''
            s = s[:m.start()] + insert + s[m.end():]
        else:
            print("FIGYELEM: AppMain class nem található:", p)

    # Direkt home-ra visszadobáló VISSZA esetek egy részét safe_go_back-re tereljük.
    s = s.replace('go_to(self.manager, "main")', 'safe_go_back(self.manager, "main")')
    s = s.replace("go_to(self.manager, 'main')", "safe_go_back(self.manager, 'main')")
    s = s.replace('self.manager.current = "main"', 'safe_go_back(self.manager, "main")')
    s = s.replace("self.manager.current = 'main'", "safe_go_back(self.manager, 'main')")

    p.write_text(s, encoding="utf-8")
    print("OK patched:", p)

for p in FILES:
    patch_file(p)
PY

echo "=== 3) Python compile teszt - build nélkül ==="
python -m py_compile main.py demo_core_engine.py
python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py

echo "=== 4) Ellenőrzés ==="
grep -nE "PATCH 02 BACK|safe_go_back|_android_back_button|Window.bind|Window.unbind|def go_back|def go_to|class AppMain" main.py | head -80
echo "--- apk_stage ---"
grep -nE "PATCH 02 BACK|safe_go_back|_android_back_button|Window.bind|Window.unbind|def go_back|def go_to|class AppMain" apk_stage/main.py | head -80

echo "=== 5) Git állapot - commit nincs, push nincs ==="
git status --short

echo "=== PATCH 02 KÉSZ ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Ha ez jó, írd: jó"
