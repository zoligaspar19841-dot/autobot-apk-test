from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
import auth_manager, version_manager

YELLOW=(1,.78,0,1)
GREEN=(0,.75,.25,1)
RED=(.85,.05,.05,1)
BLUE=(.1,.35,1,1)

class LoginView(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=18, spacing=10, **kw)
        self.add_widget(Label(text="BINANCE AUTOBOT", font_size=25, color=YELLOW))
        self.add_widget(Label(text="Biztonsági belépés: e-mail kód / 5 perc session", font_size=14))
        self.email=TextInput(hint_text="E-mail cím", multiline=False, size_hint_y=None, height=55)
        self.code=TextInput(hint_text="5 jegyű kód", multiline=False, input_filter="int", size_hint_y=None, height=55)
        self.add_widget(self.email); self.add_widget(self.code)
        b=Button(text="KÓD GENERÁLÁSA / EMAIL KÜLDÉS", size_hint_y=None, height=52); b.bind(on_press=self.make_code); self.add_widget(b)
        b=Button(text="BELÉPÉS", size_hint_y=None, height=52); b.bind(on_press=self.login); self.add_widget(b)
        b=Button(text="BIOMETRIA: 4. RÉSZBEN NATÍV ANDROID", size_hint_y=None, height=52); b.bind(on_press=self.bio); self.add_widget(b)
        self.status=Label(text="Kérj kódot, majd lépj be.", font_size=13); self.add_widget(self.status)
    def make_code(self,*_):
        r=auth_manager.generate_code(self.email.text.strip())
        self.status.text = "Email elküldve." if r.get("email_sent") else f"Demo kód: {r.get('code')} | 5 perc"
    def login(self,*_):
        r=auth_manager.verify_code(self.code.text.strip())
        if r.get("ok"): App.get_running_app().show_dashboard()
        else: self.status.text="Hiba: "+r.get("error","ismeretlen")
    def bio(self,*_):
        self.status.text="Most OTP védelem aktív. Natív biometria később."

class Dashboard(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=12, spacing=8, **kw)
        self.mode="DEMO"; self.running=False; self.symbol="BTCUSDT"; self.profit=0.0
        self.title=Label(text="AUTOBOT DASHBOARD", color=YELLOW, font_size=24, size_hint_y=None, height=42)
        self.add_widget(self.title)
        self.state=Label(text="", font_size=14, size_hint_y=None, height=45); self.add_widget(self.state)
        coins=GridLayout(cols=3, spacing=6, size_hint_y=None, height=115)
        for c in ["BTCUSDT","ETHUSDT","DOGEUSDT","BNBUSDT","SOLUSDT","XRPUSDT"]:
            b=Button(text=c); b.bind(on_press=lambda btn, s=c: self.set_coin(s)); coins.add_widget(b)
        self.add_widget(coins)
        buttons=GridLayout(cols=2, spacing=6, size_hint_y=None, height=220)
        items=[
            ("DEMO / LIVE", self.toggle_mode),
            ("BOT START / STOP", self.toggle_run),
            ("TICK TESZT", self.tick),
            ("PROFIT / LOG", self.log),
            ("UPDATE / UPGRADE", self.update),
            ("VERZIÓ MENTÉS", self.version),
            ("VISSZAÁLLÍTÁS ALAPRA", self.rollback),
            ("KIJELENTKEZÉS", self.logout),
        ]
        for t,fn in items:
            b=Button(text=t); b.bind(on_press=fn); buttons.add_widget(b)
        self.add_widget(buttons)
        self.msg=Label(text="2. rész: UI + coin lista + start/stop alap.", font_size=13)
        self.add_widget(self.msg)
        self.refresh()
    def refresh(self):
        v=version_manager.list_versions()
        self.state.text=f"Mód: {self.mode} | Bot: {'FUT' if self.running else 'ÁLL'} | Coin: {self.symbol} | P/L: {self.profit:.2f} USDC | Verzió: {v.get('current','?')}"
    def set_coin(self,s): self.symbol=s; self.msg.text=f"Coin kiválasztva: {s}"; self.refresh()
    def toggle_mode(self,*_): self.mode="LIVE" if self.mode=="DEMO" else "DEMO"; self.msg.text="LIVE API bekötés a 3. részben."; self.refresh()
    def toggle_run(self,*_): self.running=not self.running; self.msg.text="Bot állapot váltva."; self.refresh()
    def tick(self,*_): self.profit += .12 if self.running else 0; self.msg.text="Tick lefutott demo módban."; self.refresh()
    def log(self,*_): self.msg.text=f"Profit kijelzés: {self.profit:.2f} USDC. CSV/log bekötés a 3. részben."
    def update(self,*_): self.msg.text="Upgrade menü előkészítve. Fix aláírás mostantól aktív."
    def version(self,*_): version_manager.save_version("0.2.0-phase2","UI + coin lista + fix signing"); self.msg.text="Verzió mentve."; self.refresh()
    def rollback(self,*_): self.running=False; self.mode="DEMO"; self.symbol="BTCUSDT"; self.profit=0; self.msg.text="Alap állapot visszaállítva."; self.refresh()
    def logout(self,*_): auth_manager.logout(); App.get_running_app().show_login()

class AutobotApp(App):
    def build(self):
        self.title="Binance Autobot"
        self.icon="icon.png"
        return LoginView()
    def show_dashboard(self):
        self.root.clear_widgets(); self.root.add_widget(Dashboard())
    def show_login(self):
        self.root.clear_widgets(); self.root.add_widget(LoginView())

if __name__=="__main__":
    AutobotApp().run()
