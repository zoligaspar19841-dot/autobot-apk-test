# Admin + Patch Manager státusz

## Admin Security
- Alap login: admin / admin
- Session timeout: 300 sec = 5 perc
- Timeout után admin_session_active = false
- Jelszó hash + salt, plain jelszó nincs mentve
- Első használat után jelszócsere szükséges/javasolt

## Patch Manager Safe Base
- Egyelőre queue funkció
- Apply még nincs bekapcsolva
- Admin login szükséges, ha patch_require_admin = true
- Path traversal tiltva
- Engedélyezett path:
  - main.py
  - demo_core_engine.py
  - DEV_STATUS*.md
  - README*.md

## APK szabály
- APK buildhez ez a patch nem nyúl
- Működő APK referencia: APK 0.2.5
