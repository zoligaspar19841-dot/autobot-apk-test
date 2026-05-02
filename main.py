from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
import json, os, time

STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "mode": "demo",
        "bot_running": False,
        "balance": 100.0,
        "profit": 0.0,
        "last_action": "Nincs művelet"
    }

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

class MainUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=14, spacing=8, **kwargs)
        Window.clearcolor = (0, 0, 0, 1)

        self.state = load_state()

        self.title = Label(text="BINANCE AUTOBOT", font_size=20, color=(1, 0.75, 0, 1), size_hint_y=0.12)
        self.status = Label(text="", font_size=14, color=(1, 1, 1, 1), size_hint_y=0.16)

        self.add_widget(self.title)
        self.add_widget(self.status)

        self.btn_demo = Button(text="DEMO MÓD", font_size=24, size_hint_y=0.18)
        self.btn_live = Button(text="LIVE MÓD", font_size=24, size_hint_y=0.18)
        self.btn_start = Button(text="BOT INDÍTÁS", font_size=24, size_hint_y=0.18)
        self.btn_log = Button(text="NAPLÓ / STATISZTIKA", font_size=24, size_hint_y=0.18)

        self.btn_demo.bind(on_press=self.set_demo)
        self.btn_live.bind(on_press=self.set_live)
        self.btn_start.bind(on_press=self.toggle_bot)
        self.btn_log.bind(on_press=self.show_stats)

        self.add_widget(self.btn_demo)
        self.add_widget(self.btn_live)
        self.add_widget(self.btn_start)
        self.add_widget(self.btn_log)

        self.footer = Label(text="", font_size=12, color=(0.8, 0.8, 0.8, 1), size_hint_y=0.12)
        self.add_widget(self.footer)

        self.refresh()

    def refresh(self):
        mode = self.state.get("mode", "demo").upper()
        running = self.state.get("bot_running", False)
        bal = self.state.get("balance", 100.0)
        profit = self.state.get("profit", 0.0)

        self.status.text = f"Mód: {mode} | Bot: {'FUT' if running else 'ÁLL'}\nEgyenleg: {bal:.2f} USDC | Profit: {profit:.2f} USDC"
        self.btn_start.text = "BOT LEÁLLÍTÁS" if running else "BOT INDÍTÁS"
        self.footer.text = "Utolsó művelet: " + self.state.get("last_action", "Nincs")

        if self.state.get("mode") == "demo":
            self.btn_demo.background_color = (1, 0.55, 0, 1)
            self.btn_live.background_color = (0.25, 0.25, 0.25, 1)
        else:
            self.btn_demo.background_color = (0.25, 0.25, 0.25, 1)
            self.btn_live.background_color = (0, 0.35, 1, 1)

    def set_demo(self, instance):
        self.state["mode"] = "demo"
        self.state["last_action"] = "Demo mód bekapcsolva"
        save_state(self.state)
        self.refresh()

    def set_live(self, instance):
        self.state["mode"] = "live"
        self.state["last_action"] = "Live mód kiválasztva - API kulcs még nincs bekötve"
        save_state(self.state)
        self.refresh()

    def toggle_bot(self, instance):
        self.state["bot_running"] = not self.state.get("bot_running", False)
        self.state["last_action"] = "Bot elindítva" if self.state["bot_running"] else "Bot leállítva"
        save_state(self.state)
        self.refresh()

    def show_stats(self, instance):
        self.state["last_action"] = f"Statisztika megnyitva: {time.strftime('%H:%M:%S')}"
        save_state(self.state)
        self.refresh()

class MyApp(App):
    title = "Binance Autobot"
    def build(self):
        return MainUI()

if __name__ == "__main__":
    MyApp().run()
