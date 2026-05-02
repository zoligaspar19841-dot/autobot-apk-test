from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
import time
import autobot_core as core

ORANGE=(1,.50,0,1)
BLUE=(0,.25,.85,1)
DARK=(.07,.07,.08,1)
CARD=(.16,.16,.17,1)

def B(text, bg=CARD, fs=24):
    return Button(text=text, font_size=fs, bold=True, background_color=bg)

class Card(BoxLayout):
    def __init__(self,bg=CARD,**kw):
        super().__init__(**kw); self.bg=bg; self.padding=12; self.spacing=8
        self.bind(pos=self.draw,size=self.draw)
    def draw(self,*a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg); RoundedRectangle(pos=self.pos,size=self.size,radius=[20])

class CandleChart(Widget):
    def __init__(self,color=(1,.75,0,1),**kw):
        super().__init__(**kw); self.color=color; self.candles=[]; self.bind(pos=self.draw,size=self.draw)
    def set(self,c): self.candles=c[-45:]; self.draw()
    def draw(self,*a):
        self.canvas.clear()
        with self.canvas:
            Color(.035,.04,.045,1); RoundedRectangle(pos=self.pos,size=self.size,radius=[16])
            if len(self.candles)<3: return
            vals=[]
            for c in self.candles: vals += [c["h"],c["l"]]
            mn,mx=min(vals),max(vals); span=max(mx-mn,1e-9)
            w=max((self.width-20)/len(self.candles),3)
            for i,c in enumerate(self.candles):
                x=self.x+10+i*w+w/2
                yh=self.y+8+(c["h"]-mn)/span*(self.height-16)
                yl=self.y+8+(c["l"]-mn)/span*(self.height-16)
                yo=self.y+8+(c["o"]-mn)/span*(self.height-16)
                yc=self.y+8+(c["c"]-mn)/span*(self.height-16)
                up=c["c"]>=c["o"]
                Color(.25,.9,.45,1) if up else Color(.95,.25,.25,1)
                Line(points=[x,yl,x,yh],width=1)
                Rectangle(pos=(x-w*.28,min(yo,yc)),size=(w*.56,max(abs(yc-yo),2)))

class Main(Screen):
    def __init__(self,**kw):
        super().__init__(**kw)
        root=BoxLayout(orientation="vertical",padding=10,spacing=10)
        root.add_widget(Label(text="BINANCE AUTOBOT",font_size=36,bold=True,color=(1,.75,0,1),size_hint_y=.14))
        grid=GridLayout(cols=2,spacing=10,size_hint_y=.78)
        for txt,scr,col in [
            ("DEMO", "demo", ORANGE),("LIVE", "live", BLUE),
            ("BEÁLLÍTÁSOK","settings",CARD),("BIZTONSÁG / API","security",CARD),
            ("AI / STRATÉGIA","strategy",CARD),("COIN SCANNER","scanner",CARD),
            ("NAPLÓ / EXPORT","logs",CARD),("HALADÓ","advanced",CARD)]:
            b=B(txt,col,25); b.bind(on_press=lambda x,sc=scr:setattr(self.manager,"current",sc)); grid.add_widget(b)
        root.add_widget(grid)
        root.add_widget(Label(text="Patch-alapú fejlesztés • Demo/Live külön • Élő Binance adat",font_size=16,size_hint_y=.08))
        self.add_widget(root)

