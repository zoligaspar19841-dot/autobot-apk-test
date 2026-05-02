# Binance Autobot fejlesztési állapot

## Stabil referencia
- STABLE APK 0.2.5 fut telefonon.
- A működő APK-vonalat nem piszkáljuk.
- GitHub/Buildozer APK build jelenleg nem fejlesztési alap.
- Új funkciók kis patch-ekben készülnek.

## Elkészült kódoldali fejlesztések

### 1. Demo Core Engine v1
- demo_core_engine.py létrehozva
- demo reset működik
- demo balance: 100 USDC alap
- buy/sell logika
- pozíció kezelés
- realized PnL
- equity számítás
- watchlist: BTCUSDT, ETHUSDT, DOGEUSDT
- risk_pct
- max_positions
- min_profit_pct
- trailing_drop_pct
- stop_loss_pct
- trade CSV log

### 2. Demo Core teszt
- test_demo_core_engine.py létrehozva
- Termux teszt sikeres
- BUY BTCUSDT működött
- BUY ETHUSDT működött
- HOLD / PnL / equity számítás működött

### 3. Kivy UI bekötés
- DemoCoreScreen hozzáadva main.py-ba
- főmenü DEMO gomb célpontja: demo_core
- sm.add_widget(DemoCoreScreen(name="demo_core")) bent van

### 4. Demo Core KPI UI
- Balance
- Equity
- Realized PnL
- Open Positions
- Last Action
- Pozíciólista
- START / STOP / TICK / RESET / VISSZA gombok

### 5. Auto tick
- START után automatikus tick 15 másodpercenként
- STOP leállítja
- képernyőről kilépéskor stop_auto_tick fut

### 6. Vissza navigáció
- HistoryScreenManager hozzáadva
- go_to()
- go_back()
- VISSZA gombok nem fixen főmenüre dobnak, hanem előző képernyő logika szerint működnek

## Fontos szabály
- APK-buildhez nem nyúlunk addig, amíg a kódoldali funkciók stabilak.
- A működő APK 0.2.5 referencia marad.
- Következő fejlesztés: Demo Core Settings UI / motor paraméterek állítása.
