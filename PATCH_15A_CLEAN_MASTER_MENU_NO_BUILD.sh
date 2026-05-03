#!/usr/bin/env bash
set -e

echo "=== PATCH 15A: TISZTA MASTER MENU / DEMO-LIVE SZÉTVÁLASZTÁS - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, nem küld Binance ordert."

mkdir -p backups logs
TS=$(date +%Y%m%d_%H%M%S)

patch_file() {
  f="$1"
  [ -f "$f" ] || return 0

  cp "$f" "backups/$(basename "$f").bak_patch15a_$TS"

  python3 - "$f" <<'PY'
from pathlib import Path
import sys

p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8", errors="replace")

start = s.find("class MasterMenu(Screen):")
if start < 0:
    print("HIBA: MasterMenu class nem található:", p)
    sys.exit(1)

end = s.find("\n\nclass SkeletonScreen", start)
if end < 0:
    print("HIBA: SkeletonScreen class nem található MasterMenu után:", p)
    sys.exit(1)

new = r'''class MasterMenu(Screen):
    """
    PATCH 15A:
    Tiszta, felhasználói főmenü.
    Cél:
    - Demo / Live különválasztás
    - kevesebb káosz
    - rövid helper szöveg minden fő blokknál
    - csak létező route-ok használata
    - ha valami nincs kész, ne dobjon át véletlenül máshova
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation='vertical',
            padding=[10, 14, 10, 8],
            spacing=8
        )

        title = Label(
            text='[b]BINANCE AUTOBOT[/b]\n[size=13]Demo biztonságosan | Live csak API ellenőrzés után[/size]',
            markup=True,
            color=(1.0, 0.72, 0.10, 1),
            font_size=22,
            size_hint_y=None,
            height=68,
            halign='center',
            valign='middle'
        )
        title.bind(size=lambda w, *_: setattr(w, 'text_size', w.size))
        root.add_widget(title)

        self.status = Label(
            text='Válassz módot. A DEMO nem használ éles pénzt. A LIVE csak beállított API kulccsal aktív.',
            color=(0.82, 0.82, 0.82, 1),
            font_size=12,
            size_hint_y=None,
            height=42,
            halign='center',
            valign='middle'
        )
        self.status.bind(size=lambda w, *_: setattr(w, 'text_size', w.size))
        root.add_widget(self.status)

        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(
            cols=1,
            spacing=7,
            padding=[2, 4, 2, 14],
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter('height'))

        def section(text, color=(1.0, 0.72, 0.10, 1)):
            lab = Label(
                text='[b]' + text + '[/b]',
                markup=True,
                color=color,
                font_size=15,
                size_hint_y=None,
                height=32,
                halign='left',
                valign='middle'
            )
            lab.bind(size=lambda w, *_: setattr(w, 'text_size', w.size))
            grid.add_widget(lab)

        def add_btn(text, target, note='', accent='gray'):
            full = text
            if note:
                full += '\n[size=11]' + note + '[/size]'

            b = Button(
                text=full,
                markup=True,
                size_hint_y=None,
                height=64 if note else 54,
                font_size=15,
                bold=True,
                halign='center',
                valign='middle'
            )
            b.bind(size=lambda w, *_: setattr(w, 'text_size', w.size))

            try:
                if accent == 'demo':
                    b.background_color = (0.95, 0.48, 0.02, 1)
                elif accent == 'live':
                    b.background_color = (0.04, 0.18, 0.72, 1)
                elif accent == 'safe':
                    b.background_color = (0.55, 0.05, 0.05, 1)
                elif accent == 'ok':
                    b.background_color = (0.05, 0.42, 0.15, 1)
                elif accent == 'dev':
                    b.background_color = (0.25, 0.25, 0.30, 1)
                else:
                    b.background_color = (0.18, 0.18, 0.19, 1)
                b.color = (1, 1, 1, 1)
            except Exception:
                pass

            def go(_btn):
                try:
                    if self.manager and self.manager.has_screen(target):
                        self.manager.current = target
                    else:
                        self.status.text = 'Ez a modul még nincs teljesen bekötve: ' + str(target)
                except Exception as e:
                    self.status.text = 'Navigációs hiba: ' + str(e)

            b.bind(on_press=go)
            grid.add_widget(b)

        section('1) DEMO - biztonságos teszt', (1.0, 0.72, 0.10, 1))
        add_btn('📊 Demo Dashboard', 'modern_dashboard', 'KPI, trend, profit nézet, demo állapot', 'demo')
        add_btn('🧪 Demo Core', 'demo_core', 'belső demo motor állapot, teszt tick, futás', 'demo')
        add_btn('🔄 Demo Reset', 'demo_reset', '100 USDC visszaállítás, P/L nullázás', 'demo')

        section('2) Kereskedési beállítások', (0.70, 0.90, 1.0, 1))
        add_btn('💰 Trade Simple', 'trade_simple', 'symbol, risk %, min. nettó profit, max coin', 'ok')
        add_btn('📈 Strategy Advanced', 'strategy_advanced', 'SMA, RSI, ATR, fee, stratégia paraméterek', 'ok')
        add_btn('📡 Scanner / Multi Symbol', 'scanner', 'coin figyelés, rangsor, lehetőségek', 'ok')

        section('3) LIVE / API - csak ellenőrzés után', (0.35, 0.60, 1.0, 1))
        add_btn('🔐 Settings / Security', 'demo_settings', 'alap beállítások, módok, induló értékek', 'live')
        add_btn('🔑 API / E-mail / Secrets', 'secrets', 'Binance API, OpenAI API, e-mail adatok', 'live')
        add_btn('🌐 Binance Live státusz', 'binance_live', 'API kulcs ellenőrzés, live készenlét', 'live')
        add_btn('💼 Spot Portfolio', 'spot_portfolio', 'egyenleg / portfólió read-only nézet', 'live')
        add_btn('🧾 Readonly Balance', 'readonly_balance', 'csak olvasás, nem ad ordert', 'live')
        add_btn('🛡️ Live Gate / Safety', 'live_gate', 'éles mód kapu, tiltások, védelmek', 'safe')

        section('4) Riport / export / napló', (0.70, 1.0, 0.70, 1))
        add_btn('📄 Trades / Logs', 'demo_logs', 'trades.csv, log.csv, események', 'ok')
        add_btn('📊 Profit Report', 'profit_report', 'bruttó, nettó, adózás utáni nézet', 'ok')
        add_btn('📁 Package / Snapshot', 'package', 'mentés, export, snapshot csomag', 'ok')

        section('5) Safety / diagnosztika', (1.0, 0.45, 0.45, 1))
        add_btn('🩺 Health / Recovery', 'health_alert', 'Binance, e-mail, Drive, recovery állapot', 'safe')
        add_btn('✅ Pre-APK Safe Test', 'pre_apk_safe', 'build előtti ellenőrzés, APK nélkül', 'safe')
        add_btn('📋 Release Candidate', 'release_candidate', 'kiadás előtti ellenőrző lista', 'safe')
        add_btn('🧭 UI Route Check', 'ui_route_check', 'képernyő/regisztráció ellenőrzés', 'dev')

        section('6) Haladó / fejlesztői', (0.80, 0.80, 0.90, 1))
        add_btn('🛠 Patch Manager', 'patch_manager', 'csak óvatos javítás, mentéssel', 'dev')
        add_btn('🤖 AI Advisor', 'ai_advisor', 'AI javaslat, Auto/Manual/Off később', 'dev')
        add_btn('🧬 Integration Tests', 'integration_tests', 'belső tesztek és összekötések', 'dev')
        add_btn('📌 Master Status', 'master_status', 'teljes rendszer áttekintés', 'dev')

        scroll.add_widget(grid)
        root.add_widget(scroll)

        footer = Label(
            text='PATCH 15A: tiszta főmenü | Demo/Live külön | helper szövegek | APK build nem része',
            color=(0.68, 0.68, 0.68, 1),
            font_size=10,
            size_hint_y=None,
            height=28,
            halign='center',
            valign='middle'
        )
        footer.bind(size=lambda w, *_: setattr(w, 'text_size', w.size))
        root.add_widget(footer)

        self.add_widget(root)
'''

s2 = s[:start] + new + s[end:]
p.write_text(s2, encoding="utf-8")
print("OK patched:", p)
PY
}

patch_file main.py
patch_file apk_stage/main.py

echo "=== Python compile ellenőrzés ==="
python3 -m py_compile main.py
python3 -m py_compile apk_stage/main.py

cat > logs/PATCH_15A_CLEAN_MASTER_MENU_REPORT.txt <<EOF
PATCH 15A OK
Date: $(date)

Elemzés alapján javítva:
- Főmenü tisztább
- Demo / Live különválasztva
- Debug/fejlesztői részek külön csoportban
- Több helper magyarázat
- Nem létező route esetén nem dobál át véletlenül másik képernyőre
- APK build nem indult
- Binance order nem történt
EOF

echo "=== PATCH 15A KÉSZ ==="
echo "Jelentés: logs/PATCH_15A_CLEAN_MASTER_MENU_REPORT.txt"
echo "APK build NEM indult. Commit NEM történt."
