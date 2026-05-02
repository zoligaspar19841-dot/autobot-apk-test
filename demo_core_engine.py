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
AUDIT_LOG = os.path.join(LOG_DIR, "demo_core_audit.csv")
os.makedirs(LOG_DIR, exist_ok=True)



SCANNER_DEFAULTS = {
    "scanner_enabled": True,
    "scanner_top_n": 5,
    "min_edge_score_open": 0.55,
    "min_edge_score_keep": 0.50,
    "max_scan_symbols": 20,
}

PROFIT_HOLD_DEFAULTS = {
    "hold_profit_minutes": 30,
    "time_in_trend_minutes_max": 240,
    "cooldown_after_exit_min": 10,
    "profit_erosion_guard_pct": 1.5,
    "execution_mode": "AUTO",
}

DEFAULT_STATE = {
    "base": "USDC",
    "balance": 100.0,
    "positions": {},
    "cooldowns": {},
    "realized_pnl": 0.0,
    "running": False,
    "safe_mode": False,
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
        "watchlist": ["BTCUSDT", "ETHUSDT", "DOGEUSDT"],
        "execution_mode": "AUTO",
        "hold_profit_minutes": 30,
        "time_in_trend_minutes_max": 240,
        "cooldown_after_exit_min": 10,
        "profit_erosion_guard_pct": 1.5
    },
    "last_action": "Demo core engine ready",
    "last_tick_ts": 0,
    "last_heartbeat_ts": 0
}




def merge_defaults(state):
    changed = False

    if not isinstance(state, dict):
        state = {}
        changed = True

    for k, v in DEFAULT_STATE.items():
        if k not in state or state.get(k) is None:
            state[k] = v
            changed = True

    if not isinstance(state.get("settings"), dict):
        state["settings"] = {}
        changed = True

    if not isinstance(state.get("positions"), dict):
        state["positions"] = {}
        changed = True

    if not isinstance(state.get("cooldowns"), dict):
        state["cooldowns"] = {}
        changed = True

    for k, v in DEFAULT_STATE.get("settings", {}).items():
        if k not in state["settings"] or state["settings"].get(k) is None:
            state["settings"][k] = v
            changed = True

    if "PROFIT_HOLD_DEFAULTS" in globals():
        for k, v in PROFIT_HOLD_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "SCANNER_DEFAULTS" in globals():
        for k, v in SCANNER_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    return state, changed



