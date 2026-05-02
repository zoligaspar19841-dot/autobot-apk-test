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
            return json.load(open(STATE_FILE))
        except:
            pass
    return {"mode":"demo","balance":100.0,"profit":0.0,"running":False}

class Card(BoxLayout):
    def __init__(self, bg=(0.1,0.1,0.1,1), **kw):
        super().__init__(**kw)
        self.bg = bg
        self.padding = 12
        self.bind(pos=self.draw, size=self.draw)

    def draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20])

class Trend(Widget):
    def __init__(self, color=(1,0.7,0,1), **kw):
        super().__init__(**kw)
        self.color = color
        self.data = [random.uniform(40,60) for _ in range(40)]
        self.bind(pos=self.draw, size=self.draw)

    def update(self, val):
        self.data.append(val)
        if len(self.data) > 40:
            self.data.pop(0)
        self.draw()

    def draw(self, *a):
        self.canvas.clear()
        with self.canvas:
            Color(0.05,0.05,0.05,1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
            if len(self.data) > 1:
                mn, mx = min(self.data), max(self.data)
                span = max(mx-mn,0.001)
                pts=[]
                for i,v in enumerate(self.data):
                    x = self.x + i*(self.width/(len(self.data)-1))
                    y = self.y + ((v-mn)/span)*self.height
                    pts += [x,y]
                Color(*self.color)
                Line(points=pts, width=2)

class Dashboard(Screen):
    def __init__(self, mode, color, **kw):
        super().__init__(**kw)
        self.mode = mode
        self.state = load_state()

        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # HEADER
        head = Card(bg=color, size_hint_y=.15)
        self.title = Label(text=f"{mode.upper()} DASHBOARD", font_size=32, bold=True)
        head.add_widget(self.title)
        root.add_widget(head)

        # TREND
        self.trend = Trend(color=(1,0.7,0,1) if mode=="demo" else (0,0.8,1,1), size_hint_y=.25)
        root.add_widget(self.trend)

        # KPI
        kpi = GridLayout(cols=2, spacing=10, size_hint_y=.25)

        self.price = Label(text="BTC: ...", font_size=28)
        self.pnl = Label(text="PnL: 0", font_size=28)
        self.usdc = Label(text="USDC: 100", font_size=28)
        self.profit = Label(text="Profit: 0", font_size=28)

        for w in [self.price,self.pnl,self.usdc,self.profit]:
            c = Card(bg=(0.2,0.2,0.2,1))
            c.add_widget(w)
            kpi.add_widget(c)

        root.add_widget(kpi)

        # COIN LISTA
        self.coins = Label(text="BTC / ETH / DOGE", font_size=24, size_hint_y=.15)
        root.add_widget(self.coins)

        # BUTTONS
        btns = GridLayout(cols=2, size_hint_y=.20, spacing=10)

        start = Button(text="START", font_size=24, background_color=(0,0.7,0,1))
        stop = Button(text="STOP", font_size=24, background_color=(0.8,0,0,1))
        back = Button(text="VISSZA", font_size=24)

        start.bind(on_press=lambda x: self.set_run(True))
        stop.bind(on_press=lambda x: self.set_run(False))
        back.bind(on_press=lambda x: setattr(self.manager,"current","main"))

        for b in [start,stop,back]:
            btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

        Clock.schedule_interval(self.update_data, 3)

    def set_run(self,val):
        self.state["running"]=val

    def update_data(self,dt):
        try:
            r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()
            price = float(r["price"])

            self.price.text = f"BTC: {price:.0f}"
            self.trend.update(price)

            self.coins.text = "BTC ETH DOGE"
        except:
            pass

class Main(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", spacing=12, padding=12)

        title = Label(text="BINANCE AUTOBOT", font_size=36)
        root.add_widget(title)

        demo = Button(text="DEMO", font_size=30, background_color=(1,0.5,0,1))
        live = Button(text="LIVE", font_size=30, background_color=(0,0.3,1,1))

        demo.bind(on_press=lambda x: setattr(self.manager,"current","demo"))
        live.bind(on_press=lambda x: setattr(self.manager,"current","live"))

        root.add_widget(demo)
        root.add_widget(live)

        self.add_widget(root)

class AppMain(App):
    def build(self):
        Window.clearcolor=(0,0,0,1)
        sm = ScreenManager()
        sm.add_widget(Main(name="main"))
        sm.add_widget(Dashboard("demo",(1,0.4,0,1),name="demo"))
        sm.add_widget(Dashboard("live",(0,0.2,0.5,1),name="live"))
        return sm

if __name__ == "__main__":
    AppMain().run()
