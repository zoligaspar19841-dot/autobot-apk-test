# Dashboard KPI + Trend History státusz

## Elkészült
- Dashboard KPI snapshot
- Portfolio cache alapú Total Value
- Tradable USD
- USDC / USDT free
- Open positions
- Realized PnL
- Profit % from 100 reference
- Trend history state-ben
- Több trend nézet:
  - EQUITY
  - PROFIT
  - TRADABLE
  - TOTAL_VALUE

## Trend pont adat
Minden pont tartalmaz:
- ts
- equity
- total_value_usd
- realized_pnl
- pnl_pct_from_100
- tradable_usd
- quote_free_usd
- open_positions
- last_action
- reason

## Következő UI lépés
- Rajzolt mini chart
- Touch/crosshair kijelzés
- időbélyeg formázás
- export CSV

## Biztonság
- Order endpoint nincs használva
- APK buildhez nem nyúl
