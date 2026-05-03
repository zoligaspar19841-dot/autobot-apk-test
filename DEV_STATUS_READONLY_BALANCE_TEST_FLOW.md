# Read-only Binance Balance Test Flow státusz

## Egy patchben elkészült 4 rész

### 1. Read-only Balance Test Flow
- plan
- gate
- run_readonly_balance_test
- alapból nem hív hálózatot

### 2. API jogosultság / gate check
- Binance API key
- Binance API secret
- signed read-only kapcsoló
- account read kapcsoló
- real account GET kapcsoló
- network engedély

### 3. Spot balance sync preview
- portfolio status
- valuation preview
- real Binance csak akkor, ha gate zöld

### 4. Read-only report export
- logs/readonly_balance_report.json

## Biztonság
- Binance order nincs
- binance_order_allowed = false
- order_endpoint_used = false
- hálózat alapból OFF
- APK buildhez nem nyúl
