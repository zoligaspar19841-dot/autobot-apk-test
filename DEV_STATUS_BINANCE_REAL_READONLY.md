# Binance Real Read-only Account státusz

## Elkészült
- Valódi signed GET helper
- Csak /api/v3/account engedélyezett
- Timeout kezelés
- HTTPError kezelés
- Balance preview
- UI menü: BINANCE READONLY

## Kapcsolók
Valódi account GET csak akkor fut, ha mindhárom true:
- binance_signed_readonly_enabled
- binance_account_read_enabled
- binance_real_account_get_enabled

## Biztonság
- /api/v3/order tiltva
- /api/v3/order/test nincs hívva
- Csak read-only account endpoint
- API kulcs nélkül nem fut
- Order endpoint used: false

## APK szabály
- APK buildhez ez a patch nem nyúl
- Működő APK referencia: APK 0.2.5
