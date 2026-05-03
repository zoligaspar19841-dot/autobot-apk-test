#!/bin/bash
set -e

echo "=== PATCH 04: Dashboard + trend UI javítás - APK BUILD NÉLKÜL ==="

TS=$(date +%Y%m%d_%H%M%S)

echo "=== 1) Biztonsági mentés ==="
cp main.py "main.py.bak_patch04_dashboard_$TS"
cp apk_stage/main.py "apk_stage/main.py.bak_patch04_dashboard_$TS"

echo "=== 2) Demo dashboard + trend javítás main.py + apk_stage/main.py ==="
python - <<'PY'
from pathlib import Path
import re

FILES = [Path("main.py"), Path("apk_stage/main.py")]

DASHBOARD_CODE = r'''
class TrendMiniChart(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.values = [100.0]
        self.bind(pos=lambda *_: self.redraw(), size=lambda *_: self.redraw())

    def set_values(self, values):
        try:
            vals = [float(v) for v in values if v is not None]
            if len(vals) < 2:
                vals = [100.0, 100.0]
            self.values = vals[-40:]
        except Exception:
            self.values = [100.0, 100.0]
        self.redraw()

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.04, 0.04, 0.04, 1)
            Rectangle(pos=self.pos, size=self.size)

            x, y = self.pos
            w, h = self.size

            Color(0.22, 0.22, 0.22, 1)
            for i in range(1, 4):
                yy = y + h * i / 4
                Line(points=[x, yy, x + w, yy], width=1)

            vals = self.values or [100.0, 100.0]
            mn, mx = min(vals), max(vals)
            if mx - mn < 0.00001:
                mx = mn + 1.0

            pts = []
            for i, v in enumerate(vals):
                px = x + (w * i / max(1, len(vals) - 1))
                py = y + 8 + ((v - mn) / (mx - mn)) * max(1, h - 16)
                pts.extend([px, py])

            Color(1.0, 0.78, 0.10, 1)
            if len(pts) >= 4:
                Line(points=pts, width=2)

            # utolsó pont jelölés
            if len(pts) >= 2:
                Color(0.0, 0.85, 0.35, 1)
                px, py = pts[-2], pts[-1]
                Line(circle=(px, py, 4), width=2)


class DemoCoreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.chart = TrendMiniChart(size_hint_y=None, height=145)
        self.kpi_labels = {}
        self.info_labels = {}

        root = BoxLayout(orientation="vertical", padding=10, spacing=8)

        title = Label(
            text="[b]DEMO CORE ENGINE[/b]\n[size=13]Dashboard / KPI / trend[/size]",
            markup=True,
            size_hint_y=None,
            height=64,
            halign="center"
        )
        root.add_widget(title)

        kpi = GridLayout(cols=2, spacing=6, size_hint_y=None, height=132)
        for key, title_text in [
            ("balance", "Balance"),
            ("equity", "Equity"),
            ("realized_pnl", "Realized PnL"),
            ("open_positions", "Open Positions"),
        ]:
            box = BoxLayout(orientation="vertical", padding=6, spacing=2)
            lab1 = Label(
                text="[b]" + title_text + "[/b]",
                markup=True,
                font_size=18,
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=34
            )
            lab1.bind(size=lambda inst, val: setattr(inst, "text_size", val))
            lab2 = Label(
                text="-",
                font_size=18,
                halign="left",
                valign="middle"
            )
            lab2.bind(size=lambda inst, val: setattr(inst, "text_size", val))
            box.add_widget(lab1)
            box.add_widget(lab2)
            self.kpi_labels[key] = lab2
            kpi.add_widget(box)
        root.add_widget(kpi)

        root.add_widget(Label(
            text="[b]Trend[/b]  Equity / profit trend mini-grafikon",
            markup=True,
            color=(1, 0.82, 0.18, 1),
            size_hint_y=None,
            height=32,
            halign="left"
        ))
        root.add_widget(self.chart)

        status_box = BoxLayout(orientation="vertical", size_hint_y=None, height=150, spacing=2)
        for key in ["state", "safe", "execution", "market_trend", "last_action"]:
            lab = Label(
                text="-",
                markup=True,
                font_size=16,
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=28
            )
            lab.bind(size=lambda inst, val: setattr(inst, "text_size", val))
            self.info_labels[key] = lab
            status_box.add_widget(lab)
        root.add_widget(status_box)

        pos_title = Label(
            text="[b]Nyitott pozíciók[/b]",
            markup=True,
            size_hint_y=None,
            height=32,
            halign="left"
        )
        pos_title.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        root.add_widget(pos_title)

        self.positions_text = Label(
            text="Nincs nyitott pozíció.",
            markup=True,
            halign="left",
            valign="top",
            size_hint_y=None,
            height=72
        )
        self.positions_text.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        root.add_widget(self.positions_text)

        btns = GridLayout(cols=2, spacing=6, size_hint_y=None, height=210)

        buttons = [
            ("FRISSÍTÉS", self.refresh),
            ("TICK / KÉZI FUTTATÁS", self.run_tick),
            ("START", self.start_bot),
            ("STOP", self.stop_bot),
            ("DEMO RESET 100 USDC", self.demo_reset),
            ("PANIC STOP / SAFE MODE", self.panic_safe),
            ("BEÁLLÍTÁSOK", self.open_settings),
            ("VISSZA", self.go_back),
        ]

        for text, fn in buttons:
            b = Button(text=text)
            b.bind(on_press=lambda btn, f=fn: f())
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.refresh()

    def _load_state(self):
        try:
            return demo_core.load_state()
        except Exception:
            return {}

    def _save_state(self, st):
        try:
            demo_core.save_state(st)
        except Exception:
            pass

    def _get_equity_history(self, st):
        candidates = []
        for key in ("equity_history", "profit_history", "history"):
            val = st.get(key)
            if isinstance(val, list):
                candidates = val
                break

        vals = []
        for item in candidates:
            if isinstance(item, dict):
                for k in ("equity", "balance", "value", "pnl"):
                    if k in item:
                        try:
                            vals.append(float(item[k]))
                            break
                        except Exception:
                            pass
            else:
                try:
                    vals.append(float(item))
                except Exception:
                    pass

        if not vals:
            eq = st.get("equity", st.get("balance", 100.0))
            try:
                eq = float(eq)
            except Exception:
                eq = 100.0
            vals = [eq, eq]

        return vals[-40:]

    def _market_trend_text(self, st):
        # Hely a későbbi SMA9/21 trendhez.
        trend = st.get("market_trend") or st.get("trend") or {}
        if isinstance(trend, dict):
            label = trend.get("label") or trend.get("status") or "Nincs élő trend adat"
            sma = trend.get("sma") or trend.get("sma_signal") or "-"
            return f"[b]Piaci trend:[/b] {label} | SMA: {sma}"
        if isinstance(trend, str):
            return f"[b]Piaci trend:[/b] {trend}"
        return "[b]Piaci trend:[/b] előkészítve / SMA9-21 később"

    def refresh(self):
        st = self._load_state()

        balance = st.get("balance", 100.0)
        equity = st.get("equity", balance)
        realized = st.get("realized_pnl", st.get("pnl", 0.0))
        positions = st.get("positions", [])
        settings = st.get("settings", {})

        try:
            open_pos = len(positions) if isinstance(positions, list) else int(st.get("open_positions", 0))
        except Exception:
            open_pos = 0

        self.kpi_labels["balance"].text = f"{float(balance):.4f} USDC" if str(balance).replace(".","",1).isdigit() else str(balance)
        self.kpi_labels["equity"].text = f"{float(equity):.4f} USDC" if str(equity).replace(".","",1).isdigit() else str(equity)
        self.kpi_labels["realized_pnl"].text = f"{float(realized):.4f}" if str(realized).replace(".","",1).replace("-","",1).isdigit() else str(realized)
        self.kpi_labels["open_positions"].text = str(open_pos)

        running = st.get("running", False)
        safe = st.get("safe_mode", False)
        execution = settings.get("execution_mode", st.get("execution_mode", "AUTO"))
        last_action = st.get("last_action", "-")

        self.info_labels["state"].text = "[b]Állapot:[/b] " + ("FUT" if running else "ÁLL")
        self.info_labels["safe"].text = "[b]Safe mode:[/b] " + ("BE" if safe else "KI")
        self.info_labels["execution"].text = "[b]Execution mode:[/b] " + str(execution)
        self.info_labels["market_trend"].text = self._market_trend_text(st)
        self.info_labels["last_action"].text = "[b]Utolsó művelet:[/b] " + str(last_action)

        vals = self._get_equity_history(st)
        self.chart.set_values(vals)

        if isinstance(positions, list) and positions:
            lines = []
            for p in positions[:5]:
                if isinstance(p, dict):
                    sym = p.get("symbol", "?")
                    qty = p.get("qty", p.get("amount", "?"))
                    entry = p.get("entry", p.get("entry_price", "?"))
                    pnl = p.get("pnl", p.get("unrealized_pnl", "?"))
                    lines.append(f"{sym} | qty: {qty} | entry: {entry} | pnl: {pnl}")
                else:
                    lines.append(str(p))
            self.positions_text.text = "\n".join(lines)
        else:
            self.positions_text.text = "Nincs nyitott pozíció."

    def run_tick(self):
        try:
            if hasattr(demo_core, "tick"):
                demo_core.tick()
            elif hasattr(demo_core, "run_tick"):
                demo_core.run_tick()
            else:
                st = self._load_state()
                st["last_action"] = "Demo tick előkészítve"
                self._save_state(st)
        except Exception as e:
            st = self._load_state()
            st["last_action"] = "Tick hiba: " + str(e)
            self._save_state(st)
        self.refresh()

    def start_bot(self):
        st = self._load_state()
        st["running"] = True
        st["last_action"] = "Demo bot start"
        self._save_state(st)
        self.refresh()

    def stop_bot(self):
        st = self._load_state()
        st["running"] = False
        st["last_action"] = "Demo bot stop"
        self._save_state(st)
        self.refresh()

    def demo_reset(self):
        try:
            if hasattr(demo_core, "demo_reset"):
                demo_core.demo_reset()
            elif hasattr(demo_core, "reset_demo"):
                demo_core.reset_demo()
            else:
                st = self._load_state()
                st["balance"] = 100.0
                st["equity"] = 100.0
                st["realized_pnl"] = 0.0
                st["positions"] = []
                st["running"] = False
                st["last_action"] = "Demo reset 100 USDC"
                self._save_state(st)
        except Exception as e:
            st = self._load_state()
            st["last_action"] = "Reset hiba: " + str(e)
            self._save_state(st)
        self.refresh()

    def panic_safe(self):
        st = self._load_state()
        st["running"] = False
        st["safe_mode"] = True
        st["last_action"] = "Panic Stop / Safe Mode bekapcsolva"
        self._save_state(st)
        self.refresh()

    def open_settings(self):
        try:
            safe_go_to(self.manager, "demo_settings")
        except Exception:
            try:
                self.manager.current = "demo_settings"
            except Exception:
                pass

    def go_back(self):
        safe_go_back(self.manager, "main")
'''

