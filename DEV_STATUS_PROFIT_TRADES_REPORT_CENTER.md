# Profit / Trades Report Center státusz

## Egy patchben elkészült 4 rész

### 1. Trades report center
- trade log státusz
- audit log státusz
- report fájlok

### 2. Nettó + adózás utáni PnL summary
- realized_pnl
- net_before_tax_pnl
- estimated_tax_value
- after_tax_pnl
- trade/buy/sell count

### 3. Position / trade audit link
- nyitott pozíciók
- utolsó audit sorok

### 4. CSV/JSON export report
- logs/profit_report.json
- logs/profit_report.csv

## Biztonság
- Binance order nincs
- order_endpoint_used = false
- csak fájlokat/cache-t olvas
- APK buildhez nem nyúl
