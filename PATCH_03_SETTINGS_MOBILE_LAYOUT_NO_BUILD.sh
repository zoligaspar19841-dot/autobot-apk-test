#!/bin/bash
set -e

echo "=== PATCH 03: Settings mobil layout javítás - APK BUILD NÉLKÜL ==="

TS=$(date +%Y%m%d_%H%M%S)

echo "=== 1) Biztonsági mentés ==="
cp main.py "main.py.bak_patch03_settings_$TS"
cp apk_stage/main.py "apk_stage/main.py.bak_patch03_settings_$TS"

echo "=== 2) Settings screen javítás main.py + apk_stage/main.py ==="
python - <<'PY'
from pathlib import Path
import re

FILES = [Path("main.py"), Path("apk_stage/main.py")]

MOBILE_SETTINGS_CLASS = r'''
class DemoCoreSettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", padding=10, spacing=8)

        title = Label(
            text="[b]DEMO CORE SETTINGS[/b]\n[size=13]Mobilbarát beállítások[/size]",
            markup=True,
            size_hint_y=None,
            height=62,
            halign="center"
        )
        root.add_widget(title)

        scroll = ScrollView()
        form = BoxLayout(
            orientation="vertical",
            padding=6,
            spacing=8,
            size_hint_y=None
        )
        form.bind(minimum_height=form.setter("height"))

        self.inputs = {}

        fields = [
            ("risk_pct", "Risk / trade %", "10.0"),
            ("max_positions", "Max pozíció", "3"),
            ("min_profit_pct", "Min profit %", "10.0"),
            ("stop_loss_pct", "Stop loss %", "3.0"),
            ("trailing_drop_pct", "Trailing drop %", "1.5"),
            ("hold_profit_minutes", "Profit tartás perc", "30"),
            ("time_in_trend_minutes_max", "Max trend idő perc", "240"),
            ("exit_cooldown_minutes", "Exit cooldown perc", "10"),
            ("profit_erosion_guard_pct", "Profit erózió guard %", "1.5"),
            ("watchlist", "Watchlist", "BTCUSDT,ETHUSDT,DOGEUSDT"),
            ("execution_mode", "Execution mode", "AUTO"),
        ]

        for key, label, default in fields:
            row = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=86,
                spacing=3
            )

            lab = Label(
                text=label,
                size_hint_y=None,
                height=26,
                halign="left",
                valign="middle",
                color=(1, 0.82, 0.18, 1)
            )
            lab.bind(size=lambda inst, val: setattr(inst, "text_size", val))

            ti = TextInput(
                text="",
                hint_text=default,
                multiline=False,
                size_hint_y=None,
                height=48,
                foreground_color=(1, 1, 1, 1),
                background_color=(0.08, 0.08, 0.08, 1),
                cursor_color=(1, 0.82, 0.18, 1),
                padding=[10, 10, 10, 10]
            )
            self.inputs[key] = ti

            row.add_widget(lab)
            row.add_widget(ti)
            form.add_widget(row)

        scroll.add_widget(form)
        root.add_widget(scroll)

        self.info = Label(
            text="Betöltés után módosíts, majd Mentés.",
            size_hint_y=None,
            height=44,
            markup=True,
            halign="left",
            valign="middle"
        )
        self.info.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        root.add_widget(self.info)

        btns = GridLayout(cols=2, spacing=6, size_hint_y=None, height=156)

        b = Button(text="BETÖLTÉS")
        b.bind(on_press=lambda *_: self.load_values())
        btns.add_widget(b)

        b = Button(text="MENTÉS")
        b.bind(on_press=lambda *_: self.save_values())
        btns.add_widget(b)

        b = Button(text="ALAPÉRTÉK")
        b.bind(on_press=lambda *_: self.reset_defaults())
        btns.add_widget(b)

        b = Button(text="VISSZA")
        b.bind(on_press=lambda *_: safe_go_back(self.manager, "main"))
        btns.add_widget(b)

        root.add_widget(btns)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.load_values()

    def load_values(self):
        try:
            st = demo_core.load_state()
            settings = st.get("settings", {})
            for key, inp in self.inputs.items():
                val = settings.get(key, inp.hint_text)
                if isinstance(val, list):
                    val = ",".join(map(str, val))
                inp.text = str(val)
            self.info.text = "[b]OK:[/b] Beállítások betöltve."
        except Exception as e:
            self.info.text = "[b]HIBA:[/b] Betöltés sikertelen: " + str(e)

    def save_values(self):
        try:
            st = demo_core.load_state()
            settings = st.setdefault("settings", {})

            def to_float(key, fallback):
                try:
                    return float(self.inputs[key].text.strip().replace(",", "."))
                except Exception:
                    return fallback

            def to_int(key, fallback):
                try:
                    return int(float(self.inputs[key].text.strip().replace(",", ".")))
                except Exception:
                    return fallback

            settings["risk_pct"] = to_float("risk_pct", settings.get("risk_pct", 10.0))
            settings["max_positions"] = to_int("max_positions", settings.get("max_positions", 3))
            settings["min_profit_pct"] = to_float("min_profit_pct", settings.get("min_profit_pct", 10.0))
            settings["stop_loss_pct"] = to_float("stop_loss_pct", settings.get("stop_loss_pct", 3.0))
            settings["trailing_drop_pct"] = to_float("trailing_drop_pct", settings.get("trailing_drop_pct", 1.5))
            settings["hold_profit_minutes"] = to_int("hold_profit_minutes", settings.get("hold_profit_minutes", 30))
            settings["time_in_trend_minutes_max"] = to_int("time_in_trend_minutes_max", settings.get("time_in_trend_minutes_max", 240))
            settings["exit_cooldown_minutes"] = to_int("exit_cooldown_minutes", settings.get("exit_cooldown_minutes", 10))
            settings["profit_erosion_guard_pct"] = to_float("profit_erosion_guard_pct", settings.get("profit_erosion_guard_pct", 1.5))

            wl = self.inputs["watchlist"].text.strip()
            settings["watchlist"] = [x.strip().upper() for x in wl.split(",") if x.strip()]

            mode = self.inputs["execution_mode"].text.strip().upper()
            if mode not in ("AUTO", "MANUAL", "OFF"):
                mode = "AUTO"
            settings["execution_mode"] = mode

            st["last_action"] = "Demo settings mentve"
            demo_core.save_state(st)
            self.info.text = "[b]OK:[/b] Mentve. Új beállítások aktívak a következő ticknél."
        except Exception as e:
            self.info.text = "[b]HIBA:[/b] Mentés sikertelen: " + str(e)

    def reset_defaults(self):
        try:
            st = demo_core.load_state()
            defaults = dict(demo_core.DEFAULT_STATE.get("settings", {}))
            st["settings"] = defaults
            st["last_action"] = "Demo settings alapértékre állítva"
            demo_core.save_state(st)
            self.load_values()
            self.info.text = "[b]OK:[/b] Alapértékek visszaállítva."
        except Exception as e:
            self.info.text = "[b]HIBA:[/b] Reset sikertelen: " + str(e)
'''

