APP_VERSION = "0.4.9-demo-core"
WORKING_APK_REFERENCE = "APK 0.2.5 - utolsó ismert működő referencia"
# -*- coding: utf-8 -*-
import json
import glob
import shutil
import zipfile
import platform
import urllib.error
from email.message import EmailMessage
import smtplib
import secrets as py_secrets
import hashlib
import urllib.parse
import hmac
import base64
import os
import time
import csv
import math
import random
import urllib.request

STATE_FILE = "demo_core_state.json"
SECRETS_FILE = "demo_core_secrets.json"
SECRETS_ENC_FILE = "secrets.enc"
SECRETS_KEY_FILE = "demo_core_secret.key"
LOG_DIR = "logs"
PACKAGE_DIR = "packages"
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






















PRE_APK_SAFE_TEST_DEFAULTS = {
    "pre_apk_safe_test_enabled": True,
    "pre_apk_require_no_order_endpoint": True,
    "pre_apk_require_compile_ok": True,
    "pre_apk_require_master_status_ok": True,
    "pre_apk_min_readiness_score_pct": 70.0,
    "pre_apk_report_file": "logs/pre_apk_safe_report.json",
}

MASTER_STATUS_DEFAULTS = {
    "master_status_enabled": True,
    "master_status_show_next_steps": True,
    "master_status_show_modules": True,
    "master_status_show_missing": True,
}

TREND_AUTO_REFRESH_DEFAULTS = {
    "trend_auto_snapshot_enabled": True,
    "trend_auto_snapshot_interval_sec": 30,
    "trend_auto_snapshot_only_when_running": False,
    "dashboard_auto_refresh_enabled": True,
    "dashboard_auto_refresh_interval_sec": 15,
}

TREND_DASHBOARD_WIDGET_DEFAULTS = {
    "dashboard_trend_widget_enabled": True,
    "dashboard_trend_widget_view": "PROFIT",
    "dashboard_trend_widget_points": 80,
    "dashboard_show_selected_trend_point": True,
}

TREND_EXPORT_DEFAULTS = {
    "trend_export_enabled": True,
    "trend_time_format": "%Y-%m-%d %H:%M:%S",
    "trend_export_file": "logs/trend_history.csv",
}

TREND_CHART_DEFAULTS = {
    "trend_chart_enabled": True,
    "trend_chart_width": 60,
    "trend_selected_index": -1,
    "trend_show_crosshair_data": True,
}

DASHBOARD_TREND_DEFAULTS = {
    "dashboard_use_portfolio_cache": True,
    "trend_history_enabled": True,
    "trend_history_max_points": 300,
    "trend_view_mode": "PROFIT",
    "trend_supported_views": "EQUITY,PROFIT,TRADABLE,TOTAL_VALUE",
}

SPOT_PORTFOLIO_DEFAULTS = {
    "spot_sync_enabled": True,
    "spot_base_asset": "USDC",
    "spot_quote_assets": "USDC,USDT",
    "spot_safety_reserve": 10.0,
    "spot_max_tradeable_pct": 90.0,
    "spot_min_asset_value_usd": 0.01,
    "spot_last_sync_ts": 0,
    "portfolio_total_value_usd": 0.0,
    "portfolio_tradable_usd": 0.0,
}

STARTUP_SAFETY_DEFAULTS = {
    "startup_safety_summary_enabled": True,
    "first_run_require_admin_password_change": True,
    "first_run_require_secrets_review": True,
    "first_run_show_live_warning": True,
}

BINANCE_REAL_READONLY_DEFAULTS = {
    "binance_real_account_get_enabled": False,
    "binance_http_timeout_sec": 8,
    "binance_balance_preview_assets": "USDT,USDC,BTC,ETH,BNB,DOGE",
}

BINANCE_SIGNED_DEFAULTS = {
    "binance_base_url": "https://api.binance.com",
    "binance_signed_readonly_enabled": False,
    "binance_account_read_enabled": False,
    "binance_account_last_check_ts": 0,
    "binance_account_last_ok": False,
}

BINANCE_ACCOUNT_DEFAULTS = {
    "binance_account_check_enabled": True,
    "binance_test_order_enabled": True,
    "binance_test_order_symbol": "BTCUSDT",
    "binance_test_order_side": "BUY",
    "binance_test_order_type": "MARKET",
    "binance_test_order_quote_qty": 5.0,
    "binance_recv_window": 5000,
}

LIVE_EXECUTOR_GATE_DEFAULTS = {
    "live_executor_enabled": False,
    "live_hard_stop_enabled": True,
    "live_require_admin_active": True,
    "live_require_approval": True,
    "live_require_positive_after_tax": True,
    "live_min_after_tax_profit_pct": 0.10,
    "live_max_order_usdt_hard": 10.0,
    "live_block_if_health_warning": True,
    "live_block_if_spread_bad": True,
    "live_block_if_ai_hold": True,
}

APPROVAL_EXECUTOR_DEFAULTS = {
    "approval_required_for_manual": True,
    "approval_required_for_live": True,
    "dry_run_executor_enabled": True,
    "executor_last_action_ts": 0,
}

ADMIN_SECURITY_DEFAULTS = {
    "admin_username": "admin",
    "admin_password_hash": "",
    "admin_password_salt": "",
    "admin_session_active": False,
    "admin_session_ts": 0,
    "admin_timeout_sec": 300,
    "admin_must_change_default": True,
}

PATCH_MANAGER_DEFAULTS = {
    "patch_manager_enabled": True,
    "patch_require_admin": True,
    "patch_last_queue_ts": 0,
}

SYNC_DEFAULTS = {
    "sync_enabled": True,
    "sync_primary_device": "PHONE",
    "drive_sync_folder": "AutobotBackups",
    "pc_sync_folder": "PCSync",
    "auto_backup_on_start": False,
    "last_sync_export_ts": 0,
    "last_sync_import_ts": 0,
}

FIRSTRUN_DEFAULTS = {
    "first_run_done": False,
    "first_run_require_admin_change": True,
    "first_run_require_secrets_check": True,
}

SCHEDULE_DEFAULTS = {
    "schedules_enabled": True,
    "snapshot_enabled": True,
    "snapshot_time": "08:00",
    "price_trigger_enabled": True,
    "price_trigger_symbol": "BTCUSDT",
    "price_trigger_above": 0.0,
    "price_trigger_below": 0.0,
    "last_schedule_run_ts": 0,
}

LAUNCHPOOL_DEFAULTS = {
    "launchpool_enabled": True,
    "launchpool_min_apr": 5.0,
    "launchpool_watchlist": "BNB,FDUSD,USDT",
    "launchpool_scan_interval_min": 60,
    "last_launchpool_scan_ts": 0,
}

BACKTEST_DEFAULTS = {
    "backtest_symbol": "BTCUSDT",
    "backtest_limit": 240,
    "backtest_start_balance": 100.0,
    "backtest_risk_pct": 10.0,
    "backtest_fee_pct": 0.10,
}

BINANCE_LIVE_DEFAULTS = {
    "live_mode_enabled": False,
    "live_require_confirm": True,
    "live_allow_buy": False,
    "live_allow_sell": False,
    "live_max_order_usdt": 10.0,
    "live_warning_ack": False,
}

OPENAI_API_DEFAULTS = {
    "openai_model": "gpt-5-mini",
    "openai_timeout_sec": 25,
    "openai_api_enabled": False,
}

