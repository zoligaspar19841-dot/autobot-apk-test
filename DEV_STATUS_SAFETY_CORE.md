# Binance Autobot - Safety Core checkpoint

## Stabil APK
- STABLE APK 0.2.5 továbbra is a működő telefonos referencia.
- Az APK build rendszert nem piszkáltuk.
- A működő APK artifactként visszaállítható.
- A jelenlegi fejlesztés kódoldali, külön commitokban mentve.

## Kész kódoldali funkciók

### Demo Core Engine
- Demo reset
- Demo balance
- Buy / hold / sell logika
- Pozíciókezelés
- Equity
- Realized PnL
- Trade CSV log

### Demo Core UI
- DEMO főgomb demo_core képernyőre kötve
- KPI dashboard
- Balance
- Equity
- Realized PnL
- Open Positions
- START / STOP / TICK / RESET

### Settings UI
- risk_pct
- max_positions
- min_profit_pct
- stop_loss_pct
- trailing_drop_pct
- watchlist

### Logs / Export UI
- demo_core_trades.csv megjelenítés
- napló frissítés
- tick + frissítés
- napló nullázás

### Auto tick
- START után 15 mp-enként tick
- STOP leállítja
- képernyőről kilépéskor leállítás

### Safety
- Panic Stop
- safe_mode=True
- új vétel tiltása safe mode alatt
- Safe Mode KI gomb

### Healthcheck / Heartbeat
- status
- running
- safe_mode
- positions_count
- balance
- equity
- trade_log_exists
- last_tick_ts
- last_heartbeat_ts
- warnings

### Navigation
- HistoryScreenManager
- go_to()
- go_back()
- VISSZA gomb előző képernyőre megy

## Fontos szabály
- Buildozer / GitHub APK build továbbra sem fejlesztési alap.
- A működő APK 0.2.5 marad referencia.
- Új APK csak akkor, ha a kódoldali fejlesztés stabil és külön tesztelt.
