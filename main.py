import demo_core_engine as demo_core
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
import json, os, random, urllib.request

STATE_FILE = "state.json"
SETTINGS_FILE = "settings_app.json"

ORANGE = (1, 0.50, 0, 1)
BLUE = (0, 0.25, 0.85, 1)
DARK = (0.07, 0.07, 0.08, 1)
CARD = (0.16, 0.16, 0.17, 1)

NAV_STACK = []

def go_to(sm, screen):
    try:
        cur = sm.current
        if cur and cur != screen:
            NAV_STACK.append(cur)
        sm.current = screen
    except Exception:
        sm.current = screen

def go_back(sm, fallback="main"):
    try:
        if NAV_STACK:
            sm.current = NAV_STACK.pop()
        else:
            sm.current = fallback
    except Exception:
        sm.current = fallback


def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            if isinstance(d, dict):
                return d
    except Exception:
        pass
    return default.copy()

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_state():
    d = load_json(STATE_FILE, {})
    if "demo" not in d:
        d = {
            "mode": "demo",
            "demo": {"balance": 100.0, "profit": 0.0, "running": False},
            "live": {"running": False, "api_ready": False},
            "last_msg": "Stable restore kész"
        }
        save_json(STATE_FILE, d)
    return d

def load_settings():
    return load_json(SETTINGS_FILE, {
        "symbol": "BTCUSDT",
        "base": "USDC",
        "risk_pct": 10,
        "max_positions": 3,
        "min_profit_pct": 10
    })

def binance_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "BinanceAutobot"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read().decode("utf-8"))

def get_price(symbol):
    try:
        d = binance_json("https://api.binance.com/api/v3/ticker/price?symbol=" + symbol)
        return float(d["price"])
    except Exception:
        return 0.0

def get_klines(symbol):
    try:
        d = binance_json("https://api.binance.com/api/v3/klines?symbol=" + symbol + "&interval=1m&limit=60")
        return [float(x[4]) for x in d]
    except Exception:
        return []

def top_coins():
    try:
        d = binance_json("https://api.binance.com/api/v3/ticker/24hr")
        arr = [x for x in d if x.get("symbol", "").endswith("USDT")]
        arr.sort(key=lambda x: float(x.get("quoteVolume", 0) or 0), reverse=True)
        return arr[:12]
    except Exception:
        return []

class Card(BoxLayout):
    def __init__(self, bg=CARD, **kw):
        super().__init__(**kw)
        self.bg = bg
        self.padding = 10
        self.spacing = 6
        self.bind(pos=self.draw, size=self.draw)

    def draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20])