def load_state():
    if not os.path.exists(STATE_FILE):
        state = json.loads(json.dumps(DEFAULT_STATE))
        state, _ = merge_defaults(state)
        save_state(state)
        return state

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = json.loads(json.dumps(DEFAULT_STATE))

    state, changed = merge_defaults(state)

    if changed:
        save_state(state)

    return state


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def audit_event(event, detail="", data=None):
    try:
        new = not os.path.exists(AUDIT_LOG)
        with open(AUDIT_LOG, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["ts", "event", "detail", "data"])
            payload = ""
            if data is not None:
                try:
                    payload = json.dumps(data, ensure_ascii=False)
                except Exception:
                    payload = str(data)
            w.writerow([int(time.time()), event, detail, payload])
    except Exception:
        pass

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
    audit_event("RESET_DEMO", "Demo reset", {"balance": balance})
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
    audit_event("BUY", note, {"symbol": symbol, "qty": qty, "price": p, "spend": spend})
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
    state.setdefault("cooldowns", {})[symbol] = int(time.time())
    state["positions"].pop(symbol, None)

    log_trade([int(time.time()), symbol, "SELL", qty, p, pnl, note])
    audit_event("SELL", note, {"symbol": symbol, "qty": qty, "price": p, "pnl": pnl})
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
    safe_mode = bool(state.get("safe_mode", False))
    execution_mode = str(settings.get("execution_mode", "AUTO")).upper()
    max_positions = int(settings.get("max_positions", 3))
    risk_pct = float(settings.get("risk_pct", 10.0)) / 100.0
    min_profit = float(settings.get("min_profit_pct", 10.0))
    trailing_drop = float(settings.get("trailing_drop_pct", 1.2))
    stop_loss = float(settings.get("stop_loss_pct", 2.0))
    hold_profit_minutes = float(settings.get("hold_profit_minutes", 30))
    time_in_trend_minutes_max = float(settings.get("time_in_trend_minutes_max", 240))
    cooldown_after_exit_min = float(settings.get("cooldown_after_exit_min", 10))
    profit_erosion_guard_pct = float(settings.get("profit_erosion_guard_pct", 1.5))

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

        opened_ts = int(pos.get("opened_ts", int(time.time())) or int(time.time()))
        age_min = max(0.0, (time.time() - opened_ts) / 60.0)
        min_hold_ok = age_min >= hold_profit_minutes
        max_time_reached = age_min >= time_in_trend_minutes_max and pnl_pct > 0
        erosion_hit = drop_from_peak >= profit_erosion_guard_pct and pnl_pct > 0

        if pnl_pct <= -stop_loss:
            actions.append(sell(state, symbol, f"STOP LOSS {pnl_pct:.2f}%"))
        elif pnl_pct >= min_profit and ((min_hold_ok and (drop_from_peak >= trailing_drop or sig == "SELL")) or max_time_reached or erosion_hit):
            actions.append(sell(state, symbol, f"PROFIT HOLD EXIT {pnl_pct:.2f}% age={age_min:.1f}m peak_drop={drop_from_peak:.2f}%"))
        else:
            actions.append(f"HOLD {symbol} PnL={pnl_pct:.2f}% age={age_min:.1f}m")

    # 2) Új belépés, ha van hely és nincs safe mode
    open_count = len(state["positions"])
    if safe_mode:
        actions.append("SAFE MODE: új vétel tiltva")
    elif execution_mode == "OFF":
        actions.append("EXECUTION OFF: új vétel tiltva")
    elif open_count < max_positions:
        scan_order = settings.get("watchlist", [])
        if bool(settings.get("scanner_enabled", True)):
            try:
                scan_order = [r["symbol"] for r in scan_symbols().get("all", [])]
            except Exception:
                scan_order = settings.get("watchlist", [])

        for symbol in scan_order:
            if symbol in state["positions"]:
                continue

            last_exit = int(state.get("cooldowns", {}).get(symbol, 0) or 0)
            if cooldown_after_exit_min > 0 and last_exit:
                cooldown_left = cooldown_after_exit_min * 60 - (time.time() - last_exit)
                if cooldown_left > 0:
                    actions.append(f"COOLDOWN {symbol}: {int(cooldown_left)} sec")
                    continue

            sig, _ = signal(symbol, settings)
            if sig == "BUY" and len(state["positions"]) < max_positions:
                if execution_mode == "MANUAL":
                    msg = f"MANUAL JELZÉS: BUY lehetőség {symbol}"
                    actions.append(msg)
                    audit_event("MANUAL_SIGNAL", msg, {"symbol": symbol})
                    break
                spend = max(0.0, float(state["balance"]) * risk_pct)
                if spend >= 5:
                    actions.append(buy(state, symbol, spend))
                    break

    state["last_action"] = " | ".join(actions) if actions else "HOLD"
    state["last_tick_ts"] = int(time.time())
    state["last_heartbeat_ts"] = int(time.time())
    save_state(state)
    audit_event("TICK", state.get("last_action", ""), {"balance": state.get("balance"), "positions": list(state.get("positions", {}).keys())})
    return {
        "ok": True,
        "action": state["last_action"],
        "balance": state["balance"],
        "positions": state["positions"],
        "realized_pnl": state["realized_pnl"],
        "equity": equity(state)
    }


def panic_stop():
    state = load_state()
    state["running"] = False
    state["safe_mode"] = True
    state["last_action"] = "PANIC STOP: safe mode aktív, új vétel tiltva"
    save_state(state)
    audit_event("PANIC_STOP", state["last_action"], {"positions": list(state.get("positions", {}).keys())})
    return {
        "ok": True,
        "safe_mode": True,
        "running": False,
        "action": state["last_action"],
        "balance": state.get("balance", 0),
        "positions": state.get("positions", {}),
        "realized_pnl": state.get("realized_pnl", 0),
        "equity": equity(state)
    }

def safe_mode_off():
    state = load_state()
    state["safe_mode"] = False
    state["last_action"] = "Safe mode kikapcsolva"
    save_state(state)
    audit_event("SAFE_MODE_OFF", state["last_action"], {})
    return {
        "ok": True,
        "safe_mode": False,
        "running": state.get("running", False),
        "action": state["last_action"],
        "state": state
    }


def healthcheck():
    state = load_state()
    now = int(time.time())

    positions = state.get("positions", {})
    trade_log_exists = os.path.exists(TRADE_LOG)

    last_tick = int(state.get("last_tick_ts", 0) or 0)
    last_heartbeat = int(state.get("last_heartbeat_ts", 0) or 0)

    age_tick = now - last_tick if last_tick else None
    age_heartbeat = now - last_heartbeat if last_heartbeat else None

    warnings = []

    if state.get("safe_mode"):
        warnings.append("SAFE MODE aktív")

    if state.get("running") and age_tick is not None and age_tick > 120:
        warnings.append("Régi tick időbélyeg")

    if not trade_log_exists:
        warnings.append("Trade log még nem létezik")

    status = "OK" if not warnings else "FIGYELMEZTETÉS"

    state["last_heartbeat_ts"] = now
    save_state(state)
    audit_event("HEALTHCHECK", status, {"warnings": warnings, "running": state.get("running"), "safe_mode": state.get("safe_mode")})

    return {
        "ok": True,
        "status": status,
        "warnings": warnings,
        "running": bool(state.get("running")),
        "safe_mode": bool(state.get("safe_mode")),
        "positions_count": len(positions),
        "balance": state.get("balance", 0),
        "realized_pnl": state.get("realized_pnl", 0),
        "equity": equity(state),
        "trade_log_exists": trade_log_exists,
        "trade_log_path": TRADE_LOG,
        "last_tick_ts": last_tick,
        "last_heartbeat_ts": now,
        "last_tick_age_sec": age_tick,
        "last_heartbeat_age_sec": age_heartbeat,
        "last_action": state.get("last_action", "")
    }


