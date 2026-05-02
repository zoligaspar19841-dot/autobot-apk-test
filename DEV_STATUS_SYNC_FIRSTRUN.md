# Sync + First-Run státusz

## PC / Drive Sync
- Alap sync mappák:
  - AutobotBackups
  - PCSync
- Export ZIP secrets nélkül.
- Import csak engedélyezett fájlokat vesz át:
  - demo_core_state.json
  - logs/*.csv
  - logs/*.json
  - logs/*.txt
- Tiltott import/export:
  - secrets.enc
  - demo_core_secret.key
  - demo_core_secrets.json
  - .env
  - *.key
  - *.enc

## First-Run Wizard
Ellenőrzi:
- titkosított secrets fájl
- Binance API státusz
- e-mail státusz
- OpenAI kulcs státusz
- sync mappák
- live safety státusz

## APK szabály
- APK buildhez ez a patch nem nyúl.
- Működő APK referencia továbbra is APK 0.2.5.