class Trend(Widget):
    def __init__(self, color=ORANGE, **kw):
        super().__init__(**kw)
        self.color = color
        self.values = [random.uniform(40, 60) for _ in range(40)]
        self.bind(pos=self.draw, size=self.draw)

    def set_values(self, vals):
        if vals:
            self.values = vals[-50:]
        self.draw()

    def draw(self, *a):
        self.canvas.clear()
        with self.canvas:
            Color(0.035, 0.04, 0.045, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
            if len(self.values) < 2:
                return
            mn, mx = min(self.values), max(self.values)
            span = max(mx - mn, 0.000001)
            pts = []
            for i, v in enumerate(self.values):
                x = self.x + 8 + i * ((self.width - 16) / (len(self.values) - 1))
                y = self.y + 8 + ((v - mn) / span) * (self.height - 16)
                pts += [x, y]
            Color(*self.color)
            Line(points=pts, width=2.2)

def button(text, color=CARD, fs=24):
    return Button(text=text, font_size=fs, bold=True, background_color=color)

class Main(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        root.add_widget(Label(
            text="BINANCE AUTOBOT",
            font_size=36,
            bold=True,
            color=(1, .75, 0, 1),
            size_hint_y=.14
        ))

        grid = GridLayout(cols=2, spacing=10, size_hint_y=.78)
        items = [
            ("DEMO", "demo_core", ORANGE),
            ("LIVE", "live", BLUE),
            ("BEÁLLÍTÁSOK", "settings", CARD),
            ("BIZTONSÁG / API", "security", CARD),
            ("AI / STRATÉGIA", "strategy", CARD),
            ("COIN SCANNER", "scanner", CARD),
            ("NAPLÓ / EXPORT", "logs", CARD),
            ("HALADÓ", "advanced", CARD),
        ]
        for txt, scr, col in items:
            b = button(txt, col, 24)
            b.bind(on_press=lambda x, s=scr: go_to(self.manager, s))
            grid.add_widget(b)

        root.add_widget(grid)
        root.add_widget(Label(
            text="Stable alap + óvatos patch rendszer",
            font_size=16,
            size_hint_y=.08
        ))
        self.add_widget(root)

class Dashboard(Screen):
    def __init__(self, mode, color, **kw):
        super().__init__(**kw)
        self.mode = mode
        self.color = color
        self.symbol = load_settings().get("symbol", "BTCUSDT")

        root = BoxLayout(orientation="vertical", padding=8, spacing=8)

        head = Card(bg=color, size_hint_y=.13)
        head.add_widget(Label(text=mode.upper() + " DASHBOARD", font_size=31, bold=True))
        root.add_widget(head)

        self.trend = Trend(color=color, size_hint_y=.30)
        root.add_widget(self.trend)

        kpi = GridLayout(cols=2, spacing=8, size_hint_y=.25)
        self.k1 = Label(text="Ár: ...", font_size=23)
        self.k2 = Label(text="Total: 100", font_size=23)
        self.k3 = Label(text="Free: 100", font_size=23)
        self.k4 = Label(text="PnL: 0", font_size=23)

        for w in [self.k1, self.k2, self.k3, self.k4]:
            c = Card(bg=CARD)
            c.add_widget(w)
            kpi.add_widget(c)

        root.add_widget(kpi)

        self.msg = Label(text="Indulás kész.", font_size=18, size_hint_y=.10)
        root.add_widget(self.msg)

        controls = GridLayout(cols=2, spacing=8, size_hint_y=.22)
        for txt, col, fn in [
            ("START", (.05, .55, .1, 1), self.start),
            ("STOP", (.65, 0, 0, 1), self.stop),
            ("FRISSÍTÉS", (.28, .28, .28, 1), self.refresh),
            ("VISSZA", (.35, .35, .35, 1), self.back),
        ]:
            b = button(txt, col, 23)
            b.bind(on_press=fn)
            controls.add_widget(b)

        root.add_widget(controls)
        self.add_widget(root)
        Clock.schedule_once(lambda dt: self.refresh(None), 1)

    def start(self, x):
        st = load_state()
        st[self.mode]["running"] = True
        save_json(STATE_FILE, st)
        self.msg.text = "Bot elindítva."

    def stop(self, x):
        st = load_state()
        st[self.mode]["running"] = False
        save_json(STATE_FILE, st)
        self.msg.text = "Bot leállítva."

    def refresh(self, x):
        cfg = load_settings()
        self.symbol = cfg.get("symbol", "BTCUSDT")
        price = get_price(self.symbol)
        kl = get_klines(self.symbol)
        if kl:
            self.trend.set_values(kl)
        st = load_state()
        bal = st.get("demo", {}).get("balance", 100.0)
        pnl = st.get("demo", {}).get("profit", 0.0)
        self.k1.text = f"{self.symbol}\n{price:.4g}" if price else f"{self.symbol}\noffline"
        self.k2.text = f"Total\n{bal:.2f}"
        self.k3.text = f"Free\n{bal:.2f}"
        self.k4.text = f"PnL\n{pnl:.2f}"
        self.msg.text = "Frissítve." if price else "Offline / nincs adat."

    def back(self, x):
        go_back(self.manager)

class Scanner(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)
        root.add_widget(Label(text="COIN SCANNER", font_size=34, bold=True, color=(1,.75,0,1), size_hint_y=.14))
        self.list = Label(text="Nyomj FRISSÍTÉS-t.", font_size=21)
        root.add_widget(self.list)
        r = button("FRISSÍTÉS", CARD, 24)
        b = button("VISSZA", (.35,.35,.35,1), 24)
        r.bind(on_press=self.refresh)
        b.bind(on_press=lambda x: go_back(self.manager))
        root.add_widget(r)
        root.add_widget(b)
        self.add_widget(root)

    def refresh(self, x):
        arr = top_coins()
        if not arr:
            self.list.text = "Offline / Binance adat nem jött."
            return
        lines = []
        for c in arr:
            sym = c["symbol"]
            price = float(c.get("lastPrice", 0))
            chg = float(c.get("priceChangePercent", 0))
            lines.append(f"{sym}  {price:.5g}  {chg:+.2f}%")
        self.list.text = "\n".join(lines[:12])


class MasterMenu(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)
        root.add_widget(Label(text="MASTER LISTA", font_size=34, bold=True, color=(1,.75,0,1), size_hint_y=.12))

        grid = GridLayout(cols=1, spacing=7, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        items = [
            ("1. Általános működés", "main"),
            ("2. Dashboard", "demo"),
            ("3. Trade Simple", "trade_simple"),
            ("4. Strategy Advanced", "strategy_advanced"),
            ("5. Schedules", "schedules"),
            ("6. Launchpool / Airdrop", "launchpool"),
            ("7. Patch / Snapshot", "patch_snapshot"),
            ("8. Trades / Export", "logs"),
            ("9. Settings / Security", "settings"),
            ("10. PC + Google Drive Sync", "pc_drive_sync"),
            ("11. Diagnostics / Tests", "diagnostics"),
            ("12. Patch Manager UI", "patch_manager_ui"),
            ("13. Demo Reset", "demo_reset"),
            ("14. Fájlszerkezet", "file_structure"),
            ("15. Extra fejlesztések", "extra_features"),
            ("16. AI / MI kereskedés", "strategy"),
            ("17. Multi-symbol Scanner", "scanner"),
            ("18. Safety Guards", "safety_guards"),
            ("19. Healthcheck", "healthcheck"),
            ("20. Backtest / Replay", "backtest"),
            ("21. Audit log", "audit_log"),
            ("22. UI Mockup / Megjelenés", "ui_mockup"),
            ("23. Fee / Adózás", "fee_tax"),
            ("24. Profit-Hold AI", "profit_hold_ai"),
        ]

        for txt, scr in items:
            b = button(txt, CARD, 20)
            b.size_hint_y = None
            b.height = 58
            b.bind(on_press=lambda x, sc=scr: go_to(self.manager, sc))
            grid.add_widget(b)

        sv = ScrollView()
        sv.add_widget(grid)
        root.add_widget(sv)

        back = button("VISSZA", (.35,.35,.35,1), 24)
        back.size_hint_y = .11
        back.bind(on_press=lambda x: go_back(self.manager))
        root.add_widget(back)
        self.add_widget(root)

class SkeletonScreen(Screen):
    def __init__(self, title, body, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=18, spacing=12)
        root.add_widget(Label(text=title, font_size=32, bold=True, color=(1,.75,0,1), size_hint_y=.15))
        root.add_widget(Label(text=body, font_size=21))
        b = button("VISSZA", (.35,.35,.35,1), 23)
        b.bind(on_press=lambda x: go_back(self.manager))
        root.add_widget(b)
        self.add_widget(root)



class DemoResetScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=18, spacing=12)

        root.add_widget(Label(
            text="DEMO RESET",
            font_size=34,
            bold=True,
            color=(1,.75,0,1),
            size_hint_y=.16
        ))

        self.info = Label(
            text="Demo számla visszaállítása:\n\n"
                 "- egyenleg: 100 USDC\n"
                 "- profit/loss: 0\n"
                 "- futás: leállítva\n\n"
                 "Live módot nem érinti.",
            font_size=22
        )
        root.add_widget(self.info)

        reset = button("DEMO RESET FUTTATÁSA", (1,.50,0,1), 24)
        back = button("VISSZA", (.35,.35,.35,1), 23)

        reset.bind(on_press=self.do_reset)
        back.bind(on_press=lambda x: go_back(self.manager))

        root.add_widget(reset)
        root.add_widget(back)
        self.add_widget(root)

    def do_reset(self, x):
        st = load_state()
        st["mode"] = "demo"
        st["demo"] = {"balance": 100.0, "profit": 0.0, "running": False}
        if "live" not in st:
            st["live"] = {"running": False, "api_ready": False}
        st["last_msg"] = "Demo reset kész"
        save_json(STATE_FILE, st)
        self.info.text = "✅ Demo Reset kész!\n\nEgyenleg: 100 USDC\nProfit/Loss: 0\nBot: leállítva"



class TradeSimpleScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=16, spacing=10)

        root.add_widget(Label(text="TRADE SIMPLE", font_size=32, bold=True, color=(1,.75,0,1), size_hint_y=.12))

        self.symbol = TextInput(text="BTCUSDT", multiline=False, font_size=22, size_hint_y=.09)
        self.risk = TextInput(text="10", multiline=False, font_size=22, size_hint_y=.09)
        self.min_profit = TextInput(text="1.5", multiline=False, font_size=22, size_hint_y=.09)
        self.max_coin = TextInput(text="3", multiline=False, font_size=22, size_hint_y=.09)

        root.add_widget(Label(text="Symbol", font_size=20, size_hint_y=.06))
        root.add_widget(self.symbol)
        root.add_widget(Label(text="Risk %", font_size=20, size_hint_y=.06))
        root.add_widget(self.risk)
        root.add_widget(Label(text="Min Profit %", font_size=20, size_hint_y=.06))
        root.add_widget(self.min_profit)
        root.add_widget(Label(text="Max coin", font_size=20, size_hint_y=.06))
        root.add_widget(self.max_coin)

        start = button("START", (.05,.55,.1,1), 23)
        stop = button("STOP", (.65,0,0,1), 23)
        tick = button("TICK / TESZT", (.25,.25,.25,1), 23)
        back = button("VISSZA", (.35,.35,.35,1), 22)

        start.bind(on_press=self.start)
        stop.bind(on_press=self.stop)
        tick.bind(on_press=self.tick)
        back.bind(on_press=lambda x: go_back(self.manager))

        root.add_widget(start)
        root.add_widget(stop)
        root.add_widget(tick)
        root.add_widget(back)

        self.add_widget(root)

    def start(self, x):
        st = load_state()
        st.setdefault("demo", {})
        st["demo"]["running"] = True
        save_json(STATE_FILE, st)

    def stop(self, x):
        st = load_state()
        st.setdefault("demo", {})
        st["demo"]["running"] = False
        save_json(STATE_FILE, st)

    def tick(self, x):
        st = load_state()
        st["last_msg"] = "Trade Simple manual tick"
        save_json(STATE_FILE, st)



class StrategyAdvancedScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=16, spacing=8)

        root.add_widget(Label(text="STRATEGY ADVANCED", font_size=32, bold=True, color=(1,.75,0,1), size_hint_y=.11))

        self.profile = TextInput(text="normal", multiline=False, font_size=22, size_hint_y=.08)
        self.sma_fast = TextInput(text="9", multiline=False, font_size=22, size_hint_y=.08)
        self.sma_slow = TextInput(text="21", multiline=False, font_size=22, size_hint_y=.08)
        self.rsi_buy = TextInput(text="52", multiline=False, font_size=22, size_hint_y=.08)
        self.rsi_sell = TextInput(text="70", multiline=False, font_size=22, size_hint_y=.08)
        self.atr_mult = TextInput(text="1.0", multiline=False, font_size=22, size_hint_y=.08)

        fields = [
            ("Profil: normal / hybrid / sniper", self.profile),
            ("SMA fast", self.sma_fast),
            ("SMA slow", self.sma_slow),
            ("RSI buy min", self.rsi_buy),
            ("RSI sell max", self.rsi_sell),
            ("ATR szorzó", self.atr_mult),
        ]

        for label, field in fields:
            root.add_widget(Label(text=label, font_size=19, size_hint_y=.055))
            root.add_widget(field)

        save = button("STRATÉGIA MENTÉS", (.05,.55,.1,1), 23)
        back = button("VISSZA", (.35,.35,.35,1), 22)

        save.bind(on_press=self.save)
        back.bind(on_press=lambda x: go_back(self.manager))

        root.add_widget(save)
        root.add_widget(back)

        self.msg = Label(text="Csak UI. Logika bekötés később.", font_size=16, size_hint_y=.06)
        root.add_widget(self.msg)

        self.add_widget(root)

    def save(self, x):
        self.msg.text = "Stratégia UI mentve. Bekötés később."



