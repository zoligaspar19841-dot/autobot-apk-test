import json, urllib.request, time

BINANCE = "https://api.binance.com"

def http_json(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "BinanceAutobotAI/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def get_24h_all():
    return http_json(BINANCE + "/api/v3/ticker/24hr")

def score_coin(x):
    try:
        symbol = x.get("symbol", "")
        if not symbol.endswith("USDT"):
            return None

        price_change = float(x.get("priceChangePercent", 0) or 0)
        quote_volume = float(x.get("quoteVolume", 0) or 0)
        last_price = float(x.get("lastPrice", 0) or 0)

        if quote_volume <= 0 or last_price <= 0:
            return None

        # egyszerű edge score: momentum + likviditás + kockázat szűrés
        vol_score = min(quote_volume / 100_000_000, 1.0)
        mom_score = max(min(price_change / 10.0, 1.0), -1.0)

        # túl nagy pumpát óvatosan büntetünk
        pump_penalty = 0.25 if price_change > 18 else 0.0

        edge = (0.60 * mom_score) + (0.40 * vol_score) - pump_penalty

        return {
            "symbol": symbol,
            "price": last_price,
            "change": price_change,
            "volume": quote_volume,
            "edge": edge,
            "signal": "BUY WATCH" if edge >= 0.55 else "WATCH" if edge >= 0.35 else "SKIP"
        }
    except Exception:
        return None

def recommendations(limit=12):
    data = get_24h_all()
    scored = []
    for x in data:
        r = score_coin(x)
        if r:
            scored.append(r)

    scored.sort(key=lambda a: a["edge"], reverse=True)
    return scored[:limit]