class Dashboard(Screen):
    def __init__(self,mode,color,**kw):
        super().__init__(**kw); self.mode=mode; self.color=color; self.symbol=core.settings().get("symbol","BTCUSDT")
        root=BoxLayout(orientation="vertical",padding=8,spacing=8)
        head=Card(bg=color,size_hint_y=.13); self.h=Label(text=f"{mode.upper()} DASHBOARD",font_size=31,bold=True); head.add_widget(self.h); root.add_widget(head)
        self.chart=CandleChart(color=color,size_hint_y=.30); root.add_widget(self.chart)
        kpi=GridLayout(cols=2,spacing=8,size_hint_y=.25)
        self.k1=Label(font_size=23); self.k2=Label(font_size=23); self.k3=Label(font_size=23); self.k4=Label(font_size=23)
        for w in [self.k1,self.k2,self.k3,self.k4]:
            c=Card(bg=CARD); c.add_widget(w); kpi.add_widget(c)
        root.add_widget(kpi)
        self.msg=Label(text="",font_size=18,size_hint_y=.10); root.add_widget(self.msg)
        controls=GridLayout(cols=2,spacing=8,size_hint_y=.22)
        for txt,col,fn in [("START",(.05,.55,.1,1),self.start),("STOP",(.65,0,0,1),self.stop),("1X TICK / TESZT",(.28,.28,.28,1),self.tick),("VISSZA",(.35,.35,.35,1),self.back)]:
            b=B(txt,col,23); b.bind(on_press=fn); controls.add_widget(b)
        root.add_widget(controls); self.add_widget(root)
        Clock.schedule_interval(self.update,15); Clock.schedule_once(self.update,1)
    def start(self,x):
        st=core.state(); st[self.mode]["running"]=True; core.save_state(st); self.msg.text="Bot elindítva."
    def stop(self,x):
        st=core.state(); st[self.mode]["running"]=False; core.save_state(st); self.msg.text="Bot leállítva."
    def tick(self,x):
        if self.mode=="demo":
            try: self.msg.text=core.demo_tick(self.symbol)["action"]
            except Exception as e: self.msg.text="Tick hiba: "+str(e)[:80]
        else: self.msg.text="Live order tiltva. API/safety későbbi patch."
        self.update(0)
    def back(self,x): self.manager.current="main"
    def update(self,dt):
        cfg=core.settings(); self.symbol=cfg.get("symbol","BTCUSDT")
        try:
            candles=core.get_klines(self.symbol,"1m",70); price=candles[-1]["c"]; self.chart.set(candles)
        except Exception as e:
            self.msg.text="Adathiba/offline: "+str(e)[:60]; price=0
        st=core.state(); demo=st["demo"]; pos=demo.get("positions",{})
        open_value=sum(float(p["qty"])*price for s,p in pos.items() if s==self.symbol) if price else 0
        total=float(demo.get("balance",100))+open_value
        self.k1.text=f"{self.symbol}\n{price:.4g}"
        self.k2.text=f"Total\n{total:.2f} USDC"
        self.k3.text=f"Free\n{demo.get('balance',100):.2f}"
        self.k4.text=f"PnL\n{demo.get('realized_pnl',0):.2f}"
        if st[self.mode].get("running") and self.mode=="demo":
            try: self.msg.text=core.demo_tick(self.symbol)["action"]
            except Exception as e: self.msg.text="Auto hiba: "+str(e)[:60]

class Scanner(Screen):
    def __init__(self,**kw):
        super().__init__(**kw)
        root=BoxLayout(orientation="vertical",padding=10,spacing=8)
        root.add_widget(Label(text="COIN SCANNER",font_size=34,bold=True,color=(1,.75,0,1),size_hint_y=.12))
        sv=ScrollView(size_hint_y=.72); self.list=GridLayout(cols=1,spacing=6,size_hint_y=None); self.list.bind(minimum_height=self.list.setter("height")); sv.add_widget(self.list); root.add_widget(sv)
        bar=GridLayout(cols=2,spacing=8,size_hint_y=.16)
        r=B("FRISSÍTÉS",CARD,24); b=B("VISSZA",(.35,.35,.35,1),24)
        r.bind(on_press=lambda x:self.load()); b.bind(on_press=lambda x:setattr(self.manager,"current","main"))
        bar.add_widget(r); bar.add_widget(b); root.add_widget(bar); self.add_widget(root)
        Clock.schedule_once(lambda dt:self.load(),1)
    def load(self):
        self.list.clear_widgets()
        try: arr=core.scan_top_usdt(30)
        except Exception as e:
            self.list.add_widget(Label(text="Hiba/offline: "+str(e)[:100],font_size=20,size_hint_y=None,height=60)); return
        for x in arr:
            sym=x["symbol"]; price=float(x.get("lastPrice",0)); chg=float(x.get("priceChangePercent",0)); vol=float(x.get("quoteVolume",0))
            t=f"{sym:<12} {price:.5g}   {chg:+.2f}%   Vol:{vol/1_000_000:.1f}M"
            bt=B(t, ORANGE if chg>=0 else (.45,.08,.08,1), 20)
            bt.size_hint_y=None; bt.height=58
            bt.bind(on_press=lambda w,s=sym:self.pick(s))
            self.list.add_widget(bt)
    def pick(self,sym):
        cfg=core.settings(); cfg["symbol"]=sym; core.save_settings(cfg); self.manager.current="demo"

