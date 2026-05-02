from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
import requests, json, os, random

STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE, "r", encoding="utf-8"))
        except Exception:
            pass
    return {"mode":"demo","balance":100.0,"profit":0.0,"running":False}

def save_state(s):
    json.dump(s, open(STATE_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

class Card(BoxLayout):
    def __init__(self, bg=(0.1,0.1,0.1,1), **kw):
        super().__init__(**kw)
        self.bg = bg
        self.padding = 14
        self.bind(pos=self.draw, size=self.draw)

    def draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[22])

class Trend(Widget):
    def __init__(self, color=(1,0.7,0,1), **kw):
        super().__init__(**kw)
        self.color = color
        self.data = [random.uniform(40,60) for _ in range(40)]
        self.bind(pos=self.draw, size=self.draw)

    def update(self, val):
        self.data.append(val)
        self.data = self.data[-50:]
        self.draw()

    def draw(self, *a):
        self.canvas.clear()
        with self.canvas:
            Color(0.04,0.05,0.06,1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
            if len(self.data) > 1:
                mn, mx = min(self.data), max(self.data)
                span = max(mx-mn, 0.001)
                pts = []
                for i,v in enumerate(self.data):
                    x = self.x + 8 + i*((self.width-16)/(len(self.data)-1))
                    y = self.y + 8 + ((v-mn)/span)*(self.height-16)
                    pts += [x,y]
                Color(*self.color)
                Line(points=pts, width=2.2)

def btn(text, color=(.18,.18,.18,1), fs=25):
    return Button(text=text, font_size=fs, bold=True, background_color=color)

class Main(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", spacing=12, padding=12)

        title = Label(text="BINANCE AUTOBOT", font_size=38, bold=True, color=(1,.75,0,1), size_hint_y=.16)
        root.add_widget(title)

        main = GridLayout(cols=2, spacing=10, size_hint_y=.58)

        items = [
            ("DEMO", "demo", (1,.48,0,1)),
            ("LIVE", "live", (0,.26,.85,1)),
            ("BEÁLLÍTÁSOK", "settings", (.16,.16,.16,1)),
            ("BIZTONSÁG / API", "security", (.16,.16,.16,1)),
            ("AI / STRATÉGIA", "strategy", (.16,.16,.16,1)),
            ("NAPLÓ / EXPORT", "logs", (.16,.16,.16,1)),
            ("COIN SCANNER", "scanner", (.16,.16,.16,1)),
            ("HALADÓ", "advanced", (.16,.16,.16,1)),
        ]

        for text, screen, color in items:
            b = btn(text, color, 25)
            b.bind(on_press=lambda x, s=screen: setattr(self.manager, "current", s))
            main.add_widget(b)

        root.add_widget(main)
        root.add_widget(Label(text="Demo külön • Live külön • összes Binance spot figyelés később scannerrel", font_size=18, size_hint_y=.10))
        self.add_widget(root)

class Dashboard(Screen):
    def __init__(self, mode, color, **kw):
        super().__init__(**kw)
        self.mode = mode
        self.state = load_state()

        root = BoxLayout(orientation="vertical", padding=8, spacing=8)

        head = Card(bg=color, size_hint_y=.14)
        head.add_widget(Label(text=f"{mode.upper()} DASHBOARD", font_size=32, bold=True))
        root.add_widget(head)

        self.trend = Trend(color=(1,.7,0,1) if mode=="demo" else (0,.8,1,1), size_hint_y=.25)
        root.add_widget(self.trend)

        kpi = GridLayout(cols=2, spacing=8, size_hint_y=.25)
        self.price = Label(text="BTC: ...", font_size=26)
        self.pnl = Label(text="PnL: 0", font_size=26)
        self.usdc = Label(text="USDC: 100", font_size=26)
        self.profit = Label(text="Profit: 0", font_size=26)
        for w in [self.price,self.pnl,self.usdc,self.profit]:
            c = Card(bg=(.20,.20,.20,1))
            c.add_widget(w)
            kpi.add_widget(c)
        root.add_widget(kpi)

        self.coins = Label(text="Top coinok betöltése...", font_size=22, size_hint_y=.16)
        root.add_widget(self.coins)

        controls = GridLayout(cols=2, spacing=8, size_hint_y=.24)
        start = btn("START", (.0,.55,.08,1), 24)
        stop = btn("STOP", (.65,0,0,1), 24)
        scan = btn("SCANNER", (.18,.18,.18,1), 24)
        back = btn("VISSZA", (.35,.35,.35,1), 24)
        start.bind(on_press=lambda x: self.set_run(True))
        stop.bind(on_press=lambda x: self.set_run(False))
        scan.bind(on_press=lambda x: setattr(self.manager, "current", "scanner"))
        back.bind(on_press=lambda x: setattr(self.manager, "current", "main"))
        for b in [start, stop, scan, back]:
            controls.add_widget(b)
        root.add_widget(controls)

        self.add_widget(root)
        Clock.schedule_interval(self.update_data, 5)

    def set_run(self, val):
        self.state["running"] = val
        save_state(self.state)

    def update_data(self, dt):
        try:
            r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=6).json()
            price = float(r["price"])
            self.price.text = f"BTC: {price:.0f}"
            self.trend.update(price)
        except Exception:
            pass

        try:
            tickers = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=8).json()
            usdt = [x for x in tickers if x.get("symbol","").endswith("USDT")]
            usdt = sorted(usdt, key=lambda x: float(x.get("quoteVolume",0)), reverse=True)[:5]
            self.coins.text = "Top USDT: " + "  ".join([x["symbol"].replace("USDT","") for x in usdt])
        except Exception:
            self.coins.text = "Top coin lista: offline / hiba"

class Scanner(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=12, spacing=10)
        root.add_widget(Label(text="COIN SCANNER", font_size=34, bold=True, color=(1,.75,0,1), size_hint_y=.14))
        self.list = Label(text="Betöltés...", font_size=22)
        root.add_widget(self.list)
        refresh = btn("FRISSÍTÉS", (.18,.18,.18,1), 25)
        back = btn("VISSZA", (.35,.35,.35,1), 25)
        refresh.bind(on_press=lambda x: self.load())
        back.bind(on_press=lambda x: setattr(self.manager, "current", "main"))
        root.add_widget(refresh)
        root.add_widget(back)
        self.add_widget(root)
        Clock.schedule_once(lambda dt: self.load(), 1)

    def load(self):
        try:
            data = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10).json()
            usdt = [x for x in data if x.get("symbol","").endswith("USDT")]
            usdt = sorted(usdt, key=lambda x: float(x.get("quoteVolume",0)), reverse=True)[:12]
            lines = []
            for x in usdt:
                sym = x["symbol"].replace("USDT","")
                price = float(x.get("lastPrice",0))
                chg = float(x.get("priceChangePercent",0))
                lines.append(f"{sym:8} {price:.4g}   {chg:+.2f}%")
            self.list.text = "\n".join(lines)
        except Exception as e:
            self.list.text = "Hiba / offline:\n" + str(e)[:120]