class SectionScreen(Screen):
    def __init__(self, title, items, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=12, spacing=8)

        root.add_widget(Label(
            text=title,
            font_size=34,
            bold=True,
            color=(1,.75,0,1),
            size_hint_y=.13
        ))

        grid = GridLayout(cols=1, spacing=8, size_hint_y=.74)

        for txt, scr in items:
            b = button(txt, CARD, 22)
            b.bind(on_press=lambda x, sc=scr: go_to(self.manager, sc))
            grid.add_widget(b)

        root.add_widget(grid)

        back = button("VISSZA", (.35,.35,.35,1), 24)
        back.size_hint_y = .13
        back.bind(on_press=lambda x: go_back(self.manager))
        root.add_widget(back)

        self.add_widget(root)



class DemoCoreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", padding=12, spacing=10)

        title = Label(
            text="[b]DEMO CORE ENGINE[/b]",
            markup=True,
            size_hint_y=None,
            height=48
        )
        root.add_widget(title)

        self.info = Label(
            text="Betöltés...",
            halign="left",
            valign="top",
            markup=True
        )
        self.info.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = BoxLayout(orientation="vertical", size_hint_y=None, height=260, spacing=8)

        b_status = Button(text="STATUS / FRISSÍTÉS")
        b_tick = Button(text="TICK - KÉZI FUTTATÁS")
        b_start = Button(text="START")
        b_stop = Button(text="STOP")
        b_reset = Button(text="DEMO RESET 100 USDC")
        b_back = Button(text="VISSZA")

        b_status.bind(on_press=lambda x: self.refresh())
        b_tick.bind(on_press=lambda x: self.do_tick())
        b_start.bind(on_press=lambda x: self.do_start())
        b_stop.bind(on_press=lambda x: self.do_stop())
        b_reset.bind(on_press=lambda x: self.do_reset())
        b_back.bind(on_press=lambda x: setattr(self.manager, "current", "home"))

        for b in [b_status, b_tick, b_start, b_stop, b_reset, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def fmt_state(self, st, extra=""):
        try:
            eq = demo_core.equity(st)
        except Exception:
            eq = 0

        positions = st.get("positions", {})
        lines = []
        lines.append(f"[b]Running:[/b] {st.get('running')}")
        lines.append(f"[b]Balance:[/b] {st.get('balance')}")
        lines.append(f"[b]Equity:[/b] {eq:.4f}")
        lines.append(f"[b]Realized PnL:[/b] {st.get('realized_pnl')}")
        lines.append(f"[b]Last action:[/b] {st.get('last_action')}")
        lines.append("")
        lines.append("[b]Positions:[/b]")

        if not positions:
            lines.append("Nincs nyitott pozíció.")
        else:
            for sym, pos in positions.items():
                lines.append(f"{sym}: qty={pos.get('qty')}, avg={pos.get('avg')}, peak={pos.get('peak')}")

        if extra:
            lines.append("")
            lines.append("[b]Utolsó művelet:[/b]")
            lines.append(str(extra))

        return "\n".join(lines)

    def refresh(self):
        try:
            st = demo_core.load_state()
            self.info.text = self.fmt_state(st)
        except Exception as e:
            self.info.text = "Demo core hiba: " + str(e)

    def do_tick(self):
        try:
            res = demo_core.tick()
            st = demo_core.load_state()
            self.info.text = self.fmt_state(st, res.get("action", res))
        except Exception as e:
            self.info.text = "Tick hiba: " + str(e)

    def do_start(self):
        try:
            st = demo_core.load_state()
            st["running"] = True
            st["last_action"] = "Demo core START"
            demo_core.save_state(st)
            self.info.text = self.fmt_state(st, "START")
        except Exception as e:
            self.info.text = "Start hiba: " + str(e)

    def do_stop(self):
        try:
            st = demo_core.load_state()
            st["running"] = False
            st["last_action"] = "Demo core STOP"
            demo_core.save_state(st)
            self.info.text = self.fmt_state(st, "STOP")
        except Exception as e:
            self.info.text = "Stop hiba: " + str(e)

    def do_reset(self):
        try:
            st = demo_core.reset_demo(100.0)
            self.info.text = self.fmt_state(st, "RESET 100 USDC")
        except Exception as e:
            self.info.text = "Reset hiba: " + str(e)


class TextScreen(Screen):
    def __init__(self, title, body, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=18, spacing=12)
        root.add_widget(Label(text=title, font_size=34, bold=True, color=(1,.75,0,1), size_hint_y=.16))
        root.add_widget(Label(text=body, font_size=22))
        b = button("VISSZA", (.35,.35,.35,1), 24)
        b.bind(on_press=lambda x: go_back(self.manager))
        root.add_widget(b)
        self.add_widget(root)

class AppMain(App):
    title = "Binance Autobot"
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        sm = ScreenManager()
        sm.add_widget(Main(name="main"))
        sm.add_widget(Dashboard("demo", ORANGE, name="demo"))
        sm.add_widget(Dashboard("live", BLUE, name="live"))
        sm.add_widget(Scanner(name="scanner"))
        sm.add_widget(SectionScreen("BEÁLLÍTÁSOK", [("Alap beállítások", "settings_base"), ("Demo beállítások", "demo_settings"), ("Live beállítások", "live_settings"), ("Megjelenés / betűméret", "ui_mockup"), ("Fee / adózás", "fee_tax")], name="settings"))
        sm.add_widget(SectionScreen("BIZTONSÁG / API", [("App jelszó / PIN", "security_pin"), ("Binance API kulcs", "security_api"), ("E-mail beállítás", "security_email"), ("Titkosítás", "security_encrypt"), ("Healthcheck", "healthcheck")], name="security"))
        sm.add_widget(SectionScreen("AI / STRATÉGIA", [("Strategy Advanced", "strategy_advanced"), ("AI coin választás", "ai_coin"), ("Profit-Hold AI", "profit_hold_ai"), ("Backtest / Replay", "backtest"), ("Safety Guards", "safety_guards")], name="strategy"))
        sm.add_widget(SectionScreen("NAPLÓ / EXPORT", [("Trades / Export", "trades_export"), ("Audit log", "audit_log"), ("Snapshot export", "patch_snapshot"), ("Profit report", "profit_report")], name="logs"))
        sm.add_widget(SectionScreen("HALADÓ", [("Schedules", "schedules"),
                ("Háttérfutás / értesítések", "background_service"), ("Launchpool / Airdrop", "launchpool"), ("Patch Manager UI", "patch_manager_ui"), ("Diagnostics / Tests", "diagnostics"), ("PC + Google Drive Sync", "pc_drive_sync"), ("Fájlszerkezet", "file_structure"), ("Extra fejlesztések", "extra_features")], name="advanced"))

        sm.add_widget(MasterMenu(name="main"))
        sm.add_widget(SkeletonScreen("TRADE SIMPLE", "Symbol, Risk/trade %, minimum nettó profit %, SL/TP ATR szorzók.\nBekötés később.", name="trade_simple"))
        sm.add_widget(StrategyAdvancedScreen(name="strategy_advanced"))
        sm.add_widget(SkeletonScreen("SCHEDULES", "Snapshot 08:00, ár-trigger, automata state mentés, bővíthető szabályok.\nBekötés később.", name="schedules"))
        sm.add_widget(SkeletonScreen("LAUNCHPOOL / AIRDROP", "Enabled, Min APR, Watchlist, Scan now, Status.\nBekötés később.", name="launchpool"))
        sm.add_widget(SkeletonScreen("PATCH / SNAPSHOT", "Import ZIP, Export package.zip, Snapshot.zip, path-traversal védelem.\nBekötés később.", name="patch_snapshot"))
        sm.add_widget(SkeletonScreen("PC + GOOGLE DRIVE SYNC", "Primary/Secondary, Push to PC, Drive backup/import/export.\nBekötés később.", name="pc_drive_sync"))
        sm.add_widget(SkeletonScreen("DIAGNOSTICS / TESTS", "Routes, state, build/version, OpenAPI, toast visszajelzés.\nBekötés később.", name="diagnostics"))
        sm.add_widget(SkeletonScreen("PATCH MANAGER UI", "Beépített UI, JSON validáció, piros/zöld jelzés, real-time mentés.\nBekötés később.", name="patch_manager_ui"))
        sm.add_widget(DemoResetScreen(name="demo_reset"))
        sm.add_widget(SkeletonScreen("FÁJLSZERKEZET", "main.py, autobot_core.py, settings, state, trades, logs, patch.sh.\nStruktúra később részletezve.", name="file_structure"))
        sm.add_widget(SkeletonScreen("EXTRA FEJLESZTÉSEK", "Smart cooldown, volatility filter, max drawdown, auto parameter tuning.\nBekötés később.", name="extra_features"))
        sm.add_widget(SkeletonScreen("SAFETY GUARDS", "Spread guard, slippage guard, API rate-limit, Panic Stop-All, Safe Mode.\nBekötés később.", name="safety_guards"))
        sm.add_widget(SkeletonScreen("HEALTHCHECK", "Binance / Drive / E-mail / PC agent állapotjelzők, heartbeat, hibariasztás.\nBekötés később.", name="healthcheck"))
        sm.add_widget(SkeletonScreen("BACKTEST / REPLAY", "CSV/JSON betöltés, winrate, profit factor, maxDD, replay gyertyánként.\nBekötés később.", name="backtest"))
        sm.add_widget(SkeletonScreen("AUDIT LOG", "Manuális jóváhagyások, AI automata akciók indoklása, audit_log.csv.\nBekötés később.", name="audit_log"))
        sm.add_widget(SkeletonScreen("UI MOCKUP / MEGJELENÉS", "Demo narancs, Live kék sci-fi, KPI kártyák, trend, top coin mini-kártyák.\nFinomítás később.", name="ui_mockup"))
        sm.add_widget(SkeletonScreen("FEE / ADÓZÁS", "Maker/taker díjak nettó PnL-ben, opcionális HU 15% adózott profit nézet.\nNem adótanácsadás.", name="fee_tax"))
        sm.add_widget(SkeletonScreen("PROFIT-HOLD AI", "Profit tartás: hold idő, trailing take profit, edge keep, cooldown.\nBekötés később.", name="profit_hold_ai"))

        sm.add_widget(TradeSimpleScreen(name="trade_simple"))
        sm.add_widget(SkeletonScreen("ALAP BEÁLLÍTÁSOK", "Alap pénznem, nyelv, téma, értesítések, rendszer működés.\nBekötés később.", name="settings_base"))
        sm.add_widget(SkeletonScreen("DEMO BEÁLLÍTÁSOK", "Demo kezdő tőke, max coin, risk %, min profit %, reset szabályok.\nBekötés később.", name="demo_settings"))
        sm.add_widget(SkeletonScreen("LIVE BEÁLLÍTÁSOK", "Live API mód, max kitettség, safety guard, slippage, stop-all.\nBekötés később.", name="live_settings"))
        sm.add_widget(SkeletonScreen("APP JELSZÓ / PIN", "Belépési PIN, admin mód, később biometria.\nBekötés később.", name="security_pin"))
        sm.add_widget(SkeletonScreen("BINANCE API KULCS", "API key / secret mentés, read-only ellenőrzés, live engedély később.\nBekötés később.", name="security_api"))
        sm.add_widget(SkeletonScreen("E-MAIL BEÁLLÍTÁS", "Gmail app jelszó, teszt e-mail, trade értesítések.\nBekötés később.", name="security_email"))
        sm.add_widget(SkeletonScreen("TITKOSÍTÁS", "Helyi titkosítás, kulcskezelés, érzékeny adatok védelme.\nBekötés később.", name="security_encrypt"))
        sm.add_widget(SkeletonScreen("AI COIN VÁLASZTÁS", "Top coin rangsor, edge score, automata kiválasztás később.\nBekötés később.", name="ai_coin"))
        sm.add_widget(SkeletonScreen("TRADES / EXPORT", "Trade lista, CSV export, PnL napló, letöltés.\nBekötés később.", name="trades_export"))
        sm.add_widget(SkeletonScreen("PROFIT REPORT", "Profit trend, napi/heti összesítés, grafikon később.\nBekötés később.", name="profit_report"))

        sm.add_widget(SkeletonScreen("HÁTTÉRFUTÁS / ÉRTESÍTÉSEK", "Később itt lesz:\n- háttérben futó bot\n- állandó értesítés\n- trade riasztások\n- hibaértesítés\n- Android foreground service alap.\nBekötés később.", name="background_service"))
        sm.add_widget(DemoCoreScreen(name="demo_core"))
        return sm

if __name__ == "__main__":
    AppMain().run()
