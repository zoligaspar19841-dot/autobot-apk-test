from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

import auth_manager
import version_manager

BG = (0, 0, 0, 1)
YELLOW = (1, .78, 0, 1)
BLUE = (.1, .35, 1, 1)
RED = (.8, .05, .05, 1)

class LoginView(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=25, spacing=12, **kw)
        self.add_widget(Label(text="BINANCE AUTOBOT", font_size=26, color=YELLOW))
        self.add_widget(Label(text="Biztonsági belépés: e-mail kód / 5 perc session", font_size=15))

        self.email = TextInput(hint_text="E-mail cím", multiline=False)
        self.code = TextInput(hint_text="5 jegyű kód", multiline=False, input_filter="int")
        self.status = Label(text="Kérj kódot, majd lépj be.", font_size=14)

        self.add_widget(self.email)
        self.add_widget(self.code)

        btn_code = Button(text="KÓD GENERÁLÁSA / EMAIL KÜLDÉS", size_hint_y=None, height=55)
        btn_code.bind(on_press=self.make_code)
        self.add_widget(btn_code)

        btn_login = Button(text="BELÉPÉS 5 PERCES KÓDDAL", size_hint_y=None, height=55)
        btn_login.bind(on_press=self.login)
        self.add_widget(btn_login)

        btn_bio = Button(text="BIOMETRIKUS AZONOSÍTÁS - ELŐKÉSZÍTVE", size_hint_y=None, height=55)
        btn_bio.bind(on_press=self.bio_info)
        self.add_widget(btn_bio)

        self.add_widget(self.status)

    def make_code(self, *_):
        r = auth_manager.generate_code(self.email.text.strip())
        if r.get("email_sent"):
            self.status.text = "Kód elküldve e-mailben. Érvényes: 5 perc."
        else:
            self.status.text = f"Demo kód: {r.get('code')}  | Érvényes: 5 perc"

    def login(self, *_):
        r = auth_manager.verify_code(self.code.text.strip())
        if r.get("ok"):
            App.get_running_app().show_dashboard()
        else:
            self.status.text = "Hiba: " + r.get("error", "ismeretlen")

    def bio_info(self, *_):
        self.status.text = "A natív Android biometria a 4. részben jön. Most OTP a biztonságos belépés."

class Dashboard(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=18, spacing=10, **kw)
        self.mode = "DEMO"
        self.add_widget(Label(text="AUTOBOT DASHBOARD", font_size=24, color=YELLOW))
        self.info = Label(text=self._status_text(), font_size=15)
        self.add_widget(self.info)

        for txt, fn in [
            ("DEMO / LIVE VÁLTÁS", self.toggle_mode),
            ("BOT START / STOP", self.todo),
            ("COIN LISTA", self.todo),
            ("PROFIT / LOG", self.todo),
            ("UPDATE / UPGRADE", self.update_info),
            ("VERZIÓK / VISSZAÁLLÍTÁS", self.versions),
            ("KIJELENTKEZÉS", self.logout),
        ]:
            b = Button(text=txt, size_hint_y=None, height=52)
            b.bind(on_press=fn)
            self.add_widget(b)

        self.msg = Label(text="1. rész kész: login + OTP + verzió alap.", font_size=14)
        self.add_widget(self.msg)

    def _status_text(self):
        v = version_manager.list_versions()
        return f"Mód: {self.mode} | Aktuális verzió: {v.get('current','?')} | Session: 5 perc"

    def toggle_mode(self, *_):
        self.mode = "LIVE" if self.mode == "DEMO" else "DEMO"
        self.info.text = self._status_text()
        self.msg.text = "LIVE módhoz API kulcs ellenőrzés a 3. részben jön."

    def todo(self, *_):
        self.msg.text = "Ez a funkció a következő részekben lesz bekötve."

    def update_info(self, *_):
        self.msg.text = "Upgrade alap kész. APK letöltés/telepítés kezelő a 4. részben jön."

    def versions(self, *_):
        v = version_manager.save_version("0.1.1-phase1", "Security + OTP + verzió alap")
        self.msg.text = "Verzió mentve: " + v.get("current", "?")

    def logout(self, *_):
        auth_manager.logout()
        App.get_running_app().show_login()

class AutobotApp(App):
    def build(self):
        self.title = "Binance Autobot"
        return LoginView()

    def show_dashboard(self):
        self.root.clear_widgets()
        self.root.add_widget(Dashboard())

    def show_login(self):
        self.root.clear_widgets()
        self.root.add_widget(LoginView())

if __name__ == "__main__":
    AutobotApp().run()