def replace_class(s):
    if "class DemoCoreSettingsScreen(Screen):" not in s:
        return s, False

    start = s.index("class DemoCoreSettingsScreen(Screen):")
    m = re.search(r"\nclass\s+\w+\(Screen\):", s[start + 1:])
    if m:
        end = start + 1 + m.start()
        s = s[:start] + MOBILE_SETTINGS_CLASS + "\n\n" + s[end:]
    else:
        s = s[:start] + MOBILE_SETTINGS_CLASS + "\n"
    return s, True

for p in FILES:
    s = p.read_text(encoding="utf-8", errors="replace")

    for imp in [
        "from kivy.uix.scrollview import ScrollView",
        "from kivy.uix.textinput import TextInput",
        "from kivy.uix.gridlayout import GridLayout",
    ]:
        if imp not in s:
            s = imp + "\n" + s

    if "import demo_core_engine as demo_core" not in s:
        s = "import demo_core_engine as demo_core\n" + s

    s, ok = replace_class(s)
    if not ok:
        # Ha nem volt ilyen class, DemoCoreScreen elé tesszük.
        if "class DemoCoreScreen(Screen):" in s:
            s = s.replace("class DemoCoreScreen(Screen):", MOBILE_SETTINGS_CLASS + "\n\nclass DemoCoreScreen(Screen):", 1)
        else:
            s += "\n\n" + MOBILE_SETTINGS_CLASS + "\n"

    # Route biztosítása
    if 'DemoCoreSettingsScreen(name="demo_settings")' not in s:
        s = re.sub(
            r"(\n\s*return\s+sm\b)",
            '\n        sm.add_widget(DemoCoreSettingsScreen(name="demo_settings"))\\1',
            s,
            count=1
        )

    p.write_text(s, encoding="utf-8")
    print("OK patched:", p)
PY

echo "=== 3) Python compile teszt - build nélkül ==="
python -m py_compile main.py demo_core_engine.py
python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py

echo "=== 4) Ellenőrzés ==="
grep -nE "DemoCoreSettingsScreen|Mobilbarát|TextInput|foreground_color|background_color|hold_profit_minutes|profit_erosion_guard_pct" main.py | head -80
echo "--- apk_stage ---"
grep -nE "DemoCoreSettingsScreen|Mobilbarát|TextInput|foreground_color|background_color|hold_profit_minutes|profit_erosion_guard_pct" apk_stage/main.py | head -80

echo "=== 5) Git állapot - commit nincs, push nincs ==="
git status --short

echo "=== PATCH 03 KÉSZ ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Ha ez jó, írd: jó"