def read_audit_log(limit=50):
    if not os.path.exists(AUDIT_LOG):
        return []
    try:
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            rows = [x.strip() for x in f.readlines() if x.strip()]
        return rows[-int(limit):]
    except Exception:
        return []


def set_execution_mode(mode):
    mode = str(mode).upper().strip()
    if mode not in ["AUTO", "MANUAL", "OFF"]:
        mode = "MANUAL"
    state = load_state()
    state.setdefault("settings", {})
    state["settings"]["execution_mode"] = mode
    state["last_action"] = "Execution mode: " + mode
    save_state(state)
    audit_event("EXECUTION_MODE", mode, {})
    return {"ok": True, "mode": mode, "state": state}


def edge_score(symbol, settings=None):
    settings = settings or load_state().get("settings", {})
    prices = get_prices(symbol, limit=60)

    if not prices or len(prices) < 25:
        return {
            "symbol": symbol,
            "score": 0.0,
            "signal": "NO_DATA",
            "price": 0.0,
            "trend_pct": 0.0,
            "momentum_pct": 0.0,
            "volatility_pct": 0.0,
        }

    price = float(prices[-1])
    prev = float(prices[-5])
    base = float(prices[-21])

    momentum_pct = ((price - prev) / prev) * 100 if prev else 0.0
    trend_pct = ((price - base) / base) * 100 if base else 0.0

    hi = max(prices[-21:])
    lo = min(prices[-21:])
    volatility_pct = ((hi - lo) / price) * 100 if price else 0.0

    score = 0.0

    if trend_pct > 0:
        score += min(0.35, trend_pct / 20.0)

    if momentum_pct > 0:
        score += min(0.35, momentum_pct / 10.0)

    if 0.3 <= volatility_pct <= 8.0:
        score += 0.20
    elif volatility_pct > 8.0:
        score += 0.05

    sig, _ = signal(symbol, settings)
    if sig == "BUY":
        score += 0.10
    elif sig == "SELL":
        score -= 0.20

    score = max(0.0, min(1.0, score))

    if score >= float(settings.get("min_edge_score_open", 0.55)):
        out_sig = "BUY_CANDIDATE"
    elif score >= float(settings.get("min_edge_score_keep", 0.50)):
        out_sig = "WATCH"
    else:
        out_sig = "WEAK"

    return {
        "symbol": symbol,
        "score": round(score, 4),
        "signal": out_sig,
        "price": round(price, 8),
        "trend_pct": round(trend_pct, 4),
        "momentum_pct": round(momentum_pct, 4),
        "volatility_pct": round(volatility_pct, 4),
    }


def scan_symbols():
    state = load_state()
    settings = state.get("settings", {})

    raw = settings.get("watchlist", ["BTCUSDT", "ETHUSDT", "DOGEUSDT"])
    max_scan = int(settings.get("max_scan_symbols", 20) or 20)
    top_n = int(settings.get("scanner_top_n", 5) or 5)

    symbols = []
    for x in raw:
        sym = str(x).strip().upper()
        if not sym:
            continue
        if not sym.endswith("USDT"):
            sym += "USDT"
        if sym not in symbols:
            symbols.append(sym)

    symbols = symbols[:max_scan]

    rows = []
    for sym in symbols:
        try:
            rows.append(edge_score(sym, settings))
        except Exception as e:
            rows.append({
                "symbol": sym,
                "score": 0.0,
                "signal": "ERROR",
                "error": str(e),
                "price": 0.0,
                "trend_pct": 0.0,
                "momentum_pct": 0.0,
                "volatility_pct": 0.0,
            })

    rows.sort(key=lambda r: float(r.get("score", 0)), reverse=True)

    result = {
        "ok": True,
        "top_n": top_n,
        "symbols_count": len(symbols),
        "candidates": rows[:top_n],
        "all": rows,
    }

    audit_event("SCAN_SYMBOLS", "Multi-symbol scanner", {
        "symbols_count": len(symbols),
        "top": [r.get("symbol") for r in rows[:top_n]]
    })

    state["last_action"] = "Scanner futott: top " + ", ".join([r.get("symbol", "?") for r in rows[:top_n]])
    save_state(state)

    return result

if __name__ == "__main__":
    print(json.dumps(tick(), ensure_ascii=False, indent=2))
