from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class Root(BoxLayout):
    pass

class TestApp(App):
    def build(self):
        root = BoxLayout(orientation="vertical", padding=20, spacing=20)
        root.add_widget(Label(text="Autobot APK TEST", font_size=28))
        root.add_widget(Label(text="Ha ezt látod az APK-ban: OK.", font_size=18))
        btn = Button(text="OK", size_hint=(1, .3))
        btn.bind(on_press=lambda *_: setattr(btn, "text", "MUKODIK ✅"))
        root.add_widget(btn)
        return root

TestApp().run()
