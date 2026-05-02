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


class HistoryScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.previous_screen = "home"

    def go_to(self, target):
        try:
            if self.current and self.current != target:
                self.previous_screen = self.current
            self.current = target
        except Exception:
            self.current = target

    def go_back(self):
        try:
            target = self.previous_screen or "home"
            if target == self.current:
                target = "home"
            self.current = target
        except Exception:
            self.current = "home"


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
            ("NAPLÓ / EXPORT", "demo_logs", CARD),
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




















class DemoCoreIntegrationOverviewScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=8)

        root.add_widget(Label(
            text='[b]INTEGRÁCIÓK / SECRETS ÁLLAPOT[/b]\n[size=14]Binance, OpenAI, E-mail, Read-only, Live státusz[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        ))

        self.info = Label(text='Integráció státusz...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=220, spacing=8)
        buttons = [
            ('STATUS', self.refresh),
            ('SECRETS', lambda: self.manager.go_to('secrets')),
            ('BINANCE READONLY', lambda: self.manager.go_to('binance_readonly_real')),
            ('BINANCE SIGNED', lambda: self.manager.go_to('binance_signed')),
            ('EMAIL TEST', self.email_test),
            ('OPENAI/AI', lambda: self.manager.go_to('ai_advisor')),
            ('SETTINGS', lambda: self.manager.go_to('demo_settings')),
            ('VISSZA', self.go_back),
        ]

        for text, fn in buttons:
            b = Button(text=text)
            b.bind(on_press=lambda x, f=fn: f())
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self):
        try:
            res = demo_core.integration_overview_status()
            lines = ['[b]Integrációk állapota[/b]', '']
            for item in res.get('items', []):
                mark = '✅' if item.get('ok') else '⚠️'
                lines.append(f"{mark} [b]{item.get('name')}[/b]: {item.get('status')}")
                if item.get('detail'):
                    lines.append(f"   {item.get('detail')}")
            lines.append('')
            if res.get('warnings'):
                lines.append('[b]Figyelmeztetések:[/b]')
                for w in res.get('warnings', []):
                    lines.append('- ' + str(w))
                lines.append('')
            lines.append('[size=12]' + str(res.get('safe_summary')) + '[/size]')
            self.info.text = '\\n'.join(lines)
        except Exception as e:
            self.info.text = 'Integráció státusz hiba: ' + str(e)

    def email_test(self):
        try:
            res = demo_core.send_test_email()
            self.info.text = '[b]Email test eredmény[/b]\\n' + str(res)
        except Exception as e:
            self.info.text = 'Email test hiba: ' + str(e)



class DemoCoreBinanceReadOnlyRealScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=8)

        root.add_widget(Label(
            text='[b]BINANCE REAL READ-ONLY ACCOUNT[/b]\n[size=14]Valódi GET /api/v3/account, order nincs[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        ))

        self.info = Label(text='Real read-only státusz...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=220, spacing=8)
        buttons = [
            ('STATUS', self.refresh),
            ('READONLY HELP', self.help),
            ('REAL ACCOUNT GET', self.real_get),
            ('SECRETS', lambda: self.manager.go_to('secrets')),
            ('BINANCE SIGNED', lambda: self.manager.go_to('binance_signed')),
            ('SETTINGS', lambda: self.manager.go_to('demo_settings')),
            ('VISSZA', self.go_back),
        ]

        for text, fn in buttons:
            b = Button(text=text)
            b.bind(on_press=lambda x, f=fn: f())
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self):
        try:
            st = demo_core.binance_readonly_real_status()
            lines = ['[b]Binance real read-only státusz[/b]', '']
            for k, v in st.items():
                if k != 'ok':
                    lines.append(f"{k}: {v}")
            lines.append('')
            lines.append('[size=12]Csak account olvasás. Order endpoint nincs.[/size]')
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Status hiba: ' + str(e)

    def help(self):
        try:
            res = demo_core.readonly_activation_help()
            lines = ['[b]' + str(res.get('title')) + '[/b]', '']
            for step in res.get('steps', []):
                lines.append(step)
            lines.append('')
            lines.append('[b]Jelenlegi állapot:[/b]')
            cur = res.get('current') or {}
            for k, v in cur.items():
                if k != 'ok':
                    lines.append(f"{k}: {v}")
            lines.append('')
            lines.append('[b]Biztonság:[/b] ' + str(res.get('danger_note')))
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Help hiba: ' + str(e)

    def real_get(self):
        try:
            res = demo_core.binance_account_readonly_real_get()
            lines = ['[b]Real account GET eredmény[/b]', '']
            lines.append(f"OK: {res.get('ok')}")
            lines.append(f"Called: {res.get('called')}")
            lines.append(f"Status code: {res.get('status_code')}")
            lines.append(f"Error: {res.get('error')}")
            lines.append(f"Balances count: {res.get('balances_count')}")
            lines.append(f"Order endpoint used: {res.get('order_endpoint_used')}")
            lines.append('')
            lines.append('[b]Balance preview:[/b]')
            for b in res.get('balance_preview') or []:
                lines.append(f"- {b.get('asset')}: free={b.get('free')} locked={b.get('locked')}")
            lines.append('')
            lines.append(str(res.get('message') or res.get('reason') or ''))
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Real GET hiba: ' + str(e)



class DemoCoreBinanceSignedScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=8)

        root.add_widget(Label(
            text='[b]BINANCE SIGNED READ-ONLY[/b]\n[size=14]Signed preview + account read előkészítés, order nincs[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        ))

        self.info = Label(text='Signed readonly státusz...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=220, spacing=8)
        buttons = [
            ('STATUS', self.refresh),
            ('SIGNED PREVIEW', self.preview),
            ('ACCOUNT READ CHECK', self.account_read),
            ('SECRETS', lambda: self.manager.go_to('secrets')),
            ('BINANCE ACCOUNT', lambda: self.manager.go_to('binance_account')),
            ('SETTINGS', lambda: self.manager.go_to('demo_settings')),
            ('VISSZA', self.go_back),
        ]

        for text, fn in buttons:
            b = Button(text=text)
            b.bind(on_press=lambda x, f=fn: f())
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self):
        try:
            st = demo_core.binance_signed_readonly_status()
            lines = ['[b]Binance signed read-only státusz[/b]', '']
            for k, v in st.items():
                if k != 'ok':
                    lines.append(f"{k}: {v}")
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Status hiba: ' + str(e)

    def preview(self):
        try:
            res = demo_core.binance_signed_request_preview()
            lines = ['[b]Signed preview[/b]', '']
            for k, v in res.items():
                lines.append(f"{k}: {v}")
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Preview hiba: ' + str(e)

    def account_read(self):
        try:
            res = demo_core.binance_account_readonly_check()
            lines = ['[b]Account read-only check[/b]', '']
            for k, v in res.items():
                lines.append(f"{k}: {v}")
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Account read hiba: ' + str(e)



class DemoCoreBinanceAccountScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=8)

        root.add_widget(Label(
            text='[b]BINANCE ACCOUNT / TEST ORDER[/b]\n[size=14]Account státusz + test-order validate, NEM order[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        ))

        self.info = Label(text='Binance account adapter...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=220, spacing=8)
        buttons = [
            ('STATUS', self.refresh),
            ('ACCOUNT CHECK', self.account_check),
            ('TEST ORDER VALIDATE', self.test_order),
            ('LIVE GATE', lambda: self.manager.go_to('live_gate')),
            ('SECRETS', lambda: self.manager.go_to('secrets')),
            ('SETTINGS', lambda: self.manager.go_to('demo_settings')),
            ('VISSZA', self.go_back),
        ]

        for text, fn in buttons:
            b = Button(text=text)
            b.bind(on_press=lambda x, f=fn: f())
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self):
        try:
            st = demo_core.binance_account_test_status()
            lines = ['[b]Binance Account/Test státusz[/b]', '']
            for k, v in st.items():
                if k != 'ok':
                    lines.append(f"{k}: {v}")
            lines.append('')
            lines.append('[size=12]Ez még nem hív Binance order endpointot.[/size]')
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Status hiba: ' + str(e)

    def account_check(self):
        try:
            res = demo_core.binance_account_status_adapter()
            lines = ['[b]Account check[/b]', '']
            for k, v in res.items():
                lines.append(f"{k}: {v}")
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Account check hiba: ' + str(e)

    def test_order(self):
        try:
            res = demo_core.binance_test_order_validate()
            lines = ['[b]Test order validate[/b]', '']
            lines.append(f"Validated: {res.get('validated')}")
            lines.append(f"Safety allowed: {res.get('safety_gate_allowed')}")
            lines.append('')
            lines.append('[b]Blocks:[/b]')
            for b in res.get('safety_gate_blocks') or []:
                lines.append('- ' + str(b))
            lines.append('')
            lines.append('[b]Payload:[/b]')
            lines.append(str(res.get('payload')))
            lines.append('')
            lines.append(res.get('message', ''))
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Test order hiba: ' + str(e)



class DemoCoreLiveGateScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=8)

        root.add_widget(Label(
            text='[b]LIVE EXECUTOR SAFETY GATE[/b]\n[size=14]Éles order előtti végső kapu, NEM küld ordert[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        ))

        self.info = Label(text='Live gate státusz...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=220, spacing=8)
        buttons = [
            ('STATUS', self.refresh),
            ('TEST LATEST', self.test_latest),
            ('LIVE CHECK', lambda: self.manager.go_to('binance_live')),
            ('APPROVAL', lambda: self.manager.go_to('approval_executor')),
            ('SETTINGS', lambda: self.manager.go_to('demo_settings')),
            ('ADMIN', lambda: self.manager.go_to('admin')),
            ('VISSZA', self.go_back),
        ]

        for text, fn in buttons:
            b = Button(text=text)
            b.bind(on_press=lambda x, f=fn: f())
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self):
        try:
            st = demo_core.live_executor_gate_status()
            lines = []
            lines.append('[b]Live Executor Gate státusz[/b]')
            lines.append('')
            for k, v in st.items():
                if k != 'ok':
                    lines.append(f"{k}: {v}")
            lines.append('')
            lines.append('[size=12]Ez még nem küld Binance ordert.[/size]')
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Live gate status hiba: ' + str(e)

    def test_latest(self):
        try:
            res = demo_core.simulate_live_order_gate_from_latest()
            lines = []
            lines.append('[b]Live Gate teszt[/b]')
            lines.append('')
            lines.append(f"Allowed: {res.get('allowed')}")
            lines.append(f"Symbol: {res.get('symbol')}")
            lines.append(f"Side: {res.get('side')}")
            lines.append(f"Amount: {res.get('amount')}")
            lines.append('')
            lines.append('[b]Blocks:[/b]')
            for b in res.get('blocks', []):
                lines.append('- ' + str(b))
            lines.append('')
            lines.append('[b]Warnings:[/b]')
            for w in res.get('warnings', []):
                lines.append('- ' + str(w))
            lines.append('')
            lines.append(str(res.get('message') or res.get('error') or ''))
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Live gate test hiba: ' + str(e)



class DemoCoreApprovalExecutorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=8)

        root.add_widget(Label(
            text='[b]APPROVAL / DRY-RUN EXECUTOR[/b]\n[size=14]Jóváhagyás + száraz futtatás, NEM live order[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        ))

        self.info = Label(text='Approval státusz...', markup=True, halign='left', valign='top', size_hint_y=None, height=260)
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        root.add_widget(self.info)

        self.symbol = TextInput(text='BTCUSDT', hint_text='symbol', multiline=False, size_hint_y=None, height=44)
        self.side = TextInput(text='BUY', hint_text='BUY/SELL', multiline=False, size_hint_y=None, height=44)
        self.amount = TextInput(text='10', hint_text='amount', multiline=False, size_hint_y=None, height=44)

        root.add_widget(self.symbol)
        root.add_widget(self.side)
        root.add_widget(self.amount)

        btns = GridLayout(cols=2, size_hint_y=None, height=260, spacing=8)

        buttons = [
            ('STATUS', self.refresh),
            ('CREATE REQUEST', self.create_request),
            ('APPROVE LATEST', self.approve_latest),
            ('REJECT LATEST', self.reject_latest),
            ('DRY-RUN EXECUTE', self.execute_dry),
            ('ADMIN', lambda: self.manager.go_to('admin')),
            ('SETTINGS', lambda: self.manager.go_to('demo_settings')),
            ('VISSZA', self.go_back),
        ]

        for text, fn in buttons:
            b = Button(text=text)
            b.bind(on_press=lambda x, f=fn: f())
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self):
        try:
            st = demo_core.approval_executor_status()
            lines = []
            lines.append('[b]Approval / Executor státusz[/b]')
            lines.append(f"Pending: {st.get('pending_count')}")
            lines.append(f"Approved: {st.get('approved_count')}")
            lines.append(f"Dry-run executed: {st.get('executed_count')}")
            lines.append(f"Dry-run enabled: {st.get('dry_run_executor_enabled')}")
            lines.append('')
            lines.append('[b]Utolsó kérések:[/b]')
            for item in st.get('last_items', [])[-6:]:
                lines.append(f"- {item.get('id')} | {item.get('side')} {item.get('symbol')} {item.get('amount')} | {item.get('status')}")
            lines.append('')
            lines.append('[size=12]Biztonság: ez még nem küld Binance ordert.[/size]')
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Approval hiba: ' + str(e)

    def create_request(self):
        try:
            res = demo_core.create_approval_request(
                'MANUAL_TRADE_REQUEST',
                self.symbol.text,
                self.side.text,
                float(self.amount.text.replace(',', '.')),
                'UI manual request',
                {}
            )
            self.info.text = str(res)
        except Exception as e:
            self.info.text = 'Create request hiba: ' + str(e)

    def approve_latest(self):
        try:
            res = demo_core.approve_latest_pending('UI approve')
            self.info.text = str(res)
        except Exception as e:
            self.info.text = 'Approve hiba: ' + str(e)

    def reject_latest(self):
        try:
            res = demo_core.reject_latest_pending('UI reject')
            self.info.text = str(res)
        except Exception as e:
            self.info.text = 'Reject hiba: ' + str(e)

    def execute_dry(self):
        try:
            res = demo_core.execute_latest_approved_dry_run()
            self.info.text = str(res)
        except Exception as e:
            self.info.text = 'Dry-run hiba: ' + str(e)



class DemoCoreAdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=8)

        root.add_widget(Label(
            text='[b]ADMIN SECURITY[/b]\n[size=14]Admin login + 5 perc auto logout[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        ))

        self.info = Label(text='Admin státusz...', markup=True, halign='left', valign='top', size_hint_y=None, height=180)
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        root.add_widget(self.info)

        self.user = TextInput(text='admin', multiline=False, size_hint_y=None, height=44)
        self.pw = TextInput(text='', hint_text='password', password=True, multiline=False, size_hint_y=None, height=44)
        self.new_pw = TextInput(text='', hint_text='new password', password=True, multiline=False, size_hint_y=None, height=44)

        root.add_widget(self.user)
        root.add_widget(self.pw)
        root.add_widget(self.new_pw)

        btns = GridLayout(cols=2, size_hint_y=None, height=220, spacing=8)
        buttons = [
            ('LOGIN', self.login),
            ('LOGOUT', self.logout),
            ('CHANGE PW', self.change_pw),
            ('STATUS', self.refresh),
            ('PATCH MANAGER', lambda: self.manager.go_to('patch_manager')),
            ('VISSZA', self.go_back),
        ]
        for text, fn in buttons:
            b = Button(text=text)
            b.bind(on_press=lambda x, f=fn: f())
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def render(self, st, extra=''):
        lines = []
        if extra:
            lines.append('[b]' + extra + '[/b]')
            lines.append('')
        lines.append('[b]Admin státusz[/b]')
        lines.append(f"User: {st.get('admin_username')}")
        lines.append(f"Active: {st.get('admin_active')}")
        lines.append(f"Seconds left: {st.get('seconds_left')}")
        lines.append(f"Timeout sec: {st.get('admin_timeout_sec')}")
        lines.append(f"Default password change needed: {st.get('must_change_default')}")
        self.info.text = '\n'.join(lines)

    def refresh(self):
        self.render(demo_core.admin_status())

    def login(self):
        st = demo_core.admin_login(self.user.text, self.pw.text)
        self.render(st, 'Login: ' + str(st.get('login_ok')))

    def logout(self):
        self.render(demo_core.admin_logout(), 'Logout OK')

    def change_pw(self):
        res = demo_core.admin_change_password(self.pw.text, self.new_pw.text)
        self.info.text = str(res)


class DemoCorePatchManagerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=8)

        root.add_widget(Label(
            text='[b]PATCH MANAGER SAFE BASE[/b]\n[size=14]Path védelem + patch queue, apply később[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        ))

        self.info = Label(text='Patch manager...', markup=True, halign='left', valign='top', size_hint_y=None, height=220)
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        root.add_widget(self.info)

        self.path_inp = TextInput(text='main.py', hint_text='path', multiline=False, size_hint_y=None, height=44)
        self.desc_inp = TextInput(text='', hint_text='patch leírás', multiline=False, size_hint_y=None, height=44)
        self.preview_inp = TextInput(text='', hint_text='preview / megjegyzés', multiline=True, size_hint_y=None, height=100)

        root.add_widget(self.path_inp)
        root.add_widget(self.desc_inp)
        root.add_widget(self.preview_inp)

        btns = GridLayout(cols=2, size_hint_y=None, height=180, spacing=8)
        buttons = [
            ('STATUS', self.refresh),
            ('QUEUE PATCH', self.queue),
            ('READ QUEUE', self.read_queue),
            ('ADMIN', lambda: self.manager.go_to('admin')),
            ('VISSZA', self.go_back),
        ]
        for text, fn in buttons:
            b = Button(text=text)
            b.bind(on_press=lambda x, f=fn: f())
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self):
        st = demo_core.patch_manager_status()
        lines = []
        lines.append('[b]Patch Manager státusz[/b]')
        lines.append(f"Enabled: {st.get('enabled')}")
        lines.append(f"Require admin: {st.get('require_admin')}")
        lines.append(f"Admin active: {st.get('admin_active')}")
        lines.append(f"Queue file: {st.get('queue_file')}")
        lines.append('')
        lines.append('[b]Allowed paths:[/b]')
        for p in st.get('allowed_paths', []):
            lines.append('- ' + str(p))
        lines.append('')
        lines.append('[size=12]Apply funkció később, külön biztonsági lépésben.[/size]')
        self.info.text = '\n'.join(lines)

    def queue(self):
        res = demo_core.queue_patch_request(self.path_inp.text, self.desc_inp.text, self.preview_inp.text)
        self.info.text = str(res)

    def read_queue(self):
        res = demo_core.read_patch_queue()
        lines = ['[b]Patch queue[/b]', '']
        for item in res.get('items', []):
            lines.append(f"- {item.get('path')} | {item.get('status')} | {item.get('description')}")
        self.info.text = '\n'.join(lines)



class DemoCoreSyncScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(
            text='[b]PC / GOOGLE DRIVE SYNC[/b]\n[size=14]Export/import ZIP secrets nélkül[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        )
        root.add_widget(title)

        self.info = Label(text='Sync betöltés...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=220, spacing=8)

        b_status = Button(text='SYNC STATUS')
        b_drive = Button(text='EXPORT DRIVE')
        b_pc = Button(text='EXPORT PC')
        b_import_drive = Button(text='IMPORT DRIVE')
        b_import_pc = Button(text='IMPORT PC')
        b_settings = Button(text='SETTINGS')
        b_back = Button(text='VISSZA')

        b_status.bind(on_press=lambda x: self.refresh())
        b_drive.bind(on_press=lambda x: self.export('drive'))
        b_pc.bind(on_press=lambda x: self.export('pc'))
        b_import_drive.bind(on_press=lambda x: self.import_sync('drive'))
        b_import_pc.bind(on_press=lambda x: self.import_sync('pc'))
        b_settings.bind(on_press=lambda x: self.manager.go_to('demo_settings'))
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_status, b_drive, b_pc, b_import_drive, b_import_pc, b_settings, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self, extra=''):
        try:
            res = demo_core.sync_status()
            lines = []
            if extra:
                lines.append('[b]' + extra + '[/b]')
                lines.append('')
            lines.append('[b]Sync státusz[/b]')
            lines.append('')
            lines.append(f"Enabled: {res.get('sync_enabled')}")
            lines.append(f"Primary: {res.get('primary_device')}")
            lines.append(f"Drive folder: {res.get('drive_sync_folder')}")
            lines.append(f"PC folder: {res.get('pc_sync_folder')}")
            lines.append(f"Drive ZIP count: {res.get('drive_files_count')}")
            lines.append(f"PC ZIP count: {res.get('pc_files_count')}")
            lines.append(f"Last export ts: {res.get('last_sync_export_ts')}")
            lines.append(f"Last import ts: {res.get('last_sync_import_ts')}")
            lines.append('')
            lines.append('[size=12]Secrets/key/env fájlokat nem exportálunk.[/size]')
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Sync státusz hiba: ' + str(e)

    def export(self, target):
        try:
            res = demo_core.export_sync_bundle(target)
            self.refresh('Export: ' + str(res.get('path') or res.get('reason')))
        except Exception as e:
            self.info.text = 'Export hiba: ' + str(e)

    def import_sync(self, source):
        try:
            res = demo_core.import_latest_sync_bundle(source)
            self.refresh('Import: ' + str(res.get('zip') or res.get('reason')))
        except Exception as e:
            self.info.text = 'Import hiba: ' + str(e)


class DemoCoreFirstRunScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(
            text='[b]FIRST-RUN WIZARD[/b]\n[size=14]Hiányzó beállítások ellenőrzése[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        )
        root.add_widget(title)

        self.info = Label(text='First-run betöltés...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=180, spacing=8)

        b_check = Button(text='ELLENŐRZÉS')
        b_done = Button(text='KÉSZRE ÁLLÍT')
        b_secrets = Button(text='SECRETS')
        b_sync = Button(text='SYNC')
        b_back = Button(text='VISSZA')

        b_check.bind(on_press=lambda x: self.refresh())
        b_done.bind(on_press=lambda x: self.done())
        b_secrets.bind(on_press=lambda x: self.manager.go_to('secrets'))
        b_sync.bind(on_press=lambda x: self.manager.go_to('sync'))
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_check, b_done, b_secrets, b_sync, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self, extra=''):
        try:
            res = demo_core.first_run_status()
            lines = []
            if extra:
                lines.append('[b]' + extra + '[/b]')
                lines.append('')
            lines.append('[b]First-run státusz[/b]')
            lines.append('')
            lines.append(f"First run done: {res.get('first_run_done')}")
            lines.append(f"Ready: {res.get('ready')}")
            lines.append(f"Missing count: {res.get('missing_count')}")
            lines.append('')
            for item in res.get('checklist', []):
                ok = 'OK' if item.get('ok') else 'HIÁNYZIK'
                lines.append(f"- {item.get('label')}: {ok}")
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'First-run hiba: ' + str(e)

    def done(self):
        try:
            res = demo_core.mark_first_run_done()
            self.refresh('First-run készre állítva.')
        except Exception as e:
            self.info.text = 'First-run done hiba: ' + str(e)



class DemoCorePackageScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(
            text='[b]PACKAGE / SNAPSHOT[/b]\n[size=14]ZIP export secrets nélkül + APK referencia[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        )
        root.add_widget(title)

        self.info = Label(text='Package betöltés...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=180, spacing=8)

        b_pkg = Button(text='EXPORT PACKAGE')
        b_snap = Button(text='EXPORT SNAPSHOT')
        b_ref = Button(text='APK REF')
        b_back = Button(text='VISSZA')

        b_pkg.bind(on_press=lambda x: self.export_package())
        b_snap.bind(on_press=lambda x: self.export_snapshot())
        b_ref.bind(on_press=lambda x: self.refresh())
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_pkg, b_snap, b_ref, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self, extra=''):
        try:
            ref = demo_core.apk_reference_status()
            lines = []
            if extra:
                lines.append('[b]' + extra + '[/b]')
                lines.append('')
            lines.append('[b]APK / Package státusz[/b]')
            lines.append('')
            lines.append(f"App version: {ref.get('app_version')}")
            lines.append(f"Working APK ref: {ref.get('working_apk_reference')}")
            lines.append(f"Build policy: {ref.get('build_policy')}")
            lines.append(f"Dev mode: {ref.get('current_dev_mode')}")
            lines.append('')
            lines.append('[size=12]A package/snapshot ZIP nem tartalmaz secrets.enc, key vagy .env fájlt.[/size]')
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Package státusz hiba: ' + str(e)

    def export_package(self):
        try:
            res = demo_core.export_project_package('ui')
            self.refresh('Package export: ' + str(res.get('path')))
        except Exception as e:
            self.info.text = 'Package export hiba: ' + str(e)

    def export_snapshot(self):
        try:
            res = demo_core.export_full_snapshot('ui')
            self.refresh('Snapshot export: ' + str(res.get('path')))
        except Exception as e:
            self.info.text = 'Snapshot export hiba: ' + str(e)



class DemoCoreSchedulesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(
            text='[b]SCHEDULES[/b]\n[size=14]Snapshot + ár-trigger + kézi futtatás[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        )
        root.add_widget(title)

        self.info = Label(text='Schedules betöltés...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=180, spacing=8)
        b_run = Button(text='RUN SCHEDULES')
        b_snapshot = Button(text='SNAPSHOT')
        b_settings = Button(text='SETTINGS')
        b_back = Button(text='VISSZA')

        b_run.bind(on_press=lambda x: self.run())
        b_snapshot.bind(on_press=lambda x: self.snapshot())
        b_settings.bind(on_press=lambda x: self.manager.go_to('demo_settings'))
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_run, b_snapshot, b_settings, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self, extra=''):
        try:
            st = demo_core.load_state()
            cfg = st.get('settings', {})
            lines = []
            if extra:
                lines.append('[b]' + extra + '[/b]')
                lines.append('')
            lines.append(f"Schedules enabled: {cfg.get('schedules_enabled')}")
            lines.append(f"Snapshot: {cfg.get('snapshot_enabled')} at {cfg.get('snapshot_time')}")
            lines.append(f"Price trigger: {cfg.get('price_trigger_enabled')}")
            lines.append(f"Symbol: {cfg.get('price_trigger_symbol')}")
            lines.append(f"Above: {cfg.get('price_trigger_above')}")
            lines.append(f"Below: {cfg.get('price_trigger_below')}")
            lines.append(f"Last run ts: {cfg.get('last_schedule_run_ts')}")
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Schedules hiba: ' + str(e)

    def run(self):
        try:
            res = demo_core.run_schedules_once()
            self.refresh('Schedules run: ' + str(res.get('ran')))
        except Exception as e:
            self.info.text = 'Run hiba: ' + str(e)

    def snapshot(self):
        try:
            res = demo_core.snapshot_state('manual_ui')
            self.refresh('Snapshot: ' + str(res.get('path')))
        except Exception as e:
            self.info.text = 'Snapshot hiba: ' + str(e)


class DemoCoreLaunchpoolScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(
            text='[b]LAUNCHPOOL / AIRDROP WATCH[/b]\n[size=14]Demo scan, min APR, watchlist[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        )
        root.add_widget(title)

        self.info = Label(text='Launchpool betöltés...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=180, spacing=8)
        b_scan = Button(text='SCAN NOW')
        b_settings = Button(text='SETTINGS')
        b_health = Button(text='HEALTHCHECK')
        b_back = Button(text='VISSZA')

        b_scan.bind(on_press=lambda x: self.scan())
        b_settings.bind(on_press=lambda x: self.manager.go_to('demo_settings'))
        b_health.bind(on_press=lambda x: self.manager.go_to('healthcheck'))
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_scan, b_settings, b_health, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.scan()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def scan(self):
        try:
            res = demo_core.launchpool_scan()
            lines = []
            lines.append('[b]Launchpool / Airdrop scan[/b]')
            lines.append('')
            lines.append(f"Enabled: {res.get('enabled')}")
            lines.append(f"Min APR: {res.get('min_apr')}")
            lines.append(f"Watchlist: {', '.join(res.get('watchlist', []))}")
            lines.append('')
            lines.append('[b]Candidates:[/b]')
            for c in res.get('candidates', [])[:20]:
                flag = 'OK' if c.get('eligible') else 'WATCH'
                lines.append(f"- {c.get('asset')}: APR {c.get('apr')}% score={c.get('score')} {flag}")
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Launchpool hiba: ' + str(e)



class DemoCoreBacktestScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(
            text='[b]BACKTEST / REPLAY[/b]\n[size=14]Demo stratégia teszt, CSV report[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        )
        root.add_widget(title)

        self.info = Label(text='Backtest betöltés...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=180, spacing=8)
        b_run = Button(text='RUN BACKTEST')
        b_report = Button(text='REPORT CSV')
        b_settings = Button(text='SETTINGS')
        b_back = Button(text='VISSZA')

        b_run.bind(on_press=lambda x: self.run_backtest())
        b_report.bind(on_press=lambda x: self.report())
        b_settings.bind(on_press=lambda x: self.manager.go_to('demo_settings'))
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_run, b_report, b_settings, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.run_backtest()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def run_backtest(self):
        try:
            st = demo_core.load_state()
            cfg = st.get('settings', {})
            sym = cfg.get('backtest_symbol', 'BTCUSDT')
            limit = cfg.get('backtest_limit', 240)
            res = demo_core.backtest_symbol(sym, limit)

            lines = []
            lines.append('[b]Backtest eredmény[/b]')
            lines.append('')
            lines.append(f"Symbol: {res.get('symbol')}")
            lines.append(f"Start balance: {res.get('start_balance')}")
            lines.append(f"Final equity: {res.get('final_equity')}")
            lines.append(f"Total PnL: {res.get('total_pnl')}")
            lines.append(f"Total %: {res.get('total_pct')}%")
            lines.append(f"Trades: {res.get('trades_count')}")
            lines.append(f"Closed trades: {res.get('closed_trades')}")
            lines.append(f"Winrate: {res.get('winrate')}%")
            lines.append(f"Profit factor: {res.get('profit_factor')}")
            lines.append(f"Max DD: {res.get('max_drawdown_pct')}%")
            lines.append(f"Open position: {res.get('open_position')}")
            lines.append('')
            lines.append('[size=12]Report: logs/backtest_report.csv[/size]')

            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Backtest hiba: ' + str(e)

    def report(self):
        try:
            res = demo_core.read_backtest_report()
            self.info.text = res.get('text') if res.get('ok') else res.get('error')
        except Exception as e:
            self.info.text = 'Report hiba: ' + str(e)


class DemoCoreDiagnosticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(
            text='[b]DIAGNOSTICS / VERSION[/b]\n[size=14]Állapot, fájlok, modulok[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        )
        root.add_widget(title)

        self.info = Label(text='Diagnostics betöltés...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=140, spacing=8)
        b_refresh = Button(text='FRISSÍTÉS')
        b_health = Button(text='HEALTHCHECK')
        b_backtest = Button(text='BACKTEST')
        b_back = Button(text='VISSZA')

        b_refresh.bind(on_press=lambda x: self.refresh())
        b_health.bind(on_press=lambda x: self.manager.go_to('healthcheck'))
        b_backtest.bind(on_press=lambda x: self.manager.go_to('backtest'))
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_refresh, b_health, b_backtest, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self):
        try:
            res = demo_core.diagnostics_status()
            lines = []
            lines.append('[b]Diagnostics[/b]')
            lines.append('')
            lines.append(f"Version: {res.get('version')}")
            lines.append(f"Python: {res.get('python')}")
            lines.append(f"Running: {res.get('running')}")
            lines.append(f"Safe mode: {res.get('safe_mode')}")
            lines.append(f"Positions: {res.get('positions_count')}")
            lines.append(f"Settings count: {res.get('settings_count')}")
            lines.append(f"Live ready: {res.get('live_ready')}")
            lines.append(f"Last action: {res.get('last_action')}")
            lines.append('')
            lines.append('[b]Secrets ready:[/b]')
            sr = res.get('secrets_ready') or {}
            for k, v in sr.items():
                lines.append(f"- {k}: {v}")
            lines.append('')
            lines.append('[b]Files:[/b]')
            for k, v in (res.get('files') or {}).items():
                lines.append(f"- {k}: {'OK' if v else 'NINCS'}")
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Diagnostics hiba: ' + str(e)



class DemoCoreBinanceLiveScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(
            text='[b]BINANCE LIVE API CHECK[/b]\n[size=14]Csak ellenőrzés, NEM küld megbízást[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        )
        root.add_widget(title)

        self.info = Label(text='Live státusz betöltés...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=220, spacing=8)
        b_refresh = Button(text='LIVE CHECK')
        b_ack = Button(text='FIGYELMEZTETÉS OK')
        b_checkonly = Button(text='CHECK ONLY ON')
        b_disable = Button(text='LIVE OFF')
        b_secrets = Button(text='SECRETS')
        b_back = Button(text='VISSZA')

        b_refresh.bind(on_press=lambda x: self.refresh())
        b_ack.bind(on_press=lambda x: self.ack())
        b_checkonly.bind(on_press=lambda x: self.check_only())
        b_disable.bind(on_press=lambda x: self.disable())
        b_secrets.bind(on_press=lambda x: self.manager.go_to('secrets'))
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_refresh, b_ack, b_checkonly, b_disable, b_secrets, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def render(self, res):
        lines = []
        lines.append('[b]Binance Live státusz[/b]')
        lines.append('')
        lines.append(f"API key: {'OK' if res.get('has_api_key') else 'HIÁNYZIK'}")
        lines.append(f"API secret: {'OK' if res.get('has_api_secret') else 'HIÁNYZIK'}")
        lines.append(f"Live mode: {res.get('live_mode_enabled')}")
        lines.append(f"BUY allowed: {res.get('live_allow_buy')}")
        lines.append(f"SELL allowed: {res.get('live_allow_sell')}")
        lines.append(f"Max order USDT: {res.get('live_max_order_usdt')}")
        lines.append(f"Execution mode: {res.get('execution_mode')}")
        lines.append(f"Safe mode: {res.get('safe_mode')}")
        lines.append(f"Warning ACK: {res.get('live_warning_ack')}")
        lines.append('')
        lines.append(f"[b]Ready for live:[/b] {res.get('ready_for_live')}")
        lines.append('')

        warns = res.get('warnings') or []
        if warns:
            lines.append('[b]Figyelmeztetések:[/b]')
            for w in warns:
                lines.append('- ' + str(w))
        else:
            lines.append('Nincs figyelmeztetés.')

        lines.append('')
        lines.append('[size=12]Biztonság: ez a képernyő még nem küld valódi Binance megbízást.[/size]')

        self.info.text = '\n'.join(lines)

    def refresh(self):
        try:
            self.render(demo_core.binance_live_status())
        except Exception as e:
            self.info.text = 'Live check hiba: ' + str(e)

    def ack(self):
        try:
            self.render(demo_core.acknowledge_live_warning())
        except Exception as e:
            self.info.text = 'ACK hiba: ' + str(e)

    def check_only(self):
        try:
            self.render(demo_core.enable_live_check_only())
        except Exception as e:
            self.info.text = 'Check only hiba: ' + str(e)

    def disable(self):
        try:
            self.render(demo_core.disable_live_mode())
        except Exception as e:
            self.info.text = 'Live off hiba: ' + str(e)



class DemoCoreSecretsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=8)

        title = Label(
            text='[b]SECRETS / INTEGRÁCIÓK[/b]\n[size=14]Binance API, OpenAI, E-mail, Drive, PC Sync[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        )
        root.add_widget(title)

        self.info = Label(text='Betöltés...', markup=True, halign='left', valign='top', size_hint_y=None, height=220)
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        root.add_widget(self.info)

        form_scroll = ScrollView()
        form = GridLayout(cols=1, size_hint_y=None, spacing=6)
        form.bind(minimum_height=form.setter('height'))

        self.inputs = {}

        fields = [
            ('binance_api_key', 'Binance API key'),
            ('binance_api_secret', 'Binance API secret'),
            ('openai_api_key', 'OpenAI API key'),
            ('email_smtp_host', 'SMTP host'),
            ('email_smtp_port', 'SMTP port'),
            ('email_user', 'E-mail user'),
            ('email_app_password', 'E-mail app password'),
            ('email_to', 'E-mail címzett'),
            ('google_drive_token', 'Google Drive token'),
            ('pc_sync_token', 'PC sync token'),
            ('ngrok_token', 'ngrok token'),
        ]

        data = {}
        try:
            data = demo_core.load_secrets()
        except Exception:
            data = {}

        for key, label in fields:
            form.add_widget(Label(text='[b]' + label + '[/b]', markup=True, size_hint_y=None, height=28))
            inp = TextInput(
                text=str(data.get(key, '')),
                multiline=False,
                password=('password' in key or 'secret' in key or 'token' in key or 'api_key' in key),
                size_hint_y=None,
                height=44
            )
            self.inputs[key] = inp
            form.add_widget(inp)

        form_scroll.add_widget(form)
        root.add_widget(form_scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=250, spacing=8)

        b_save = Button(text='MENTÉS')
        b_refresh = Button(text='STÁTUSZ')
        b_binance = Button(text='TESZT BINANCE')
        b_openai = Button(text='TESZT OPENAI')
        b_email = Button(text='TESZT EMAIL')
        b_drive = Button(text='TESZT DRIVE')
        b_pc = Button(text='TESZT PC')
        b_back = Button(text='VISSZA')

        b_save.bind(on_press=lambda x: self.save())
        b_refresh.bind(on_press=lambda x: self.refresh())
        b_binance.bind(on_press=lambda x: self.test('binance'))
        b_openai.bind(on_press=lambda x: self.test('openai'))
        b_email.bind(on_press=lambda x: self.test('email'))
        b_drive.bind(on_press=lambda x: self.test('drive'))
        b_pc.bind(on_press=lambda x: self.test('pc'))
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_save, b_refresh, b_binance, b_openai, b_email, b_drive, b_pc, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def save(self):
        try:
            data = {}
            for k, inp in self.inputs.items():
                data[k] = inp.text.strip()
            demo_core.save_secrets(data)
            demo_core.audit_event("SECRETS_SAVE_UI", "Secrets UI mentés", {"keys": list(data.keys())})
            self.refresh("Mentve.")
        except Exception as e:
            self.info.text = "Mentési hiba: " + str(e)

    def refresh(self, prefix=''):
        try:
            st = demo_core.secrets_status()
            m = st.get('masked', {})
            lines = []
            if prefix:
                lines.append('[b]' + prefix + '[/b]')
                lines.append('')

            lines.append('[b]Integráció státusz[/b]')
            lines.append('')
            lines.append(f"Binance API: {'OK' if st.get('binance_api') else 'HIÁNYZIK'}")
            lines.append(f"OpenAI API: {'OK' if st.get('openai_api') else 'HIÁNYZIK'}")
            lines.append(f"E-mail: {'OK' if st.get('email') else 'HIÁNYZIK'}")
            lines.append(f"Google Drive: {'OK' if st.get('google_drive') else 'HIÁNYZIK'}")
            lines.append(f"PC Sync: {'OK' if st.get('pc_sync') else 'HIÁNYZIK'}")
            lines.append(f"ngrok: {'OK' if st.get('ngrok') else 'HIÁNYZIK'}")
            lines.append('')
            lines.append('[b]Maszkolt értékek[/b]')
            lines.append(f"Binance key: {m.get('binance_api_key')}")
            lines.append(f"Binance secret: {m.get('binance_api_secret')}")
            lines.append(f"OpenAI key: {m.get('openai_api_key')}")
            lines.append(f"Email user: {m.get('email_user')}")
            lines.append(f"Email to: {m.get('email_to')}")
            lines.append('')
            lines.append('[size=12]Figyelem: kulcsot/jelszót ne commitolj GitHubra. Ez a helyi secrets fájlba kerül.[/size]')

            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Státusz hiba: ' + str(e)

    def test(self, kind):
        try:
            if kind == 'email':
                res = demo_core.send_test_email()
                self.refresh('Email teszt: ' + str(res.get('reason') or res.get('sent')))
                return
            if kind == 'openai':
                cfg = demo_core.openai_config_status()
                self.refresh('OpenAI ready: ' + str(cfg.get('ready')) + ' key: ' + str(cfg.get('has_key')))
                return
            res = demo_core.integration_test(kind)
            self.refresh(res.get('message', 'Teszt kész.'))
        except Exception as e:
            self.info.text = 'Teszt hiba: ' + str(e)



class DemoCoreAIScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(
            text='[b]AI SEGÉDLET / DÖNTÉSMAGYARÁZAT[/b]\n[size=14]Offline advisor: scanner + BBO + fee/tax + safety[/size]',
            markup=True,
            size_hint_y=None,
            height=76
        )
        root.add_widget(title)

        self.info = Label(text='AI advisor betöltés...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=170, spacing=8)
        b_run = Button(text='AI ELEMZÉS')
        b_scan = Button(text='SCANNER')
        b_trade = Button(text='TRADE LOGIKA')
        b_back = Button(text='VISSZA')

        b_run.bind(on_press=lambda x: self.run_ai())
        b_scan.bind(on_press=lambda x: self.manager.go_to('scanner'))
        b_trade.bind(on_press=lambda x: self.manager.go_to('trade_logic'))
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_run, b_scan, b_trade, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.run_ai()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def run_ai(self):
        try:
            st = demo_core.load_state()
            cfg = st.get('settings', {})
            sym = (cfg.get('watchlist') or ['BTCUSDT'])[0]
            res = demo_core.ai_advisor(sym)

            lines = []
            lines.append('[b]AI Advisor eredmény[/b]')
            lines.append('')
            lines.append(f"Symbol: {res.get('symbol')}")
            lines.append(f"Recommendation: [b]{res.get('recommendation')}[/b]")
            lines.append(f"Confidence: {res.get('confidence')}")
            lines.append(f"AI mode: {res.get('ai_mode')}")
            lines.append(f"Execution mode: {res.get('execution_mode')}")
            lines.append(f"Safe mode: {res.get('safe_mode')}")
            lines.append(f"Health: {res.get('health_status')}")
            lines.append('')

            sc = res.get('scanner') or {}
            lines.append('[b]Scanner:[/b]')
            lines.append(f"score={sc.get('score')} signal={sc.get('signal')} trend={sc.get('trend_pct')}% momentum={sc.get('momentum_pct')}%")
            lines.append('')

            tg = res.get('trade_guard') or {}
            lines.append('[b]Trade guard:[/b]')
            lines.append(f"allowed={tg.get('allowed')} spread={tg.get('spread_pct')}% bbo={tg.get('bbo_price')} limit={tg.get('limit_price')}")
            lines.append('')

            ft = res.get('fee_tax_example_1pct') or {}
            lines.append('[b]Fee/adó példa 1% profitnál:[/b]')
            lines.append(f"after_tax_pct={ft.get('after_tax_pct')} roundtrip_fee={ft.get('roundtrip_fee_pct')} tax_cut={ft.get('tax_cut_pct')}")
            lines.append('')

            lines.append('[b]Indoklás:[/b]')
            for r in res.get('reasons', []):
                lines.append('- ' + str(r))

            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'AI advisor hiba: ' + str(e)



class DemoCoreTradeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(
            text='[b]BINANCE TRADE LOGIKA[/b]\n[size=14]BBO / Spread / Slippage / Orderbook demo[/size]',
            markup=True,
            size_hint_y=None,
            height=72
        )
        root.add_widget(title)

        self.info = Label(text='Trade logika betöltés...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=170, spacing=8)
        b_check = Button(text='BBO CHECK')
        b_scan = Button(text='SCANNER')
        b_settings = Button(text='SETTINGS')
        b_back = Button(text='VISSZA')

        b_check.bind(on_press=lambda x: self.check())
        b_scan.bind(on_press=lambda x: self.manager.go_to('scanner'))
        b_settings.bind(on_press=lambda x: self.manager.go_to('demo_settings'))
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_check, b_scan, b_settings, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.check()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def check(self):
        try:
            st = demo_core.load_state()
            cfg = st.get('settings', {})
            watch = cfg.get('watchlist') or ['BTCUSDT']
            sym = watch[0]
            res = demo_core.trade_screen_check(sym, 'BUY', cfg)

            lines = []
            lines.append('[b]Binance Trade demo check[/b]')
            lines.append('')
            lines.append(f"Symbol: {res.get('symbol')}")
            lines.append(f"Side: {res.get('side')}")
            lines.append(f"Allowed: {res.get('allowed')}")
            lines.append(f"BBO price: {res.get('bbo_price')}")
            lines.append(f"Limit price: {res.get('limit_price')}")
            lines.append(f"Spread: {res.get('spread_pct')}%")
            lines.append(f"Bid ratio: {res.get('bid_ratio')}")
            lines.append(f"Ask ratio: {res.get('ask_ratio')}")
            lines.append('')
            lines.append('[b]Indoklás:[/b]')
            for r in res.get('reasons', []):
                lines.append('- ' + str(r))

            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Trade screen hiba: ' + str(e)



class DemoCoreFeeTaxScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(
            text='[b]FEE + ADÓZÁS MODUL[/b]\n[size=14]Bruttó / nettó / adózás utáni PnL[/size]',
            markup=True,
            size_hint_y=None,
            height=72
        )
        root.add_widget(title)

        self.info = Label(text='Betöltés...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        root.add_widget(self.info)

        btns = GridLayout(cols=2, size_hint_y=None, height=160, spacing=8)
        b_refresh = Button(text='FRISSÍTÉS')
        b_settings = Button(text='SETTINGS')
        b_back = Button(text='VISSZA')
        b_health = Button(text='HEALTHCHECK')

        b_refresh.bind(on_press=lambda x: self.refresh())
        b_settings.bind(on_press=lambda x: self.manager.go_to('demo_settings'))
        b_health.bind(on_press=lambda x: self.health())
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_refresh, b_settings, b_health, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self):
        try:
            st = demo_core.load_state()
            cfg = st.get('settings', {})
            pb = demo_core.portfolio_pnl_breakdown()
            lines = []
            lines.append('[b]Fee / adózás státusz[/b]')
            lines.append('')
            lines.append(f"Maker fee: {cfg.get('maker_fee_pct')}%")
            lines.append(f"Taker fee: {cfg.get('taker_fee_pct')}%")
            lines.append(f"Tax enabled: {cfg.get('tax_enabled')}")
            lines.append(f"Tax pct: {cfg.get('tax_pct')}%")
            lines.append('')
            lines.append(f"Gross realized PnL: {pb.get('gross_pnl')}")
            lines.append(f"Fee estimate: {pb.get('fee')}")
            lines.append(f"Net PnL: {pb.get('net_pnl')}")
            lines.append(f"Tax estimate: {pb.get('tax')}")
            lines.append(f"After tax PnL: {pb.get('after_tax_pnl')}")
            lines.append('')
            lines.append('[size=12]Megjegyzés: az adózás utáni profit csak tájékoztató becslés, nem adótanácsadás.[/size]')
            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Fee/tax hiba: ' + str(e)

    def health(self):
        try:
            demo_core.healthcheck()
            self.refresh()
        except Exception as e:
            self.info.text = 'Health hiba: ' + str(e)



class DemoCoreScannerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(
            text='[b]MULTI-SYMBOL SCANNER[/b]\n[size=14]Watchlist rangsor / edge score[/size]',
            markup=True,
            size_hint_y=None,
            height=72
        )
        root.add_widget(title)

        self.info = Label(text='Scanner betöltés...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=170, spacing=8)
        b_scan = Button(text='SCAN NOW')
        b_tick = Button(text='SCAN + TICK')
        b_settings = Button(text='SETTINGS')
        b_back = Button(text='VISSZA')

        b_scan.bind(on_press=lambda x: self.scan())
        b_tick.bind(on_press=lambda x: self.scan_tick())
        b_settings.bind(on_press=lambda x: self.manager.go_to('demo_settings'))
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_scan, b_tick, b_settings, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.scan()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def scan(self):
        try:
            res = demo_core.scan_symbols()
            lines = []
            lines.append('[b]Scanner status:[/b] OK')
            lines.append(f"[b]Symbols:[/b] {res.get('symbols_count')}")
            lines.append(f"[b]Top N:[/b] {res.get('top_n')}")
            lines.append('')

            rows = res.get('candidates') or []
            if not rows:
                lines.append('Nincs jelölt.')
            else:
                lines.append('[b]Top jelöltek:[/b]')
                for i, r in enumerate(rows, 1):
                    lines.append(
                        f"{i}. [b]{r.get('symbol')}[/b] | score={r.get('score')} | {r.get('signal')} | "
                        f"trend={r.get('trend_pct')}% | mom={r.get('momentum_pct')}% | vol={r.get('volatility_pct')}%"
                    )

            self.info.text = '\n'.join(lines)
        except Exception as e:
            self.info.text = 'Scanner hiba: ' + str(e)

    def scan_tick(self):
        try:
            demo_core.scan_symbols()
            demo_core.tick()
            self.scan()
        except Exception as e:
            self.info.text = 'Scan+Tick hiba: ' + str(e)



class DemoCoreAuditScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(text='[b]AUDIT NAPLÓ / JÓVÁHAGYÁSOK[/b]\\n[size=14]Demo Core eseménynapló[/size]', markup=True, size_hint_y=None, height=72)
        root.add_widget(title)

        self.info = Label(text='Betöltés...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=160, spacing=8)
        b_refresh = Button(text='FRISSÍTÉS')
        b_health = Button(text='HEALTHCHECK + LOG')
        b_clear = Button(text='AUDIT NAPLÓ NULLÁZÁS')
        b_back = Button(text='VISSZA')
        b_refresh.bind(on_press=lambda x: self.refresh())
        b_health.bind(on_press=lambda x: self.health_and_refresh())
        b_clear.bind(on_press=lambda x: self.clear_audit())
        b_back.bind(on_press=lambda x: self.go_back())
        for b in [b_refresh, b_health, b_clear, b_back]:
            btns.add_widget(b)
        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self):
        try:
            rows = demo_core.read_audit_log(80)
            lines = []
            lines.append('[b]Fájl:[/b] ' + str(demo_core.AUDIT_LOG))
            lines.append('')
            if not rows:
                lines.append('Még nincs audit napló.')
            else:
                lines.append('[b]Utolsó audit események:[/b]')
                for r in rows:
                    lines.append(r)
            self.info.text = '\\n'.join(lines)
        except Exception as e:
            self.info.text = 'Audit hiba: ' + str(e)

    def health_and_refresh(self):
        try:
            demo_core.healthcheck()
            self.refresh()
        except Exception as e:
            self.info.text = 'Health/audit hiba: ' + str(e)

    def clear_audit(self):
        try:
            if demo_core.os.path.exists(demo_core.AUDIT_LOG):
                demo_core.os.remove(demo_core.AUDIT_LOG)
            self.info.text = '[b]OK:[/b] Audit napló törölve.'
        except Exception as e:
            self.info.text = 'Audit törlés hiba: ' + str(e)


class DemoCoreLogsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(text='[b]DEMO TRADE NAPLÓ / EXPORT[/b]\\n[size=14]demo_core_trades.csv megjelenítés[/size]', markup=True, size_hint_y=None, height=72)
        root.add_widget(title)

        self.info = Label(text='Betöltés...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=170, spacing=8)
        b_refresh = Button(text='FRISSÍTÉS')
        b_tick = Button(text='TICK + FRISSÍTÉS')
        b_clear = Button(text='NAPLÓ NULLÁZÁS')
        b_back = Button(text='VISSZA')

        b_refresh.bind(on_press=lambda x: self.refresh())
        b_tick.bind(on_press=lambda x: self.tick_and_refresh())
        b_clear.bind(on_press=lambda x: self.clear_log())
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_refresh, b_tick, b_clear, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def refresh(self):
        try:
            path = demo_core.TRADE_LOG
            lines = []
            lines.append('[b]Fájl:[/b] ' + str(path))
            lines.append('')

            if not demo_core.os.path.exists(path):
                lines.append('Még nincs trade napló.')
                self.info.text = '\\n'.join(lines)
                return

            with open(path, 'r', encoding='utf-8') as f:
                rows = [x.strip() for x in f.readlines() if x.strip()]

            if not rows:
                lines.append('Üres napló.')
            else:
                lines.append('[b]Utolsó trade-ek:[/b]')
                for row in rows[-25:]:
                    lines.append(row)

            self.info.text = '\\n'.join(lines)
        except Exception as e:
            self.info.text = 'Napló hiba: ' + str(e)

    def tick_and_refresh(self):
        try:
            demo_core.tick()
            self.refresh()
        except Exception as e:
            self.info.text = 'Tick/log hiba: ' + str(e)

    def clear_log(self):
        try:
            path = demo_core.TRADE_LOG
            if demo_core.os.path.exists(path):
                demo_core.os.remove(path)
            self.info.text = '[b]OK:[/b] Demo trade napló törölve.'
        except Exception as e:
            self.info.text = 'Napló törlés hiba: ' + str(e)


class DemoCoreSettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(text='[b]DEMO CORE SETTINGS[/b]\\n[size=14]Demo motor paraméterek[/size]', markup=True, size_hint_y=None, height=72)
        root.add_widget(title)

        grid = GridLayout(cols=2, spacing=8, size_hint_y=None, height=360)
        self.inputs = {}

        fields = [
            ('risk_pct', 'Risk / trade %'),
            ('max_positions', 'Max coin / pozíció'),
            ('min_profit_pct', 'Min profit %'),
            ('stop_loss_pct', 'Stop loss %'),
            ('trailing_drop_pct', 'Trailing drop %'),
            ('watchlist', 'Watchlist vesszővel'),
            ('execution_mode', 'Execution mode AUTO/MANUAL/OFF'),
            ('hold_profit_minutes', 'Hold profit minutes'),
            ('time_in_trend_minutes_max', 'Max time in trend min'),
            ('cooldown_after_exit_min', 'Cooldown after exit min'),
            ('profit_erosion_guard_pct', 'Profit erosion guard %'),
            ('scanner_enabled', 'Scanner enabled true/false'),
            ('scanner_top_n', 'Scanner top N'),
            ('min_edge_score_open', 'Min edge open'),
            ('min_edge_score_keep', 'Min edge keep'),
            ('max_scan_symbols', 'Max scan symbols'),
            ('maker_fee_pct', 'Maker fee %'),
            ('taker_fee_pct', 'Taker fee %'),
            ('tax_enabled', 'Tax enabled true/false'),
            ('tax_pct', 'HU tax %'),
            ('min_after_tax_profit_pct', 'Min after tax profit %'),
            ('order_type', 'Order type LIMIT_BBO'),
            ('use_bbo', 'Use BBO true/false'),
            ('max_spread_pct', 'Max spread %'),
            ('slippage_buffer_pct', 'Slippage buffer %'),
            ('min_orderbook_imbalance', 'Min orderbook imbalance'),
            ('tp_sl_enabled', 'TP/SL enabled true/false'),
            ('take_profit_pct', 'Take profit %'),
            ('ai_advisor_enabled', 'AI advisor enabled true/false'),
            ('ai_mode', 'AI mode OFFLINE/API'),
            ('ai_min_confidence', 'AI min confidence'),
            ('ai_allow_auto_trade', 'AI allow auto trade true/false'),
            ('email_notify_enabled', 'Email notify enabled true/false'),
            ('email_on_buy', 'Email on BUY true/false'),
            ('email_on_sell', 'Email on SELL true/false'),
            ('email_on_error', 'Email on ERROR true/false'),
            ('email_on_health_warning', 'Email on health warning true/false'),
            ('openai_api_enabled', 'OpenAI API enabled true/false'),
            ('openai_model', 'OpenAI model'),
            ('openai_timeout_sec', 'OpenAI timeout sec'),
            ('live_mode_enabled', 'Live mode enabled true/false'),
            ('live_require_confirm', 'Live require confirm true/false'),
            ('live_allow_buy', 'Live allow BUY true/false'),
            ('live_allow_sell', 'Live allow SELL true/false'),
            ('live_max_order_usdt', 'Live max order USDT'),
            ('live_warning_ack', 'Live warning ACK true/false'),
            ('backtest_symbol', 'Backtest symbol'),
            ('backtest_limit', 'Backtest limit'),
            ('backtest_start_balance', 'Backtest start balance'),
            ('backtest_risk_pct', 'Backtest risk %'),
            ('backtest_fee_pct', 'Backtest fee %'),
            ('schedules_enabled', 'Schedules enabled true/false'),
            ('snapshot_enabled', 'Snapshot enabled true/false'),
            ('snapshot_time', 'Snapshot time HH:MM'),
            ('price_trigger_enabled', 'Price trigger enabled true/false'),
            ('price_trigger_symbol', 'Price trigger symbol'),
            ('price_trigger_above', 'Price trigger above'),
            ('price_trigger_below', 'Price trigger below'),
            ('launchpool_enabled', 'Launchpool enabled true/false'),
            ('launchpool_min_apr', 'Launchpool min APR'),
            ('launchpool_watchlist', 'Launchpool watchlist'),
            ('launchpool_scan_interval_min', 'Launchpool scan interval min'),
            ('sync_enabled', 'Sync enabled true/false'),
            ('sync_primary_device', 'Sync primary PHONE/PC'),
            ('drive_sync_folder', 'Drive sync folder'),
            ('pc_sync_folder', 'PC sync folder'),
            ('auto_backup_on_start', 'Auto backup on start true/false'),
            ('first_run_done', 'First run done true/false'),
            ('admin_timeout_sec', 'Admin timeout sec'),
            ('patch_manager_enabled', 'Patch manager enabled true/false'),
            ('patch_require_admin', 'Patch require admin true/false'),
            ('approval_required_for_manual', 'Approval required manual true/false'),
            ('approval_required_for_live', 'Approval required live true/false'),
            ('dry_run_executor_enabled', 'Dry-run executor enabled true/false'),
            ('live_executor_enabled', 'Live executor enabled true/false'),
            ('live_hard_stop_enabled', 'Live hard stop enabled true/false'),
            ('live_require_admin_active', 'Live require admin active true/false'),
            ('live_require_approval', 'Live require approval true/false'),
            ('live_require_positive_after_tax', 'Live require positive after tax true/false'),
            ('live_min_after_tax_profit_pct', 'Live min after tax profit %'),
            ('live_max_order_usdt_hard', 'Live max order hard USDT'),
            ('live_block_if_health_warning', 'Live block if health warning true/false'),
            ('live_block_if_spread_bad', 'Live block if spread bad true/false'),
            ('live_block_if_ai_hold', 'Live block if AI hold true/false'),
            ('binance_account_check_enabled', 'Binance account check enabled true/false'),
            ('binance_test_order_enabled', 'Binance test order enabled true/false'),
            ('binance_test_order_symbol', 'Binance test order symbol'),
            ('binance_test_order_side', 'Binance test order side'),
            ('binance_test_order_type', 'Binance test order type'),
            ('binance_test_order_quote_qty', 'Binance test order quote qty'),
            ('binance_recv_window', 'Binance recvWindow'),
            ('binance_base_url', 'Binance base URL'),
            ('binance_signed_readonly_enabled', 'Binance signed readonly enabled true/false'),
            ('binance_account_read_enabled', 'Binance account read enabled true/false'),
            ('binance_real_account_get_enabled', 'Binance real account GET enabled true/false'),
            ('binance_http_timeout_sec', 'Binance HTTP timeout sec'),
            ('binance_balance_preview_assets', 'Binance balance preview assets'),
        ]

        for key, label in fields:
            grid.add_widget(Label(text=label))
            ti = TextInput(text='', multiline=False)
            self.inputs[key] = ti
            grid.add_widget(ti)

        root.add_widget(grid)

        self.info = Label(text='Beállítások betöltése...', markup=True, halign='left', valign='top')
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        root.add_widget(self.info)

        btns = GridLayout(cols=2, size_hint_y=None, height=180, spacing=8)
        b_load = Button(text='BETÖLTÉS')
        b_save = Button(text='MENTÉS')
        b_reset = Button(text='ALAPÉRTÉK')
        b_back = Button(text='VISSZA')

        b_load.bind(on_press=lambda x: self.load_values())
        b_save.bind(on_press=lambda x: self.save_values())
        b_reset.bind(on_press=lambda x: self.reset_defaults())
        b_back.bind(on_press=lambda x: self.go_back())

        for b in [b_load, b_save, b_reset, b_back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.load_values()

    def go_back(self):
        try:
            self.manager.go_back()
        except Exception:
            self.manager.current = 'home'

    def load_values(self):
        try:
            st = demo_core.load_state()
            cfg = st.get('settings', {})
            for key, ti in self.inputs.items():
                val = cfg.get(key, '')
                if isinstance(val, list):
                    ti.text = ','.join(val)
                else:
                    ti.text = str(val)
            self.info.text = '[b]OK:[/b] Beállítások betöltve.'
        except Exception as e:
            self.info.text = '[b]HIBA:[/b] Betöltés sikertelen: ' + str(e)

    def save_values(self):
        try:
            st = demo_core.load_state()
            cfg = st.setdefault('settings', {})

            cfg['risk_pct'] = float(self.inputs['risk_pct'].text.replace(',', '.'))
            cfg['max_positions'] = int(float(self.inputs['max_positions'].text.replace(',', '.')))
            cfg['min_profit_pct'] = float(self.inputs['min_profit_pct'].text.replace(',', '.'))
            cfg['stop_loss_pct'] = float(self.inputs['stop_loss_pct'].text.replace(',', '.'))
            cfg['trailing_drop_pct'] = float(self.inputs['trailing_drop_pct'].text.replace(',', '.'))

            raw_watch = self.inputs['watchlist'].text.strip()
            watch = []
            for item in raw_watch.split(','):
                sym = item.strip().upper()
                if sym:
                    if not sym.endswith('USDT'):
                        sym = sym + 'USDT'
                    watch.append(sym)
            cfg['watchlist'] = watch or ['BTCUSDT', 'ETHUSDT', 'DOGEUSDT']
            mode = self.inputs['execution_mode'].text.strip().upper() or 'AUTO'
            if mode not in ['AUTO', 'MANUAL', 'OFF']:
                mode = 'MANUAL'
            cfg['execution_mode'] = mode
            cfg['hold_profit_minutes'] = float(self.inputs['hold_profit_minutes'].text.replace(',', '.'))
            cfg['time_in_trend_minutes_max'] = float(self.inputs['time_in_trend_minutes_max'].text.replace(',', '.'))
            cfg['cooldown_after_exit_min'] = float(self.inputs['cooldown_after_exit_min'].text.replace(',', '.'))
            cfg['profit_erosion_guard_pct'] = float(self.inputs['profit_erosion_guard_pct'].text.replace(',', '.'))
            cfg['scanner_enabled'] = self.inputs['scanner_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['scanner_top_n'] = int(float(self.inputs['scanner_top_n'].text.replace(',', '.')))
            cfg['min_edge_score_open'] = float(self.inputs['min_edge_score_open'].text.replace(',', '.'))
            cfg['min_edge_score_keep'] = float(self.inputs['min_edge_score_keep'].text.replace(',', '.'))
            cfg['max_scan_symbols'] = int(float(self.inputs['max_scan_symbols'].text.replace(',', '.')))
            cfg['maker_fee_pct'] = float(self.inputs['maker_fee_pct'].text.replace(',', '.'))
            cfg['taker_fee_pct'] = float(self.inputs['taker_fee_pct'].text.replace(',', '.'))
            cfg['tax_enabled'] = self.inputs['tax_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['tax_pct'] = float(self.inputs['tax_pct'].text.replace(',', '.'))
            cfg['min_after_tax_profit_pct'] = float(self.inputs['min_after_tax_profit_pct'].text.replace(',', '.'))
            cfg['order_type'] = self.inputs['order_type'].text.strip().upper() or 'LIMIT_BBO'
            cfg['use_bbo'] = self.inputs['use_bbo'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['max_spread_pct'] = float(self.inputs['max_spread_pct'].text.replace(',', '.'))
            cfg['slippage_buffer_pct'] = float(self.inputs['slippage_buffer_pct'].text.replace(',', '.'))
            cfg['min_orderbook_imbalance'] = float(self.inputs['min_orderbook_imbalance'].text.replace(',', '.'))
            cfg['tp_sl_enabled'] = self.inputs['tp_sl_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['take_profit_pct'] = float(self.inputs['take_profit_pct'].text.replace(',', '.'))
            cfg['ai_advisor_enabled'] = self.inputs['ai_advisor_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['ai_mode'] = self.inputs['ai_mode'].text.strip().upper() or 'OFFLINE'
            cfg['ai_min_confidence'] = float(self.inputs['ai_min_confidence'].text.replace(',', '.'))
            cfg['ai_allow_auto_trade'] = self.inputs['ai_allow_auto_trade'].text.strip().lower() in ['1', 'true', 'igen', 'yes', 'on']
            cfg['email_notify_enabled'] = self.inputs['email_notify_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['email_on_buy'] = self.inputs['email_on_buy'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['email_on_sell'] = self.inputs['email_on_sell'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['email_on_error'] = self.inputs['email_on_error'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['email_on_health_warning'] = self.inputs['email_on_health_warning'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['openai_api_enabled'] = self.inputs['openai_api_enabled'].text.strip().lower() in ['1', 'true', 'igen', 'yes', 'on']
            cfg['openai_model'] = self.inputs['openai_model'].text.strip() or 'gpt-5-mini'
            cfg['openai_timeout_sec'] = int(float(self.inputs['openai_timeout_sec'].text.replace(',', '.')))
            cfg['live_mode_enabled'] = self.inputs['live_mode_enabled'].text.strip().lower() in ['1', 'true', 'igen', 'yes', 'on']
            cfg['live_require_confirm'] = self.inputs['live_require_confirm'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['live_allow_buy'] = self.inputs['live_allow_buy'].text.strip().lower() in ['1', 'true', 'igen', 'yes', 'on']
            cfg['live_allow_sell'] = self.inputs['live_allow_sell'].text.strip().lower() in ['1', 'true', 'igen', 'yes', 'on']
            cfg['live_max_order_usdt'] = float(self.inputs['live_max_order_usdt'].text.replace(',', '.'))
            cfg['live_warning_ack'] = self.inputs['live_warning_ack'].text.strip().lower() in ['1', 'true', 'igen', 'yes', 'on']
            cfg['backtest_symbol'] = self.inputs['backtest_symbol'].text.strip().upper() or 'BTCUSDT'
            cfg['backtest_limit'] = int(float(self.inputs['backtest_limit'].text.replace(',', '.')))
            cfg['backtest_start_balance'] = float(self.inputs['backtest_start_balance'].text.replace(',', '.'))
            cfg['backtest_risk_pct'] = float(self.inputs['backtest_risk_pct'].text.replace(',', '.'))
            cfg['backtest_fee_pct'] = float(self.inputs['backtest_fee_pct'].text.replace(',', '.'))
            cfg['schedules_enabled'] = self.inputs['schedules_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['snapshot_enabled'] = self.inputs['snapshot_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['snapshot_time'] = self.inputs['snapshot_time'].text.strip() or '08:00'
            cfg['price_trigger_enabled'] = self.inputs['price_trigger_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['price_trigger_symbol'] = self.inputs['price_trigger_symbol'].text.strip().upper() or 'BTCUSDT'
            cfg['price_trigger_above'] = float(self.inputs['price_trigger_above'].text.replace(',', '.'))
            cfg['price_trigger_below'] = float(self.inputs['price_trigger_below'].text.replace(',', '.'))
            cfg['launchpool_enabled'] = self.inputs['launchpool_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['launchpool_min_apr'] = float(self.inputs['launchpool_min_apr'].text.replace(',', '.'))
            cfg['launchpool_watchlist'] = self.inputs['launchpool_watchlist'].text.strip() or 'BNB,FDUSD,USDT'
            cfg['launchpool_scan_interval_min'] = int(float(self.inputs['launchpool_scan_interval_min'].text.replace(',', '.')))
            cfg['sync_enabled'] = self.inputs['sync_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['sync_primary_device'] = self.inputs['sync_primary_device'].text.strip().upper() or 'PHONE'
            cfg['drive_sync_folder'] = self.inputs['drive_sync_folder'].text.strip() or 'AutobotBackups'
            cfg['pc_sync_folder'] = self.inputs['pc_sync_folder'].text.strip() or 'PCSync'
            cfg['auto_backup_on_start'] = self.inputs['auto_backup_on_start'].text.strip().lower() in ['1', 'true', 'igen', 'yes', 'on']
            cfg['first_run_done'] = self.inputs['first_run_done'].text.strip().lower() in ['1', 'true', 'igen', 'yes', 'on']
            cfg['admin_timeout_sec'] = int(float(self.inputs['admin_timeout_sec'].text.replace(',', '.')))
            cfg['patch_manager_enabled'] = self.inputs['patch_manager_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['patch_require_admin'] = self.inputs['patch_require_admin'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['approval_required_for_manual'] = self.inputs['approval_required_for_manual'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['approval_required_for_live'] = self.inputs['approval_required_for_live'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['dry_run_executor_enabled'] = self.inputs['dry_run_executor_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['live_executor_enabled'] = self.inputs['live_executor_enabled'].text.strip().lower() in ['1', 'true', 'igen', 'yes', 'on']
            cfg['live_hard_stop_enabled'] = self.inputs['live_hard_stop_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['live_require_admin_active'] = self.inputs['live_require_admin_active'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['live_require_approval'] = self.inputs['live_require_approval'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['live_require_positive_after_tax'] = self.inputs['live_require_positive_after_tax'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['live_min_after_tax_profit_pct'] = float(self.inputs['live_min_after_tax_profit_pct'].text.replace(',', '.'))
            cfg['live_max_order_usdt_hard'] = float(self.inputs['live_max_order_usdt_hard'].text.replace(',', '.'))
            cfg['live_block_if_health_warning'] = self.inputs['live_block_if_health_warning'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['live_block_if_spread_bad'] = self.inputs['live_block_if_spread_bad'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['live_block_if_ai_hold'] = self.inputs['live_block_if_ai_hold'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['binance_account_check_enabled'] = self.inputs['binance_account_check_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['binance_test_order_enabled'] = self.inputs['binance_test_order_enabled'].text.strip().lower() not in ['0', 'false', 'nem', 'no', 'off']
            cfg['binance_test_order_symbol'] = self.inputs['binance_test_order_symbol'].text.strip().upper() or 'BTCUSDT'
            cfg['binance_test_order_side'] = self.inputs['binance_test_order_side'].text.strip().upper() or 'BUY'
            cfg['binance_test_order_type'] = self.inputs['binance_test_order_type'].text.strip().upper() or 'MARKET'
            cfg['binance_test_order_quote_qty'] = float(self.inputs['binance_test_order_quote_qty'].text.replace(',', '.'))
            cfg['binance_recv_window'] = int(float(self.inputs['binance_recv_window'].text.replace(',', '.')))
            cfg['binance_base_url'] = self.inputs['binance_base_url'].text.strip() or 'https://api.binance.com'
            cfg['binance_signed_readonly_enabled'] = self.inputs['binance_signed_readonly_enabled'].text.strip().lower() in ['1', 'true', 'igen', 'yes', 'on']
            cfg['binance_account_read_enabled'] = self.inputs['binance_account_read_enabled'].text.strip().lower() in ['1', 'true', 'igen', 'yes', 'on']
            cfg['binance_real_account_get_enabled'] = self.inputs['binance_real_account_get_enabled'].text.strip().lower() in ['1', 'true', 'igen', 'yes', 'on']
            cfg['binance_http_timeout_sec'] = float(self.inputs['binance_http_timeout_sec'].text.replace(',', '.'))
            cfg['binance_balance_preview_assets'] = self.inputs['binance_balance_preview_assets'].text.strip() or 'USDT,USDC,BTC,ETH,BNB,DOGE'

            st['last_action'] = 'Demo settings mentve'
            demo_core.save_state(st)
            self.info.text = '[b]OK:[/b] Mentve. Új beállítások aktívak a következő ticknél.'
        except Exception as e:
            self.info.text = '[b]HIBA:[/b] Mentés sikertelen: ' + str(e)

    def reset_defaults(self):
        try:
            st = demo_core.load_state()
            st['settings'] = dict(demo_core.DEFAULT_STATE['settings'])
            st['last_action'] = 'Demo settings alapértékre állítva'
            demo_core.save_state(st)
            self.load_values()
            self.info.text = '[b]OK:[/b] Alapértékek visszaállítva.'
        except Exception as e:
            self.info.text = '[b]HIBA:[/b] Reset sikertelen: ' + str(e)


class DemoCoreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._demo_core_auto_event = None
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        title = Label(text='[b]DEMO CORE ENGINE[/b]\n[size=14]Demo motor / pozíciók / PnL[/size]', markup=True, size_hint_y=None, height=72)
        root.add_widget(title)

        self.kpi = GridLayout(cols=2, spacing=8, size_hint_y=None, height=140)
        self.lbl_balance = Label(text='[b]Balance[/b]\n-', markup=True)
        self.lbl_equity = Label(text='[b]Equity[/b]\n-', markup=True)
        self.lbl_pnl = Label(text='[b]Realized PnL[/b]\n-', markup=True)
        self.lbl_positions = Label(text='[b]Open Positions[/b]\n-', markup=True)
        for w in [self.lbl_balance, self.lbl_equity, self.lbl_pnl, self.lbl_positions]:
            self.kpi.add_widget(w)
        root.add_widget(self.kpi)

        self.info = Label(text='Betöltés...', halign='left', valign='top', markup=True)
        self.info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        scroll = ScrollView()
        scroll.add_widget(self.info)
        root.add_widget(scroll)

        btns = GridLayout(cols=2, size_hint_y=None, height=520, spacing=8)
        buttons = [
            ('FRISSÍTÉS', self.refresh),
            ('TICK / KÉZI FUTTATÁS', self.do_tick),
            ('START', self.do_start),
            ('STOP', self.do_stop),
            ('DEMO RESET 100 USDC', self.do_reset),
            ('PANIC STOP / SAFE MODE', self.do_panic_stop),
            ('SAFE MODE KI', self.do_safe_mode_off),
            ('VISSZA', self.go_back),
        ]
        for txt, fn in buttons:
            b = Button(text=txt)
            b.bind(on_press=lambda x, f=fn: f())
            btns.add_widget(b)
        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh()

    def go_back(self):
        self.manager.go_back()

    def update_kpi(self, st):
        try:
            eq = demo_core.equity(st)
        except Exception:
            eq = 0.0
        bal = float(st.get('balance', 0.0))
        pnl = float(st.get('realized_pnl', 0.0))
        positions = st.get('positions', {})
        base = st.get('base', 'USDC')
        self.lbl_balance.text = f'[b]Balance[/b]\n{bal:.4f} {base}'
        self.lbl_equity.text = f'[b]Equity[/b]\n{eq:.4f} {base}'
        self.lbl_pnl.text = f'[b]Realized PnL[/b]\n{pnl:.4f}'
        self.lbl_positions.text = f'[b]Open Positions[/b]\n{len(positions)}'

    def fmt_state(self, st, extra=''):
        lines = []
        lines.append(f'[b]Állapot:[/b] {"FUT" if st.get("running") else "ÁLL"}')
        lines.append(f'[b]Safe mode:[/b] {"AKTÍV" if st.get("safe_mode") else "KI"}')
        lines.append(f'[b]Execution mode:[/b] {st.get("settings", {}).get("execution_mode", "AUTO")}')
        lines.append(f'[b]Utolsó művelet:[/b] {st.get("last_action", "-")}')
        lines.append('')
        lines.append('[b]Nyitott pozíciók:[/b]')
        positions = st.get('positions', {})
        if not positions:
            lines.append('Nincs nyitott pozíció.')
        else:
            for sym, pos in positions.items():
                qty = float(pos.get('qty', 0))
                avg = float(pos.get('avg', 0))
                peak = float(pos.get('peak', 0))
                try:
                    now = demo_core.price(sym)
                    pnl_pct = ((now - avg) / avg) * 100 if avg else 0
                    lines.append(f'[b]{sym}[/b] qty={qty:.8f} avg={avg:.4f} now={now:.4f} peak={peak:.4f} PnL={pnl_pct:.2f}%')
                except Exception:
                    lines.append(f'[b]{sym}[/b] qty={qty:.8f} avg={avg:.4f} peak={peak:.4f}')
        settings = st.get('settings', {})
        lines.append('')
        lines.append('[b]Beállítások:[/b]')
        lines.append(f'Risk/trade: {settings.get("risk_pct")}%')
        lines.append(f'Max positions: {settings.get("max_positions")}')
        lines.append(f'Min profit: {settings.get("min_profit_pct")}%')
        lines.append(f'Watchlist: {", ".join(settings.get("watchlist", []))}')
        lines.append(f'Hold profit: {settings.get("hold_profit_minutes")} min')
        lines.append(f'Max trend time: {settings.get("time_in_trend_minutes_max")} min')
        lines.append(f'Exit cooldown: {settings.get("cooldown_after_exit_min")} min')
        lines.append(f'Profit erosion guard: {settings.get("profit_erosion_guard_pct")}%')
        if extra:
            lines.append('')
            lines.append('[b]Most futott:[/b]')
            lines.append(str(extra))
        return '\n'.join(lines)

    def refresh(self):
        try:
            st = demo_core.load_state()
            self.update_kpi(st)
            self.info.text = self.fmt_state(st)
        except Exception as e:
            self.info.text = 'Demo core hiba: ' + str(e)


    def on_leave(self):
        self.stop_auto_tick()

    def stop_auto_tick(self):
        try:
            if self._demo_core_auto_event is not None:
                self._demo_core_auto_event.cancel()
        except Exception:
            pass
        self._demo_core_auto_event = None

    def auto_tick(self, dt):
        try:
            st = demo_core.load_state()
            if not st.get("running"):
                self.stop_auto_tick()
                return False
            res = demo_core.tick()
            st = demo_core.load_state()
            self.update_kpi(st)
            self.info.text = self.fmt_state(st, res.get("action", res))
            return True
        except Exception as e:
            self.info.text = "Auto tick hiba: " + str(e)
            self.stop_auto_tick()
            return False

    def do_tick(self):
        try:
            res = demo_core.tick()
            st = demo_core.load_state()
            self.update_kpi(st)
            self.info.text = self.fmt_state(st, res.get('action', res))
        except Exception as e:
            self.info.text = 'Tick hiba: ' + str(e)


    def do_start(self):
        try:
            st = demo_core.load_state()
            st["running"] = True
            st["last_action"] = "Demo core START - auto tick aktív"
            demo_core.save_state(st)

            self.stop_auto_tick()
            self._demo_core_auto_event = Clock.schedule_interval(self.auto_tick, 15)

            self.update_kpi(st)
            self.info.text = self.fmt_state(st, "START - automatikus tick 15 mp")
        except Exception as e:
            self.info.text = "Start hiba: " + str(e)



    def do_stop(self):
        try:
            self.stop_auto_tick()
            st = demo_core.load_state()
            st["running"] = False
            st["last_action"] = "Demo core STOP - auto tick leállítva"
            demo_core.save_state(st)
            self.update_kpi(st)
            self.info.text = self.fmt_state(st, "STOP")
        except Exception as e:
            self.info.text = "Stop hiba: " + str(e)



    def do_panic_stop(self):
        try:
            self.stop_auto_tick()
            res = demo_core.panic_stop()
            st = demo_core.load_state()
            self.update_kpi(st)
            self.info.text = self.fmt_state(st, res.get("action", "PANIC STOP"))
        except Exception as e:
            self.info.text = "Panic stop hiba: " + str(e)


    def do_safe_mode_off(self):
        try:
            res = demo_core.safe_mode_off()
            st = demo_core.load_state()
            self.update_kpi(st)
            self.info.text = self.fmt_state(st, res.get("action", "Safe mode kikapcsolva"))
        except Exception as e:
            self.info.text = "Safe mode kikapcsolás hiba: " + str(e)


    def open_integrations(self):
        try:
            self.manager.go_to("integrations")
        except Exception:
            self.manager.current = "integrations"

    def open_binance_readonly_real(self):
        try:
            self.manager.go_to("binance_readonly_real")
        except Exception:
            self.manager.current = "binance_readonly_real"

    def open_binance_signed(self):
        try:
            self.manager.go_to("binance_signed")
        except Exception:
            self.manager.current = "binance_signed"

    def open_binance_account(self):
        try:
            self.manager.go_to("binance_account")
        except Exception:
            self.manager.current = "binance_account"

    def open_live_gate(self):
        try:
            self.manager.go_to("live_gate")
        except Exception:
            self.manager.current = "live_gate"

    def open_approval_executor(self):
        try:
            self.manager.go_to("approval_executor")
        except Exception:
            self.manager.current = "approval_executor"

    def open_admin(self):
        try:
            self.manager.go_to("admin")
        except Exception:
            self.manager.current = "admin"

    def open_patch_manager(self):
        try:
            self.manager.go_to("patch_manager")
        except Exception:
            self.manager.current = "patch_manager"

    def open_first_run(self):
        try:
            self.manager.go_to("first_run")
        except Exception:
            self.manager.current = "first_run"

    def open_sync(self):
        try:
            self.manager.go_to("sync")
        except Exception:
            self.manager.current = "sync"

    def open_package(self):
        try:
            self.manager.go_to("package")
        except Exception:
            self.manager.current = "package"

    def open_schedules(self):
        try:
            self.manager.go_to("schedules")
        except Exception:
            self.manager.current = "schedules"

    def open_launchpool(self):
        try:
            self.manager.go_to("launchpool")
        except Exception:
            self.manager.current = "launchpool"

    def open_backtest(self):
        try:
            self.manager.go_to("backtest")
        except Exception:
            self.manager.current = "backtest"

    def open_diagnostics(self):
        try:
            self.manager.go_to("diagnostics")
        except Exception:
            self.manager.current = "diagnostics"

    def open_binance_live(self):
        try:
            self.manager.go_to("binance_live")
        except Exception:
            self.manager.current = "binance_live"

    def open_secrets(self):
        try:
            self.manager.go_to("secrets")
        except Exception:
            self.manager.current = "secrets"

    def open_ai_advisor(self):
        try:
            self.manager.go_to("ai_advisor")
        except Exception:
            self.manager.current = "ai_advisor"

    def open_trade_logic(self):
        try:
            self.manager.go_to("trade_logic")
        except Exception:
            self.manager.current = "trade_logic"

    def open_fee_tax(self):
        try:
            self.manager.go_to("fee_tax")
        except Exception:
            self.manager.current = "fee_tax"

    def open_scanner(self):
        try:
            self.manager.go_to("scanner")
        except Exception:
            self.manager.current = "scanner"

    def do_healthcheck(self):
        try:
            res = demo_core.healthcheck()
            lines = []
            lines.append("[b]HEALTHCHECK / HEARTBEAT[/b]")
            lines.append("")
            lines.append(f"[b]Status:[/b] {res.get('status')}")
            lines.append(f"[b]Running:[/b] {res.get('running')}")
            lines.append(f"[b]Safe mode:[/b] {res.get('safe_mode')}")
            lines.append(f"[b]Positions:[/b] {res.get('positions_count')}")
            lines.append(f"[b]Balance:[/b] {res.get('balance')}")
            lines.append(f"[b]Equity:[/b] {res.get('equity'):.4f}")
            lines.append(f"[b]Realized PnL:[/b] {res.get('realized_pnl')}")
            lines.append(f"[b]Trade log:[/b] {'van' if res.get('trade_log_exists') else 'nincs'}")
            lines.append(f"[b]Last tick age sec:[/b] {res.get('last_tick_age_sec')}")
            lines.append(f"[b]Last action:[/b] {res.get('last_action')}")

            warns = res.get("warnings") or []
            if warns:
                lines.append("")
                lines.append("[b]Figyelmeztetések:[/b]")
                for w in warns:
                    lines.append("- " + str(w))
            else:
                lines.append("")
                lines.append("[b]Nincs aktív figyelmeztetés.[/b]")

            st = demo_core.load_state()
            self.update_kpi(st)
            self.info.text = "\n".join(lines)
        except Exception as e:
            self.info.text = "Healthcheck hiba: " + str(e)


    def set_mode_ui(self, mode):
        try:
            res = demo_core.set_execution_mode(mode)
            st = demo_core.load_state()
            self.update_kpi(st)
            self.info.text = self.fmt_state(st, "Execution mode: " + res.get("mode", mode))
        except Exception as e:
            self.info.text = "Mode hiba: " + str(e)

    def mode_auto(self):
        self.set_mode_ui("AUTO")

    def mode_manual(self):
        self.set_mode_ui("MANUAL")

    def mode_off(self):
        self.set_mode_ui("OFF")

    def do_reset(self):
        try:
            st = demo_core.reset_demo(100.0)
            self.update_kpi(st)
            self.info.text = self.fmt_state(st, 'RESET 100 USDC')
        except Exception as e:
            self.info.text = 'Reset hiba: ' + str(e)


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
        sm = HistoryScreenManager()
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
        sm.add_widget(DemoCoreSettingsScreen(name="demo_settings"))
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
        sm.add_widget(DemoCoreLogsScreen(name="demo_logs"))
        sm.add_widget(DemoCoreAuditScreen(name="audit_log"))
        sm.add_widget(DemoCoreScannerScreen(name="scanner"))
        sm.add_widget(DemoCoreFeeTaxScreen(name="fee_tax"))
        sm.add_widget(DemoCoreTradeScreen(name="trade_logic"))
        sm.add_widget(DemoCoreAIScreen(name="ai_advisor"))
        sm.add_widget(DemoCoreSecretsScreen(name="secrets"))
        sm.add_widget(DemoCoreBinanceLiveScreen(name="binance_live"))
        sm.add_widget(DemoCoreBacktestScreen(name="backtest"))
        sm.add_widget(DemoCoreDiagnosticsScreen(name="diagnostics"))
        sm.add_widget(DemoCoreSchedulesScreen(name="schedules"))
        sm.add_widget(DemoCoreLaunchpoolScreen(name="launchpool"))
        sm.add_widget(DemoCorePackageScreen(name="package"))
        sm.add_widget(DemoCoreSyncScreen(name="sync"))
        sm.add_widget(DemoCoreFirstRunScreen(name="first_run"))
        sm.add_widget(DemoCoreAdminScreen(name="admin"))
        sm.add_widget(DemoCorePatchManagerScreen(name="patch_manager"))
        sm.add_widget(DemoCoreApprovalExecutorScreen(name="approval_executor"))
        sm.add_widget(DemoCoreLiveGateScreen(name="live_gate"))
        sm.add_widget(DemoCoreBinanceAccountScreen(name="binance_account"))
        sm.add_widget(DemoCoreBinanceSignedScreen(name="binance_signed"))
        sm.add_widget(DemoCoreBinanceReadOnlyRealScreen(name="binance_readonly_real"))
        sm.add_widget(DemoCoreIntegrationOverviewScreen(name="integrations"))
        return sm

if __name__ == "__main__":
    AppMain().run()