def ensure_import(s, imp):
    if imp not in s:
        return imp + "\n" + s
    return s

def replace_screen_class(s, class_name, new_code):
    pattern = rf"\nclass {class_name}\(Screen\):"
    m = re.search(pattern, s)
    if not m:
        return s + "\n\n" + new_code + "\n", False

    start = m.start() + 1
    next_m = re.search(r"\nclass\s+\w+\(Screen\):", s[start + 1:])
    if next_m:
        end = start + 1 + next_m.start()
        return s[:start] + new_code + "\n\n" + s[end:], True
    return s[:start] + new_code + "\n", True

for p in FILES:
    s = p.read_text(encoding="utf-8", errors="replace")

    for imp in [
        "from kivy.uix.widget import Widget",
        "from kivy.graphics import Color, Line, Rectangle",
        "from kivy.uix.boxlayout import BoxLayout",
        "from kivy.uix.gridlayout import GridLayout",
        "from kivy.uix.button import Button",
        "from kivy.uix.label import Label",
        "from kivy.uix.screenmanager import Screen",
    ]:
        s = ensure_import(s, imp)

    if "import demo_core_engine as demo_core" not in s:
        s = "import demo_core_engine as demo_core\n" + s

    if "class TrendMiniChart(Widget):" in s:
        # Ha már létezik, nem duplázzuk, csak DemoCoreScreen-t cseréljük a TrendMiniChart utáni kóddal együtt.
        pass

    s, existed = replace_screen_class(s, "DemoCoreScreen", DASHBOARD_CODE)

    # route biztosítás
    if 'DemoCoreScreen(name="demo_core")' not in s:
        s = re.sub(
            r"(\n\s*return\s+sm\b)",
            '\n        sm.add_widget(DemoCoreScreen(name="demo_core"))\\1',
            s,
            count=1
        )

    p.write_text(s, encoding="utf-8")
    print("OK patched:", p, "existed:", existed)
PY

echo "=== 3) Python compile teszt - build nélkül ==="
python -m py_compile main.py demo_core_engine.py
python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py

echo "=== 4) Ellenőrzés ==="
grep -nE "TrendMiniChart|DEMO CORE ENGINE|Dashboard / KPI / trend|Piaci trend|run_tick|demo_reset|panic_safe|open_settings" main.py | head -100
echo "--- apk_stage ---"
grep -nE "TrendMiniChart|DEMO CORE ENGINE|Dashboard / KPI / trend|Piaci trend|run_tick|demo_reset|panic_safe|open_settings" apk_stage/main.py | head -100

echo "=== 5) Git állapot - commit nincs, push nincs ==="
git status --short

echo "=== PATCH 04 KÉSZ ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Ha ez jó, írd: jó"
