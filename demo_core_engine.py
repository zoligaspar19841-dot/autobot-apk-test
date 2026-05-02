# -*- coding: utf-8 -*-
import json
import os
import time
import csv
import math
import random
import urllib.request

STATE_FILE = "demo_core_state.json"
SECRETS_FILE = "demo_core_secrets.json"
LOG_DIR = "logs"
TRADE_LOG = os.path.join(LOG_DIR, "demo_core_trades.csv")
AUDIT_LOG = os.path.join(LOG_DIR, "demo_core_audit.csv")
os.makedirs(LOG_DIR, exist_ok=True)







SECRETS_DEFAULTS = {
    "binance_api_key": "",
    "binance_api_secret": "",
    "openai_api_key": "",
    "email_smtp_host": "smtp.gmail.com",
    "email_smtp_port": "587",
    "email_user": "",
    "email_app_password": "",
    "email_to": "",
    "google_drive_token": "",
    "pc_sync_token": "",
    "ngrok_token": "",
}

AI_ADVISOR_DEFAULTS = {
    "ai_advisor_enabled": True,
    "ai_mode": "OFFLINE",
    "ai_min_confidence": 0.55,
    "ai_allow_auto_trade": False,
}

TRADE_SCREEN_DEFAULTS = {
    "order_type": "LIMIT_BBO",
    "use_bbo": True,
    "max_spread_pct": 0.25,
    "slippage_buffer_pct": 0.10,
    "min_orderbook_imbalance": 0.48,
    "tp_sl_enabled": True,
    "take_profit_pct": 3.0,
}

FEE_TAX_DEFAULTS = {
    "maker_fee_pct": 0.10,
    "taker_fee_pct": 0.10,
    "tax_enabled": True,
    "tax_pct": 15.0,
    "min_after_tax_profit_pct": 0.10,
}

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

    if "AI_ADVISOR_DEFAULTS" in globals():
        for k, v in AI_ADVISOR_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "TRADE_SCREEN_DEFAULTS" in globals():
        for k, v in TRADE_SCREEN_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "FEE_TAX_DEFAULTS" in globals():
        for k, v in FEE_TAX_DEFAULTS.items():
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
    pnl_info = pnl_breakdown(pnl, state.get("settings", {}))
    audit_event("SELL", note, {"symbol": symbol, "qty": qty, "price": p, "pnl": pnl, "pnl_breakdown": pnl_info, "profit_pct_breakdown": profit_pct_breakdown(((p - avg) / avg) * 100 if avg else 0, state.get("settings", {}))})
    return f"SELL {symbol} PnL={pnl:.4f} USDC | {note}"


