#!/usr/bin/env bash
set -e

echo "=== PATCH 15B: MENU HELPER / DEMO-LIVE MAGYARÁZAT / MOBILBARÁT GOMBOK - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, nem küld Binance ordert."

mkdir -p backups logs
TS=$(date +%Y%m%d_%H%M%S)

patch_file() {
  f="$1"
  [ -f "$f" ] || return 0

  cp "$f" "backups/$(basename "$f").bak_patch15b_$TS"

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
    PATCH 15B:
    Letisztított főmenü.
    - Emoji nélkül, mert Android/Kivy alatt sok ikon négyzetként jelenik meg.
    - Demo és Live világosan külön.
    - Rövid helper szöveg minden fő részhez.
    - Fejlesztői/teszt képernyők külön alul.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation='vertical',
            padding=[10, 12, 10, 8],
            spacing=7
        )

        title = Label(
            text='[b]BINANCE AUTOBOT[/b]',
            markup=True,
            color=(1.0, 0.72, 0.10, 1),
            font_size=23,
            size_hint_y=None,
            height=42,
            halign='center',
            valign='middle'
        )
        title.bind(size=lambda w, *_: setattr(w, 'text_size', w.size))
        root.add_widget(title)

        info = Label(
            text='[b]DEMO:[/b] teszt pénzzel fut.  [b]LIVE:[/b] csak API kulcs után mutat éles adatot. Order tiltva, amíg nincs engedélyezve.',
            markup=True,
            color=(0.88, 0.88, 0.88, 1),
            font_size=12,
            size_hint_y=None,
            height=56,
            halign='center',
            valign='middle'
        )
        info.bind(size=lambda w, *_: setattr(w, 'text_size', w.size))
        root.add_widget(info)

        self.status = Label(
            text='Javasolt sorrend: 1) Demo Dashboard  2) Settings  3) API/Secrets  4) Live státusz.',
            color=(1.0, 0.72, 0.10, 1),
            font_size=11,
            size_hint_y=None,
            height=34,
            halign='center',
            valign='middle'
        )
        self.status.bind(size=lambda w, *_: setattr(w, 'text_size', w.size))
        root.add_widget(self.status)

        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(
            cols=1,
            spacing=8,
            padding=[0, 4, 0, 16],
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter('height'))

        def section(text, color):
            lab = Label(
                text='[b]' + text + '[/b]',
                markup=True,
                color=color,
                font_size=15,
                size_hint_y=None,
                height=30,
                halign='left',
                valign='middle'
            )
            lab.bind(size=lambda w, *_: setattr(w, 'text_size', w.size))
            grid.add_widget(lab)

        def add_btn(title, target, note='', mode='normal'):
            text = '[b]' + title + '[/b]'
            if note:
                text += '\n[size=11]' + note + '[/size]'

            b = Button(
                text=text,
                markup=True,
                size_hint_y=None,
                height=66 if note else 54,
                font_size=14,
                halign='center',
                valign='middle'
            )
            b.bind(size=lambda w, *_: setattr(w, 'text_size', w.size))

            try:
                if mode == 'demo':
                    b.background_color = (0.92, 0.44, 0.02, 1)
                elif mode == 'live':
                    b.background_color = (0.03, 0.16, 0.62, 1)
                elif mode == 'danger':
                    b.background_color = (0.45, 0.04, 0.04, 1)
                elif mode == 'report':
                    b.background_color = (0.05, 0.35, 0.16, 1)
                elif mode == 'dev':
                    b.background_color = (0.22, 0.22, 0.25, 1)
                else:
                    b.background_color = (0.16, 0.16, 0.17, 1)
                b.color = (1, 1, 1, 1)
            except Exception:
                pass

            def go(_):
                try:
                    if self.manager and self.manager.has_screen(target):
                        self.manager.current = target
                    else:
                        self.status.text = 'Ez a rész még nincs teljesen bekötve: ' + str(target)
                except Exception as e:
                    self.status.text = 'Navigációs hiba: ' + str(e)

            b.bind(on_press=go)
            grid.add_widget(b)

        section('1. DEMO - biztonságos teszt', (1.0, 0.72, 0.10, 1))
        add_btn('Demo Dashboard', 'modern_dashboard', 'Fő nézet: KPI, trend, demo egyenleg, profit.', 'demo')
        add_btn('Demo motor / teszt tick', 'demo_core', 'Csak demo logika. Nem használ éles pénzt.', 'demo')
        add_btn('Demo Reset', 'demo_reset', '100 USDC visszaállítás, P/L és pozíciók nullázása.', 'demo')

        section('2. KERESKEDÉSI BEÁLLÍTÁSOK', (0.70, 0.90, 1.0, 1))
        add_btn('Trade Simple', 'trade_simple', 'Symbol, risk %, min. profit, max pozíció.', 'normal')
        add_btn('Strategy Advanced', 'strategy_advanced', 'SMA, RSI, ATR, fee, TP/SL, stratégia finomhangolás.', 'normal')
        add_btn('Scanner / Coin figyelő', 'scanner', 'Több coin figyelése, rangsor, lehetőségek.', 'normal')

        section('3. LIVE / API - éles adat csak kulccsal', (0.35, 0.60, 1.0, 1))
        add_btn('Settings / alap beállítások', 'demo_settings', 'Módok, alap tőke, paraméterek, induló értékek.', 'live')
        add_btn('API / E-mail / Secrets', 'secrets', 'Binance API key/secret, OpenAI, e-mail app password.', 'live')
        add_btn('Binance Live státusz', 'binance_live', 'Megmutatja, hogy az API készen áll-e. Order még tiltott.', 'live')
        add_btn('Spot Portfolio', 'spot_portfolio', 'Read-only egyenleg/portfólió nézet, ha API engedélyezett.', 'live')
        add_btn('Readonly Balance', 'readonly_balance', 'Csak olvasás. Ha nincs API, nem lesz live adat.', 'live')
        add_btn('Live Safety Gate', 'live_gate', 'Éles kereskedés előtti biztonsági kapu.', 'danger')

        section('4. RIPORT / EXPORT / NAPLÓ', (0.70, 1.0, 0.70, 1))
        add_btn('Trades / Logs', 'demo_logs', 'Trade lista, log.csv, trades.csv.', 'report')
        add_btn('Profit Report', 'profit_report', 'Bruttó, nettó, adózás utáni PnL nézet.', 'report')
        add_btn('Package / Snapshot', 'package', 'Projekt mentés, snapshot, export csomag.', 'report')

        section('5. SAFETY / DIAGNOSZTIKA', (1.0, 0.45, 0.45, 1))
        add_btn('Health / Recovery', 'health_alert', 'Kapcsolatok, hibák, újraindítás utáni állapot.', 'danger')
        add_btn('Pre-APK Safe Test', 'pre_apk_safe', 'Build előtti ellenőrzés, APK nélkül.', 'danger')
        add_btn('Release Candidate Check', 'release_candidate', 'Kiadás előtti ellenőrzés.', 'danger')

        section('6. HALADÓ / FEJLESZTŐI', (0.80, 0.80, 0.90, 1))
        add_btn('Patch Manager', 'patch_manager', 'Óvatos javítás mentéssel. Csak ha kell.', 'dev')
        add_btn('AI Advisor', 'ai_advisor', 'AI javaslatok későbbi Auto/Manual/Off móddal.', 'dev')
        add_btn('Integration Tests', 'integration_tests', 'Belső tesztek, fejlesztői ellenőrzés.', 'dev')
        add_btn('UI Route Check', 'ui_route_check', 'Képernyők és route-ok ellenőrzése.', 'dev')
        add_btn('Master Status', 'master_status', 'Teljes rendszer állapot áttekintés.', 'dev')

        scroll.add_widget(grid)
        root.add_widget(scroll)

        footer = Label(
            text='PATCH 15B | Demo/Live helper | emoji nélkül | mobilbarát főmenü',
            color=(0.68, 0.68, 0.68, 1),
            font_size=10,
            size_hint_y=None,
            height=24,
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

cat > logs/PATCH_15B_MENU_HELPER_MOBILE_CLARITY_REPORT.txt <<EOF
PATCH 15B OK
Date: $(date)

Videó alapján javítva:
- Emoji ikonok kivéve, mert Android/Kivy alatt több helyen hibás négyzetként látszottak
- Főmenü rövidebb és érthetőbb lett
- Demo/Live helper szöveg bekerült
- Live adat hiányának oka kiírva: API nélkül nincs live adat
- Fejlesztői képernyők külön csoportba kerültek
- APK build nem indult
- Binance order nem történt
EOF

echo "=== PATCH 15B KÉSZ ==="
echo "Jelentés: logs/PATCH_15B_MENU_HELPER_MOBILE_CLARITY_REPORT.txt"
echo "APK build NEM indult. Commit NEM történt."
