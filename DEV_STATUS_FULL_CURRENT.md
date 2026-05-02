# Binance Autobot aktuális fejlesztési státusz

## Utolsó ismert működő APK referencia
- APK 0.2.5
- APK buildhez a fejlesztés alatt nem nyúlunk.
- Új APK csak külön stabil build-lépésben.

## Stabil Git checkpointok
- stable-sync-firstrun
- stable-admin-patchmanager
- stable-approval-dryrun
- stable-live-gate
- stable-binance-account-testorder
- stable-binance-signed-readonly

## Elkészült modulok

### Demo Core
- Demo state
- Tick motor
- Pozíciókezelés
- Demo reset
- Equity számítás

### UI
- Demo Core dashboard
- KPI mezők
- Vissza navigáció
- Settings
- Logs / Export
- Healthcheck
- Audit log
- Approval / Dry-run
- Live Gate
- Binance Account
- Binance Signed Read-only

### Safety
- Panic Stop
- Safe Mode
- Healthcheck / Heartbeat
- Execution mode AUTO / MANUAL / OFF
- Approval Queue
- Dry-run Executor
- Live Safety Gate
- Hard-stop szabályok

### Profit / fee / adó
- Maker/taker fee
- HU 15% irányadó adó utáni profit kalkuláció
- Min after-tax profit guard
- Profit-hold / smart exit alap

### Binance logika
- Trade screen BBO / spread / slippage guard
- Test order payload validate
- Signed request preview
- Read-only account előkészítés
- Valódi order endpoint nincs bekötve

### AI
- Offline AI advisor
- OpenAI API fallback előkészítve
- AI HOLD/BLOCKED safety gate-ben figyelve

### Integrációk
- Encrypted secrets
- Email notification base
- PC / Drive sync alap
- Package / Snapshot export
- First-run wizard
- Admin 5 perc timeout
- Patch Manager queue

## Fontos biztonsági állapot
- Live executor alapból OFF
- Live BUY/SELL alapból tiltott
- Order endpoint nincs bekötve
- /api/v3/order nincs hívva
- /api/v3/order/test nincs hívva
- /api/v3/account valódi hálózati GET még nincs hívva
- Secrets nincs GitHubon

## Következő biztonságos lépés
1. Read-only Binance GET /api/v3/account valódi hívás külön kapcsolóval
2. Timeout / hibakezelés / rate-limit védelem
3. Csak account balance olvasás
4. Utána külön teszt-order endpoint, még mindig éles order nélkül
