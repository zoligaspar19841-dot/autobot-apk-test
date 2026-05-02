from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class MainUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)

        self.add_widget(Label(text="BINANCE AUTOBOT", font_size=22))
        self.add_widget(Label(text="FŐ MENÜ", font_size=16))

        self.add_widget(Button(text="DEMO MÓD"))
        self.add_widget(Button(text="LIVE MÓD"))
        self.add_widget(Button(text="BOT INDÍTÁS"))
        self.add_widget(Button(text="NAPLÓ / STATISZTIKA"))

class MyApp(App):
    def build(self):
        return MainUI()

if __name__ == "__main__":
    MyApp().run()
