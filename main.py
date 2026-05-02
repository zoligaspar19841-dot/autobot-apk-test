from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
import json, os, random, time

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
    def __init__(self, bg=(0.12,0.12,0.12,1), radius=22, **kw):
        super().__init__(**kw)
        self.bg = bg
        self.radius = radius
        self.padding = 14
        self.spacing = 8
        self.bind(pos=self.redraw, size=self.redraw)

    def redraw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])

class TrendChart(Widget):
    def __init__(self, color=(1,0.75,0,1), **kw):
        super().__init__(**kw)
        self.color = color
        self.values = [random.uniform(40,60) for _ in range(40)]
        self.bind(pos=self.draw, size=self.draw)

    def draw(self, *a):
        self.canvas.clear()
        with self.canvas:
            Color(0.05,0.06,0.07,1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
            Color(0.18,0.20,0.22,1)
            for i in range(1,5):
                y = self.y + self.height*i/5
                Line(points=[self.x+10,y,self.x+self.width-10,y], width=1)
            if len(self.values) > 1:
                mn, mx = min(self.values), max(self.values)
                span = max(mx-mn, 0.001)
                pts=[]
                for i,v in enumerate(self.values):
                    x = self.x + 15 + i*(self.width-30)/(len(self.values)-1)
                    y = self.y + 15 + ((v-mn)/span)*(self.height-30)
                    pts += [x,y]
                Color(*self.color)
                Line(points=pts, width=2)

class MainMenu(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=14, spacing=12)

        header = Card(bg=(0.03,0.03,0.03,1), orientation="vertical", size_hint_y=.22)
        header.add_widget(Label(text="🤖 BINANCE AUTOBOT", font_size=26, bold=True, color=(1,0.75,0,1)))
        header.add_widget(Label(text="Demo / Live külön menü • Binance adat • AI/Stratégia • Export", font_size=16, color=(.85,.85,.85,1)))
        root.add_widget(header)

        big = GridLayout(cols=2, spacing=12, size_hint_y=.30)

        demo = Button(text="DEMO\nNarancs / sárga dashboard", font_size=24, bold=True, background_color=(1,.55,0,1))
        live = Button(text="LIVE\nKék sci-fi dashboard", font_size=24, bold=True, background_color=(0,.32,1,1))

        demo.bind(on_press=lambda x: setattr(self.manager, "current", "demo"))
        live.bind(on_press=lambda x: setattr(self.manager, "current", "live"))

        big.add_widget(demo)
        big.add_widget(live)
        root.add_widget(big)

        menu = GridLayout(cols=2, spacing=10, size_hint_y=.40)

        items = [
            ("BIZTONSÁG / API", "security", (.18,.18,.18,1)),
            ("BEÁLLÍTÁSOK", "settings", (.18,.18,.18,1)),
            ("AI / STRATÉGIA", "strategy", (.18,.18,.18,1)),
            ("NAPLÓ / EXPORT", "logs", (.18,.18,.18,1)),
            ("HALADÓ", "advanced", (.18,.18,.18,1)),
        ]

        for txt, scr, col in items:
            b = Button(text=txt, font_size=22, bold=True, background_color=col)
            b.bind(on_press=lambda x, s=scr: setattr(self.manager, "current", s))
            menu.add_widget(b)

        root.add_widget(menu)

        self.add_widget(root)

class DashboardScreen(Screen):
    def __init__(self, title, mode, theme, **kw):
        super().__init__(**kw)
        self.mode = mode
        self.theme = theme
        self.state = load_state()

        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        top = Card(bg=theme, orientation="vertical", size_hint_y=.16)
        top.add_widget(Label(text=title, font_size=24, bold=True, color=(1,1,1,1)))
        top.add_widget(Label(text=f"Mód: {mode.upper()} | Bot: {'FUT' if self.state.get('running') else 'ÁLL'}", font_size=14))
        root.add_widget(top)

        self.chart = TrendChart(color=(1,.75,0,1) if mode=="demo" else (0,.8,1,1), size_hint_y=.28)
        root.add_widget(self.chart)

        kpis = GridLayout(cols=2, spacing=10, size_hint_y=.30)
        for name, val in [
            ("Total Equity", "$100.00"),
            ("Realized PnL", "$0.00"),
            ("USDC Free", "100.00"),
            ("USDT Profit", "0.00"),
        ]:
            c = Card(bg=(1,.65,.18,.35) if mode=="demo" else (.18,.45,.9,.35), orientation="vertical")
            c.add_widget(Label(text=val, font_size=25, bold=True))
            c.add_widget(Label(text=name, font_size=14))
            kpis.add_widget(c)
        root.add_widget(kpis)

        buttons = GridLayout(cols=2, spacing=10, size_hint_y=.20)
        start = Button(text="🚀 START BOT", font_size=22, bold=True, background_color=(0.15,.7,.25,1))
        stop = Button(text="⏹ STOP BOT", font_size=22, bold=True, background_color=(.9,.1,.1,1))
        reset = Button(text="🔄 DEMO RESET" if mode=="demo" else "🔐 API CHECK", font_size=22, bold=True, background_color=(1,.55,0,1))
        back = Button(text="⬅ VISSZA", font_size=22, bold=True, background_color=(.25,.25,.25,1))

        start.bind(on_press=self.start_bot)
        stop.bind(on_press=self.stop_bot)
        reset.bind(on_press=self.reset_or_check)
        back.bind(on_press=lambda x: setattr(self.manager, "current", "main"))

        for b in [start, stop, reset, back]:
            buttons.add_widget(b)

        root.add_widget(buttons)
        self.footer = Label(text="Trend + KPI dashboard alap kész. Következő: coin lista, Demo beállítások, stratégia, export.", font_size=15, size_hint_y=.06)
        root.add_widget(self.footer)

        self.add_widget(root)

    def start_bot(self, x):
        self.state["running"] = True
        save_state(self.state)
        self.footer.text = "Bot elindítva."

    def stop_bot(self, x):
        self.state["running"] = False
        save_state(self.state)
        self.footer.text = "Bot leállítva."

    def reset_or_check(self, x):
        if self.mode == "demo":
            self.state = {"mode":"demo","balance":100.0,"profit":0.0,"running":False}
            save_state(self.state)
            self.footer.text = "Demo reset kész: 100 USDC."
        else:
            self.footer.text = "Live API még nincs bekötve. Következő körben jön."

class SimpleScreen(Screen):
    def __init__(self, title, body, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=18, spacing=12)
        root.add_widget(Label(text=title, font_size=24, bold=True, color=(1,.75,0,1), size_hint_y=.16))
        root.add_widget(Label(text=body, font_size=16, halign="center"))
        b = Button(text="⬅ VISSZA", font_size=22, size_hint_y=.15, background_color=(.25,.25,.25,1))
        b.bind(on_press=lambda x: setattr(self.manager, "current", "main"))
        root.add_widget(b)
        self.add_widget(root)

class MyApp(App):
    title = "Binance Autobot"
    def build(self):
        Window.clearcolor = (0,0,0,1)
        sm = ScreenManager()
        sm.add_widget(MainMenu(name="main"))
        sm.add_widget(DashboardScreen("📊 DEMO DASHBOARD", "demo", (1,.48,0,1), name="demo"))
        sm.add_widget(DashboardScreen("💎 LIVE DASHBOARD", "live", (.04,.20,.48,1), name="live"))
        sm.add_widget(SimpleScreen("BIZTONSÁG / API", "Itt lesz:\nBinance API kulcs\nE-mail\nJelszó / PIN\nTitkosítás", name="security"))
        sm.add_widget(SimpleScreen("BEÁLLÍTÁSOK", "Itt lesz:\nDemo beállítások\nLive beállítások\nAlap pénznem\nKockázat %\nNyelv / téma", name="settings"))
        sm.add_widget(SimpleScreen("BEÁLLÍTÁSOK", "Itt lesz:\nDemo beállítások\nLive beállítások\nAlap pénznem\nKockázat %\nNyelv / téma", name="settings"))
        sm.add_widget(SimpleScreen("AI / STRATÉGIA", "Itt lesz:\nNormal / Hybrid / Sniper\nSMA / RSI / ATR\nAI mód: Auto / Manual / Off", name="strategy"))
        sm.add_widget(SimpleScreen("NAPLÓ / EXPORT", "Itt lesz:\nTrades lista\nCSV export\nProfit report", name="logs"))
        sm.add_widget(SimpleScreen("HALADÓ", "Itt lesz:\nSchedules\nLaunchpool / Airdrop\nPatch Manager\nDiagnostics", name="advanced"))
        return sm

if __name__ == "__main__":
    MyApp().run()
