import json, os, time, urllib.request, urllib.parse

STATE_FILE="state.json"
SETTINGS_FILE="settings_app.json"
BINANCE="https://api.binance.com"

DEFAULT_SETTINGS={
    "base":"USDC",
    "symbol":"BTCUSDT",
    "risk_pct":10.0,
    "min_profit_pct":10.0,
    "new_coin_min_profit_pct":5.0,
    "max_positions":3,
    "sma_fast":9,
    "sma_slow":21,
    "rsi_len":14,
    "profit_hold":"AI-Adaptive",
    "fee_pct":0.10,
    "theme_font":24
}

DEFAULT_STATE={
    "demo":{"balance":100.0,"positions":{},"realized_pnl":0.0,"running":False,"trades":[]},
    "live":{"running":False,"api_ready":False,"warning":"Éles order tiltva, API még nincs bekötve."},
    "mode":"demo",
    "last_msg":"Rendszer indulásra kész."
}

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path,"r",encoding="utf-8") as f: return json.load(f)
        except Exception:
            pass
    save_json(path, default)
    return json.loads(json.dumps(default))

def save_json(path, data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

def settings(): return load_json(SETTINGS_FILE, DEFAULT_SETTINGS)
def save_settings(d): save_json(SETTINGS_FILE,d)
def state():
    d = load_json(STATE_FILE, DEFAULT_STATE)
    # régi state.json kompatibilitás
    if "demo" not in d:
        d = DEFAULT_STATE.copy()
        save_json(STATE_FILE, d)
    if "live" not in d:
        d["live"] = DEFAULT_STATE["live"]
    if "demo" not in d:
        d["demo"] = DEFAULT_STATE["demo"]
    return d
def save_state(d): save_json(STATE_FILE,d)

def http_json(url, timeout=8):
    req=urllib.request.Request(url,headers={"User-Agent":"BinanceAutobot/0.3"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def get_ticker_24h(symbol=None):
    if symbol:
        return http_json(BINANCE+"/api/v3/ticker/24hr?symbol="+urllib.parse.quote(symbol))
    return http_json(BINANCE+"/api/v3/ticker/24hr")

def get_klines(symbol="BTCUSDT", interval="1m", limit=80):
    url=f"{BINANCE}/api/v3/klines?symbol={urllib.parse.quote(symbol)}&interval={interval}&limit={int(limit)}"
    raw=http_json(url)
    return [{
        "t":int(x[0]),"o":float(x[1]),"h":float(x[2]),"l":float(x[3]),
        "c":float(x[4]),"v":float(x[5])
    } for x in raw]

def sma(vals,n):
    if len(vals)<n or n<=0: return None
    return sum(vals[-n:])/n

def rsi(vals,n=14):
    if len(vals)<n+1: return 50.0
    gains=[]; losses=[]
    for a,b in zip(vals[-n-1:-1],vals[-n:]):
        d=b-a
        gains.append(max(d,0)); losses.append(max(-d,0))
    ag=sum(gains)/n; al=sum(losses)/n
    if al==0: return 100.0
    rs=ag/al
    return 100-(100/(1+rs))

def scan_top_usdt(limit=20):
    data=get_ticker_24h()
    arr=[x for x in data if x.get("symbol","").endswith("USDT")]
    arr=[x for x in arr if float(x.get("quoteVolume",0) or 0)>0]
    arr.sort(key=lambda x: float(x.get("quoteVolume",0) or 0), reverse=True)
    return arr[:limit]

def demo_reset():
    st=state()
    st["demo"]={"balance":100.0,"positions":{},"realized_pnl":0.0,"running":False,"trades":[]}
    st["last_msg"]="Demo reset kész: 100 USDC."
    save_state(st)
    return st

def demo_tick(symbol=None):
    cfg=settings()
    st=state()
    demo=st["demo"]
    symbol=symbol or cfg.get("symbol","BTCUSDT")
    candles=get_klines(symbol, "1m", 80)
    closes=[c["c"] for c in candles]
    price=closes[-1]
    fast=sma(closes,int(cfg.get("sma_fast",9))) or price
    slow=sma(closes,int(cfg.get("sma_slow",21))) or price
    rr=rsi(closes,int(cfg.get("rsi_len",14)))

    bal=float(demo.get("balance",100.0))
    pos=demo.setdefault("positions",{})
    p=pos.get(symbol)
    fee=float(cfg.get("fee_pct",0.10))/100.0
    risk=float(cfg.get("risk_pct",10.0))/100.0
    maxpos=int(cfg.get("max_positions",3))
    action="HOLD"

    if p:
        qty=float(p["qty"]); avg=float(p["avg"])
        pnl_pct=(price-avg)/avg*100 if avg else 0
        p["peak"]=max(float(p.get("peak",price)),price)
        trail_drop=(p["peak"]-price)/p["peak"]*100 if p["peak"] else 0

        sell = False
        reason = ""
        if pnl_pct >= float(cfg.get("min_profit_pct",10.0)) and fast < slow:
            sell=True; reason="profit + trend gyengül"
        elif pnl_pct >= 0.8 and trail_drop >= 0.35:
            sell=True; reason="trailing take profit"
        elif pnl_pct <= -1.2:
            sell=True; reason="stop loss"

        if sell:
            gross=qty*price
            net=gross*(1-fee)
            cost=qty*avg
            pnl=net-cost
            demo["balance"]=bal+net
            demo["realized_pnl"]=float(demo.get("realized_pnl",0))+pnl
            pos.pop(symbol,None)
            action=f"SELL {symbol} PnL {pnl:.3f} USDC ({reason})"
    else:
        if fast>slow and rr>52 and len(pos)<maxpos and bal>10:
            spend=min(bal*risk, bal, 25.0)
            qty=(spend*(1-fee))/price
            demo["balance"]=bal-spend
            pos[symbol]={"qty":qty,"avg":price,"peak":price,"ts":int(time.time())}
            action=f"BUY {symbol} {qty:.6f} @ {price:.4f}"

    demo.setdefault("trades",[]).append({"ts":int(time.time()),"symbol":symbol,"price":price,"action":action})
    demo["trades"]=demo["trades"][-80:]
    st["last_msg"]=action
    save_state(st)
    return {"state":st,"price":price,"rsi":rr,"fast":fast,"slow":slow,"action":action}
