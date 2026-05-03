# Health / Alert / Recovery Center státusz

## Egy patchben elkészült 4 rész

### 1. Healthcheck Center
- health_alert_center_status()
- integration/master státusz kapcsolás

### 2. Heartbeat / Last Seen
- heartbeat_status()
- update_heartbeat()
- stale_after_sec

### 3. Error Alert Summary
- safe mode
- warnings
- healthcheck
- live gate
- readonly gate

### 4. Crash Recovery / Resume Status
- pozíciók száma
- safe mode blocker
- resume flag
- ajánlott lépések

## Biztonság
- Binance order nincs
- order_endpoint_used = false
- csak state/log/status olvasás
- APK buildhez nem nyúl