class Settings(Screen):
    def __init__(self,**kw):
        super().__init__(**kw)
        root=BoxLayout(orientation="vertical",padding=12,spacing=8)
        root.add_widget(Label(text="BEÁLLÍTÁSOK",font_size=34,bold=True,color=(1,.75,0,1),size_hint_y=.12))
        self.inputs={}
        grid=GridLayout(cols=2,spacing=8,size_hint_y=.66)
        for key,label in [("symbol","Symbol"),("risk_pct","Risk %"),("min_profit_pct","Min profit %"),("max_positions","Max coin"),("sma_fast","SMA fast"),("sma_slow","SMA slow"),("fee_pct","Fee %"),("theme_font","Betűméret")]:
            grid.add_widget(Label(text=label,font_size=22))
            ti=TextInput(text=str(core.settings().get(key,"")),font_size=22,multiline=False)
            self.inputs[key]=ti; grid.add_widget(ti)
        root.add_widget(grid)
        bar=GridLayout(cols=2,spacing=8,size_hint_y=.18)
        save=B("MENTÉS",(.05,.55,.1,1),24); back=B("VISSZA",(.35,.35,.35,1),24)
        save.bind(on_press=self.save); back.bind(on_press=lambda x:setattr(self.manager,"current","main"))
        bar.add_widget(save); bar.add_widget(back); root.add_widget(bar)
        self.msg=Label(text="",font_size=17,size_hint_y=.08); root.add_widget(self.msg); self.add_widget(root)
    def save(self,x):
        cfg=core.settings()
        for k,ti in self.inputs.items():
            v=ti.text.strip()
            if k=="symbol": cfg[k]=v.upper()
            elif k in ("max_positions","sma_fast","sma_slow","theme_font"): cfg[k]=int(float(v))
            else: cfg[k]=float(v)
        core.save_settings(cfg); self.msg.text="Beállítások mentve."

class TextScreen(Screen):
    def __init__(self,title,body,**kw):
        super().__init__(**kw)
        root=BoxLayout(orientation="vertical",padding=18,spacing=12)
        root.add_widget(Label(text=title,font_size=34,bold=True,color=(1,.75,0,1),size_hint_y=.15))
        root.add_widget(Label(text=body,font_size=22))
        b=B("VISSZA",(.35,.35,.35,1),24); b.bind(on_press=lambda x:setattr(self.manager,"current","main")); root.add_widget(b)
        self.add_widget(root)

class AppMain(App):
    title="Binance Autobot"
    def build(self):
        Window.clearcolor=(0,0,0,1)
        sm=ScreenManager()
        sm.add_widget(Main(name="main"))
        sm.add_widget(Dashboard("demo",ORANGE,name="demo"))
        sm.add_widget(Dashboard("live",BLUE,name="live"))
        sm.add_widget(Settings(name="settings"))
        sm.add_widget(Scanner(name="scanner"))
        sm.add_widget(TextScreen("BIZTONSÁG / API","App jelszó, PIN, Binance API kulcs, e-mail, titkosítás.\nLive order jelenleg tiltva.",name="security"))
        sm.add_widget(TextScreen("AI / STRATÉGIA","Normal / Hybrid / Sniper\nSMA / RSI / ATR\nProfit-Hold: Off / Fixed / AI-Adaptive",name="strategy"))
        sm.add_widget(TextScreen("NAPLÓ / EXPORT","Trades lista, CSV export, profit report, audit napló.",name="logs"))
        sm.add_widget(TextScreen("HALADÓ","Schedules, Launchpool/Airdrop, Patch Manager, Diagnostics.",name="advanced"))
        return sm

if __name__=="__main__":
    AppMain().run()
