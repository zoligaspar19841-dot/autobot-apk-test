from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
import json, os, random

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
        self.values = [random.uniform(40,70) for _ in range(45)]
        self.bind(pos=self.draw, size=self.draw)

    def draw(self, *a):
        self.canvas.clear()
        with self.canvas:
            Color(0.04,0.05,0.06,1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
            Color(0.16,0.18,0.20,1)
            for i in range(1,5):
                y = self.y + self.height*i/5
                Line(points=[self.x+12,y,self.x+self.width-12,y], width=1)
            mn, mx = min(self.values), max(self.values)
            span = max(mx-mn, 0.001)
            pts=[]
            for i,v in enumerate(self.values):
                x = self.x + 15 + i*(self.width-30)/(len(self.values)-1)
                y = self.y + 15 + ((v-mn)/span)*(self.height-30)
                pts += [x,y]
            Color(*self.color)
            Line(points=pts, width=2)

def menu_button(text, color=(0.18,0.18,0.18,1)):
    return Button(text=text, font_size=21, bold=True, background_color=color)

class MainMenu(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=14, spacing=12)

        header = Card(bg=(0.03,0.03,0.03,1), orientation="vertical", size_hint_y=.20)
        header.add_widget(Label(text="BINANCE AUTOBOT", font_size=28, bold=True, color=(1,.75,0,1)))
        header.add_widget(Label(text="Demo / Live külön menü • Binance adat • AI / stratégia • export", font_size=15))
        root.add_widget(header)

        main = GridLayout(cols=2, spacing=12, size_hint_y=.42)
        buttons = [
            ("DEMO\nNarancs / sárga dashboard", "demo_menu", (1,.50,0,1)),
            ("LIVE\nKék sci-fi dashboard", "live_menu", (0,.28,.85,1)),
            ("BIZTONSÁG / API", "security", (.16,.16,.16,1)),
            ("BEÁLLÍTÁSOK", "settings", (.16,.16,.16,1)),
            ("AI / STRATÉGIA", "strategy", (.16,.16,.16,1)),
            ("NAPLÓ / EXPORT", "logs", (.16,.16,.16,1)),
        ]
        for txt, scr, col in buttons:
            b = menu_button(txt, col)
            b.bind(on_press=lambda x, s=scr: setattr(self.manager, "current", s))
            main.add_widget(b)
        root.add_widget(main)

        adv = menu_button("HALADÓ / SCHEDULES / DIAGNOSZTIKA", (.12,.12,.12,1))
        adv.bind(on_press=lambda x: setattr(self.manager, "current", "advanced"))
        root.add_widget(adv)

        self.add_widget(root)

class ModeMenu(Screen):
    def __init__(self, title, mode, color, **kw):
        super().__init__(**kw)
        self.mode = mode
        root = BoxLayout(orientation="vertical", padding=16, spacing=12)

        top = Card(bg=color, orientation="vertical", size_hint_y=.18)
        top.add_widget(Label(text=title, font_size=27, bold=True))
        top.add_widget(Label(text="Külön menü, külön beállítások, külön működés", font_size=15))
        root.add_widget(top)

        grid = GridLayout(cols=1, spacing=10, size_hint_y=.72)
        items = [
            (f"{mode.upper()} DASHBOARD", f"{mode}_dashboard"),
            (f"{mode.upper()} TRADING", f"{mode}_trading"),
            (f"{mode.upper()} BEÁLLÍTÁSOK", f"{mode}_settings"),
            ("DEMO RESET" if mode=="demo" else "API STÁTUSZ / FIGYELMEZTETÉS", f"{mode}_extra"),
            ("VISSZA A FŐMENÜBE", "main"),
        ]
        for txt, scr in items:
            b = menu_button(txt, color if txt.startswith(mode.upper()) else (.22,.22,.22,1))
            b.bind(on_press=lambda x, s=scr: setattr(self.manager, "current", s))
            grid.add_widget(b)
        root.add_widget(grid)
        self.add_widget(root)

class Dashboard(Screen):
    def __init__(self, title, mode, theme, line_color, **kw):
        super().__init__(**kw)
        self.mode = mode
        self.state = load_state()
        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        top = Card(bg=theme, orientation="vertical", size_hint_y=.15)
        top.add_widget(Label(text=title, font_size=25, bold=True))
        top.add_widget(Label(text=f"Mód: {mode.upper()} | Bot: {'FUT' if self.state.get('running') else 'ÁLL'}", font_size=15))
        root.add_widget(top)

        root.add_widget(TrendChart(color=line_color, size_hint_y=.28))

        kpis = GridLayout(cols=2, spacing=10, size_hint_y=.30)
        for name, val in [
            ("Total Equity", "$100.00"),
            ("Realized PnL", "$0.00"),
            ("USDC Free", "100.00"),
            ("USDT Profit", "0.00"),
        ]:
            c = Card(bg=(1,.60,.12,.38) if mode=="demo" else (.12,.38,.85,.38), orientation="vertical")
            c.add_widget(Label(text=val, font_size=26, bold=True))
            c.add_widget(Label(text=name, font_size=16))
            kpis.add_widget(c)
        root.add_widget(kpis)

        controls = GridLayout(cols=2, spacing=10, size_hint_y=.22)
        for txt, col in [
            ("START BOT", (.1,.65,.22,1)),
            ("STOP BOT", (.85,.08,.08,1)),
            ("RESET / CHECK", (1,.55,0,1)),
            ("VISSZA", (.25,.25,.25,1)),
        ]:
            b = menu_button(txt, col)
            if txt == "VISSZA":
                b.bind(on_press=lambda x: setattr(self.manager, "current", f"{self.mode}_menu"))
            controls.add_widget(b)
        root.add_widget(controls)

        self.add_widget(root)

class TextScreen(Screen):
    def __init__(self, title, body, back="main", **kw):
        super().__init__(**kw)
        self.back = back
        root = BoxLayout(orientation="vertical", padding=18, spacing=12)
        root.add_widget(Label(text=title, font_size=25, bold=True, color=(1,.75,0,1), size_hint_y=.16))
        root.add_widget(Label(text=body, font_size=18, halign="center"))
        b = menu_button("VISSZA", (.25,.25,.25,1))
        b.bind(on_press=lambda x: setattr(self.manager, "current", self.back))
        root.add_widget(b)
        self.add_widget(root)

class MyApp(App):
    title = "Binance Autobot"

    def build(self):
        Window.clearcolor = (0,0,0,1)
        sm = ScreenManager()

        sm.add_widget(MainMenu(name="main"))
        sm.add_widget(ModeMenu("DEMO MÓD", "demo", (1,.50,0,1), name="demo_menu"))
        sm.add_widget(ModeMenu("LIVE MÓD", "live", (0,.25,.80,1), name="live_menu"))

        sm.add_widget(Dashboard("DEMO DASHBOARD", "demo", (1,.48,0,1), (1,.75,0,1), name="demo_dashboard"))
        sm.add_widget(Dashboard("LIVE DASHBOARD", "live", (.04,.18,.48,1), (0,.85,1,1), name="live_dashboard"))

        sm.add_widget(TextScreen("DEMO TRADING", "Itt jön a demo vétel/eladás, élő Binance árakkal, de teszt pénzzel.", "demo_menu", name="demo_trading"))
        sm.add_widget(TextScreen("DEMO BEÁLLÍTÁSOK", "Risk/trade %, min. profit %, stratégia, max pozíció, demo kezdő tőke.", "demo_menu", name="demo_settings"))
        sm.add_widget(TextScreen("DEMO RESET", "Demo egyenleg 100 USDC-re, profit és pozíciók nullázása.", "demo_menu", name="demo_extra"))

        sm.add_widget(TextScreen("LIVE TRADING", "Éles kereskedés csak API kulcs után, külön figyelmeztetéssel.", "live_menu", name="live_trading"))
        sm.add_widget(TextScreen("LIVE BEÁLLÍTÁSOK", "API mód, max kitettség, safety guard, slippage, stop-all.", "live_menu", name="live_settings"))
        sm.add_widget(TextScreen("API STÁTUSZ", "Binance API kulcs még nincs bekötve. Éles order tiltva.", "live_menu", name="live_extra"))

        sm.add_widget(TextScreen("BIZTONSÁG / API", "App jelszó, PIN, Binance API kulcs, e-mail, titkosítás.", "main", name="security"))
        sm.add_widget(TextScreen("BEÁLLÍTÁSOK", "Közös beállítások: nyelv, téma, alap pénznem, értesítések.", "main", name="settings"))
        sm.add_widget(TextScreen("AI / STRATÉGIA", "Normal / Hybrid / Sniper, AI Auto / Manual / Off, RSI/SMA/ATR.", "main", name="strategy"))
        sm.add_widget(TextScreen("NAPLÓ / EXPORT", "Trades lista, CSV export, profit report, audit napló.", "main", name="logs"))
        sm.add_widget(TextScreen("HALADÓ", "Schedules, Launchpool/Airdrop, Patch Manager, Diagnostics.", "main", name="advanced"))

        return sm

if __name__ == "__main__":
    MyApp().run()
