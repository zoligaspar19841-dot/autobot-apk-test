from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
import json, os

STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    return {"mode":"demo","balance":100,"profit":0}

def save_state(s):
    json.dump(s, open(STATE_FILE,"w"))

# ===== FŐMENÜ =====
class MainMenu(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation="vertical", spacing=10, padding=20)

        layout.add_widget(Label(text="BINANCE AUTOBOT", font_size=24, color=(1,0.7,0,1)))

        btn_demo = Button(text="DEMO MÓD", size_hint_y=None, height=80)
        btn_live = Button(text="LIVE MÓD", size_hint_y=None, height=80)
        btn_sec  = Button(text="BIZTONSÁG / API", size_hint_y=None, height=80)

        btn_demo.bind(on_press=lambda x: self.go("demo"))
        btn_live.bind(on_press=lambda x: self.go("live"))
        btn_sec.bind(on_press=lambda x: self.go("security"))

        layout.add_widget(btn_demo)
        layout.add_widget(btn_live)
        layout.add_widget(btn_sec)

        self.add_widget(layout)

    def go(self, screen):
        self.manager.current = screen

# ===== DEMO =====
class DemoScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.state = load_state()

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        self.lbl = Label(text="", font_size=16)
        self.update()

        btn_trade = Button(text="DEMO TRADE TESZT")
        btn_reset = Button(text="DEMO RESET")
        btn_back  = Button(text="VISSZA")

        btn_trade.bind(on_press=self.trade)
        btn_reset.bind(on_press=self.reset)
        btn_back.bind(on_press=lambda x: self.back())

        layout.add_widget(Label(text="DEMO MÓD", font_size=22))
        layout.add_widget(self.lbl)
        layout.add_widget(btn_trade)
        layout.add_widget(btn_reset)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def update(self):
        self.lbl.text = f"Egyenleg: {self.state['balance']} USDC\nProfit: {self.state['profit']}"

    def trade(self, x):
        self.state["balance"] -= 1
        self.state["profit"] += 0.5
        save_state(self.state)
        self.update()

    def reset(self, x):
        self.state = {"mode":"demo","balance":100,"profit":0}
        save_state(self.state)
        self.update()

    def back(self):
        self.manager.current = "main"

# ===== LIVE =====
class LiveScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(Label(text="LIVE MÓD", font_size=22))
        layout.add_widget(Label(text="⚠️ API még nincs beállítva", color=(1,0,0,1)))

        btn_back = Button(text="VISSZA")
        btn_back.bind(on_press=lambda x: self.back())

        layout.add_widget(btn_back)

        self.add_widget(layout)

    def back(self):
        self.manager.current = "main"

# ===== BIZTONSÁG =====
class SecurityScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(Label(text="BIZTONSÁG / API", font_size=22))
        layout.add_widget(Label(text="Itt lesz:\n- API kulcs\n- jelszó\n- email"))

        btn_back = Button(text="VISSZA")
        btn_back.bind(on_press=lambda x: self.back())

        layout.add_widget(btn_back)

        self.add_widget(layout)

    def back(self):
        self.manager.current = "main"

# ===== APP =====
class MyApp(App):
    def build(self):
        Window.clearcolor = (0,0,0,1)

        sm = ScreenManager()
        sm.add_widget(MainMenu(name="main"))
        sm.add_widget(DemoScreen(name="demo"))
        sm.add_widget(LiveScreen(name="live"))
        sm.add_widget(SecurityScreen(name="security"))

        return sm

MyApp().run()
