# APK / fejlesztési státusz

## Utolsó ismert működő APK referencia
- APK 0.2.5
- Ezt tekintjük stabil referencia APK-nak.
- A jelenlegi fejlesztés kódoldali patch sorozat.
- Új APK build csak akkor induljon, ha a kódoldali tesztek stabilak.

## Build szabály
- APK buildhez nem nyúlunk fejlesztés közben.
- Build csak külön, tudatos lépésben.
- Ha build hibázik, a stabil APK referencia továbbra is APK 0.2.5.

## Jelenlegi modulok
- Demo Core
- Settings
- Logs / Export
- Panic Stop / Safe Mode
- Healthcheck / Heartbeat
- Audit log
- Execution mode AUTO/MANUAL/OFF
- Profit hold / smart exit
- Multi-symbol scanner
- Fee + HU tax estimate
- Binance trade screen BBO / spread / slippage logic
- Offline AI advisor + optional OpenAI API fallback
- Encrypted secrets
- Email notification base
- Binance Live API check only
- Backtest / Replay base
- Diagnostics
- Schedules
- Launchpool / Airdrop watch
- Package / Snapshot export

## Secrets
- secrets.enc nincs GitHubon
- demo_core_secret.key nincs GitHubon
- .env nincs GitHubon
