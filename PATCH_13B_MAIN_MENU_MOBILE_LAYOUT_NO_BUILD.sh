#!/bin/bash
set -e

echo "=== PATCH 13B: MAIN MENU MOBILE LAYOUT FIX - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, csak főmenü layout javítás."

TS=$(date +%Y%m%d_%H%M%S)

echo "=== 1) Biztonsági mentés ==="
cp main.py "main.py.bak_patch13b_main_menu_$TS"
cp apk_stage/main.py "apk_stage/main.py.bak_patch13b_main_menu_$TS"

echo "=== 2) MasterMenu osztály mobilbarát cseréje ==="

python - <<'PY'
from pathlib import Path
import re

FILES = [Path("main.py"), Path("apk_stage/main.py")]

NEW_CLASS = r'''class MasterMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation='vertical',
            padding=[8, 18, 8, 10],
            spacing=10
        )

        title = Label(
            text='BINANCE AUTOBOT',
            color=(1.0, 0.72, 0.10, 1),
            bold=True,
            font_size=22,
            size_hint_y=None,
            height=52,
            halign='center',
            valign='middle'
        )
        title.bind(size=lambda w, *_: setattr(w, 'text_size', w.size))
        root.add_widget(title)

        sub = Label(
            text='Stabil alap + óvatos patch rendszer',
            color=(0.78, 0.78, 0.78, 1),
            font_size=12,
            size_hint_y=None,
            height=24,
            halign='center',
            valign='middle'
        )
        sub.bind(size=lambda w, *_: setattr(w, 'text_size', w.size))
        root.add_widget(sub)

        scroll = ScrollView(size_hint=(1, 1))

        grid = GridLayout(
            cols=1,
            spacing=8,
            padding=[2, 4, 2, 10],
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter('height'))

        def add_btn(text, target, accent='yellow'):
            b = Button(
                text=text,
                size_hint_y=None,
                height=58,
                font_size=16,
                bold=True,
                halign='center',
                valign='middle'
            )
            b.bind(size=lambda w, *_: setattr(w, 'text_size', w.size))

            try:
                if accent == 'blue':
                    b.background_color = (0.05, 0.18, 0.75, 1)
                elif accent == 'red':
                    b.background_color = (0.55, 0.05, 0.05, 1)
                elif accent == 'green':
                    b.background_color = (0.05, 0.45, 0.16, 1)
                else:
                    b.background_color = (0.34, 0.34, 0.34, 1)
                b.color = (1, 1, 1, 1)
            except Exception:
                pass

            def go(_btn):
                try:
                    if self.manager and self.manager.has_screen(target):
                        self.manager.current = target
                    elif self.manager and self.manager.has_screen('demo_core'):
                        self.manager.current = 'demo_core'
                except Exception:
                    pass

            b.bind(on_press=go)
            grid.add_widget(b)

        # Fő, működéshez fontos menük
        add_btn('📊 DEMO CORE / DASHBOARD', 'demo_core', 'yellow')
        add_btn('📈 MODERN DASHBOARD / TREND', 'modern_dashboard', 'yellow')
        add_btn('💰 TRADE SIMPLE', 'trade_simple', 'green')
        add_btn('📉 STRATEGY ADVANCED', 'strategy_advanced', 'blue')
        add_btn('🧪 SCANNER / MULTI SYMBOL', 'scanner', 'blue')

        # Biztonság / beállítások
        add_btn('🔐 SETTINGS / SECURITY', 'settings', 'yellow')
        add_btn('🔑 SECRETS / API / EMAIL', 'secrets', 'yellow')
        add_btn('🛡️ PANIC / SAFE MODE', 'safety_guards', 'red')

        # Export / audit / fejlesztői részek
        add_btn('📄 TRADES / EXPORT', 'trades_export', 'green')
        add_btn('📦 PACKAGE / SNAPSHOT', 'package', 'blue')
        add_btn('🩺 HEALTHCHECK', 'health_alert', 'blue')
        add_btn('🛠 PATCH MANAGER', 'patch_manager', 'blue')
        add_btn('✅ PRE-APK SAFE TEST', 'pre_apk_safe', 'green')
        add_btn('📋 RELEASE CANDIDATE', 'release_candidate', 'green')

        scroll.add_widget(grid)
        root.add_widget(scroll)

        footer = Label(
            text='DEMO mód: biztonságos teszt | LIVE csak API ellenőrzés után',
            color=(0.70, 0.70, 0.70, 1),
            font_size=11,
            size_hint_y=None,
            height=30,
            halign='center',
            valign='middle'
        )
        footer.bind(size=lambda w, *_: setattr(w, 'text_size', w.size))
        root.add_widget(footer)

        self.add_widget(root)
'''

def replace_mastermenu(src: str) -> str:
    pattern = re.compile(
        r"^class\s+MasterMenu\s*\(Screen\):.*?(?=^class\s+[A-Za-z_][A-Za-z0-9_]*\s*\(|\Z)",
        re.M | re.S
    )
    if not pattern.search(src):
        raise SystemExit("HIBA: class MasterMenu(Screen) nem található")
    return pattern.sub(NEW_CLASS + "\n\n", src, count=1)

for p in FILES:
    s = p.read_text(encoding="utf-8", errors="replace")
    s2 = replace_mastermenu(s)
    p.write_text(s2, encoding="utf-8")
    print("OK patched:", p)
PY

echo "=== 3) Python compile teszt ==="
python -m py_compile main.py demo_core_engine.py
python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py
echo "OK: compile jó"

echo "=== 4) Ellenőrzés ==="
grep -n "class MasterMenu" main.py apk_stage/main.py
grep -n "DEMO CORE / DASHBOARD" main.py apk_stage/main.py

echo "=== 5) Git állapot - commit nincs, push nincs ==="
git status --short

echo "=== PATCH 13B KÉSZ ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Ha ez jó, írd: jó"
