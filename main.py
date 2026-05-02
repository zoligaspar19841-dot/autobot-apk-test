from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
import json, os, time, urllib.request

STATE_FILE = "state.json"
SYMBOL = "BTCUSDT"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE, "r", encoding="utf-8"))
        except Exception:
            pass
    return {
        "mode": "demo",
        "bot_running": False,
        "balance": 100.0,
        "coin_qty": 0.0,
        "avg_price": 0.0,
        "profit": 0.0,
        "trades": [],
        "last_action": "Indulásra kész"
    }

def save_state(s):
    json.dump(s, open(STATE_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def get_json(url, timeout=8):
    req = urllib.request.Request(url, headers={"User-Agent": "AutobotAPK/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def fetch_klines(symbol=SYMBOL, limit=60):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit={limit}"
    data = get_json(url)
    return [float(x[4]) for x in data]

def fetch_24h(symbol=SYMBOL):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    return get_json(url)

def sma(values, n):
    if len(values) < n:
        return None
    return sum(values[-n:]) / n

class MiniChart(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.values = []
        self.bind(pos=self.draw, size=self.draw)

    def set_values(self, values):
        self.values = values[-60:]
        self.draw()

    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.05, 0.05, 0.05, 1)
            Rectangle(pos=self.pos, size=self.size)
            if len(self.values) < 2:
                return
            mn, mx = min(self.values), max(self.values)
            span = max(mx - mn, 0.000001)
            pts = []
            for i, v in enumerate(self.values):
                x = self.x + (i / (len(self.values)-1)) * self.width
                y = self.y + ((v - mn) / span) * self.height
                pts += [x, y]
            Color(1, 0.75, 0, 1)
            Line(points=pts, width=2)

class MainUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=10, spacing=8, **kwargs)
        Window.clearcolor = (0, 0, 0, 1)

        self.state = load_state()
        self.prices = []
        self.last_price = 0.0

        self.title = Label(text="BINANCE AUTOBOT", font_size=19, color=(1, .75, 0, 1), size_hint_y=.08)
        self.status = Label(text="", font_size=13, color=(1, 1, 1, 1), size_hint_y=.13)
        self.chart = MiniChart(size_hint_y=.25)

        self.btn_demo = Button(text="DEMO MÓD", font_size=21, size_hint_y=.13)
        self.btn_live = Button(text="LIVE MÓD - CSAK ADAT", font_size=21, size_hint_y=.13)
        self.btn_start = Button(text="BOT INDÍTÁS", font_size=21, size_hint_y=.13)
        self.btn_tick = Button(text="1X DEMO TICK / TESZT", font_size=20, size_hint_y=.13)
        self.btn_reset = Button(text="DEMO RESET", font_size=20, size_hint_y=.11)
        self.footer = Label(text="", font_size=11, color=(.85, .85, .85, 1), size_hint_y=.11)

        self.btn_demo.bind(on_press=self.set_demo)
        self.btn_live.bind(on_press=self.set_live)
        self.btn_start.bind(on_press=self.toggle_bot)
        self.btn_tick.bind(on_press=self.manual_tick)
        self.btn_reset.bind(on_press=self.demo_reset)

        for w in [self.title, self.status, self.chart, self.btn_demo, self.btn_live, self.btn_start, self.btn_tick, self.btn_reset, self.footer]:
            self.add_widget(w)

        self.refresh_ui()
        Clock.schedule_interval(self.update_market, 15)
        Clock.schedule_interval(self.auto_tick, 20)
        Clock.schedule_once(lambda dt: self.update_market(0), 1)

    def set_demo(self, instance):
        self.state["mode"] = "demo"
        self.state["last_action"] = "Demo mód bekapcsolva"
        save_state(self.state)
        self.refresh_ui()

    def set_live(self, instance):
        self.state["mode"] = "live"
        self.state["last_action"] = "Live mód: most csak élő adat, éles order még tiltva"
        save_state(self.state)
        self.refresh_ui()

    def toggle_bot(self, instance):
        self.state["bot_running"] = not self.state.get("bot_running", False)
        self.state["last_action"] = "Bot elindítva" if self.state["bot_running"] else "Bot leállítva"
        save_state(self.state)
        self.refresh_ui()

    def demo_reset(self, instance):
        self.state.update({
            "mode": "demo",
            "bot_running": False,
            "balance": 100.0,
            "coin_qty": 0.0,
            "avg_price": 0.0,
            "profit": 0.0,
            "trades": [],
            "last_action": "Demo reset: 100 USDC"
        })
        save_state(self.state)
        self.refresh_ui()

    def update_market(self, dt):
        try:
            self.prices = fetch_klines(SYMBOL, 80)
            self.last_price = self.prices[-1]
            self.chart.set_values(self.prices)
            t = fetch_24h(SYMBOL)
            chg = float(t.get("priceChangePercent", 0))
            self.state["market_24h"] = chg
            self.state["last_action"] = f"Élő adat frissítve: {SYMBOL} {self.last_price:.2f} USDT"
        except Exception as e:
            self.state["last_action"] = "Adathiba / offline: " + str(e)[:70]
        save_state(self.state)
        self.refresh_ui()

    def manual_tick(self, instance):
        self.do_demo_logic(force=True)

    def auto_tick(self, dt):
        if self.state.get("bot_running"):
            self.do_demo_logic(force=False)

    def do_demo_logic(self, force=False):
        if self.state.get("mode") != "demo":
            self.state["last_action"] = "Live order tiltva. Először demo logika."
            save_state(self.state)
            self.refresh_ui()
            return

        if len(self.prices) < 30:
            try:
                self.prices = fetch_klines(SYMBOL, 80)
                self.last_price = self.prices[-1]
            except Exception:
                self.state["last_action"] = "Nincs ár adat."
                save_state(self.state)
                self.refresh_ui()
                return

        price = self.last_price or self.prices[-1]
        fast = sma(self.prices, 9)
        slow = sma(self.prices, 21)
        balance = float(self.state.get("balance", 100))
        qty = float(self.state.get("coin_qty", 0))
        avg = float(self.state.get("avg_price", 0))
        fee = 0.001

        action = "HOLD"

        if fast and slow and fast > slow and qty <= 0 and balance >= 10:
            spend = min(balance * 0.25, 25)
            buy_qty = (spend * (1 - fee)) / price
            self.state["balance"] = balance - spend
            self.state["coin_qty"] = buy_qty
            self.state["avg_price"] = price
            action = f"DEMO BUY {buy_qty:.6f} {SYMBOL} @ {price:.2f}"

        elif qty > 0:
            pnl_pct = ((price - avg) / avg) * 100 if avg else 0
            if (fast and slow and fast < slow) or pnl_pct >= 0.8 or pnl_pct <= -0.8 or force:
                sell_value = qty * price * (1 - fee)
                pnl = sell_value - (qty * avg)
                self.state["balance"] = balance + sell_value
                self.state["coin_qty"] = 0.0
                self.state["avg_price"] = 0.0
                self.state["profit"] = float(self.state.get("profit", 0)) + pnl
                action = f"DEMO SELL PnL {pnl:.3f} USDC @ {price:.2f}"

        self.state["last_action"] = action
        self.state.setdefault("trades", []).append({"time": time.strftime("%H:%M:%S"), "action": action, "price": price})
        self.state["trades"] = self.state["trades"][-30:]
        save_state(self.state)
        self.refresh_ui()

    def refresh_ui(self):
        mode = self.state.get("mode", "demo").upper()
        running = "FUT" if self.state.get("bot_running") else "ÁLL"
        bal = float(self.state.get("balance", 100))
        qty = float(self.state.get("coin_qty", 0))
        avg = float(self.state.get("avg_price", 0))
        profit = float(self.state.get("profit", 0))
        open_value = qty * self.last_price if self.last_price else 0
        total = bal + open_value
        chg = self.state.get("market_24h", 0)

        self.status.text = (
            f"Mód: {mode} | Bot: {running} | {SYMBOL}\n"
            f"Ár: {self.last_price:.2f} | 24h: {chg}%\n"
            f"Total: {total:.2f} USDC | Free: {bal:.2f} | PnL: {profit:.2f}"
        )

        self.btn_start.text = "BOT LEÁLLÍTÁS" if self.state.get("bot_running") else "BOT INDÍTÁS"
        self.footer.text = self.state.get("last_action", "")

        self.btn_demo.background_color = (1, .52, 0, 1) if self.state.get("mode") == "demo" else (.18, .18, .18, 1)
        self.btn_live.background_color = (0, .28, .9, 1) if self.state.get("mode") == "live" else (.18, .18, .18, 1)
        self.btn_start.background_color = (.1, .55, .1, 1) if self.state.get("bot_running") else (.35, .35, .35, 1)

class MyApp(App):
    title = "Binance Autobot"
    def build(self):
        return MainUI()

if __name__ == "__main__":
    MyApp().run()
