# Binance Signed Read-only státusz

## Elkészült
- Signed query helper
- Signed request preview
- Read-only account check előkészítés
- API key/secret hiány kezelése
- UI menü: BINANCE SIGNED

## Biztonság
- Order endpoint nincs bekötve
- /api/v3/order nincs hívva
- /api/v3/order/test nincs hívva
- /api/v3/account valódi hálózati GET még nincs hívva ebben a patchben

## Következő lehetséges lépés
- Read-only GET /api/v3/account valódi hívás csak külön kapcsolóval
- timeout + error handling
- rate-limit kezelés

## APK szabály
- APK buildhez ez a patch nem nyúl
- Működő APK referencia: APK 0.2.5