class TextScreen(Screen):
    def __init__(self, title, body, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=18, spacing=12)
        root.add_widget(Label(text=title, font_size=34, bold=True, color=(1,.75,0,1), size_hint_y=.16))
        root.add_widget(Label(text=body, font_size=22))
        b = btn("VISSZA", (.35,.35,.35,1), 25)
        b.bind(on_press=lambda x: setattr(self.manager, "current", "main"))
        root.add_widget(b)
        self.add_widget(root)

class AppMain(App):
    def build(self):
        Window.clearcolor = (0,0,0,1)
        sm = ScreenManager()
        sm.add_widget(Main(name="main"))
        sm.add_widget(Dashboard("demo", (1,.42,0,1), name="demo"))
        sm.add_widget(Dashboard("live", (0,.20,.62,1), name="live"))
        sm.add_widget(Scanner(name="scanner"))
        sm.add_widget(TextScreen("BEÁLLÍTÁSOK", "Közös beállítások:\n- alap pénznem\n- nyelv / téma\n- értesítések\n- stratégia alapértékek\n- rendszer beállítások", name="settings"))
        sm.add_widget(TextScreen("BIZTONSÁG / API", "Itt lesz:\n- app jelszó / PIN\n- Binance API kulcs\n- e-mail\n- titkosítás", name="security"))
        sm.add_widget(TextScreen("AI / STRATÉGIA", "Itt lesz:\n- Normal / Hybrid / Sniper\n- SMA / RSI / ATR\n- AI Auto / Manual / Off\n- profit-hold", name="strategy"))
        sm.add_widget(TextScreen("NAPLÓ / EXPORT", "Itt lesz:\n- trades.csv\n- log.csv\n- profit report\n- export", name="logs"))
        sm.add_widget(TextScreen("HALADÓ", "Itt lesz:\n- schedules\n- launchpool / airdrop\n- patch manager\n- diagnostics", name="advanced"))
        return sm

if __name__ == "__main__":
    AppMain().run()