def get_prices(symbol, limit=60):
    """
    Demo árlista fallback scannerhez / BBO-hoz.
    Ha később lesz live Binance klines/ticker adat, ezt lehet kiváltani.
    Most stabil, determinisztikus, symbol-függő demo ármozgást ad.
    """
    try:
        limit = int(limit or 60)
    except Exception:
        limit = 60

    symbol = str(symbol or "BTCUSDT").upper()

    base_map = {
        "BTCUSDT": 78836.41,
        "ETHUSDT": 2328.98,
        "DOGEUSDT": 0.168,
        "BNBUSDT": 618.54,
        "BNBBTC": 0.007863,
    }

    base = base_map.get(symbol, None)
    if base is None:
        seed = sum(ord(c) for c in symbol)
        base = 1.0 + (seed % 5000) / 10.0

    seed = sum(ord(c) for c in symbol)
    now_bucket = int(time.time() // 60)

    prices = []
    for i in range(limit):
        t = now_bucket - (limit - i)
        wave = math.sin((t + seed) / 7.0) * 0.006
        wave2 = math.sin((t + seed) / 17.0) * 0.003
        drift = ((i - limit / 2.0) / max(limit, 1)) * 0.002
        price = base * (1.0 + wave + wave2 + drift)
        if price <= 0:
            price = base
        prices.append(float(price))

    return prices


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
    min_after_tax_profit_pct = float(settings.get("min_after_tax_profit_pct", 0.10) or 0.10)

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
            tax_ok, tax_bd = is_after_tax_profit_ok(pnl_pct, settings)
            if tax_ok:
                actions.append(sell(state, symbol, f"PROFIT HOLD EXIT gross={pnl_pct:.2f}% after_tax={tax_bd.get('after_tax_pct'):.2f}% age={age_min:.1f}m peak_drop={drop_from_peak:.2f}%"))
            else:
                actions.append(f"HOLD {symbol} gross={pnl_pct:.2f}% after_tax={tax_bd.get('after_tax_pct'):.2f}% < min_after_tax={min_after_tax_profit_pct:.2f}%")
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
                    check = trade_screen_check(symbol, "BUY", settings)
                    if check.get("allowed"):
                        actions.append("BBO OK " + symbol + " limit=" + str(check.get("limit_price")))
                        actions.append(buy(state, symbol, spend))
                        audit_event("BBO_BUY_ALLOWED", symbol, check)
                        break
                    else:
                        actions.append("BBO GUARD TILT " + symbol + ": " + " | ".join(check.get("reasons", [])))
                        audit_event("BBO_BUY_BLOCKED", symbol, check)
                        continue

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


def fee_amount(amount, fee_pct):
    try:
        return float(amount) * (float(fee_pct) / 100.0)
    except Exception:
        return 0.0


def pnl_breakdown(gross_pnl, settings=None):
    settings = settings or load_state().get("settings", {})
    gross = float(gross_pnl or 0.0)
    taker_fee_pct = float(settings.get("taker_fee_pct", 0.10) or 0.10)
    tax_pct = float(settings.get("tax_pct", 15.0) or 15.0)
    tax_enabled = bool(settings.get("tax_enabled", True))

    fee = abs(gross) * (taker_fee_pct / 100.0)
    net = gross - fee

    tax = 0.0
    after_tax = net

    if tax_enabled and net > 0:
        tax = net * (tax_pct / 100.0)
        after_tax = net - tax

    return {
        "gross_pnl": round(gross, 8),
        "fee": round(fee, 8),
        "net_pnl": round(net, 8),
        "tax": round(tax, 8),
        "after_tax_pnl": round(after_tax, 8),
        "tax_pct": tax_pct,
        "taker_fee_pct": taker_fee_pct,
    }



def profit_pct_breakdown(gross_profit_pct, settings=None):
    """
    Konzervatív becslés: nyitás + zárás taker fee-vel számol.
    Cél: döntésnél csak olyan profit legyen elfogadva, ami fee + becsült adó után is pozitív.
    """
    settings = settings or load_state().get("settings", {})

    gross_pct = float(gross_profit_pct or 0.0)
    taker_fee_pct = float(settings.get("taker_fee_pct", 0.10) or 0.10)
    tax_pct = float(settings.get("tax_pct", 15.0) or 15.0)
    tax_enabled = bool(settings.get("tax_enabled", True))

    # vétel + eladás díj, konzervatívan
    roundtrip_fee_pct = taker_fee_pct * 2.0

    net_before_tax_pct = gross_pct - roundtrip_fee_pct

    tax_cut_pct = 0.0
    after_tax_pct = net_before_tax_pct

    if tax_enabled and net_before_tax_pct > 0:
        tax_cut_pct = net_before_tax_pct * (tax_pct / 100.0)
        after_tax_pct = net_before_tax_pct - tax_cut_pct

    return {
        "gross_profit_pct": round(gross_pct, 6),
        "roundtrip_fee_pct": round(roundtrip_fee_pct, 6),
        "net_before_tax_pct": round(net_before_tax_pct, 6),
        "tax_cut_pct": round(tax_cut_pct, 6),
        "after_tax_pct": round(after_tax_pct, 6),
        "positive_after_tax": after_tax_pct > 0,
    }


def is_after_tax_profit_ok(gross_profit_pct, settings=None):
    settings = settings or load_state().get("settings", {})
    min_after_tax = float(settings.get("min_after_tax_profit_pct", 0.10) or 0.10)
    bd = profit_pct_breakdown(gross_profit_pct, settings)
    return bd["after_tax_pct"] >= min_after_tax, bd

def portfolio_pnl_breakdown():
    st = load_state()
    settings = st.get("settings", {})
    gross = float(st.get("realized_pnl", 0.0) or 0.0)
    out = pnl_breakdown(gross, settings)
    out["ok"] = True
    out["realized_pnl"] = gross
    out["equity"] = equity(st)
    out["balance"] = st.get("balance", 0)
    return out


def demo_orderbook(symbol, settings=None):
    """
    Binance Trade screen demo modell:
    best bid / best ask / spread / bid-ask imbalance.
    Live módban ezt majd valós Binance orderbook API váltja ki.
    """
    settings = settings or load_state().get("settings", {})
    prices = get_prices(symbol, limit=30)
    price = float(prices[-1]) if prices else 1.0

    # Demo spread: volatilitásból becsülünk
    hi = max(prices[-10:]) if prices else price
    lo = min(prices[-10:]) if prices else price
    vol_pct = ((hi - lo) / price) * 100 if price else 0.0

    spread_pct = max(0.02, min(0.50, vol_pct / 10.0))
    half = spread_pct / 200.0

    best_bid = price * (1.0 - half)
    best_ask = price * (1.0 + half)

    # Demo imbalance: momentum alapján becsült bid/ask erő
    prev = float(prices[-5]) if prices and len(prices) >= 5 else price
    momentum_pct = ((price - prev) / prev) * 100 if prev else 0.0

    bid_ratio = 0.50 + max(-0.20, min(0.20, momentum_pct / 20.0))
    ask_ratio = 1.0 - bid_ratio

    return {
        "symbol": symbol,
        "mid": round(price, 8),
        "best_bid": round(best_bid, 8),
        "best_ask": round(best_ask, 8),
        "spread_pct": round(spread_pct, 6),
        "bid_ratio": round(bid_ratio, 4),
        "ask_ratio": round(ask_ratio, 4),
        "momentum_pct": round(momentum_pct, 4),
    }


def trade_screen_check(symbol, side="BUY", settings=None):
    """
    Binance Trade képernyőből átvett guard:
    - BBO ár
    - spread tiltás
    - slippage buffer
    - orderbook imbalance
    - fee + after-tax becsléshez használható ár
    """
    settings = settings or load_state().get("settings", {})
    ob = demo_orderbook(symbol, settings)

    max_spread = float(settings.get("max_spread_pct", 0.25) or 0.25)
    slip = float(settings.get("slippage_buffer_pct", 0.10) or 0.10)
    min_imb = float(settings.get("min_orderbook_imbalance", 0.48) or 0.48)

    side = str(side).upper()

    if side == "BUY":
        bbo_price = float(ob["best_ask"])
        limit_price = bbo_price * (1.0 + slip / 100.0)
        imbalance_ok = float(ob["bid_ratio"]) >= min_imb
    else:
        bbo_price = float(ob["best_bid"])
        limit_price = bbo_price * (1.0 - slip / 100.0)
        imbalance_ok = float(ob["ask_ratio"]) >= (1.0 - min_imb)

    spread_ok = float(ob["spread_pct"]) <= max_spread

    allowed = spread_ok and imbalance_ok

    reasons = []
    if not spread_ok:
        reasons.append(f"Spread túl nagy: {ob['spread_pct']}% > {max_spread}%")
    if not imbalance_ok:
        reasons.append(f"Orderbook imbalance gyenge: bid={ob['bid_ratio']} ask={ob['ask_ratio']}")

    if allowed:
        reasons.append("BBO/spread/orderbook OK")

    return {
        "ok": True,
        "allowed": allowed,
        "side": side,
        "symbol": symbol,
        "bbo_price": round(bbo_price, 8),
        "limit_price": round(limit_price, 8),
        "spread_pct": ob["spread_pct"],
        "bid_ratio": ob["bid_ratio"],
        "ask_ratio": ob["ask_ratio"],
        "reasons": reasons,
        "orderbook": ob,
    }


def ai_advisor(symbol=None):
    """
    Offline AI-segédlet alap.
    Nem küld adatot külső API-nak.
    A meglévő bot-adatokból készít döntésmagyarázatot.
    Később ezt lehet OpenAI / hírek / sentiment modullal bővíteni.
    """
    state = load_state()
    settings = state.get("settings", {})

    watch = settings.get("watchlist") or ["BTCUSDT"]
    if symbol is None:
        symbol = watch[0]
    symbol = str(symbol).upper()

    health = healthcheck()
    scanner = scan_symbols()
    scan_rows = scanner.get("all", [])

    row = None
    for r in scan_rows:
        if r.get("symbol") == symbol:
            row = r
            break

    if row is None:
        row = edge_score(symbol, settings)

    trade = trade_screen_check(symbol, "BUY", settings)

    execution_mode = str(settings.get("execution_mode", "AUTO")).upper()
    safe_mode = bool(state.get("safe_mode", False))
    running = bool(state.get("running", False))

    score = float(row.get("score", 0.0) or 0.0)
    min_conf = float(settings.get("ai_min_confidence", 0.55) or 0.55)

    recommendation = "HOLD"
    confidence = score
    reasons = []

    reasons.append(f"Scanner score: {score}")
    reasons.append(f"Scanner signal: {row.get('signal')}")
    reasons.append(f"Spread: {trade.get('spread_pct')}%")
    reasons.append(f"BBO allowed: {trade.get('allowed')}")
    reasons.append(f"Execution mode: {execution_mode}")
    reasons.append(f"Safe mode: {safe_mode}")
    reasons.append(f"Health: {health.get('status')}")

    if safe_mode:
        recommendation = "BLOCKED_SAFE_MODE"
        reasons.append("Safe mode aktív, új vétel tiltva.")
    elif execution_mode == "OFF":
        recommendation = "BLOCKED_EXECUTION_OFF"
        reasons.append("Execution mode OFF, új vétel tiltva.")
    elif not trade.get("allowed"):
        recommendation = "BLOCKED_TRADE_GUARD"
        reasons.extend(trade.get("reasons", []))
    elif score >= min_conf and row.get("signal") in ["BUY_CANDIDATE", "WATCH"]:
        if execution_mode == "MANUAL":
            recommendation = "MANUAL_REVIEW_BUY"
            reasons.append("Jelölt van, de MANUAL módban csak jóváhagyási javaslat.")
        else:
            recommendation = "BUY_CANDIDATE"
            reasons.append("Scanner + BBO guard alapján vételi jelölt.")
    else:
        recommendation = "HOLD"
        reasons.append("Nincs elég erős edge a vételhez.")

    # Konzervatív profit példa 1%-ra
    fee_tax_1pct = profit_pct_breakdown(1.0, settings)

    out = {
        "ok": True,
        "symbol": symbol,
        "recommendation": recommendation,
        "confidence": round(confidence, 4),
        "ai_mode": settings.get("ai_mode", "OFFLINE"),
        "execution_mode": execution_mode,
        "safe_mode": safe_mode,
        "running": running,
        "scanner": row,
        "trade_guard": trade,
        "fee_tax_example_1pct": fee_tax_1pct,
        "health_status": health.get("status"),
        "reasons": reasons,
    }

    audit_event("AI_ADVISOR", recommendation, out)
    state["last_action"] = "AI advisor: " + recommendation + " " + symbol
    save_state(state)

    return out


def mask_secret(value, keep=4):
    value = str(value or "")
    if not value:
        return ""
    if len(value) <= keep:
        return "*" * len(value)
    return "*" * max(0, len(value) - keep) + value[-keep:]


def load_secrets():
    if not os.path.exists(SECRETS_FILE):
        return dict(SECRETS_DEFAULTS)

    try:
        with open(SECRETS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}

    if not isinstance(data, dict):
        data = {}

    changed = False
    for k, v in SECRETS_DEFAULTS.items():
        if k not in data or data.get(k) is None:
            data[k] = v
            changed = True

    if changed:
        save_secrets(data)

    return data


def save_secrets(data):
    safe = dict(SECRETS_DEFAULTS)
    if isinstance(data, dict):
        for k in safe:
            if k in data:
                safe[k] = str(data.get(k) or "")

    with open(SECRETS_FILE, "w", encoding="utf-8") as f:
        json.dump(safe, f, ensure_ascii=False, indent=2)

    return safe


def update_secret(key, value):
    data = load_secrets()
    if key not in SECRETS_DEFAULTS:
        return {"ok": False, "error": "Unknown secret key: " + str(key)}

    data[key] = str(value or "")
    save_secrets(data)
    audit_event("SECRET_UPDATE", key, {"key": key, "has_value": bool(data[key])})
    return {"ok": True, "key": key, "has_value": bool(data[key])}


def secrets_status():
    data = load_secrets()

    status = {
        "ok": True,
        "binance_api": bool(data.get("binance_api_key")) and bool(data.get("binance_api_secret")),
        "openai_api": bool(data.get("openai_api_key")),
        "email": bool(data.get("email_user")) and bool(data.get("email_app_password")) and bool(data.get("email_to")),
        "google_drive": bool(data.get("google_drive_token")),
        "pc_sync": bool(data.get("pc_sync_token")),
        "ngrok": bool(data.get("ngrok_token")),
        "masked": {
            "binance_api_key": mask_secret(data.get("binance_api_key")),
            "binance_api_secret": mask_secret(data.get("binance_api_secret")),
            "openai_api_key": mask_secret(data.get("openai_api_key")),
            "email_user": data.get("email_user", ""),
            "email_to": data.get("email_to", ""),
            "email_app_password": mask_secret(data.get("email_app_password")),
            "google_drive_token": mask_secret(data.get("google_drive_token")),
            "pc_sync_token": mask_secret(data.get("pc_sync_token")),
            "ngrok_token": mask_secret(data.get("ngrok_token")),
        }
    }

    return status


def integration_test(kind):
    kind = str(kind or "").lower().strip()
    st = secrets_status()

    if kind == "binance":
        if st["binance_api"]:
            msg = "Binance API adatok megvannak. Live ellenőrzés később külön modulban."
            ok = True
        else:
            msg = "Binance API key/secret hiányzik."
            ok = False

    elif kind == "openai":
        if st["openai_api"]:
            msg = "OpenAI API key megvan. API hívás később külön modulban."
            ok = True
        else:
            msg = "OpenAI API key hiányzik."
            ok = False

    elif kind == "email":
        if st["email"]:
            msg = "E-mail beállítások megvannak. Tesztküldés később külön modulban."
            ok = True
        else:
            msg = "E-mail user/app password/címzett hiányzik."
            ok = False

    elif kind == "drive":
        if st["google_drive"]:
            msg = "Google Drive token megvan. Sync később külön modulban."
            ok = True
        else:
            msg = "Google Drive token hiányzik."
            ok = False

    elif kind == "pc":
        if st["pc_sync"]:
            msg = "PC sync token megvan. PC agent később külön modulban."
            ok = True
        else:
            msg = "PC sync token hiányzik."
            ok = False

    else:
        msg = "Ismeretlen integration test: " + str(kind)
        ok = False

    audit_event("INTEGRATION_TEST", kind, {"ok": ok, "message": msg})

    return {
        "ok": ok,
        "kind": kind,
        "message": msg,
        "status": st,
    }

if __name__ == "__main__":
    print(json.dumps(tick(), ensure_ascii=False, indent=2))
