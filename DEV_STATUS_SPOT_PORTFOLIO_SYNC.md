# Spot Balance / Portfolio Sync státusz

## Elkészült
- Spot balance normalizálás
- Demo fallback, ha nincs Binance API
- Read-only Binance account használható, ha külön be van kapcsolva
- Portfolio USD/USDC valuation
- Tradable amount számítás
- Safety reserve
- Max tradeable %
- UI menü: SPOT PORTFOLIO

## Számítás
Tradable USD:
- quote free USD
- mínusz safety reserve
- maximum spot_max_tradeable_pct szerint

## Biztonság
- Order endpoint nincs használva
- /api/v3/order nincs bekötve
- /api/v3/order/test nincs hívva
- Csak balance sync / valuation
- APK buildhez nem nyúl