EMAIL_NOTIFY_DEFAULTS = {
    "email_notify_enabled": True,
    "email_on_buy": True,
    "email_on_sell": True,
    "email_on_error": True,
    "email_on_health_warning": True,
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

    if "PRE_APK_SAFE_TEST_DEFAULTS" in globals():
        for k, v in PRE_APK_SAFE_TEST_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "MASTER_STATUS_DEFAULTS" in globals():
        for k, v in MASTER_STATUS_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "TREND_AUTO_REFRESH_DEFAULTS" in globals():
        for k, v in TREND_AUTO_REFRESH_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "TREND_DASHBOARD_WIDGET_DEFAULTS" in globals():
        for k, v in TREND_DASHBOARD_WIDGET_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "TREND_EXPORT_DEFAULTS" in globals():
        for k, v in TREND_EXPORT_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "TREND_CHART_DEFAULTS" in globals():
        for k, v in TREND_CHART_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "DASHBOARD_TREND_DEFAULTS" in globals():
        for k, v in DASHBOARD_TREND_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "SPOT_PORTFOLIO_DEFAULTS" in globals():
        for k, v in SPOT_PORTFOLIO_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "STARTUP_SAFETY_DEFAULTS" in globals():
        for k, v in STARTUP_SAFETY_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "BINANCE_REAL_READONLY_DEFAULTS" in globals():
        for k, v in BINANCE_REAL_READONLY_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "BINANCE_SIGNED_DEFAULTS" in globals():
        for k, v in BINANCE_SIGNED_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "BINANCE_ACCOUNT_DEFAULTS" in globals():
        for k, v in BINANCE_ACCOUNT_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "LIVE_EXECUTOR_GATE_DEFAULTS" in globals():
        for k, v in LIVE_EXECUTOR_GATE_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "APPROVAL_EXECUTOR_DEFAULTS" in globals():
        for k, v in APPROVAL_EXECUTOR_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "ADMIN_SECURITY_DEFAULTS" in globals():
        for k, v in ADMIN_SECURITY_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "PATCH_MANAGER_DEFAULTS" in globals():
        for k, v in PATCH_MANAGER_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "SYNC_DEFAULTS" in globals():
        for k, v in SYNC_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "FIRSTRUN_DEFAULTS" in globals():
        for k, v in FIRSTRUN_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "SCHEDULE_DEFAULTS" in globals():
        for k, v in SCHEDULE_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "LAUNCHPOOL_DEFAULTS" in globals():
        for k, v in LAUNCHPOOL_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "BACKTEST_DEFAULTS" in globals():
        for k, v in BACKTEST_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "BINANCE_LIVE_DEFAULTS" in globals():
        for k, v in BINANCE_LIVE_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "OPENAI_API_DEFAULTS" in globals():
        for k, v in OPENAI_API_DEFAULTS.items():
            if k not in state["settings"] or state["settings"].get(k) is None:
                state["settings"][k] = v
                changed = True

    if "EMAIL_NOTIFY_DEFAULTS" in globals():
        for k, v in EMAIL_NOTIFY_DEFAULTS.items():
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
    try:
        notify_trade_event("BUY", note, {"symbol": symbol, "qty": qty, "price": p, "spend": spend})
    except Exception:
        pass
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
    try:
        notify_trade_event("SELL", note, {"symbol": symbol, "qty": qty, "price": p, "pnl": pnl})
    except Exception:
        pass
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
        "encrypted_file": os.path.exists(SECRETS_ENC_FILE),
        "plain_file_exists": os.path.exists(SECRETS_FILE),
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

    api_res = {"ok": False, "used_api": False, "reason": "not_requested"}
    try:
        if str(settings.get("ai_mode", "OFFLINE")).upper() == "API" and bool(settings.get("openai_api_enabled", False)):
            api_res = call_openai_advisor(symbol, out)
    except Exception as e:
        api_res = {"ok": False, "used_api": False, "reason": str(e)}

    out["openai_api"] = api_res

    audit_event("AI_ADVISOR", recommendation, out)
    state["last_action"] = "AI advisor: " + recommendation + " " + symbol
    save_state(state)

    return out



def _secret_key_bytes():
    """
    Helyi eszközön tárolt kulcs.
    GitHubra nem kerülhet, .gitignore védi.
    """
    env_key = os.environ.get("AUTOBOT_SECRET_KEY", "").strip()
    if env_key:
        raw = env_key.encode("utf-8")
    else:
        if not os.path.exists(SECRETS_KEY_FILE):
            token = py_secrets.token_urlsafe(48)
            with open(SECRETS_KEY_FILE, "w", encoding="utf-8") as f:
                f.write(token)
        with open(SECRETS_KEY_FILE, "r", encoding="utf-8") as f:
            raw = f.read().strip().encode("utf-8")

    return hashlib.sha256(raw).digest()


def _xor_crypt(data_bytes, key_bytes):
    """
    Minimal fallback titkosítás külső függőség nélkül.
    Nem banki HSM-szint, de sokkal jobb, mint plain JSON.
    Később Fernet/AES modulra cserélhető.
    """
    out = bytearray()
    for i, b in enumerate(data_bytes):
        out.append(b ^ key_bytes[i % len(key_bytes)])
    return bytes(out)


def encrypt_text(plain_text):
    key = _secret_key_bytes()
    raw = plain_text.encode("utf-8")
    enc = _xor_crypt(raw, key)
    return base64.urlsafe_b64encode(enc).decode("ascii")


def decrypt_text(enc_text):
    key = _secret_key_bytes()
    enc = base64.urlsafe_b64decode(str(enc_text).encode("ascii"))
    raw = _xor_crypt(enc, key)
    return raw.decode("utf-8")


def save_secrets_encrypted(data):
    safe = dict(SECRETS_DEFAULTS)
    if isinstance(data, dict):
        for k in safe:
            if k in data:
                safe[k] = str(data.get(k) or "")

    payload = json.dumps(safe, ensure_ascii=False, indent=2)
    enc = encrypt_text(payload)

    with open(SECRETS_ENC_FILE, "w", encoding="utf-8") as f:
        f.write(enc)

    return safe


def load_secrets_encrypted():
    if not os.path.exists(SECRETS_ENC_FILE):
        return None

    try:
        with open(SECRETS_ENC_FILE, "r", encoding="utf-8") as f:
            enc = f.read().strip()
        if not enc:
            return None
        plain = decrypt_text(enc)
        data = json.loads(plain)
        if not isinstance(data, dict):
            return None
        return data
    except Exception:
        return None


def migrate_plain_secrets_to_encrypted():
    """
    Ha van régi demo_core_secrets.json, átmásolja secrets.enc-be,
    majd a plain fájlt törli.
    """
    if os.path.exists(SECRETS_ENC_FILE):
        return {"ok": True, "migrated": False, "reason": "encrypted already exists"}

    if not os.path.exists(SECRETS_FILE):
        save_secrets_encrypted(dict(SECRETS_DEFAULTS))
        return {"ok": True, "migrated": False, "reason": "created empty encrypted secrets"}

    try:
        with open(SECRETS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = dict(SECRETS_DEFAULTS)

        save_secrets_encrypted(data)

        try:
            os.remove(SECRETS_FILE)
        except Exception:
            pass

        audit_event("SECRETS_MIGRATE_ENC", "plain json -> secrets.enc", {"removed_plain": not os.path.exists(SECRETS_FILE)})
        return {"ok": True, "migrated": True, "reason": "plain json migrated to encrypted"}
    except Exception as e:
        return {"ok": False, "migrated": False, "error": str(e)}


def mask_secret(value, keep=4):
    value = str(value or "")
    if not value:
        return ""
    if len(value) <= keep:
        return "*" * len(value)
    return "*" * max(0, len(value) - keep) + value[-keep:]



def load_secrets():
    # 1) plain -> enc migráció
    migrate_plain_secrets_to_encrypted()

    # 2) enc betöltés
    data = load_secrets_encrypted()

    if data is None:
        data = dict(SECRETS_DEFAULTS)
        save_secrets_encrypted(data)

    if not isinstance(data, dict):
        data = {}

    changed = False
    for k, v in SECRETS_DEFAULTS.items():
        if k not in data or data.get(k) is None:
            data[k] = v
            changed = True

    if changed:
        save_secrets_encrypted(data)

    return data



def save_secrets(data):
    safe = save_secrets_encrypted(data)

    # plain JSON-t nem tartunk meg
    try:
        if os.path.exists(SECRETS_FILE):
            os.remove(SECRETS_FILE)
    except Exception:
        pass

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


def email_config_status():
    sec = load_secrets()
    ok = bool(sec.get("email_user")) and bool(sec.get("email_app_password")) and bool(sec.get("email_to"))
    return {
        "ok": ok,
        "smtp_host": sec.get("email_smtp_host", "smtp.gmail.com"),
        "smtp_port": sec.get("email_smtp_port", "587"),
        "email_user": sec.get("email_user", ""),
        "email_to": sec.get("email_to", ""),
        "has_password": bool(sec.get("email_app_password")),
    }


def send_email_notification(subject, body):
    state = load_state()
    settings = state.get("settings", {})

    if not bool(settings.get("email_notify_enabled", True)):
        return {"ok": False, "sent": False, "reason": "email_notify_disabled"}

    sec = load_secrets()
    host = sec.get("email_smtp_host", "smtp.gmail.com") or "smtp.gmail.com"
    port = int(sec.get("email_smtp_port", "587") or 587)
    user = sec.get("email_user", "")
    password = sec.get("email_app_password", "")
    to_addr = sec.get("email_to", "")

    if not user or not password or not to_addr:
        return {"ok": False, "sent": False, "reason": "email_config_missing"}

    msg = EmailMessage()
    msg["Subject"] = str(subject)
    msg["From"] = user
    msg["To"] = to_addr
    msg.set_content(str(body))

    try:
        with smtplib.SMTP(host, port, timeout=20) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)

        audit_event("EMAIL_SENT", subject, {"to": to_addr})
        return {"ok": True, "sent": True, "to": to_addr}

    except Exception as e:
        audit_event("EMAIL_ERROR", subject, {"error": str(e)})
        return {"ok": False, "sent": False, "reason": str(e)}


def send_test_email():
    st = load_state()
    body = []
    body.append("Binance Autobot test email")
    body.append("")
    body.append("Status: működik, ha ezt látod.")
    body.append("Mode: " + str(st.get("settings", {}).get("execution_mode", "AUTO")))
    body.append("Safe mode: " + str(st.get("safe_mode", False)))
    body.append("Equity: " + str(equity(st)))
    body.append("")
    body.append("Ez automatikus teszt értesítés.")
    return send_email_notification("Binance Autobot - Test Email", "\n".join(body))


def notify_trade_event(kind, text, data=None):
    state = load_state()
    settings = state.get("settings", {})

    kind = str(kind or "").upper()

    if kind == "BUY" and not bool(settings.get("email_on_buy", True)):
        return {"ok": False, "sent": False, "reason": "email_on_buy_disabled"}

    if kind == "SELL" and not bool(settings.get("email_on_sell", True)):
        return {"ok": False, "sent": False, "reason": "email_on_sell_disabled"}

    subject = "Binance Autobot - " + kind
    body = []
    body.append(str(text))
    body.append("")
    body.append("Equity: " + str(equity(state)))
    body.append("Balance: " + str(state.get("balance")))
    body.append("Realized PnL: " + str(state.get("realized_pnl")))
    body.append("")
    if data is not None:
        try:
            body.append(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception:
            body.append(str(data))

    return send_email_notification(subject, "\n".join(body))



def openai_config_status():
    sec = load_secrets()
    state = load_state()
    settings = state.get("settings", {})

    has_key = bool(sec.get("openai_api_key"))
    api_enabled = bool(settings.get("openai_api_enabled", False))
    mode = str(settings.get("ai_mode", "OFFLINE")).upper()

    return {
        "ok": True,
        "has_key": has_key,
        "api_enabled": api_enabled,
        "ai_mode": mode,
        "model": settings.get("openai_model", "gpt-5-mini"),
        "ready": has_key and api_enabled and mode == "API",
    }


def build_ai_prompt(symbol, offline_result):
    scanner = offline_result.get("scanner", {})
    trade = offline_result.get("trade_guard", {})
    fee = offline_result.get("fee_tax_example_1pct", {})

    lines = []
    lines.append("Te egy óvatos kripto trading advisor vagy a felhasználó SAJÁT Binance botjához.")
    lines.append("Nem adhatsz túl kockázatos tanácsot. Ha bizonytalan a jel, HOLD/BLOCKED legyen.")
    lines.append("Adj rövid JSON választ magyarul.")
    lines.append("")
    lines.append("Elérhető adatok:")
    lines.append("symbol=" + str(symbol))
    lines.append("offline_recommendation=" + str(offline_result.get("recommendation")))
    lines.append("confidence=" + str(offline_result.get("confidence")))
    lines.append("execution_mode=" + str(offline_result.get("execution_mode")))
    lines.append("safe_mode=" + str(offline_result.get("safe_mode")))
    lines.append("health_status=" + str(offline_result.get("health_status")))
    lines.append("")
    lines.append("scanner=" + json.dumps(scanner, ensure_ascii=False))
    lines.append("trade_guard=" + json.dumps(trade, ensure_ascii=False))
    lines.append("fee_tax_1pct=" + json.dumps(fee, ensure_ascii=False))
    lines.append("")
    lines.append("Válasz JSON séma:")
    lines.append('{"decision":"BUY|HOLD|BLOCKED|MANUAL_REVIEW","confidence":0.0,"reason":"rövid magyar indoklás","risk_notes":["..."],"action_allowed":true}')
    return "\n".join(lines)


def call_openai_advisor(symbol, offline_result):
    """
    OpenAI API hívás opcionálisan.
    Csak akkor fut, ha:
    - ai_mode == API
    - openai_api_enabled == True
    - openai_api_key megvan secrets.enc-ben
    """
    cfg = openai_config_status()

    if not cfg.get("ready"):
        return {
            "ok": False,
            "used_api": False,
            "reason": "openai_not_ready",
            "config": cfg,
        }

    sec = load_secrets()
    state = load_state()
    settings = state.get("settings", {})

    api_key = sec.get("openai_api_key", "")
    model = settings.get("openai_model", "gpt-5-mini")
    timeout = int(settings.get("openai_timeout_sec", 25) or 25)

    prompt = build_ai_prompt(symbol, offline_result)

    payload = {
        "model": model,
        "input": prompt,
        "max_output_tokens": 500,
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            data = json.loads(raw)

        # Responses API text kinyerése többféle formátumból
        text = ""
        if isinstance(data, dict):
            if isinstance(data.get("output_text"), str):
                text = data.get("output_text")
            elif isinstance(data.get("output"), list):
                parts = []
                for item in data.get("output", []):
                    for c in item.get("content", []) if isinstance(item, dict) else []:
                        if isinstance(c, dict) and c.get("type") in ["output_text", "text"]:
                            parts.append(str(c.get("text", "")))
                text = "\n".join([x for x in parts if x])

        result = {
            "ok": True,
            "used_api": True,
            "model": model,
            "text": text,
            "raw_type": str(type(data)),
        }

        audit_event("OPENAI_ADVISOR_OK", symbol, {"model": model, "text_preview": text[:300]})
        return result

    except Exception as e:
        result = {
            "ok": False,
            "used_api": False,
            "reason": str(e),
            "model": model,
        }
        audit_event("OPENAI_ADVISOR_ERROR", symbol, {"error": str(e)})
        return result



def binance_live_status():
    """
    Binance Live API státusz.
    Ez még NEM küld megbízást.
    Csak azt ellenőrzi, hogy a Live módhoz szükséges adatok és kapcsolók rendben vannak-e.
    """
    state = load_state()
    settings = state.get("settings", {})
    sec = load_secrets()

    has_key = bool(sec.get("binance_api_key"))
    has_secret = bool(sec.get("binance_api_secret"))
    safe_mode = bool(state.get("safe_mode", False))

    live_mode_enabled = bool(settings.get("live_mode_enabled", False))
    live_warning_ack = bool(settings.get("live_warning_ack", False))
    live_require_confirm = bool(settings.get("live_require_confirm", True))
    live_allow_buy = bool(settings.get("live_allow_buy", False))
    live_allow_sell = bool(settings.get("live_allow_sell", False))
    execution_mode = str(settings.get("execution_mode", "AUTO")).upper()

    warnings = []

    if not has_key:
        warnings.append("Binance API key hiányzik.")

    if not has_secret:
        warnings.append("Binance API secret hiányzik.")

    if safe_mode:
        warnings.append("Safe Mode aktív: live vétel tiltva.")

    if execution_mode == "OFF":
        warnings.append("Execution mode OFF: bot nem kereskedhet.")

    if live_mode_enabled and live_require_confirm and not live_warning_ack:
        warnings.append("Live figyelmeztetés nincs jóváhagyva.")

    if live_mode_enabled and not live_allow_buy and not live_allow_sell:
        warnings.append("Live mód bekapcsolva, de BUY és SELL engedély nincs.")

    ready_for_live = (
        has_key
        and has_secret
        and live_mode_enabled
        and not safe_mode
        and execution_mode != "OFF"
        and (live_warning_ack or not live_require_confirm)
        and (live_allow_buy or live_allow_sell)
    )

    out = {
        "ok": True,
        "has_api_key": has_key,
        "has_api_secret": has_secret,
        "live_mode_enabled": live_mode_enabled,
        "live_require_confirm": live_require_confirm,
        "live_warning_ack": live_warning_ack,
        "live_allow_buy": live_allow_buy,
        "live_allow_sell": live_allow_sell,
        "live_max_order_usdt": settings.get("live_max_order_usdt", 10.0),
        "execution_mode": execution_mode,
        "safe_mode": safe_mode,
        "ready_for_live": ready_for_live,
        "warnings": warnings,
    }

    audit_event("BINANCE_LIVE_STATUS", "Live státusz ellenőrzés", out)
    return out


def acknowledge_live_warning():
    state = load_state()
    settings = state.setdefault("settings", {})
    settings["live_warning_ack"] = True
    save_state(state)
    audit_event("LIVE_WARNING_ACK", "Live warning jóváhagyva", {})
    return binance_live_status()


def disable_live_mode():
    state = load_state()
    settings = state.setdefault("settings", {})
    settings["live_mode_enabled"] = False
    settings["live_allow_buy"] = False
    settings["live_allow_sell"] = False
    save_state(state)
    audit_event("LIVE_MODE_DISABLED", "Live mód kikapcsolva", {})
    return binance_live_status()


def enable_live_check_only():
    """
    Csak Live státusz bekapcsolása ellenőrzéshez.
    Nem enged automatikus vételt/eladást.
    """
    state = load_state()
    settings = state.setdefault("settings", {})
    settings["live_mode_enabled"] = True
    settings["live_allow_buy"] = False
    settings["live_allow_sell"] = False
    save_state(state)
    audit_event("LIVE_CHECK_ONLY", "Live check only bekapcsolva", {})
    return binance_live_status()



def ensure_log_dir():
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception:
        pass


def sma_values(values, length):
    length = int(length or 1)
    out = []
    for i in range(len(values)):
        if i + 1 < length:
            out.append(None)
        else:
            out.append(sum(values[i + 1 - length:i + 1]) / length)
    return out


def backtest_symbol(symbol=None, limit=None):
    """
    Egyszerű demo backtest:
    SMA fast/slow keresztezés + fee számítás.
    Nem live kereskedés.
    """
    state = load_state()
    settings = state.get("settings", {})

    symbol = str(symbol or settings.get("backtest_symbol", "BTCUSDT")).upper()
    limit = int(limit or settings.get("backtest_limit", 240) or 240)

    start_balance = float(settings.get("backtest_start_balance", 100.0) or 100.0)
    risk_pct = float(settings.get("backtest_risk_pct", settings.get("risk_pct", 10.0)) or 10.0)
    fee_pct = float(settings.get("backtest_fee_pct", settings.get("taker_fee_pct", 0.10)) or 0.10)

    sma_fast_len = int(settings.get("sma_fast", 9) or 9)
    sma_slow_len = int(settings.get("sma_slow", 21) or 21)

    prices = get_prices(symbol, limit)
    fast = sma_values(prices, sma_fast_len)
    slow = sma_values(prices, sma_slow_len)

    balance = start_balance
    qty = 0.0
    entry = 0.0
    equity_curve = []
    trades = []
    peak_equity = start_balance
    max_dd = 0.0

    for i, price in enumerate(prices):
        price = float(price)
        f = fast[i]
        sl = slow[i]

        equity_now = balance + qty * price
        peak_equity = max(peak_equity, equity_now)
        dd = ((peak_equity - equity_now) / peak_equity) * 100 if peak_equity else 0.0
        max_dd = max(max_dd, dd)
        equity_curve.append(equity_now)

        if f is None or sl is None:
            continue

        if qty <= 0 and f > sl:
            spend = balance * (risk_pct / 100.0)
            fee = spend * (fee_pct / 100.0)
            net_spend = max(0.0, spend - fee)

            if net_spend > 0 and balance >= spend:
                qty = net_spend / price
                balance -= spend
                entry = price
                trades.append({
                    "i": i,
                    "type": "BUY",
                    "price": round(price, 8),
                    "qty": qty,
                    "fee": fee,
                    "balance": balance,
                })

        elif qty > 0 and f < sl:
            gross = qty * price
            fee = gross * (fee_pct / 100.0)
            net = gross - fee
            pnl = net - (qty * entry)
            pnl_pct = ((price - entry) / entry) * 100 if entry else 0.0

            balance += net
            trades.append({
                "i": i,
                "type": "SELL",
                "price": round(price, 8),
                "qty": qty,
                "fee": fee,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "balance": balance,
            })

            qty = 0.0
            entry = 0.0

    # záró equity
    final_equity = balance + qty * float(prices[-1])
    total_pnl = final_equity - start_balance
    total_pct = (total_pnl / start_balance) * 100 if start_balance else 0.0

    sell_trades = [t for t in trades if t.get("type") == "SELL"]
    wins = [t for t in sell_trades if float(t.get("pnl", 0)) > 0]
    losses = [t for t in sell_trades if float(t.get("pnl", 0)) <= 0]

    gross_win = sum(float(t.get("pnl", 0)) for t in wins)
    gross_loss = abs(sum(float(t.get("pnl", 0)) for t in losses))
    profit_factor = gross_win / gross_loss if gross_loss else (gross_win if gross_win else 0.0)
    winrate = (len(wins) / len(sell_trades) * 100.0) if sell_trades else 0.0

    result = {
        "ok": True,
        "symbol": symbol,
        "limit": limit,
        "start_balance": round(start_balance, 4),
        "final_equity": round(final_equity, 4),
        "total_pnl": round(total_pnl, 4),
        "total_pct": round(total_pct, 4),
        "trades_count": len(trades),
        "closed_trades": len(sell_trades),
        "winrate": round(winrate, 4),
        "profit_factor": round(profit_factor, 4),
        "max_drawdown_pct": round(max_dd, 4),
        "open_position": qty > 0,
        "trades": trades[-50:],
    }

    ensure_log_dir()
    report_path = os.path.join(LOG_DIR, "backtest_report.csv")

    with open(report_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["symbol", "metric", "value"])
        for k in ["start_balance", "final_equity", "total_pnl", "total_pct", "trades_count", "closed_trades", "winrate", "profit_factor", "max_drawdown_pct", "open_position"]:
            w.writerow([symbol, k, result.get(k)])

    audit_event("BACKTEST", "Backtest futtatva", result)
    state["last_action"] = "Backtest kész: " + symbol + " PnL=" + str(result["total_pct"]) + "%"
    save_state(state)

    return result


def read_backtest_report():
    path = os.path.join(LOG_DIR, "backtest_report.csv")
    if not os.path.exists(path):
        return {"ok": False, "error": "backtest_report.csv nincs még"}
    with open(path, "r", encoding="utf-8") as f:
        return {"ok": True, "path": path, "text": f.read()}


def diagnostics_status():
    state = load_state()
    sec_status = secrets_status() if "secrets_status" in globals() else {"ok": False}
    live_status = binance_live_status() if "binance_live_status" in globals() else {"ok": False}
    health = healthcheck() if "healthcheck" in globals() else {"ok": False}

    files = {}
    for fn in [
        "main.py",
        "demo_core_engine.py",
        "demo_core_state.json",
        "secrets.enc",
        "demo_core_secret.key",
        os.path.join(LOG_DIR, "demo_core_trades.csv"),
        os.path.join(LOG_DIR, "demo_core_audit.csv"),
        os.path.join(LOG_DIR, "backtest_report.csv"),
    ]:
        files[fn] = os.path.exists(fn)

    return {
        "ok": True,
        "version": APP_VERSION,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "state_keys": sorted(list(state.keys())),
        "settings_count": len(state.get("settings", {})),
        "positions_count": len(state.get("positions", {})),
        "running": state.get("running"),
        "safe_mode": state.get("safe_mode"),
        "last_action": state.get("last_action"),
        "files": files,
        "health": health,
        "secrets_ready": {
            "binance_api": sec_status.get("binance_api"),
            "openai_api": sec_status.get("openai_api"),
            "email": sec_status.get("email"),
        },
        "live_ready": live_status.get("ready_for_live"),
    }



def snapshot_state(label="manual"):
    ensure_log_dir()
    state = load_state()
    ts = int(time.time())
    path = os.path.join(LOG_DIR, f"snapshot_{label}_{ts}.json")

    payload = {
        "ts": ts,
        "label": label,
        "equity": equity(state),
        "balance": state.get("balance"),
        "realized_pnl": state.get("realized_pnl"),
        "positions": state.get("positions", {}),
        "settings": state.get("settings", {}),
        "last_action": state.get("last_action"),
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    audit_event("SNAPSHOT", "Snapshot mentve", {"path": path, "label": label})
    state["last_action"] = "Snapshot mentve: " + path
    save_state(state)

    return {
        "ok": True,
        "path": path,
        "label": label,
        "equity": payload["equity"],
    }


def price_trigger_check():
    state = load_state()
    settings = state.get("settings", {})

    symbol = str(settings.get("price_trigger_symbol", "BTCUSDT") or "BTCUSDT").upper()
    enabled = bool(settings.get("price_trigger_enabled", True))
    above = float(settings.get("price_trigger_above", 0.0) or 0.0)
    below = float(settings.get("price_trigger_below", 0.0) or 0.0)

    prices = get_prices(symbol, 5)
    price = float(prices[-1]) if prices else 0.0

    hit = False
    reasons = []

    if not enabled:
        reasons.append("Price trigger kikapcsolva.")
    else:
        if above > 0 and price >= above:
            hit = True
            reasons.append(f"{symbol} ár >= above trigger: {price} >= {above}")
        if below > 0 and price <= below:
            hit = True
            reasons.append(f"{symbol} ár <= below trigger: {price} <= {below}")
        if not hit:
            reasons.append(f"Nincs trigger: {symbol} ár={price}")

    out = {
        "ok": True,
        "enabled": enabled,
        "symbol": symbol,
        "price": price,
        "above": above,
        "below": below,
        "hit": hit,
        "reasons": reasons,
    }

    if hit:
        audit_event("PRICE_TRIGGER_HIT", symbol, out)
        try:
            send_email_notification("Binance Autobot - Price Trigger", json.dumps(out, ensure_ascii=False, indent=2))
        except Exception:
            pass

    return out


def run_schedules_once():
    state = load_state()
    settings = state.get("settings", {})

    if not bool(settings.get("schedules_enabled", True)):
        return {"ok": True, "ran": False, "reason": "schedules_disabled"}

    actions = []

    # kézi futtatáskor snapshot, ha engedélyezett
    if bool(settings.get("snapshot_enabled", True)):
        actions.append(snapshot_state("schedule"))

    actions.append(price_trigger_check())

    state = load_state()
    state.setdefault("settings", {})["last_schedule_run_ts"] = int(time.time())
    state["last_action"] = "Schedules futtatva"
    save_state(state)

    audit_event("SCHEDULES_RUN", "Schedules egyszeri futtatás", {"actions_count": len(actions)})

    return {
        "ok": True,
        "ran": True,
        "actions": actions,
    }


def launchpool_scan():
    state = load_state()
    settings = state.get("settings", {})

    enabled = bool(settings.get("launchpool_enabled", True))
    min_apr = float(settings.get("launchpool_min_apr", 5.0) or 5.0)
    raw_watch = str(settings.get("launchpool_watchlist", "BNB,FDUSD,USDT") or "")
    watch = [x.strip().upper() for x in raw_watch.split(",") if x.strip()]

    if not enabled:
        return {"ok": True, "enabled": False, "candidates": [], "message": "Launchpool watch kikapcsolva."}

    candidates = []
    base_symbols = ["BNB", "FDUSD", "USDT", "BTC", "ETH", "DOGE"]

    now_bucket = int(time.time() // 3600)

    for sym in base_symbols:
        seed = sum(ord(c) for c in sym) + now_bucket
        apr = round(2.0 + (seed % 1600) / 100.0, 2)
        score = round(apr / max(min_apr, 1.0), 4)

        if sym in watch or apr >= min_apr:
            candidates.append({
                "asset": sym,
                "apr": apr,
                "score": score,
                "watchlisted": sym in watch,
                "eligible": apr >= min_apr,
                "note": "demo launchpool/airdrop watch",
            })

    candidates.sort(key=lambda x: (x["eligible"], x["apr"]), reverse=True)

    state.setdefault("settings", {})["last_launchpool_scan_ts"] = int(time.time())
    state["last_action"] = "Launchpool scan kész"
    save_state(state)

    out = {
        "ok": True,
        "enabled": True,
        "min_apr": min_apr,
        "watchlist": watch,
        "candidates": candidates,
    }

    audit_event("LAUNCHPOOL_SCAN", "Launchpool scan", out)

    if any(c.get("eligible") for c in candidates):
        try:
            send_email_notification("Binance Autobot - Launchpool/Airdrop jelölt", json.dumps(out, ensure_ascii=False, indent=2))
        except Exception:
            pass

    return out



def ensure_package_dir():
    try:
        os.makedirs(PACKAGE_DIR, exist_ok=True)
    except Exception:
        pass


def safe_zip_add(zf, file_path, arc_name=None):
    """
    Csak biztonságos relatív fájlokat csomagolunk.
    Secrets / key / enc / env nem mehet bele.
    """
    if not file_path or not os.path.exists(file_path):
        return False

    blocked = [
        "secrets.enc",
        "demo_core_secret.key",
        "demo_core_secrets.json",
        ".env",
    ]

    base = os.path.basename(file_path)
    if base in blocked or base.endswith(".key") or base.endswith(".enc"):
        return False

    arc_name = arc_name or file_path
    arc_name = str(arc_name).replace("\\", "/").lstrip("/")

    if ".." in arc_name.split("/"):
        return False

    zf.write(file_path, arc_name)
    return True


def export_project_package(label="manual"):
    """
    Projekt csomag export ZIP.
    Secrets nélkül.
    GitHub backup mellé helyi/telefonos átadható csomag.
    """
    ensure_package_dir()
    ensure_log_dir()

    ts = int(time.time())
    path = os.path.join(PACKAGE_DIR, f"autobot_package_{label}_{ts}.zip")

    files = [
        "main.py",
        "demo_core_engine.py",
        "demo_core_state.json",
        "DEV_STATUS.md",
        "DEV_STATUS_SAFETY_CORE.md",
        ".gitignore",
    ]

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        added = []
        for f in files:
            if safe_zip_add(zf, f):
                added.append(f)

        # logs közül csak csv/json reportok, secrets nélkül
        if os.path.isdir(LOG_DIR):
            for root, dirs, fs in os.walk(LOG_DIR):
                for name in fs:
                    fp = os.path.join(root, name)
                    if name.endswith((".csv", ".json", ".txt")):
                        if safe_zip_add(zf, fp, fp):
                            added.append(fp)

        # kis státusz fájl a ZIP-be
        status = {
            "app_version": APP_VERSION,
            "working_apk_reference": WORKING_APK_REFERENCE,
            "created_ts": ts,
            "label": label,
            "note": "Secrets/key/env fájlok szándékosan nincsenek a csomagban.",
        }
        zf.writestr("PACKAGE_STATUS.json", json.dumps(status, ensure_ascii=False, indent=2))

    audit_event("PACKAGE_EXPORT", "Project package export", {"path": path, "label": label})
    st = load_state()
    st["last_action"] = "Package export: " + path
    save_state(st)

    return {
        "ok": True,
        "path": path,
        "label": label,
        "working_apk_reference": WORKING_APK_REFERENCE,
    }


def export_full_snapshot(label="manual"):
    """
    Snapshot ZIP: state + logs + státusz, secrets nélkül.
    """
    ensure_package_dir()
    ensure_log_dir()

    ts = int(time.time())
    path = os.path.join(PACKAGE_DIR, f"snapshot_{label}_{ts}.zip")

    snap = snapshot_state(label)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        safe_zip_add(zf, "demo_core_state.json", "demo_core_state.json")
        safe_zip_add(zf, snap.get("path"), snap.get("path"))

        if os.path.isdir(LOG_DIR):
            for root, dirs, fs in os.walk(LOG_DIR):
                for name in fs:
                    fp = os.path.join(root, name)
                    if name.endswith((".csv", ".json", ".txt")):
                        safe_zip_add(zf, fp, fp)

        zf.writestr("SNAPSHOT_STATUS.json", json.dumps({
            "app_version": APP_VERSION,
            "working_apk_reference": WORKING_APK_REFERENCE,
            "created_ts": ts,
            "label": label,
            "secrets_included": False,
        }, ensure_ascii=False, indent=2))

    audit_event("SNAPSHOT_EXPORT", "Snapshot zip export", {"path": path, "label": label})

    st = load_state()
    st["last_action"] = "Snapshot ZIP export: " + path
    save_state(st)

    return {
        "ok": True,
        "path": path,
        "label": label,
        "working_apk_reference": WORKING_APK_REFERENCE,
    }


def apk_reference_status():
    """
    Megmondja, melyik APK-t tekintjük utolsó működő referenciának.
    """
    return {
        "ok": True,
        "working_apk_reference": WORKING_APK_REFERENCE,
        "app_version": APP_VERSION,
        "build_policy": "APK buildhez csak külön stabil build-lépésben nyúlunk.",
        "current_dev_mode": "code_patch_only",
    }



def ensure_sync_dirs():
    state = load_state()
    settings = state.get("settings", {})

    drive_dir = str(settings.get("drive_sync_folder", "AutobotBackups") or "AutobotBackups")
    pc_dir = str(settings.get("pc_sync_folder", "PCSync") or "PCSync")

    for d in [drive_dir, pc_dir, PACKAGE_DIR, LOG_DIR]:
        try:
            os.makedirs(d, exist_ok=True)
        except Exception:
            pass

    return {
        "ok": True,
        "drive_sync_folder": drive_dir,
        "pc_sync_folder": pc_dir,
        "drive_exists": os.path.isdir(drive_dir),
        "pc_exists": os.path.isdir(pc_dir),
    }


def sync_status():
    state = load_state()
    settings = state.get("settings", {})
    dirs = ensure_sync_dirs()

    drive_dir = dirs.get("drive_sync_folder")
    pc_dir = dirs.get("pc_sync_folder")

    drive_files = []
    pc_files = []

    try:
        drive_files = sorted(glob.glob(os.path.join(drive_dir, "*.zip")))[-10:]
    except Exception:
        drive_files = []

    try:
        pc_files = sorted(glob.glob(os.path.join(pc_dir, "*.zip")))[-10:]
    except Exception:
        pc_files = []

    return {
        "ok": True,
        "sync_enabled": bool(settings.get("sync_enabled", True)),
        "primary_device": settings.get("sync_primary_device", "PHONE"),
        "drive_sync_folder": drive_dir,
        "pc_sync_folder": pc_dir,
        "drive_files_count": len(drive_files),
        "pc_files_count": len(pc_files),
        "last_drive_files": drive_files,
        "last_pc_files": pc_files,
        "last_sync_export_ts": settings.get("last_sync_export_ts", 0),
        "last_sync_import_ts": settings.get("last_sync_import_ts", 0),
    }


def export_sync_bundle(target="drive"):
    """
    Sync ZIP export secrets nélkül.
    target: drive / pc
    """
    state = load_state()
    settings = state.get("settings", {})

    if not bool(settings.get("sync_enabled", True)):
        return {"ok": False, "reason": "sync_disabled"}

    dirs = ensure_sync_dirs()
    target = str(target or "drive").lower().strip()

    if target == "pc":
        out_dir = dirs.get("pc_sync_folder")
    else:
        out_dir = dirs.get("drive_sync_folder")

    snap = export_full_snapshot("sync_" + target)
    src = snap.get("path")

    ts = int(time.time())
    dst = os.path.join(out_dir, f"autobot_sync_{target}_{ts}.zip")

    shutil.copyfile(src, dst)

    state = load_state()
    state.setdefault("settings", {})["last_sync_export_ts"] = ts
    state["last_action"] = "Sync export: " + dst
    save_state(state)

    audit_event("SYNC_EXPORT", "Sync export " + target, {"path": dst, "target": target})

    return {
        "ok": True,
        "target": target,
        "path": dst,
        "source_snapshot": src,
        "secrets_included": False,
    }


def import_latest_sync_bundle(source="drive"):
    """
    Biztonságos import: csak demo_core_state.json-t és logs fájlokat enged.
    Secrets/key/env import tiltva.
    """
    dirs = ensure_sync_dirs()
    source = str(source or "drive").lower().strip()

    if source == "pc":
        folder = dirs.get("pc_sync_folder")
    else:
        folder = dirs.get("drive_sync_folder")

    files = sorted(glob.glob(os.path.join(folder, "*.zip")))
    if not files:
        return {"ok": False, "reason": "no_sync_zip_found", "folder": folder}

    latest = files[-1]

    imported = []
    blocked = []

    with zipfile.ZipFile(latest, "r") as zf:
        for name in zf.namelist():
            clean = name.replace("\\", "/").lstrip("/")

            if ".." in clean.split("/"):
                blocked.append(clean)
                continue

            base = os.path.basename(clean)

            if base in ["secrets.enc", "demo_core_secret.key", "demo_core_secrets.json", ".env"] or base.endswith(".key") or base.endswith(".enc"):
                blocked.append(clean)
                continue

            allowed = False
            if clean == "demo_core_state.json":
                allowed = True
            if clean.startswith("logs/") and base.endswith((".csv", ".json", ".txt")):
                allowed = True

            if not allowed:
                blocked.append(clean)
                continue

            target = clean
            parent = os.path.dirname(target)
            if parent:
                os.makedirs(parent, exist_ok=True)

            with zf.open(name) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)

            imported.append(clean)

    state = load_state()
    state.setdefault("settings", {})["last_sync_import_ts"] = int(time.time())
    state["last_action"] = "Sync import: " + latest
    save_state(state)

    audit_event("SYNC_IMPORT", "Sync import " + source, {"zip": latest, "imported": imported, "blocked": blocked})

    return {
        "ok": True,
        "source": source,
        "zip": latest,
        "imported": imported,
        "blocked": blocked,
    }


def first_run_status():
    """
    Első indítási ellenőrző lista.
    Nem módosít secretet, csak jelzi, mi hiányzik.
    """
    state = load_state()
    settings = state.get("settings", {})
    sec = secrets_status() if "secrets_status" in globals() else {"ok": False}
    live = binance_live_status() if "binance_live_status" in globals() else {"ok": False}
    email = email_config_status() if "email_config_status" in globals() else {"ok": False}
    openai = openai_config_status() if "openai_config_status" in globals() else {"ok": False}

    checklist = []

    checklist.append({
        "id": "secrets_file",
        "label": "Titkosított secrets fájl",
        "ok": os.path.exists(SECRETS_ENC_FILE),
    })

    checklist.append({
        "id": "binance_api",
        "label": "Binance API key/secret megadva",
        "ok": bool(sec.get("binance_api")),
    })

    checklist.append({
        "id": "email",
        "label": "E-mail értesítés beállítva",
        "ok": bool(email.get("ok")),
    })

    checklist.append({
        "id": "openai",
        "label": "OpenAI API kulcs megadva",
        "ok": bool(openai.get("has_key")),
    })

    checklist.append({
        "id": "sync_dirs",
        "label": "Drive/PC sync mappák létrehozva",
        "ok": bool(ensure_sync_dirs().get("drive_exists")) and bool(ensure_sync_dirs().get("pc_exists")),
    })

    checklist.append({
        "id": "live_safe",
        "label": "Live mód biztonsági állapot ellenőrizve",
        "ok": live.get("ok") is True,
    })

    required_missing = [x for x in checklist if not x.get("ok")]

    out = {
        "ok": True,
        "first_run_done": bool(settings.get("first_run_done", False)),
        "missing_count": len(required_missing),
        "ready": len(required_missing) == 0,
        "checklist": checklist,
    }

    audit_event("FIRST_RUN_STATUS", "First run státusz", out)
    return out


def mark_first_run_done():
    state = load_state()
    state.setdefault("settings", {})["first_run_done"] = True
    state["last_action"] = "First-run készre állítva"
    save_state(state)
    audit_event("FIRST_RUN_DONE", "First-run kész", {})
    return first_run_status()



def _admin_hash(password, salt):
    return hashlib.sha256((str(salt) + "::" + str(password)).encode("utf-8")).hexdigest()


def _admin_ensure_initialized():
    state = load_state()
    settings = state.setdefault("settings", {})
    changed = False

    if not settings.get("admin_password_salt"):
        settings["admin_password_salt"] = py_secrets.token_urlsafe(24)
        changed = True

    if not settings.get("admin_password_hash"):
        settings["admin_password_hash"] = _admin_hash("admin", settings["admin_password_salt"])
        settings["admin_must_change_default"] = True
        changed = True

    if changed:
        save_state(state)

    return load_state()


def admin_status():
    state = _admin_ensure_initialized()
    settings = state.get("settings", {})

    active = bool(settings.get("admin_session_active", False))
    ts = int(settings.get("admin_session_ts", 0) or 0)
    timeout = int(settings.get("admin_timeout_sec", 300) or 300)
    now = int(time.time())

    expired = False
    if active and ts and now - ts > timeout:
        expired = True
        settings["admin_session_active"] = False
        settings["admin_session_ts"] = 0
        state["last_action"] = "Admin session lejárt"
        save_state(state)
        active = False

    return {
        "ok": True,
        "admin_username": settings.get("admin_username", "admin"),
        "admin_active": active,
        "admin_timeout_sec": timeout,
        "seconds_left": max(0, timeout - (now - ts)) if active and ts else 0,
        "expired": expired,
        "must_change_default": bool(settings.get("admin_must_change_default", True)),
    }


def admin_login(username, password):
    state = _admin_ensure_initialized()
    settings = state.get("settings", {})

    username = str(username or "").strip()
    password = str(password or "")

    ok = (
        username == str(settings.get("admin_username", "admin"))
        and _admin_hash(password, settings.get("admin_password_salt", "")) == settings.get("admin_password_hash", "")
    )

    if ok:
        settings["admin_session_active"] = True
        settings["admin_session_ts"] = int(time.time())
        state["last_action"] = "Admin login OK"
        save_state(state)
        audit_event("ADMIN_LOGIN", "Admin login OK", {"username": username})
    else:
        audit_event("ADMIN_LOGIN_FAIL", "Admin login fail", {"username": username})

    out = admin_status()
    out["login_ok"] = ok
    return out


def admin_logout():
    state = load_state()
    settings = state.setdefault("settings", {})
    settings["admin_session_active"] = False
    settings["admin_session_ts"] = 0
    state["last_action"] = "Admin logout"
    save_state(state)
    audit_event("ADMIN_LOGOUT", "Admin logout", {})
    return admin_status()


def admin_change_password(old_password, new_password):
    state = _admin_ensure_initialized()
    settings = state.get("settings", {})

    old_password = str(old_password or "")
    new_password = str(new_password or "")

    if len(new_password) < 4:
        return {"ok": False, "changed": False, "error": "Az új jelszó legalább 4 karakter legyen."}

    if _admin_hash(old_password, settings.get("admin_password_salt", "")) != settings.get("admin_password_hash", ""):
        return {"ok": False, "changed": False, "error": "Rossz régi jelszó."}

    salt = py_secrets.token_urlsafe(24)
    settings["admin_password_salt"] = salt
    settings["admin_password_hash"] = _admin_hash(new_password, salt)
    settings["admin_must_change_default"] = False
    settings["admin_session_active"] = False
    settings["admin_session_ts"] = 0
    save_state(state)

    audit_event("ADMIN_PASSWORD_CHANGED", "Admin jelszó cserélve", {})
    return {"ok": True, "changed": True}


def patch_manager_status():
    st = load_state()
    cfg = st.get("settings", {})
    adm = admin_status()
    qf = os.path.join(LOG_DIR, "patch_queue.jsonl")

    return {
        "ok": True,
        "enabled": bool(cfg.get("patch_manager_enabled", True)),
        "require_admin": bool(cfg.get("patch_require_admin", True)),
        "admin_active": adm.get("admin_active"),
        "queue_file": qf,
        "queue_exists": os.path.exists(qf),
        "allowed_paths": ["main.py", "demo_core_engine.py", "DEV_STATUS*.md", "README*.md"],
    }


def _patch_path_allowed(path):
    path = str(path or "").strip().replace("\\", "/").lstrip("/")
    if not path or ".." in path.split("/"):
        return False, "Tiltott path."

    if path in ["main.py", "demo_core_engine.py"]:
        return True, "OK"

    base = os.path.basename(path)
    if base.startswith("DEV_STATUS") and base.endswith(".md"):
        return True, "OK"

    if base.startswith("README") and base.endswith(".md"):
        return True, "OK"

    return False, "Nem engedélyezett fájl."


def queue_patch_request(path, description, content_preview=""):
    ensure_log_dir()

    st = load_state()
    cfg = st.setdefault("settings", {})

    if not bool(cfg.get("patch_manager_enabled", True)):
        return {"ok": False, "queued": False, "error": "Patch manager kikapcsolva."}

    if bool(cfg.get("patch_require_admin", True)) and not admin_status().get("admin_active"):
        return {"ok": False, "queued": False, "error": "Admin login szükséges."}

    allowed, reason = _patch_path_allowed(path)
    if not allowed:
        return {"ok": False, "queued": False, "error": reason}

    row = {
        "ts": int(time.time()),
        "path": str(path),
        "description": str(description or ""),
        "content_preview": str(content_preview or "")[:1000],
        "status": "QUEUED",
    }

    qf = os.path.join(LOG_DIR, "patch_queue.jsonl")
    with open(qf, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\\n")

    cfg["patch_last_queue_ts"] = row["ts"]
    st["last_action"] = "Patch queued: " + str(path)
    save_state(st)
    audit_event("PATCH_QUEUED", "Patch queued", row)

    return {"ok": True, "queued": True, "row": row, "queue_file": qf}


def read_patch_queue(limit=20):
    qf = os.path.join(LOG_DIR, "patch_queue.jsonl")
    if not os.path.exists(qf):
        return {"ok": True, "items": [], "queue_file": qf}

    items = []
    with open(qf, "r", encoding="utf-8") as f:
        for line in f:
            try:
                items.append(json.loads(line))
            except Exception:
                pass

    return {"ok": True, "items": items[-int(limit or 20):], "queue_file": qf}



def _approval_file():
    ensure_log_dir()
    return os.path.join(LOG_DIR, "approvals.jsonl")


def create_approval_request(action, symbol, side, amount, reason="", data=None):
    """
    Manuális / AI / Live előtti approval request.
    Ez még NEM kereskedik.
    """
    state = load_state()
    settings = state.get("settings", {})

    req = {
        "id": "APR-" + str(int(time.time())) + "-" + str(len(read_approval_queue().get("items", [])) + 1),
        "ts": int(time.time()),
        "status": "PENDING",
        "action": str(action or "TRADE_REQUEST"),
        "symbol": str(symbol or "").upper(),
        "side": str(side or "").upper(),
        "amount": float(amount or 0),
        "reason": str(reason or ""),
        "data": data or {},
        "execution_mode": settings.get("execution_mode", "AUTO"),
        "live_mode_enabled": settings.get("live_mode_enabled", False),
        "dry_run": True,
    }

    with open(_approval_file(), "a", encoding="utf-8") as f:
        f.write(json.dumps(req, ensure_ascii=False) + "\n")

    audit_event("APPROVAL_CREATED", "Approval request created", req)
    state["last_action"] = "Approval pending: " + req["id"]
    save_state(state)

    return {"ok": True, "request": req}


def read_approval_queue(limit=50):
    path = _approval_file()
    if not os.path.exists(path):
        return {"ok": True, "items": [], "path": path}

    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                items.append(json.loads(line))
            except Exception:
                pass

    return {"ok": True, "items": items[-int(limit or 50):], "path": path}


def _rewrite_approval_queue(items):
    path = _approval_file()
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def update_approval_status(request_id, status, note=""):
    adm = admin_status()
    if not adm.get("admin_active"):
        return {"ok": False, "error": "Admin login szükséges."}

    q = read_approval_queue(500)
    items = q.get("items", [])

    found = None
    for item in items:
        if item.get("id") == request_id:
            item["status"] = status
            item["review_ts"] = int(time.time())
            item["review_note"] = str(note or "")
            found = item
            break

    if not found:
        return {"ok": False, "error": "Approval ID nem található."}

    _rewrite_approval_queue(items)
    audit_event("APPROVAL_" + str(status).upper(), "Approval státusz módosítva", found)

    return {"ok": True, "request": found}


def approve_latest_pending(note=""):
    q = read_approval_queue(500)
    pending = [x for x in q.get("items", []) if x.get("status") == "PENDING"]
    if not pending:
        return {"ok": False, "error": "Nincs pending approval."}
    return update_approval_status(pending[-1].get("id"), "APPROVED", note)


def reject_latest_pending(note=""):
    q = read_approval_queue(500)
    pending = [x for x in q.get("items", []) if x.get("status") == "PENDING"]
    if not pending:
        return {"ok": False, "error": "Nincs pending approval."}
    return update_approval_status(pending[-1].get("id"), "REJECTED", note)


def dry_run_execute_request(req):
    """
    Dry-run executor:
    - nem hív Binance API-t
    - nem küld valódi megbízást
    - csak naplózza, hogy mit tenne
    """
    state = load_state()
    settings = state.get("settings", {})

    if not bool(settings.get("dry_run_executor_enabled", True)):
        return {"ok": False, "executed": False, "error": "Dry-run executor kikapcsolva."}

    side = str(req.get("side", "")).upper()
    symbol = str(req.get("symbol", "")).upper()
    amount = float(req.get("amount", 0) or 0)

    if side not in ["BUY", "SELL"]:
        return {"ok": False, "executed": False, "error": "Csak BUY/SELL támogatott."}

    if not symbol:
        return {"ok": False, "executed": False, "error": "Symbol hiányzik."}

    if amount <= 0:
        return {"ok": False, "executed": False, "error": "Amount <= 0."}

    live = binance_live_status()
    trade_guard = trade_screen_check(symbol, side, settings) if "trade_screen_check" in globals() else {"ok": True}

    out = {
        "ok": True,
        "executed": True,
        "dry_run": True,
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "live_ready": live.get("ready_for_live"),
        "trade_guard_ok": trade_guard.get("ok"),
        "message": "DRY-RUN: valódi Binance megbízás NEM lett elküldve.",
        "request_id": req.get("id"),
    }

    settings["executor_last_action_ts"] = int(time.time())
    state["last_action"] = "Dry-run executor: " + side + " " + symbol
    save_state(state)

    audit_event("DRY_RUN_EXECUTOR", "Dry-run executor", out)

    return out


def execute_latest_approved_dry_run():
    adm = admin_status()
    if not adm.get("admin_active"):
        return {"ok": False, "executed": False, "error": "Admin login szükséges."}

    q = read_approval_queue(500)
    approved = [x for x in q.get("items", []) if x.get("status") == "APPROVED"]

    if not approved:
        return {"ok": False, "executed": False, "error": "Nincs approved request."}

    req = approved[-1]
    res = dry_run_execute_request(req)

    items = q.get("items", [])
    for item in items:
        if item.get("id") == req.get("id"):
            item["status"] = "DRY_RUN_EXECUTED" if res.get("ok") else "EXECUTION_ERROR"
            item["execute_ts"] = int(time.time())
            item["execute_result"] = res
            break

    _rewrite_approval_queue(items)

    return res


def approval_executor_status():
    state = load_state()
    settings = state.get("settings", {})
    q = read_approval_queue(500)
    items = q.get("items", [])

    return {
        "ok": True,
        "approval_required_for_manual": settings.get("approval_required_for_manual", True),
        "approval_required_for_live": settings.get("approval_required_for_live", True),
        "dry_run_executor_enabled": settings.get("dry_run_executor_enabled", True),
        "pending_count": len([x for x in items if x.get("status") == "PENDING"]),
        "approved_count": len([x for x in items if x.get("status") == "APPROVED"]),
        "executed_count": len([x for x in items if x.get("status") == "DRY_RUN_EXECUTED"]),
        "last_items": items[-10:],
    }



def live_order_safety_gate(req=None):
    """
    Végső live order előtti safety gate.
    Ez NEM küld Binance ordert.
    Csak megmondja, hogy később engedhető lenne-e.
    """
    state = load_state()
    settings = state.get("settings", {})
    req = req or {}

    symbol = str(req.get("symbol") or (settings.get("watchlist") or ["BTCUSDT"])[0]).upper()
    side = str(req.get("side") or "BUY").upper()
    amount = float(req.get("amount") or 0)

    blocks = []
    warnings = []

    live_status = binance_live_status() if "binance_live_status" in globals() else {"ok": False, "ready_for_live": False}
    admin = admin_status() if "admin_status" in globals() else {"ok": False, "admin_active": False}
    health = healthcheck() if "healthcheck" in globals() else {"ok": False, "status": "UNKNOWN", "warnings": ["healthcheck_missing"]}

    if not bool(settings.get("live_executor_enabled", False)):
        blocks.append("Live executor nincs bekapcsolva.")

    if bool(settings.get("live_hard_stop_enabled", True)):
        if not live_status.get("ready_for_live"):
            blocks.append("Binance live status nem ready.")

        if bool(settings.get("live_require_admin_active", True)) and not admin.get("admin_active"):
            blocks.append("Admin session nem aktív.")

        if state.get("safe_mode"):
            blocks.append("Safe Mode aktív.")

        if str(settings.get("execution_mode", "AUTO")).upper() == "OFF":
            blocks.append("Execution mode OFF.")

        if side == "BUY" and not bool(settings.get("live_allow_buy", False)):
            blocks.append("Live BUY nincs engedélyezve.")

        if side == "SELL" and not bool(settings.get("live_allow_sell", False)):
            blocks.append("Live SELL nincs engedélyezve.")

        max_order = float(settings.get("live_max_order_usdt_hard", settings.get("live_max_order_usdt", 10.0)) or 10.0)
        if amount > max_order:
            blocks.append(f"Order amount túl nagy: {amount} > hard limit {max_order}")

        if amount <= 0:
            blocks.append("Order amount <= 0.")

        if bool(settings.get("live_block_if_health_warning", True)):
            hw = health.get("warnings") or []
            if hw:
                blocks.append("Healthcheck warning van: " + ", ".join([str(x) for x in hw[:3]]))

    trade_guard = {"ok": True}
    if "trade_screen_check" in globals():
        try:
            trade_guard = trade_screen_check(symbol, side, settings)
        except Exception as e:
            trade_guard = {"ok": False, "error": str(e)}

    if bool(settings.get("live_block_if_spread_bad", True)) and not trade_guard.get("ok", False):
        blocks.append("Trade guard / spread / slippage nem OK.")

    ai = {}
    if "ai_advisor" in globals():
        try:
            ai = ai_advisor(symbol)
        except Exception as e:
            ai = {"ok": False, "error": str(e)}

    rec = str(ai.get("recommendation", "")).upper()
    if bool(settings.get("live_block_if_ai_hold", True)):
        if rec in ["HOLD", "BLOCKED", "BLOCKED_SAFE_MODE", "BLOCKED_EXECUTION_OFF", "BLOCKED_TRADE_GUARD"]:
            blocks.append("AI advisor nem engedi: " + rec)

    if bool(settings.get("live_require_positive_after_tax", True)):
        # BUY-nál nincs realizált pnl, ezért csak figyelmeztetés.
        # SELL-nél ha van becsült gross profit, ellenőrizzük.
        gross_pct = req.get("gross_profit_pct", None)
        if gross_pct is not None:
            ok_tax, tax_bd = is_after_tax_profit_ok(float(gross_pct), settings)
            if not ok_tax:
                blocks.append(
                    "Adó/fee utáni profit nem elég: "
                    + str(tax_bd.get("after_tax_pct"))
                    + "% < "
                    + str(settings.get("live_min_after_tax_profit_pct", settings.get("min_after_tax_profit_pct", 0.10)))
                    + "%"
                )
        else:
            warnings.append("Nincs gross_profit_pct adat, csak BUY/előzetes gate ellenőrzés.")

    approved_ok = False
    if bool(settings.get("live_require_approval", True)):
        q = read_approval_queue(500) if "read_approval_queue" in globals() else {"items": []}
        rid = req.get("id") or req.get("request_id")
        for item in q.get("items", []):
            if rid and item.get("id") == rid and item.get("status") in ["APPROVED", "DRY_RUN_EXECUTED"]:
                approved_ok = True
                break

        if not approved_ok:
            blocks.append("Nincs jóváhagyott approval request ehhez az orderhez.")
    else:
        approved_ok = True

    allowed = len(blocks) == 0

    out = {
        "ok": True,
        "allowed": allowed,
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "blocks": blocks,
        "warnings": warnings,
        "live_status": live_status,
        "admin_active": admin.get("admin_active"),
        "health_status": health.get("status"),
        "trade_guard_ok": trade_guard.get("ok"),
        "ai_recommendation": rec,
        "approved_ok": approved_ok,
        "message": "LIVE ORDER NEM lett elküldve. Ez csak safety gate.",
    }

    audit_event("LIVE_ORDER_SAFETY_GATE", "Live order safety gate", out)
    return out


def simulate_live_order_gate_from_latest():
    """
    Legutóbbi approved/dry-run request alapján live gate szimuláció.
    Nem küld ordert.
    """
    adm = admin_status()
    if not adm.get("admin_active"):
        return {"ok": False, "allowed": False, "error": "Admin login szükséges."}

    q = read_approval_queue(500)
    items = q.get("items", [])
    candidates = [x for x in items if x.get("status") in ["APPROVED", "DRY_RUN_EXECUTED"]]

    if not candidates:
        return {"ok": False, "allowed": False, "error": "Nincs approved/dry-run request."}

    req = candidates[-1]
    return live_order_safety_gate(req)


def live_executor_gate_status():
    state = load_state()
    settings = state.get("settings", {})

    return {
        "ok": True,
        "live_executor_enabled": settings.get("live_executor_enabled", False),
        "live_hard_stop_enabled": settings.get("live_hard_stop_enabled", True),
        "live_require_admin_active": settings.get("live_require_admin_active", True),
        "live_require_approval": settings.get("live_require_approval", True),
        "live_require_positive_after_tax": settings.get("live_require_positive_after_tax", True),
        "live_max_order_usdt_hard": settings.get("live_max_order_usdt_hard", 10.0),
        "live_block_if_health_warning": settings.get("live_block_if_health_warning", True),
        "live_block_if_spread_bad": settings.get("live_block_if_spread_bad", True),
        "live_block_if_ai_hold": settings.get("live_block_if_ai_hold", True),
    }



def binance_account_status_adapter():
    """
    Binance account/status adapter.
    Alapból nem hív order endpointot.
    Ha nincs API kulcs, csak hiány státuszt ad.
    """
    state = load_state()
    settings = state.get("settings", {})
    sec = load_secrets_encrypted() if "load_secrets_encrypted" in globals() else {}

    api_key = sec.get("binance_api_key", "")
    api_secret = sec.get("binance_api_secret", "")

    out = {
        "ok": True,
        "enabled": bool(settings.get("binance_account_check_enabled", True)),
        "has_api_key": bool(api_key),
        "has_api_secret": bool(api_secret),
        "ready_for_private_api": bool(api_key and api_secret),
        "live_status": binance_live_status() if "binance_live_status" in globals() else {},
        "message": "",
        "balances_preview": [],
    }

    if not out["enabled"]:
        out["message"] = "Binance account check kikapcsolva."
        return out

    if not api_key or not api_secret:
        out["message"] = "Binance API key/secret hiányzik. Private account check nem fut."
        audit_event("BINANCE_ACCOUNT_STATUS", out["message"], out)
        return out

    # Direkt nem hívunk éles Binance account endpointot ebben a patchben.
    # Következő lépésben külön adapterben lehet majd signed GET /api/v3/account.
    out["message"] = "API kulcs megvan. Signed account endpoint bekötés következő patch."
    audit_event("BINANCE_ACCOUNT_STATUS", out["message"], {"ready": True})
    return out


def binance_test_order_payload(symbol=None, side=None, order_type=None, quote_qty=None):
    """
    Test order payload előállítás.
    Nem küld Binance-re semmit.
    """
    state = load_state()
    settings = state.get("settings", {})

    symbol = str(symbol or settings.get("binance_test_order_symbol", "BTCUSDT")).upper()
    side = str(side or settings.get("binance_test_order_side", "BUY")).upper()
    order_type = str(order_type or settings.get("binance_test_order_type", "MARKET")).upper()
    quote_qty = float(quote_qty or settings.get("binance_test_order_quote_qty", 5.0) or 5.0)

    errors = []
    if not symbol:
        errors.append("symbol hiányzik")
    if side not in ["BUY", "SELL"]:
        errors.append("side csak BUY/SELL lehet")
    if order_type not in ["MARKET", "LIMIT"]:
        errors.append("type csak MARKET/LIMIT lehet")
    if quote_qty <= 0:
        errors.append("quote_qty <= 0")

    payload = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "timestamp": int(time.time() * 1000),
        "recvWindow": int(settings.get("binance_recv_window", 5000) or 5000),
    }

    if order_type == "MARKET":
        payload["quoteOrderQty"] = quote_qty
    else:
        # LIMIT orderhez később price + quantity kell.
        errors.append("LIMIT test order payloadhoz price/quantity későbbi patchben.")

    return {
        "ok": len(errors) == 0,
        "payload": payload,
        "errors": errors,
        "note": "Ez csak payload validate. Binance test order endpoint NEM lett meghívva.",
    }


def binance_test_order_validate(symbol=None, side=None, quote_qty=None):
    """
    Binance test order validate.
    Nem küld ordert, nem hív Binance endpointot.
    Safety gate + payload ellenőrzés.
    """
    state = load_state()
    settings = state.get("settings", {})

    if not bool(settings.get("binance_test_order_enabled", True)):
        return {"ok": False, "validated": False, "error": "Binance test order validate kikapcsolva."}

    payload_res = binance_test_order_payload(symbol=symbol, side=side, quote_qty=quote_qty)

    req = {
        "symbol": payload_res.get("payload", {}).get("symbol"),
        "side": payload_res.get("payload", {}).get("side"),
        "amount": float(quote_qty or settings.get("binance_test_order_quote_qty", 5.0) or 5.0),
        "gross_profit_pct": None,
    }

    gate = live_order_safety_gate(req) if "live_order_safety_gate" in globals() else {"ok": False, "allowed": False}

    out = {
        "ok": payload_res.get("ok") is True,
        "validated": payload_res.get("ok") is True,
        "payload": payload_res.get("payload"),
        "payload_errors": payload_res.get("errors"),
        "safety_gate_allowed": gate.get("allowed"),
        "safety_gate_blocks": gate.get("blocks"),
        "message": "TEST ORDER VALIDATE ONLY. Binance order/test endpoint NEM lett meghívva.",
    }

    audit_event("BINANCE_TEST_ORDER_VALIDATE", out["message"], out)
    return out


def binance_account_test_status():
    state = load_state()
    settings = state.get("settings", {})

    return {
        "ok": True,
        "account_check_enabled": settings.get("binance_account_check_enabled", True),
        "test_order_enabled": settings.get("binance_test_order_enabled", True),
        "test_order_symbol": settings.get("binance_test_order_symbol", "BTCUSDT"),
        "test_order_side": settings.get("binance_test_order_side", "BUY"),
        "test_order_type": settings.get("binance_test_order_type", "MARKET"),
        "test_order_quote_qty": settings.get("binance_test_order_quote_qty", 5.0),
        "recv_window": settings.get("binance_recv_window", 5000),
    }



def binance_signed_query(params, secret):
    """
    Binance signed query string előállítás.
    Nem küld hálózati kérést.
    """
    params = dict(params or {})
    qs = urllib.parse.urlencode(params, doseq=True)
    sig = hmac.new(str(secret).encode("utf-8"), qs.encode("utf-8"), hashlib.sha256).hexdigest()
    return qs + "&signature=" + sig


def binance_signed_request_preview(method="GET", endpoint="/api/v3/account", params=None):
    """
    Signed request preview.
    Nem küld kérést Binance felé.
    """
    state = load_state()
    settings = state.get("settings", {})
    sec = load_secrets_encrypted() if "load_secrets_encrypted" in globals() else {}

    api_key = sec.get("binance_api_key", "")
    api_secret = sec.get("binance_api_secret", "")

    if not api_key or not api_secret:
        return {
            "ok": False,
            "ready": False,
            "error": "Binance API key/secret hiányzik.",
            "method": method,
            "endpoint": endpoint,
        }

    params = dict(params or {})
    params.setdefault("timestamp", int(time.time() * 1000))
    params.setdefault("recvWindow", int(settings.get("binance_recv_window", 5000) or 5000))

    signed_qs = binance_signed_query(params, api_secret)

    base_url = str(settings.get("binance_base_url", "https://api.binance.com")).rstrip("/")
    url_preview = base_url + endpoint + "?" + signed_qs

    # Secretet nem logolunk. Signature benne van a previewban, de csak local.
    return {
        "ok": True,
        "ready": True,
        "method": method.upper(),
        "endpoint": endpoint,
        "base_url": base_url,
        "has_api_key": True,
        "has_api_secret": True,
        "headers": {"X-MBX-APIKEY": mask_secret(api_key) if "mask_secret" in globals() else "***"},
        "signed_query_preview": signed_qs[:80] + "...",
        "url_preview": url_preview[:120] + "...",
        "note": "Preview only. Hálózati kérés NEM ment ki.",
    }


def binance_account_readonly_check():
    """
    Read-only Binance account check előkészítés.
    Alapból nem küld hálózati kérést, amíg binance_account_read_enabled=False.
    """
    state = load_state()
    settings = state.get("settings", {})

    if not bool(settings.get("binance_signed_readonly_enabled", False)):
        return {
            "ok": False,
            "called": False,
            "reason": "binance_signed_readonly_enabled false",
            "message": "Read-only signed Binance funkció kikapcsolva.",
        }

    preview = binance_signed_request_preview("GET", "/api/v3/account", {})

    if not preview.get("ok"):
        audit_event("BINANCE_ACCOUNT_READONLY_PREVIEW_FAIL", preview.get("error", ""), preview)
        return preview | {"called": False}

    if not bool(settings.get("binance_account_read_enabled", False)):
        out = preview | {
            "called": False,
            "message": "Signed account request preview kész, de valós GET /api/v3/account nincs bekapcsolva.",
        }
        audit_event("BINANCE_ACCOUNT_READONLY_PREVIEW", "Read-only account preview", out)
        return out

    # Biztonsági okból ebben a patchben még akkor sem hívunk hálózatot.
    out = preview | {
        "called": False,
        "message": "Read-only account GET még nincs aktiválva ebben a patchben. Következő külön lépés.",
    }
    audit_event("BINANCE_ACCOUNT_READONLY_NOT_CALLED", "Account read not called", out)
    return out


def binance_signed_readonly_status():
    state = load_state()
    settings = state.get("settings", {})
    sec = load_secrets_encrypted() if "load_secrets_encrypted" in globals() else {}

    return {
        "ok": True,
        "base_url": settings.get("binance_base_url", "https://api.binance.com"),
        "signed_readonly_enabled": settings.get("binance_signed_readonly_enabled", False),
        "account_read_enabled": settings.get("binance_account_read_enabled", False),
        "has_api_key": bool(sec.get("binance_api_key")),
        "has_api_secret": bool(sec.get("binance_api_secret")),
        "last_check_ts": settings.get("binance_account_last_check_ts", 0),
        "last_ok": settings.get("binance_account_last_ok", False),
        "note": "Order endpoint nincs bekötve.",
    }



def _binance_http_get_signed(endpoint="/api/v3/account", params=None):
    """
    Valódi signed GET helper.
    CSAK read-only endpointre engedjük.
    Order endpoint tiltva.
    """
    state = load_state()
    settings = state.get("settings", {})
    sec = load_secrets_encrypted() if "load_secrets_encrypted" in globals() else {}

    api_key = sec.get("binance_api_key", "")
    api_secret = sec.get("binance_api_secret", "")

    if not api_key or not api_secret:
        return {
            "ok": False,
            "called": False,
            "error": "Binance API key/secret hiányzik.",
        }

    endpoint = str(endpoint or "").strip()

    allowed_readonly = [
        "/api/v3/account",
    ]

    if endpoint not in allowed_readonly:
        return {
            "ok": False,
            "called": False,
            "error": "Tiltott endpoint. Csak read-only /api/v3/account engedélyezett.",
            "endpoint": endpoint,
        }

    params = dict(params or {})
    params.setdefault("timestamp", int(time.time() * 1000))
    params.setdefault("recvWindow", int(settings.get("binance_recv_window", 5000) or 5000))

    signed_qs = binance_signed_query(params, api_secret)

    base_url = str(settings.get("binance_base_url", "https://api.binance.com")).rstrip("/")
    url = base_url + endpoint + "?" + signed_qs

    timeout = float(settings.get("binance_http_timeout_sec", 8) or 8)

    headers = {
        "X-MBX-APIKEY": api_key,
        "User-Agent": "BinanceAutobot-ReadOnly/0.3.8",
    }

    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            status = getattr(resp, "status", 200)
            data = json.loads(raw) if raw else {}

        return {
            "ok": 200 <= int(status) < 300,
            "called": True,
            "status_code": int(status),
            "data": data,
            "endpoint": endpoint,
        }

    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")[:1000]
        except Exception:
            body = ""

        return {
            "ok": False,
            "called": True,
            "status_code": int(getattr(e, "code", 0) or 0),
            "error": "HTTPError",
            "body": body,
            "endpoint": endpoint,
        }

    except Exception as e:
        return {
            "ok": False,
            "called": True,
            "error": str(e),
            "endpoint": endpoint,
        }


def _extract_balance_preview(account_data, assets_csv=None):
    """
    Account válaszból rövid balance preview.
    """
    assets_csv = assets_csv or "USDT,USDC,BTC,ETH,BNB,DOGE"
    wanted = [x.strip().upper() for x in str(assets_csv).split(",") if x.strip()]

    balances = account_data.get("balances", []) if isinstance(account_data, dict) else []
    out = []

    for row in balances:
        try:
            asset = str(row.get("asset", "")).upper()
            if asset not in wanted:
                continue

            free = float(row.get("free", 0) or 0)
            locked = float(row.get("locked", 0) or 0)

            if free == 0 and locked == 0:
                continue

            out.append({
                "asset": asset,
                "free": free,
                "locked": locked,
                "total": free + locked,
            })
        except Exception:
            pass

    return out


def binance_account_readonly_real_get():
    """
    Valódi Binance GET /api/v3/account.
    Csak akkor fut, ha:
    - binance_signed_readonly_enabled = true
    - binance_account_read_enabled = true
    - binance_real_account_get_enabled = true

    Order endpoint nincs.
    """
    state = load_state()
    settings = state.setdefault("settings", {})

    if not bool(settings.get("binance_signed_readonly_enabled", False)):
        return {
            "ok": False,
            "called": False,
            "reason": "binance_signed_readonly_enabled false",
            "message": "Signed read-only nincs bekapcsolva.",
        }

    if not bool(settings.get("binance_account_read_enabled", False)):
        return {
            "ok": False,
            "called": False,
            "reason": "binance_account_read_enabled false",
            "message": "Account read nincs bekapcsolva.",
        }

    if not bool(settings.get("binance_real_account_get_enabled", False)):
        return {
            "ok": False,
            "called": False,
            "reason": "binance_real_account_get_enabled false",
            "message": "Valódi Binance account GET nincs bekapcsolva.",
        }

    res = _binance_http_get_signed("/api/v3/account", {})

    settings["binance_account_last_check_ts"] = int(time.time())
    settings["binance_account_last_ok"] = bool(res.get("ok"))

    preview = []
    if res.get("ok"):
        preview = _extract_balance_preview(
            res.get("data", {}),
            settings.get("binance_balance_preview_assets", "USDT,USDC,BTC,ETH,BNB,DOGE")
        )

    state["last_action"] = "Binance read-only account GET: " + ("OK" if res.get("ok") else "FAIL")
    save_state(state)

    out = {
        "ok": bool(res.get("ok")),
        "called": bool(res.get("called")),
        "status_code": res.get("status_code"),
        "error": res.get("error"),
        "body": res.get("body"),
        "balance_preview": preview,
        "balances_count": len(res.get("data", {}).get("balances", [])) if isinstance(res.get("data"), dict) else 0,
        "message": "Read-only GET /api/v3/account lefutott." if res.get("called") else "Nem futott.",
        "order_endpoint_used": False,
    }

    audit_event("BINANCE_ACCOUNT_REAL_READONLY_GET", out["message"], {
        "ok": out.get("ok"),
        "called": out.get("called"),
        "status_code": out.get("status_code"),
        "balances_count": out.get("balances_count"),
        "order_endpoint_used": False,
    })

    return out


def binance_readonly_real_status():
    state = load_state()
    settings = state.get("settings", {})
    sec = load_secrets_encrypted() if "load_secrets_encrypted" in globals() else {}

    return {
        "ok": True,
        "signed_readonly_enabled": settings.get("binance_signed_readonly_enabled", False),
        "account_read_enabled": settings.get("binance_account_read_enabled", False),
        "real_account_get_enabled": settings.get("binance_real_account_get_enabled", False),
        "has_api_key": bool(sec.get("binance_api_key")),
        "has_api_secret": bool(sec.get("binance_api_secret")),
        "timeout_sec": settings.get("binance_http_timeout_sec", 8),
        "preview_assets": settings.get("binance_balance_preview_assets", "USDT,USDC,BTC,ETH,BNB,DOGE"),
        "last_check_ts": settings.get("binance_account_last_check_ts", 0),
        "last_ok": settings.get("binance_account_last_ok", False),
        "order_endpoint_used": False,
    }



def integration_overview_status():
    """
    Secrets + integrációk összesített, UI-barát státusz.
    Nem mutat secret értéket.
    Nem hív hálózatot.
    """
    sec = secrets_status() if "secrets_status" in globals() else {"ok": False}
    email = email_config_status() if "email_config_status" in globals() else {"ok": False}
    openai = openai_config_status() if "openai_config_status" in globals() else {"ok": False}
    live = binance_live_status() if "binance_live_status" in globals() else {"ok": False}
    signed = binance_signed_readonly_status() if "binance_signed_readonly_status" in globals() else {"ok": False}
    readonly = binance_readonly_real_status() if "binance_readonly_real_status" in globals() else {"ok": False}

    items = []

    items.append({
        "name": "Encrypted secrets",
        "ok": bool(sec.get("encrypted_file")),
        "status": "OK" if sec.get("encrypted_file") else "HIÁNYZIK",
        "detail": "secrets.enc helyi titkosított fájl",
    })

    items.append({
        "name": "Binance API",
        "ok": bool(sec.get("binance_api")),
        "status": "OK" if sec.get("binance_api") else "HIÁNYZIK",
        "detail": "API key + secret szükséges live/read-only funkcióhoz",
    })

    items.append({
        "name": "OpenAI API",
        "ok": bool(openai.get("has_key")),
        "status": "OK" if openai.get("has_key") else "OPCIONÁLIS / HIÁNYZIK",
        "detail": "AI advisor API módhoz kell, offline AI enélkül is működik",
    })

    items.append({
        "name": "E-mail értesítő",
        "ok": bool(email.get("ok")),
        "status": "OK" if email.get("ok") else "NINCS BEÁLLÍTVA",
        "detail": "SMTP user/app password/to cím szükséges",
    })

    items.append({
        "name": "Binance Live Safety",
        "ok": bool(live.get("ready_for_live")),
        "status": "READY" if live.get("ready_for_live") else "NEM READY",
        "detail": "; ".join(live.get("warnings", [])) if isinstance(live.get("warnings"), list) else "",
    })

    items.append({
        "name": "Signed Read-only",
        "ok": bool(signed.get("signed_readonly_enabled")),
        "status": "ON" if signed.get("signed_readonly_enabled") else "OFF",
        "detail": "Csak olvasási előkészítés, order nincs",
    })

    items.append({
        "name": "Real Account GET",
        "ok": bool(readonly.get("real_account_get_enabled")),
        "status": "ON" if readonly.get("real_account_get_enabled") else "OFF",
        "detail": "Valódi /api/v3/account csak 3 kapcsolóval fut",
    })

    warnings = []
    if readonly.get("real_account_get_enabled") and not readonly.get("has_api_key"):
        warnings.append("Real account GET ON, de Binance API key hiányzik.")
    if readonly.get("real_account_get_enabled") and not readonly.get("has_api_secret"):
        warnings.append("Real account GET ON, de Binance API secret hiányzik.")
    if live.get("live_mode_enabled") and not live.get("ready_for_live"):
        warnings.append("Live mód nincs kész, order tiltva.")

    return {
        "ok": True,
        "items": items,
        "warnings": warnings,
        "safe_summary": "Order endpoint nincs bekötve. Secrets nincs GitHubon.",
    }


def readonly_activation_help():
    """
    Magyarázat: milyen kapcsolók kellenek a read-only account olvasáshoz.
    """
    st = binance_readonly_real_status() if "binance_readonly_real_status" in globals() else {}
    return {
        "ok": True,
        "title": "Read-only Binance account bekapcsolási feltételek",
        "steps": [
            "1. Secrets menüben Binance API key + API secret megadása.",
            "2. API kulcsnál csak olvasási jogosultság javasolt első teszthez.",
            "3. Settings: binance_signed_readonly_enabled = true.",
            "4. Settings: binance_account_read_enabled = true.",
            "5. Settings: binance_real_account_get_enabled = true.",
            "6. BINANCE READONLY menüben REAL ACCOUNT GET gomb.",
        ],
        "current": st,
        "danger_note": "Ez csak /api/v3/account olvasás. Order endpoint továbbra sincs bekötve.",
    }



def first_run_security_check():
    """
    First-run wizard biztonsági állapot.
    Nem hív hálózatot, nem küld ordert.
    """
    state = load_state()
    settings = state.get("settings", {})

    admin = admin_status() if "admin_status" in globals() else {"ok": False}
    integ = integration_overview_status() if "integration_overview_status" in globals() else {"ok": False, "items": []}
    live = binance_live_status() if "binance_live_status" in globals() else {"ok": False}
    readonly = binance_readonly_real_status() if "binance_readonly_real_status" in globals() else {"ok": False}

    tasks = []

    tasks.append({
        "id": "admin_password",
        "title": "Admin jelszó csere",
        "required": bool(settings.get("first_run_require_admin_password_change", True)),
        "ok": not bool(admin.get("must_change_default", True)),
        "detail": "Alap admin/admin jelszót első használatkor cserélni kell.",
    })

    tasks.append({
        "id": "secrets_review",
        "title": "Secrets / integrációk ellenőrzése",
        "required": bool(settings.get("first_run_require_secrets_review", True)),
        "ok": bool(integ.get("ok")),
        "detail": "Binance/OpenAI/E-mail kulcsok helyi titkosított tárolóban kezelhetők.",
    })

    tasks.append({
        "id": "live_warning",
        "title": "Live mód figyelmeztetés",
        "required": bool(settings.get("first_run_show_live_warning", True)),
        "ok": not bool(live.get("live_mode_enabled", False)) or bool(live.get("ready_for_live", False)),
        "detail": "Live order csak safety gate, approval, API és külön kapcsolók után engedhető.",
    })

    tasks.append({
        "id": "readonly_warning",
        "title": "Read-only Binance olvasás",
        "required": False,
        "ok": not bool(readonly.get("real_account_get_enabled", False)) or bool(readonly.get("has_api_key") and readonly.get("has_api_secret")),
        "detail": "Valódi account olvasás csak 3 külön kapcsolóval és API kulccsal fut.",
    })

    required_bad = [t for t in tasks if t.get("required") and not t.get("ok")]

    return {
        "ok": True,
        "complete": len(required_bad) == 0,
        "required_missing_count": len(required_bad),
        "tasks": tasks,
        "message": "First-run kész." if len(required_bad) == 0 else "First-run teendők vannak.",
    }


def startup_safety_summary():
    """
    Indulási biztonsági összefoglaló.
    UI-nak és diagnosztikának.
    """
    state = load_state()
    settings = state.get("settings", {})

    health = healthcheck() if "healthcheck" in globals() else {"ok": False}
    admin = admin_status() if "admin_status" in globals() else {"ok": False}
    live = live_executor_gate_status() if "live_executor_gate_status" in globals() else {"ok": False}
    binance = binance_readonly_real_status() if "binance_readonly_real_status" in globals() else {"ok": False}
    integ = integration_overview_status() if "integration_overview_status" in globals() else {"ok": False, "warnings": []}
    first = first_run_security_check() if "first_run_security_check" in globals() else {"ok": False}

    safety_flags = {
        "safe_mode": bool(state.get("safe_mode", False)),
        "running": bool(state.get("running", False)),
        "execution_mode": settings.get("execution_mode", "AUTO"),
        "live_executor_enabled": settings.get("live_executor_enabled", False),
        "live_buy_allowed": settings.get("live_allow_buy", False),
        "live_sell_allowed": settings.get("live_allow_sell", False),
        "order_endpoint_bound": False,
        "readonly_real_get_enabled": binance.get("real_account_get_enabled", False),
        "admin_active": admin.get("admin_active", False),
        "first_run_complete": first.get("complete", False),
    }

    warnings = []
    warnings.extend(integ.get("warnings", []) or [])

    if settings.get("live_executor_enabled", False):
        warnings.append("Live executor ON. Csak safety gate + approval után engedhető.")

    if settings.get("live_allow_buy", False) or settings.get("live_allow_sell", False):
        warnings.append("Live BUY/SELL kapcsoló ON. Ellenőrizd API és approval állapotot.")

    if first.get("required_missing_count", 0) > 0:
        warnings.append("First-run kötelező teendő van: " + str(first.get("required_missing_count")))

    return {
        "ok": True,
        "app_version": globals().get("APP_VERSION", ""),
        "health": health.get("status", "UNKNOWN"),
        "safety_flags": safety_flags,
        "warnings": warnings,
        "first_run": first,
        "safe_message": "Order endpoint nincs bekötve. APK buildhez nem nyúltunk.",
    }



def _normalize_spot_balances(account_result=None):
    """
    Binance /api/v3/account balances -> egységes spot balance lista.
    Ha nincs valódi Binance adat, demo fallbacket ad.
    """
    state = load_state()
    settings = state.get("settings", {})

    balances = []

    data = None
    if isinstance(account_result, dict):
        data = account_result.get("data") or account_result

    raw_balances = data.get("balances", []) if isinstance(data, dict) else []

    for row in raw_balances:
        try:
            asset = str(row.get("asset", "")).upper()
            free = float(row.get("free", 0) or 0)
            locked = float(row.get("locked", 0) or 0)
            total = free + locked
            if total <= 0:
                continue
            balances.append({
                "asset": asset,
                "free": free,
                "locked": locked,
                "total": total,
                "source": "binance",
            })
        except Exception:
            pass

    if balances:
        return balances

    # Demo fallback: jelenlegi demo state alapján.
    base = str(settings.get("spot_base_asset", state.get("base", "USDC")) or "USDC").upper()
    balances.append({
        "asset": base,
        "free": float(state.get("balance", 0) or 0),
        "locked": 0.0,
        "total": float(state.get("balance", 0) or 0),
        "source": "demo",
    })

    for sym, pos in (state.get("positions", {}) or {}).items():
        try:
            asset = str(sym).replace("USDT", "").replace("USDC", "").upper()
            qty = float(pos.get("qty", 0) or 0)
            if qty <= 0:
                continue
            balances.append({
                "asset": asset,
                "free": qty,
                "locked": 0.0,
                "total": qty,
                "source": "demo_position",
                "symbol": sym,
            })
        except Exception:
            pass

    return balances


def _asset_usd_price(asset):
    """
    Egyszerű USD árbecslés.
    USDC/USDT = 1.
    Egyéb coinoknál demo get_prices fallback.
    """
    asset = str(asset or "").upper()

    if asset in ["USDT", "USDC", "USD"]:
        return 1.0

    # Próbáljuk USDT párral.
    symbol = asset + "USDT"

    try:
        prices = get_prices(symbol, limit=5) if "get_prices" in globals() else []
        if prices:
            return float(prices[-1])
    except Exception:
        pass

    # Demo fallback ismert pozícióból.
    state = load_state()
    for sym, pos in (state.get("positions", {}) or {}).items():
        if str(sym).upper().startswith(asset):
            try:
                return float(pos.get("peak") or pos.get("avg") or 0)
            except Exception:
                pass

    return 0.0


def portfolio_valuation_from_balances(balances=None):
    """
    Spot portfolio értékelés USD/USDC alapon.
    """
    state = load_state()
    settings = state.get("settings", {})

    balances = balances if balances is not None else _normalize_spot_balances()
    min_value = float(settings.get("spot_min_asset_value_usd", 0.01) or 0.01)

    rows = []
    total_value = 0.0
    quote_free = 0.0
    quote_assets = [x.strip().upper() for x in str(settings.get("spot_quote_assets", "USDC,USDT")).split(",") if x.strip()]

    for b in balances:
        asset = str(b.get("asset", "")).upper()
        total = float(b.get("total", 0) or 0)
        free = float(b.get("free", 0) or 0)
        locked = float(b.get("locked", 0) or 0)
        price = _asset_usd_price(asset)
        value = total * price

        if asset in quote_assets:
            quote_free += free * price

        if value < min_value and asset not in quote_assets:
            continue

        total_value += value

        rows.append({
            "asset": asset,
            "free": free,
            "locked": locked,
            "total": total,
            "price_usd": round(price, 8),
            "value_usd": round(value, 8),
            "source": b.get("source", ""),
        })

    safety_reserve = float(settings.get("spot_safety_reserve", 10.0) or 0)
    max_pct = float(settings.get("spot_max_tradeable_pct", 90.0) or 90.0)

    tradable_raw = max(0.0, quote_free - safety_reserve)
    tradable_cap = max(0.0, quote_free * (max_pct / 100.0))
    tradable = min(tradable_raw, tradable_cap)

    return {
        "ok": True,
        "base_asset": settings.get("spot_base_asset", "USDC"),
        "quote_assets": quote_assets,
        "total_value_usd": round(total_value, 8),
        "quote_free_usd": round(quote_free, 8),
        "safety_reserve_usd": safety_reserve,
        "tradable_usd": round(tradable, 8),
        "assets_count": len(rows),
        "assets": sorted(rows, key=lambda x: x.get("value_usd", 0), reverse=True),
        "source": "portfolio_valuation",
    }


def sync_spot_portfolio():
    """
    Spot sync:
    - ha read-only Binance account engedélyezett, megpróbálja használni
    - ha nincs bekapcsolva/API, demo fallback
    - cache-eli a state settingsbe
    - order nincs
    """
    state = load_state()
    settings = state.setdefault("settings", {})

    if not bool(settings.get("spot_sync_enabled", True)):
        return {"ok": False, "synced": False, "reason": "spot_sync_enabled false"}

    account_res = None

    # Csak akkor próbál valódi read-only accountot, ha a kapcsolók engedik.
    if (
        bool(settings.get("binance_signed_readonly_enabled", False))
        and bool(settings.get("binance_account_read_enabled", False))
        and bool(settings.get("binance_real_account_get_enabled", False))
    ):
        try:
            account_res = binance_account_readonly_real_get()
        except Exception as e:
            account_res = {"ok": False, "error": str(e), "called": False}

    balances = _normalize_spot_balances(account_res)
    portfolio = portfolio_valuation_from_balances(balances)

    settings["spot_last_sync_ts"] = int(time.time())
    settings["portfolio_total_value_usd"] = portfolio.get("total_value_usd", 0.0)
    settings["portfolio_tradable_usd"] = portfolio.get("tradable_usd", 0.0)

    state["spot_balances_cache"] = balances
    state["portfolio_cache"] = portfolio
    state["last_action"] = "Spot portfolio sync OK"
    save_state(state)

    audit_event("SPOT_PORTFOLIO_SYNC", "Spot portfolio sync", {
        "total_value_usd": portfolio.get("total_value_usd"),
        "tradable_usd": portfolio.get("tradable_usd"),
        "assets_count": portfolio.get("assets_count"),
        "order_endpoint_used": False,
    })

    try:
        append_trend_history("spot_portfolio_sync")
    except Exception:
        pass

    return {
        "ok": True,
        "synced": True,
        "account_called": bool(account_res.get("called")) if isinstance(account_res, dict) else False,
        "portfolio": portfolio,
        "message": "Spot portfolio sync kész. Order endpoint nincs használva.",
        "order_endpoint_used": False,
    }


def spot_portfolio_status():
    state = load_state()
    settings = state.get("settings", {})
    cache = state.get("portfolio_cache") or {}

    return {
        "ok": True,
        "spot_sync_enabled": settings.get("spot_sync_enabled", True),
        "spot_base_asset": settings.get("spot_base_asset", "USDC"),
        "spot_quote_assets": settings.get("spot_quote_assets", "USDC,USDT"),
        "spot_safety_reserve": settings.get("spot_safety_reserve", 10.0),
        "spot_max_tradeable_pct": settings.get("spot_max_tradeable_pct", 90.0),
        "spot_last_sync_ts": settings.get("spot_last_sync_ts", 0),
        "portfolio_total_value_usd": settings.get("portfolio_total_value_usd", cache.get("total_value_usd", 0.0)),
        "portfolio_tradable_usd": settings.get("portfolio_tradable_usd", cache.get("tradable_usd", 0.0)),
        "assets_count": cache.get("assets_count", 0),
        "top_assets": (cache.get("assets") or [])[:8],
        "order_endpoint_used": False,
    }



def dashboard_kpi_snapshot():
    """
    Dashboard KPI snapshot:
    portfolio_cache + demo state + PnL.
    Nem hív order endpointot.
    """
    state = load_state()
    settings = state.get("settings", {})
    portfolio = state.get("portfolio_cache") or {}

    eq = equity(state) if "equity" in globals() else float(state.get("balance", 0) or 0)
    realized = float(state.get("realized_pnl", 0) or 0)
    positions = state.get("positions", {}) or {}

    use_portfolio = bool(settings.get("dashboard_use_portfolio_cache", True))

    total_value = float(portfolio.get("total_value_usd", 0) or 0)
    tradable = float(portfolio.get("tradable_usd", 0) or 0)

    if not use_portfolio or total_value <= 0:
        total_value = float(eq or 0)
        tradable = max(0.0, float(state.get("balance", 0) or 0) - float(settings.get("spot_safety_reserve", 10) or 10))

    quote_assets = [x.strip().upper() for x in str(settings.get("spot_quote_assets", "USDC,USDT")).split(",") if x.strip()]
    assets = portfolio.get("assets") or []

    quote_free = 0.0
    usdc_free = 0.0
    usdt_free = 0.0

    for a in assets:
        asset = str(a.get("asset", "")).upper()
        free = float(a.get("free", 0) or 0)
        price = float(a.get("price_usd", 1) or 1)
        if asset in quote_assets:
            quote_free += free * price
        if asset == "USDC":
            usdc_free += free
        if asset == "USDT":
            usdt_free += free

    if not assets:
        base = str(settings.get("spot_base_asset", state.get("base", "USDC"))).upper()
        if base == "USDC":
            usdc_free = float(state.get("balance", 0) or 0)
        elif base == "USDT":
            usdt_free = float(state.get("balance", 0) or 0)
        quote_free = float(state.get("balance", 0) or 0)

    pnl_pct = 0.0
    start_ref = 100.0
    try:
        pnl_pct = ((total_value - start_ref) / start_ref) * 100.0
    except Exception:
        pnl_pct = 0.0

    out = {
        "ok": True,
        "ts": int(time.time()),
        "mode": "DEMO" if not settings.get("live_mode_enabled") else "LIVE",
        "total_value_usd": round(total_value, 8),
        "equity": round(float(eq or 0), 8),
        "realized_pnl": round(realized, 8),
        "pnl_pct_from_100": round(pnl_pct, 6),
        "tradable_usd": round(tradable, 8),
        "quote_free_usd": round(quote_free, 8),
        "usdc_free": round(usdc_free, 8),
        "usdt_free": round(usdt_free, 8),
        "open_positions": len(positions),
        "safe_mode": bool(state.get("safe_mode")),
        "running": bool(state.get("running")),
        "execution_mode": settings.get("execution_mode", "AUTO"),
        "last_action": state.get("last_action", ""),
        "order_endpoint_used": False,
    }

    return out


def append_trend_history(reason="snapshot"):
    """
    Időalapú trend history mentés.
    Profit/equity/portfolio ingadozás követéséhez.
    """
    state = load_state()
    settings = state.get("settings", {})

    if not bool(settings.get("trend_history_enabled", True)):
        return {"ok": False, "saved": False, "reason": "trend_history_enabled false"}

    snap = dashboard_kpi_snapshot()
    row = {
        "ts": int(time.time()),
        "reason": reason,
        "equity": snap.get("equity"),
        "total_value_usd": snap.get("total_value_usd"),
        "realized_pnl": snap.get("realized_pnl"),
        "pnl_pct_from_100": snap.get("pnl_pct_from_100"),
        "tradable_usd": snap.get("tradable_usd"),
        "quote_free_usd": snap.get("quote_free_usd"),
        "open_positions": snap.get("open_positions"),
        "last_action": snap.get("last_action"),
    }

    hist = state.get("trend_history") or []
    hist.append(row)

    max_points = int(settings.get("trend_history_max_points", 300) or 300)
    if len(hist) > max_points:
        hist = hist[-max_points:]

    state["trend_history"] = hist
    state["last_trend_snapshot_ts"] = row["ts"]
    save_state(state)

    return {"ok": True, "saved": True, "row": row, "points": len(hist)}


def trend_history_status(view=None, limit=80):
    """
    Trend history adatok UI-nak.
    view:
    - EQUITY
    - PROFIT
    - TRADABLE
    - TOTAL_VALUE
    """
    state = load_state()
    settings = state.get("settings", {})

    view = str(view or settings.get("trend_view_mode", "PROFIT")).upper()
    supported = [x.strip().upper() for x in str(settings.get("trend_supported_views", "EQUITY,PROFIT,TRADABLE,TOTAL_VALUE")).split(",") if x.strip()]
    if view not in supported:
        view = "PROFIT"

    hist = state.get("trend_history") or []

    if not hist:
        append_trend_history("auto_empty_history")
        state = load_state()
        hist = state.get("trend_history") or []

    hist = hist[-int(limit or 80):]

    key_map = {
        "EQUITY": "equity",
        "PROFIT": "pnl_pct_from_100",
        "TRADABLE": "tradable_usd",
        "TOTAL_VALUE": "total_value_usd",
    }
    value_key = key_map.get(view, "pnl_pct_from_100")

    points = []
    for i, row in enumerate(hist):
        points.append({
            "i": i,
            "ts": row.get("ts"),
            "value": row.get(value_key),
            "equity": row.get("equity"),
            "total_value_usd": row.get("total_value_usd"),
            "realized_pnl": row.get("realized_pnl"),
            "pnl_pct_from_100": row.get("pnl_pct_from_100"),
            "tradable_usd": row.get("tradable_usd"),
            "quote_free_usd": row.get("quote_free_usd"),
            "open_positions": row.get("open_positions"),
            "last_action": row.get("last_action"),
            "reason": row.get("reason"),
        })

    values = [float(p.get("value") or 0) for p in points]
    min_v = min(values) if values else 0.0
    max_v = max(values) if values else 0.0
    last = points[-1] if points else {}

    return {
        "ok": True,
        "view": view,
        "value_key": value_key,
        "supported_views": supported,
        "points_count": len(points),
        "min": round(min_v, 8),
        "max": round(max_v, 8),
        "last": last,
        "points": points,
        "note": "Érintés/célkereszt UI később ezekből a pontokból olvas adatot.",
    }


def set_trend_view_mode(view):
    state = load_state()
    settings = state.setdefault("settings", {})
    view = str(view or "PROFIT").upper()

    supported = [x.strip().upper() for x in str(settings.get("trend_supported_views", "EQUITY,PROFIT,TRADABLE,TOTAL_VALUE")).split(",") if x.strip()]
    if view not in supported:
        return {"ok": False, "error": "Nem támogatott trend nézet.", "supported": supported}

    settings["trend_view_mode"] = view
    save_state(state)
    return trend_history_status(view=view)


def cycle_trend_view_mode():
    state = load_state()
    settings = state.setdefault("settings", {})
    supported = [x.strip().upper() for x in str(settings.get("trend_supported_views", "EQUITY,PROFIT,TRADABLE,TOTAL_VALUE")).split(",") if x.strip()]
    cur = str(settings.get("trend_view_mode", "PROFIT")).upper()
    if cur not in supported:
        cur = supported[0] if supported else "PROFIT"
    idx = supported.index(cur)
    nxt = supported[(idx + 1) % len(supported)] if supported else "PROFIT"
    settings["trend_view_mode"] = nxt
    save_state(state)
    return trend_history_status(view=nxt)



def _sparkline_from_values(values, width=None):
    """
    Egyszerű unicode mini chart.
    UI-ban később Canvas chart válthatja.
    """
    if not values:
        return ""

    try:
        width = int(width or 60)
    except Exception:
        width = 60

    vals = [float(v or 0) for v in values]

    if len(vals) > width:
        step = max(1, int(len(vals) / width))
        vals = vals[::step][-width:]

    blocks = "▁▂▃▄▅▆▇█"
    mn = min(vals)
    mx = max(vals)

    if mx == mn:
        return blocks[3] * len(vals)

    out = []
    for v in vals:
        idx = int((v - mn) / (mx - mn) * (len(blocks) - 1))
        idx = max(0, min(len(blocks) - 1, idx))
        out.append(blocks[idx])

    return "".join(out)


def trend_chart_data(view=None, limit=80):
    """
    Trend mini chart adatcsomag.
    Tartalmaz:
    - sparkline
    - min/max/last
    - pontlista
    - kiválasztott pont
    """
    state = load_state()
    settings = state.get("settings", {})

    tr = trend_history_status(view=view, limit=limit)
    points = tr.get("points") or []
    values = [p.get("value") for p in points]

    selected_index = int(settings.get("trend_selected_index", -1) or -1)

    if not points:
        selected = None
    else:
        if selected_index < 0 or selected_index >= len(points):
            selected_index = len(points) - 1
        selected = points[selected_index]

    chart_width = int(settings.get("trend_chart_width", 60) or 60)

    return {
        "ok": True,
        "view": tr.get("view"),
        "value_key": tr.get("value_key"),
        "sparkline": _sparkline_from_values(values, chart_width),
        "points_count": len(points),
        "min": tr.get("min"),
        "max": tr.get("max"),
        "last": tr.get("last"),
        "selected_index": selected_index,
        "selected": selected,
        "points": points,
        "chart_width": chart_width,
        "note": "Ez a chart adat alap. Később Canvas érintés/célkereszt ebből dolgozik.",
    }


def select_trend_point(index=None):
    """
    Trend pont kijelölése index alapján.
    UI touch/crosshair később ezt fogja hívni.
    """
    state = load_state()
    settings = state.setdefault("settings", {})

    tr = trend_history_status()
    points = tr.get("points") or []

    if not points:
        return {"ok": False, "error": "Nincs trend pont."}

    try:
        idx = int(index)
    except Exception:
        idx = len(points) - 1

    idx = max(0, min(len(points) - 1, idx))
    settings["trend_selected_index"] = idx
    save_state(state)

    selected = points[idx]

    return {
        "ok": True,
        "selected_index": idx,
        "selected": selected,
        "message": "Trend pont kijelölve.",
    }


def select_trend_latest():
    tr = trend_history_status()
    points = tr.get("points") or []
    if not points:
        return {"ok": False, "error": "Nincs trend pont."}
    return select_trend_point(len(points) - 1)


def trend_crosshair_summary():
    """
    Kijelölt trendpont emberi olvasható adatpanel.
    """
    ch = trend_chart_data()
    sel = ch.get("selected") or {}

    if not sel:
        return {"ok": False, "message": "Nincs kijelölt trendpont."}

    return {
        "ok": True,
        "view": ch.get("view"),
        "selected_index": ch.get("selected_index"),
        "ts": sel.get("ts"),
        "value": sel.get("value"),
        "equity": sel.get("equity"),
        "total_value_usd": sel.get("total_value_usd"),
        "realized_pnl": sel.get("realized_pnl"),
        "pnl_pct_from_100": sel.get("pnl_pct_from_100"),
        "tradable_usd": sel.get("tradable_usd"),
        "quote_free_usd": sel.get("quote_free_usd"),
        "open_positions": sel.get("open_positions"),
        "last_action": sel.get("last_action"),
        "reason": sel.get("reason"),
    }



def format_trend_ts(ts=None):
    """
    Trend timestamp emberi idővé alakítása.
    """
    state = load_state()
    fmt = state.get("settings", {}).get("trend_time_format", "%Y-%m-%d %H:%M:%S")
    try:
        return time.strftime(fmt, time.localtime(int(ts or time.time())))
    except Exception:
        return str(ts)


def trend_history_stats(view=None, limit=300):
    """
    Trend statisztika: min/max/last/avg/change.
    """
    tr = trend_history_status(view=view, limit=limit)
    pts = tr.get("points") or []
    vals = []

    for p in pts:
        try:
            vals.append(float(p.get("value") or 0))
        except Exception:
            pass

    if not vals:
        return {
            "ok": True,
            "view": tr.get("view"),
            "points_count": 0,
            "message": "Nincs trend adat.",
        }

    first = vals[0]
    last = vals[-1]
    change = last - first
    change_pct = (change / abs(first) * 100.0) if first else 0.0

    return {
        "ok": True,
        "view": tr.get("view"),
        "value_key": tr.get("value_key"),
        "points_count": len(vals),
        "first": round(first, 8),
        "last": round(last, 8),
        "min": round(min(vals), 8),
        "max": round(max(vals), 8),
        "avg": round(sum(vals) / len(vals), 8),
        "change": round(change, 8),
        "change_pct": round(change_pct, 6),
        "first_time": format_trend_ts(pts[0].get("ts")),
        "last_time": format_trend_ts(pts[-1].get("ts")),
    }


def export_trend_history_csv(path=None):
    """
    Trend history export CSV-be.
    """
    state = load_state()
    settings = state.get("settings", {})

    if not bool(settings.get("trend_export_enabled", True)):
        return {"ok": False, "exported": False, "reason": "trend_export_enabled false"}

    hist = state.get("trend_history") or []

    if path is None:
        path = settings.get("trend_export_file", "logs/trend_history.csv") or "logs/trend_history.csv"

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    fields = [
        "ts",
        "time",
        "reason",
        "equity",
        "total_value_usd",
        "realized_pnl",
        "pnl_pct_from_100",
        "tradable_usd",
        "quote_free_usd",
        "open_positions",
        "last_action",
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()

        for row in hist:
            out = {}
            for k in fields:
                if k == "time":
                    out[k] = format_trend_ts(row.get("ts"))
                else:
                    out[k] = row.get(k, "")
            w.writerow(out)

    audit_event("TREND_EXPORT_CSV", "Trend history CSV export", {
        "path": path,
        "rows": len(hist),
        "order_endpoint_used": False,
    })

    return {
        "ok": True,
        "exported": True,
        "path": path,
        "rows": len(hist),
        "order_endpoint_used": False,
    }


def trend_export_status():
    state = load_state()
    settings = state.get("settings", {})
    path = settings.get("trend_export_file", "logs/trend_history.csv")

    return {
        "ok": True,
        "trend_export_enabled": settings.get("trend_export_enabled", True),
        "trend_export_file": path,
        "trend_time_format": settings.get("trend_time_format", "%Y-%m-%d %H:%M:%S"),
        "file_exists": os.path.exists(path),
        "history_points": len(state.get("trend_history") or []),
        "order_endpoint_used": False,
    }



def _trend_points_for_current_view(limit=300):
    tr = trend_history_status(limit=limit)
    return tr.get("points") or []


def select_trend_prev():
    """
    Kijelölt trendpont balra léptetése.
    """
    state = load_state()
    settings = state.setdefault("settings", {})
    pts = _trend_points_for_current_view()

    if not pts:
        return {"ok": False, "error": "Nincs trend pont."}

    cur = int(settings.get("trend_selected_index", len(pts) - 1) or 0)
    if cur < 0 or cur >= len(pts):
        cur = len(pts) - 1

    nxt = max(0, cur - 1)
    settings["trend_selected_index"] = nxt
    save_state(state)

    return {
        "ok": True,
        "selected_index": nxt,
        "selected": pts[nxt],
        "message": "Trend pont balra léptetve.",
    }


def select_trend_next():
    """
    Kijelölt trendpont jobbra léptetése.
    """
    state = load_state()
    settings = state.setdefault("settings", {})
    pts = _trend_points_for_current_view()

    if not pts:
        return {"ok": False, "error": "Nincs trend pont."}

    cur = int(settings.get("trend_selected_index", len(pts) - 1) or 0)
    if cur < 0 or cur >= len(pts):
        cur = len(pts) - 1

    nxt = min(len(pts) - 1, cur + 1)
    settings["trend_selected_index"] = nxt
    save_state(state)

    return {
        "ok": True,
        "selected_index": nxt,
        "selected": pts[nxt],
        "message": "Trend pont jobbra léptetve.",
    }


def select_trend_by_ratio(ratio=1.0):
    """
    Touch/crosshair előkészítés.
    ratio: 0.0 = bal széle, 1.0 = jobb széle.
    """
    state = load_state()
    settings = state.setdefault("settings", {})
    pts = _trend_points_for_current_view()

    if not pts:
        return {"ok": False, "error": "Nincs trend pont."}

    try:
        r = float(ratio)
    except Exception:
        r = 1.0

    r = max(0.0, min(1.0, r))
    idx = int(round(r * (len(pts) - 1)))

    settings["trend_selected_index"] = idx
    save_state(state)

    return {
        "ok": True,
        "ratio": r,
        "selected_index": idx,
        "selected": pts[idx],
        "message": "Trend pont arány alapján kijelölve.",
    }


def trend_selected_detail():
    """
    Részletes kijelölt trendpont adatpanel.
    """
    cross = trend_crosshair_summary()

    if not cross.get("ok"):
        return cross

    ts = cross.get("ts")

    return {
        "ok": True,
        "view": cross.get("view"),
        "selected_index": cross.get("selected_index"),
        "ts": ts,
        "time": format_trend_ts(ts),
        "value": cross.get("value"),
        "equity": cross.get("equity"),
        "total_value_usd": cross.get("total_value_usd"),
        "realized_pnl": cross.get("realized_pnl"),
        "pnl_pct_from_100": cross.get("pnl_pct_from_100"),
        "tradable_usd": cross.get("tradable_usd"),
        "quote_free_usd": cross.get("quote_free_usd"),
        "open_positions": cross.get("open_positions"),
        "last_action": cross.get("last_action"),
        "reason": cross.get("reason"),
        "order_endpoint_used": False,
    }


def trend_ascii_crosshair_bar(width=60):
    """
    Egyszerű vizuális bar, ahol a kijelölt indexnél | jel van.
    """
    chart = trend_chart_data()
    pts_count = int(chart.get("points_count", 0) or 0)
    idx = int(chart.get("selected_index", -1) or -1)

    try:
        width = int(width or 60)
    except Exception:
        width = 60

    if pts_count <= 0:
        return ""

    if pts_count == 1:
        pos = width - 1
    else:
        pos = int(round((idx / max(1, pts_count - 1)) * (width - 1)))

    chars = ["─"] * width
    if 0 <= pos < width:
        chars[pos] = "│"

    return "".join(chars)



def dashboard_trend_widget_data():
    """
    Dashboard trend widget rövid adat.
    Canvas chart és KPI alá.
    """
    state = load_state()
    settings = state.get("settings", {})

    if not bool(settings.get("dashboard_trend_widget_enabled", True)):
        return {
            "ok": False,
            "enabled": False,
            "reason": "dashboard_trend_widget_enabled false",
        }

    view = str(settings.get("dashboard_trend_widget_view", settings.get("trend_view_mode", "PROFIT")) or "PROFIT").upper()
    limit = int(settings.get("dashboard_trend_widget_points", 80) or 80)

    chart = trend_chart_data(view=view, limit=limit)
    detail = trend_selected_detail() if bool(settings.get("dashboard_show_selected_trend_point", True)) else {}

    stats = trend_history_stats(view=view, limit=limit)

    return {
        "ok": True,
        "enabled": True,
        "view": chart.get("view"),
        "value_key": chart.get("value_key"),
        "sparkline": chart.get("sparkline"),
        "crosshair_bar": trend_ascii_crosshair_bar(int(settings.get("trend_chart_width", 60) or 60)),
        "points_count": chart.get("points_count"),
        "selected": detail,
        "stats": stats,
        "note": "Dashboard trend widget adat kész.",
        "order_endpoint_used": False,
    }



def trend_auto_snapshot_tick(reason="auto_timer"):
    """
    Automata trend snapshot tick.
    UI Clock hívhatja.
    Order nincs.
    """
    state = load_state()
    settings = state.get("settings", {})

    if not bool(settings.get("trend_auto_snapshot_enabled", True)):
        return {
            "ok": False,
            "saved": False,
            "reason": "trend_auto_snapshot_enabled false",
            "order_endpoint_used": False,
        }

    if bool(settings.get("trend_auto_snapshot_only_when_running", False)) and not bool(state.get("running", False)):
        return {
            "ok": False,
            "saved": False,
            "reason": "bot_not_running",
            "order_endpoint_used": False,
        }

    try:
        # Portfolio cache frissítés, order nélkül.
        if bool(settings.get("spot_sync_enabled", True)):
            sync_spot_portfolio()
    except Exception:
        pass

    res = append_trend_history(reason)

    return {
        "ok": bool(res.get("ok")),
        "saved": bool(res.get("saved")),
        "points": res.get("points"),
        "row": res.get("row"),
        "order_endpoint_used": False,
    }


def trend_auto_refresh_status():
    state = load_state()
    settings = state.get("settings", {})
    hist = state.get("trend_history") or []

    return {
        "ok": True,
        "trend_auto_snapshot_enabled": settings.get("trend_auto_snapshot_enabled", True),
        "trend_auto_snapshot_interval_sec": settings.get("trend_auto_snapshot_interval_sec", 30),
        "trend_auto_snapshot_only_when_running": settings.get("trend_auto_snapshot_only_when_running", False),
        "dashboard_auto_refresh_enabled": settings.get("dashboard_auto_refresh_enabled", True),
        "dashboard_auto_refresh_interval_sec": settings.get("dashboard_auto_refresh_interval_sec", 15),
        "last_trend_snapshot_ts": state.get("last_trend_snapshot_ts", 0),
        "history_points": len(hist),
        "order_endpoint_used": False,
    }



def _safe_call(fn_name, default=None):
    try:
        fn = globals().get(fn_name)
        if callable(fn):
            return fn()
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return default if default is not None else {"ok": False, "reason": "missing_" + str(fn_name)}


def module_readiness_status():
    """
    Fő modulok készültségi állapota.
    Ez nem futtat ordert, csak meglévő status/cache függvényekből olvas.
    """
    state = load_state()
    settings = state.get("settings", {})

    checks = []

    def add(mid, title, ok, detail="", weight=1):
        checks.append({
            "id": mid,
            "title": title,
            "ok": bool(ok),
            "detail": detail,
            "weight": weight,
        })

    secrets = _safe_call("secrets_status", {})
    email = _safe_call("email_config_status", {})
    openai = _safe_call("openai_config_status", {})
    live = _safe_call("binance_live_status", {})
    health = _safe_call("healthcheck", {})
    trend = _safe_call("trend_auto_refresh_status", {})
    portfolio = _safe_call("spot_portfolio_status", {})
    live_gate = _safe_call("live_executor_gate_status", {})
    readonly = _safe_call("binance_readonly_real_status", {})
    package = _safe_call("apk_reference_status", {})

    add("demo_core", "Demo Core", True, "Core modul aktív")
    add("settings", "Settings", bool(settings), "settings state létezik")
    add("logs", "Logs / Audit", bool(globals().get("AUDIT_LOG")), "audit/trade log modul")
    add("healthcheck", "Healthcheck / Heartbeat", health.get("ok"), str(health.get("status", "")))
    add("safe_mode", "Panic Stop / Safe Mode", "panic_stop" in globals() and "safe_mode_off" in globals(), "panic + safe mode függvények")
    add("execution_mode", "Execution Mode", bool(settings.get("execution_mode")), str(settings.get("execution_mode")))
    add("profit_hold", "Profit Hold / Smart Exit", "hold_profit_minutes" in str(settings), "profit tartás beállítások")
    add("scanner", "Multi-symbol Scanner", "scan_symbols" in globals(), "scanner függvény")
    add("fee_tax", "Fee + Tax", "pnl_pct_breakdown" in globals(), "nettó/adó utáni PnL")
    add("trade_guard", "Trade Screen Guard", "trade_screen_check" in globals(), "BBO/spread/slippage")
    add("ai_advisor", "AI Advisor", "ai_advisor" in globals(), "offline/API advisor alap")
    add("secrets", "Encrypted Secrets", secrets.get("encrypted_file") or secrets.get("openai_ok"), "secrets.enc státusz")
    add("email", "Email Notify", "send_email_notification" in globals(), "email alap modul")
    add("openai", "OpenAI API", "call_openai_advisor" in globals(), "opcionális API fallback")
    add("binance_live_check", "Binance Live Check", live.get("ok"), "nem küld ordert")
    add("readonly_account", "Read-only Account", readonly.get("ok"), str(readonly.get("message", readonly.get("reason", ""))))
    add("live_gate", "Live Safety Gate", live_gate.get("ok"), "hard-stop gate")
    add("approval", "Approval / Dry-run", "create_approval_request" in globals() and "execute_latest_approved_dry_run" in globals(), "approval queue")
    add("portfolio", "Spot Portfolio Sync", portfolio.get("ok"), "total/tradable cache")
    add("trend", "Trend / Chart / Export", trend.get("ok"), "trend auto snapshot")
    add("backtest", "Backtest / Diagnostics", "backtest_symbol" in globals() and "diagnostics_status" in globals(), "backtest alap")
    add("schedules", "Schedules", "run_schedules_once" in globals(), "snapshot/trigger alap")
    add("launchpool", "Launchpool / Airdrop", "launchpool_scan" in globals(), "watch alap")
    add("package", "Package / Snapshot", package.get("ok") if isinstance(package, dict) else "export_project_package" in globals(), "APK reference/package")
    add("sync", "PC / Drive Sync", "sync_status" in globals(), "sync alap")
    add("first_run", "First-run Safety", "first_run_security_check" in globals(), "startup safety")
    add("admin", "Admin Security", "admin_status" in globals() and "admin_login" in globals(), "5 perc timeout")
    add("patch_manager", "Patch Manager", "queue_patch" in globals() or "patch_manager_status" in globals(), "safe queue")

    total_weight = sum(int(x.get("weight", 1)) for x in checks) or 1
    ok_weight = sum(int(x.get("weight", 1)) for x in checks if x.get("ok"))

    score = round((ok_weight / total_weight) * 100.0, 2)

    return {
        "ok": True,
        "score_pct": score,
        "ok_count": sum(1 for x in checks if x.get("ok")),
        "total_count": len(checks),
        "modules": checks,
        "order_endpoint_used": False,
    }


def missing_setup_status():
    """
    Hiányzó vagy még bekapcsolatlan kritikus beállítások.
    """
    state = load_state()
    settings = state.get("settings", {})
    missing = []
    warnings = []

    sec = _safe_call("load_secrets", {})
    if not isinstance(sec, dict):
        sec = {}

    def miss(key, title, level="warning", detail=""):
        row = {
            "key": key,
            "title": title,
            "level": level,
            "detail": detail,
        }
        if level == "critical":
            missing.append(row)
        else:
            warnings.append(row)

    if not sec.get("binance_api_key"):
        miss("binance_api_key", "Binance API key nincs megadva", "warning", "Live/read-only teszthez kell.")
    if not sec.get("binance_api_secret"):
        miss("binance_api_secret", "Binance API secret nincs megadva", "warning", "Signed read-only ellenőrzéshez kell.")
    if not sec.get("openai_api_key"):
        miss("openai_api_key", "OpenAI API key nincs megadva", "warning", "AI API módhoz kell, offline AI ettől még működik.")
    if not sec.get("email_user") or not sec.get("email_app_password") or not sec.get("email_to"):
        miss("email_config", "E-mail adatok hiányosak", "warning", "Teszt e-mailhez és riasztáshoz kell.")
    if not sec.get("google_drive_token"):
        miss("google_drive_token", "Google Drive token nincs megadva", "warning", "Drive sync teljes működéséhez kell.")
    if not sec.get("pc_sync_token"):
        miss("pc_sync_token", "PC sync token nincs megadva", "warning", "PC agent későbbi kapcsolathoz kell.")

    if not bool(settings.get("binance_signed_readonly_enabled", False)):
        miss("binance_signed_readonly_enabled", "Signed read-only nincs bekapcsolva", "warning", "Első valódi account olvasáshoz külön engedély kell.")
    if not bool(settings.get("binance_account_read_enabled", False)):
        miss("binance_account_read_enabled", "Account read nincs bekapcsolva", "warning", "Balance sync valódi Binance olvasáshoz kell.")
    if not bool(settings.get("binance_real_account_get_enabled", False)):
        miss("binance_real_account_get_enabled", "Real account GET nincs bekapcsolva", "warning", "Valódi /api/v3/account olvasáshoz kell.")

    if bool(settings.get("live_mode_enabled", False)):
        live = _safe_call("binance_live_status", {})
        if not live.get("ready_for_live"):
            miss("live_not_ready", "Live mód aktív, de nem ready", "critical", "Hiányzó API/jóváhagyás/safety miatt.")

    # Ez szándékosan jó: order endpoint még nincs bekötve
    if bool(settings.get("live_executor_enabled", False)):
        miss("live_executor_enabled", "Live executor be van kapcsolva", "critical", "Csak végső hard-confirm után legyen engedve.")

    return {
        "ok": True,
        "critical_missing_count": len(missing),
        "warnings_count": len(warnings),
        "critical": missing,
        "warnings": warnings,
        "safe_note": "Order endpoint továbbra sincs bekötve.",
        "order_endpoint_used": False,
    }


def next_recommended_steps():
    """
    Következő logikus fejlesztési lépések.
    """
    state = load_state()
    settings = state.get("settings", {})
    mod = module_readiness_status()
    miss = missing_setup_status()

    steps = []

    def add(priority, title, reason, patch=""):
        steps.append({
            "priority": priority,
            "title": title,
            "reason": reason,
            "patch": patch,
        })

    if miss.get("warnings_count", 0) > 0:
        add(1, "Secrets / Integrációk kitöltése és tesztelése", "API/OpenAI/email/Drive/PC mezők hiányozhatnak.", "PATCH_INTEGRATION_TESTS_UI.sh")

    if "master_status" not in str(settings):
        add(2, "Master Status UI finomítás", "Áttekintő képernyő után könnyebb fejleszteni.", "PATCH_MASTER_STATUS_UI_POLISH.sh")

    add(3, "Modern Dashboard KPI kártyák", "A dashboard adat már megvan, most UI-kártyákba kell rendezni.", "PATCH_DASHBOARD_MODERN_KPI_CARDS.sh")
    add(4, "Top coin mini-kártyák", "Scanner + portfolio cache alapján top coin lista kell.", "PATCH_TOP_COIN_CARDS.sh")
    add(5, "Demo Reset megerősítő popup", "Biztonságosabb reset, csak Demo módban.", "PATCH_DEMO_RESET_CONFIRM_MODAL.sh")
    add(6, "Trade Simple / Advanced szétválasztás", "Beállítások már vannak, UI-t kell rendezni.", "PATCH_TRADE_SIMPLE_ADVANCED_UI.sh")
    add(7, "Read-only Binance valós balance teszt", "Order nélkül, csak /api/v3/account olvasás.", "PATCH_READONLY_BALANCE_TEST_FLOW.sh")
    add(8, "APK build előtti safe full test", "Csak akkor build, ha minden compile és status zöld.", "PATCH_PRE_APK_FULL_SAFE_TEST.sh")

    return {
        "ok": True,
        "readiness_score_pct": mod.get("score_pct"),
        "steps": steps,
        "order_endpoint_used": False,
    }


def master_status_overview():
    """
    Egy helyen minden fontos állapot.
    """
    state = load_state()
    settings = state.get("settings", {})

    kpi = _safe_call("dashboard_kpi_snapshot", {})
    portfolio = _safe_call("spot_portfolio_status", {})
    trend = _safe_call("trend_auto_refresh_status", {})
    health = _safe_call("healthcheck", {})
    secrets = _safe_call("secrets_status", {})
    email = _safe_call("email_config_status", {})
    openai = _safe_call("openai_config_status", {})
    live = _safe_call("binance_live_status", {})
    live_gate = _safe_call("live_executor_gate_status", {})
    readonly = _safe_call("binance_readonly_real_status", {})
    package = _safe_call("apk_reference_status", {})
    modules = module_readiness_status()
    missing = missing_setup_status()
    steps = next_recommended_steps()

    return {
        "ok": True,
        "app_version": globals().get("APP_VERSION", "unknown"),
        "mode": "LIVE" if settings.get("live_mode_enabled") else "DEMO",
        "running": bool(state.get("running", False)),
        "safe_mode": bool(state.get("safe_mode", False)),
        "execution_mode": settings.get("execution_mode", "AUTO"),
        "last_action": state.get("last_action", ""),
        "portfolio": {
            "total_value_usd": kpi.get("total_value_usd", portfolio.get("portfolio_total_value_usd")),
            "tradable_usd": kpi.get("tradable_usd", portfolio.get("portfolio_tradable_usd")),
            "open_positions": kpi.get("open_positions"),
            "usdc_free": kpi.get("usdc_free"),
            "usdt_free": kpi.get("usdt_free"),
        },
        "trend": {
            "history_points": trend.get("history_points"),
            "last_trend_snapshot_ts": trend.get("last_trend_snapshot_ts"),
            "auto_enabled": trend.get("trend_auto_snapshot_enabled"),
        },
        "integrations": {
            "secrets_encrypted": secrets.get("encrypted_file"),
            "plain_file_exists": secrets.get("plain_file_exists"),
            "email_ok": email.get("ok") if isinstance(email, dict) else False,
            "openai_ok": openai.get("has_key") if isinstance(openai, dict) else secrets.get("openai_ok"),
            "binance_live_ready": live.get("ready_for_live") if isinstance(live, dict) else False,
            "readonly_ok": readonly.get("ok") if isinstance(readonly, dict) else False,
        },
        "safety": {
            "health_status": health.get("status"),
            "live_gate_ok": live_gate.get("ok") if isinstance(live_gate, dict) else False,
            "order_endpoint_used": False,
            "safe_note": "Valódi Binance order endpoint továbbra sincs bekötve.",
        },
        "package": package,
        "readiness": {
            "score_pct": modules.get("score_pct"),
            "ok_count": modules.get("ok_count"),
            "total_count": modules.get("total_count"),
        },
        "missing": missing,
        "modules": modules.get("modules", []),
        "next_steps": steps.get("steps", []),
        "order_endpoint_used": False,
    }



def order_endpoint_safety_scan():
    """
    Biztonsági scan: van-e éles order küldésre utaló bekötés.
    Ez csak szöveget/állapotot vizsgál, nem hív hálózatot.
    """
    suspicious = []
    files = ["demo_core_engine.py", "main.py"]

    patterns = [
        "api/v3/order",
        "/api/v3/order",
        "create_order",
        "new_order",
        "order/test",
        "signed_order",
        "LIVE ORDER SENT",
    ]

    for fn in files:
        try:
            with open(fn, "r", encoding="utf-8") as f:
                text = f.read()
            for pat in patterns:
                if pat in text:
                    suspicious.append({
                        "file": fn,
                        "pattern": pat,
                        "note": "Találat csak ellenőrzést jelent; lehet biztonságos test/validate szöveg is.",
                    })
        except Exception as e:
            suspicious.append({
                "file": fn,
                "pattern": "READ_ERROR",
                "note": str(e),
            })

    safe = True
    hard_blocks = []

    # A jelenlegi rendszerben az order/test szöveg validáció miatt elfogadható,
    # de valódi /api/v3/order endpoint használat nem lehet engedélyezett.
    for x in suspicious:
        pat = x.get("pattern")
        if pat in ["api/v3/order", "/api/v3/order", "create_order", "new_order", "signed_order", "LIVE ORDER SENT"]:
            hard_blocks.append(x)
            safe = False

    return {
        "ok": True,
        "safe": safe,
        "suspicious_count": len(suspicious),
        "hard_block_count": len(hard_blocks),
        "suspicious": suspicious,
        "hard_blocks": hard_blocks,
        "order_endpoint_used": False,
        "message": "Order endpoint safety scan lefutott.",
    }


def compile_status_check():
    """
    Runtime oldalról csak import/függvény jelenlét check.
    A shell py_compile külön fut.
    """
    required = [
        "master_status_overview",
        "module_readiness_status",
        "missing_setup_status",
        "next_recommended_steps",
        "healthcheck",
        "trend_auto_refresh_status",
        "spot_portfolio_status",
    ]

    missing = [x for x in required if x not in globals()]

    return {
        "ok": len(missing) == 0,
        "missing": missing,
        "checked": required,
        "order_endpoint_used": False,
    }


def export_module_status_report(path=None):
    """
    Master/module/missing/next_steps JSON report.
    """
    state = load_state()
    settings = state.get("settings", {})

    if path is None:
        path = settings.get("pre_apk_report_file", "logs/pre_apk_safe_report.json") or "logs/pre_apk_safe_report.json"

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    report = {
        "ts": int(time.time()),
        "app_version": globals().get("APP_VERSION", "unknown"),
        "compile_status": compile_status_check(),
        "order_scan": order_endpoint_safety_scan(),
        "master_status": master_status_overview(),
        "module_readiness": module_readiness_status(),
        "missing_setup": missing_setup_status(),
        "next_steps": next_recommended_steps(),
        "order_endpoint_used": False,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    audit_event("PRE_APK_REPORT_EXPORT", "Pre-APK safe report export", {
        "path": path,
        "order_endpoint_used": False,
    })

    return {
        "ok": True,
        "path": path,
        "order_endpoint_used": False,
        "message": "Module status report export kész.",
    }


def stable_checkpoint_summary():
    """
    Aktuális stabil checkpoint összefoglaló.
    Git tag shellből pontosabb, itt app szintű summary.
    """
    st = master_status_overview()

    return {
        "ok": True,
        "app_version": st.get("app_version"),
        "mode": st.get("mode"),
        "readiness": st.get("readiness"),
        "safety": st.get("safety"),
        "portfolio": st.get("portfolio"),
        "trend": st.get("trend"),
        "recommended_next_patch": (st.get("next_steps") or [{}])[0].get("patch"),
        "apk_build_touched": False,
        "order_endpoint_used": False,
    }


def pre_apk_full_safe_test():
    """
    Build előtti teljes safe gate.
    Nem buildel APK-t.
    Nem küld ordert.
    """
    state = load_state()
    settings = state.get("settings", {})

    compile_check = compile_status_check()
    order_scan = order_endpoint_safety_scan()
    master = master_status_overview()
    modules = module_readiness_status()
    missing = missing_setup_status()

    min_score = float(settings.get("pre_apk_min_readiness_score_pct", 70.0) or 70.0)
    score = float(modules.get("score_pct", 0.0) or 0.0)

    blockers = []
    warnings = []

    if bool(settings.get("pre_apk_require_compile_ok", True)) and not compile_check.get("ok"):
        blockers.append("compile/runtime required function missing")

    if bool(settings.get("pre_apk_require_no_order_endpoint", True)) and not order_scan.get("safe"):
        blockers.append("order endpoint suspicious hard block found")

    if bool(settings.get("pre_apk_require_master_status_ok", True)) and not master.get("ok"):
        blockers.append("master status not ok")

    if score < min_score:
        warnings.append(f"readiness score alacsony: {score}% < {min_score}%")

    if missing.get("critical_missing_count", 0) > 0:
        blockers.append("critical missing setup exists")

    report_export = export_module_status_report(settings.get("pre_apk_report_file", "logs/pre_apk_safe_report.json"))

    ready_for_apk_test_build = len(blockers) == 0

    return {
        "ok": True,
        "ready_for_apk_test_build": ready_for_apk_test_build,
        "blockers": blockers,
        "warnings": warnings,
        "compile": compile_check,
        "order_scan": order_scan,
        "readiness_score_pct": score,
        "min_required_score_pct": min_score,
        "report": report_export,
        "apk_build_touched": False,
        "order_endpoint_used": False,
        "message": "Pre-APK full safe test lefutott. Ez még nem APK build.",
    }


if __name__ == "__main__":
    print(json.dumps(tick(), ensure_ascii=False, indent=2))
