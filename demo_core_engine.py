# -*- coding: utf-8 -*-
import json
import os
import time
import csv
import math
import random
import urllib.request

STATE_FILE = "demo_core_state.json"
LOG_DIR = "logs"
TRADE_LOG = os.path.join(LOG_DIR, "demo_core_trades.csv")
os.makedirs(LOG_DIR, exist_ok=True)

DEFAULT_STATE = {
    "base": "USDC",
    "balance": 100.0,
    "positions": {},
    "realized_pnl": 0.0,
    "running": False,
    "settings": {
        "risk_pct": 10.0,
        "max_positions": 3,
        "min_profit_pct": 10.0,
        "new_coin_min_profit_pct": 5.0,
        "trailing_drop_pct": 1.2,
        "stop_loss_pct": 2.0,
        "fee_pct": 0.10,
        "sma_fast": 9,
        "sma_slow": 21,
        "watchlist": ["BTCUSDT", "ETHUSDT", "DOGEUSDT"]
    },
    "last_action": "Demo core engine ready"
}

def load_state():
    if not os.path.exists(STATE_FILE):
        save_state(DEFAULT_STATE)
        return json.loads(json.dumps(DEFAULT_STATE))
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        for k, v in DEFAULT_STATE.items():
            d.setdefault(k, v)
        d.setdefault("settings", DEFAULT_STATE["settings"])
        return d
    except Exception:
        save_state(DEFAULT_STATE)
        return json.loads(json.dumps(DEFAULT_STATE))

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def log_trade(row):
    new = not os.path.exists(TRADE_LOG)
    with open(TRADE_LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts", "symbol", "side", "qty", "price", "pnl", "note"])
        w.writerow(row)

def http_json(url, timeout=6):
    req = urllib.request.Request(url, headers={"User-Agent": "BinanceAutobotDemoCore/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def fallback_prices(symbol, limit=60):
    base = 60000.0 if symbol.startswith("BTC") else 3000.0 if symbol.startswith("ETH") else 0.15
    out = []
    for i in range(limit):
        out.append(base + math.sin(i / 5.0) * base * 0.004 + random.uniform(-1, 1) * base * 0.001)
    return out

def get_closes(symbol, limit=60):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit={limit}"
        data = http_json(url)
        return [float(x[4]) for x in data]
    except Exception:
        return fallback_prices(symbol, limit)

def sma(values, length):
    if len(values) < length or length <= 0:
        return None
    return sum(values[-length:]) / length

def price(symbol):
    closes = get_closes(symbol, 3)
    return float(closes[-1])

def equity(state=None):
    state = state or load_state()
    total = float(state.get("balance", 0))
    for symbol, pos in state.get("positions", {}).items():
        try:
            total += float(pos["qty"]) * price(symbol)
        except Exception:
            pass
    return total

def reset_demo(balance=100.0):
    state = json.loads(json.dumps(DEFAULT_STATE))
    state["balance"] = float(balance)
    state["last_action"] = "Demo reset kész"
    save_state(state)
    return state

def buy(state, symbol, spend):
    p = price(symbol)
    fee = float(state["settings"].get("fee_pct", 0.10)) / 100.0
    spend = min(float(spend), float(state["balance"]))
    if spend <= 0:
        return "NO BUY: nincs egyenleg"

    qty = (spend * (1 - fee)) / p
    state["balance"] -= spend
    state["positions"][symbol] = {
        "qty": qty,
        "avg": p,
        "peak": p,
        "opened_ts": int(time.time())
    }
    note = f"BUY {symbol} spend={spend:.2f}"
    log_trade([int(time.time()), symbol, "BUY", qty, p, 0.0, note])
    return note

def sell(state, symbol, note="SELL"):
    pos = state["positions"].get(symbol)
    if not pos:
        return "NO SELL: nincs pozíció"

    p = price(symbol)
    qty = float(pos["qty"])
    avg = float(pos["avg"])
    fee = float(state["settings"].get("fee_pct", 0.10)) / 100.0

    gross = qty * p
    net = gross * (1 - fee)
    cost = qty * avg
    pnl = net - cost

    state["balance"] += net
    state["realized_pnl"] += pnl
    state["positions"].pop(symbol, None)

    log_trade([int(time.time()), symbol, "SELL", qty, p, pnl, note])
    return f"SELL {symbol} PnL={pnl:.4f} USDC | {note}"

def signal(symbol, settings):
    closes = get_closes(symbol, 80)
    if len(closes) < 25:
        return "HOLD", closes[-1] if closes else 0

    fast = sma(closes, int(settings.get("sma_fast", 9)))
    slow = sma(closes, int(settings.get("sma_slow", 21)))
    last = closes[-1]

    if fast and slow and fast > slow:
        return "BUY", last
    if fast and slow and fast < slow:
        return "SELL", last
    return "HOLD", last

def tick():
    state = load_state()
    settings = state["settings"]
    max_positions = int(settings.get("max_positions", 3))
    risk_pct = float(settings.get("risk_pct", 10.0)) / 100.0
    min_profit = float(settings.get("min_profit_pct", 10.0))
    trailing_drop = float(settings.get("trailing_drop_pct", 1.2))
    stop_loss = float(settings.get("stop_loss_pct", 2.0))

    actions = []

    # 1) Meglévő pozíciók kezelése
    for symbol in list(state["positions"].keys()):
        pos = state["positions"][symbol]
        p = price(symbol)
        avg = float(pos["avg"])
        pos["peak"] = max(float(pos.get("peak", p)), p)

        pnl_pct = ((p - avg) / avg) * 100 if avg else 0
        drop_from_peak = ((float(pos["peak"]) - p) / float(pos["peak"])) * 100 if pos["peak"] else 0
        sig, _ = signal(symbol, settings)

        if pnl_pct <= -stop_loss:
            actions.append(sell(state, symbol, f"STOP LOSS {pnl_pct:.2f}%"))
        elif pnl_pct >= min_profit and (drop_from_peak >= trailing_drop or sig == "SELL"):
            actions.append(sell(state, symbol, f"PROFIT HOLD EXIT {pnl_pct:.2f}%"))
        else:
            actions.append(f"HOLD {symbol} PnL={pnl_pct:.2f}%")

    # 2) Új belépés, ha van hely
    open_count = len(state["positions"])
    if open_count < max_positions:
        for symbol in settings.get("watchlist", []):
            if symbol in state["positions"]:
                continue
            sig, _ = signal(symbol, settings)
            if sig == "BUY" and len(state["positions"]) < max_positions:
                spend = max(0.0, float(state["balance"]) * risk_pct)
                if spend >= 5:
                    actions.append(buy(state, symbol, spend))
                    break

    state["last_action"] = " | ".join(actions) if actions else "HOLD"
    save_state(state)
    return {
        "ok": True,
        "action": state["last_action"],
        "balance": state["balance"],
        "positions": state["positions"],
        "realized_pnl": state["realized_pnl"],
        "equity": equity(state)
    }

if __name__ == "__main__":
    print(json.dumps(tick(), ensure_ascii=False, indent=2))
