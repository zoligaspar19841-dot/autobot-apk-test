# Live Executor Safety Gate státusz

## Cél
Éles Binance order előtt végső safety kapu.

## Ez még NEM orderküldés
- Nem hív Binance order endpointot
- Nem vesz / nem ad el
- Csak ellenőriz és auditál

## Hard-stop szabályok
Live csak akkor engedhető később, ha:
- live_executor_enabled = true
- Binance live status ready
- admin session aktív
- approval request jóváhagyva
- Safe Mode false
- execution_mode nem OFF
- BUY/SELL külön engedélyezve
- amount <= live_max_order_usdt_hard
- healthcheck warning nincs
- trade guard OK
- AI nem HOLD/BLOCKED
- fee/adó utáni profit elég, ha van gross profit adat

## APK szabály
- APK buildhez ez a patch nem nyúl
- Működő APK referencia: APK 0.2.5
