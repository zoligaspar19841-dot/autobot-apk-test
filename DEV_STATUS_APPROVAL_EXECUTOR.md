# Approval Queue + Dry-run Executor státusz

## Approval Queue
- Trade request létrehozás
- Pending / Approved / Rejected státusz
- Admin login kell jóváhagyáshoz/elutasításhoz

## Dry-run Executor
- Csak száraz futtatás
- Nem küld Binance ordert
- Audit logba ír
- Ellenőrzi a trade guardot és live státuszt
- Később erre épülhet a live executor, külön biztonsági patchként

## APK szabály
- APK buildhez ez a patch nem nyúl
- Működő APK referencia: APK 0.2.5
