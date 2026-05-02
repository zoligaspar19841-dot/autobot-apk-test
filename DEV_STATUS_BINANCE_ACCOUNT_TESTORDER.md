# Binance Account + Test Order Validate státusz

## Account adapter
- API key/secret meglétét ellenőrzi
- Private account endpointot még nem hív
- Secrets továbbra is encrypted local

## Test order validate
- Payload formátumot ellenőriz
- Live safety gate-et meghívja
- Binance order/test endpointot még NEM hív
- Valódi order NEM megy ki

## Következő biztonságos lépés
- Signed request helper
- GET /api/v3/account read-only account check
- POST /api/v3/order/test csak külön kapcsolóval
- Valódi /api/v3/order még később, külön engedéllyel

## APK szabály
- APK buildhez ez a patch nem nyúl
- Működő APK referencia: APK 0.2.5
