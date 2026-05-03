# Trade Simple / Strategy Advanced UI státusz

## Egy patchben elkészült 4 rész

### 1. Trade Simple UI data
- symbol
- side
- quote amount
- risk %
- min after-tax profit
- guard
- AI preview
- fee/tax preview

### 2. Strategy Advanced UI data
- SMA/RSI/ATR
- stop/trailing/hold/cooldown
- scanner edge score
- fee/tax beállítások

### 3. Strategy validation
- numerikus értékek
- risk/max positions
- SMA fast/slow
- fee/tax/min profit
- edge score
- warning/error lista

### 4. Strategy safety preview
- guard
- AI
- after-tax preview
- blockers
- would_send_live_order = false

## Biztonság
- Binance order nincs
- order_endpoint_used = false
- csak beállítás mentés és előnézet
- APK buildhez nem nyúl
