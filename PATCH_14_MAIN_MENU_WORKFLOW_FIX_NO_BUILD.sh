#!/usr/bin/env bash
set -u

echo "=== PATCH 14: MAIN MENU + GITHUB WORKFLOW FIX - APK BUILD NELKUL ==="
echo "Nem buildel, nem kuld Binance ordert. Csak main menu es workflow javitas."

cd "${1:-$PWD}"

if [ ! -f main.py ]; then
  echo "HIBA: main.py nem talalhato. Elobb: cd ~/autobot-apk-test"
  exit 1
fi

TS=$(date +%Y%m%d_%H%M%S)
mkdir -p backups logs .github/workflows

backup_file() {
  f="$1"
  if [ -f "$f" ]; then
    cp "$f" "backups/$(basename "$f").bak_patch14_$TS"
    echo "BACKUP: $f -> backups/$(basename "$f").bak_patch14_$TS"
  fi
}

backup_file main.py
backup_file apk_stage/main.py
backup_file .github/workflows/android.yml

patch_main() {
  f="$1"
  [ -f "$f" ] || return 0
  python3 - "$f" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
s = p.read_text(encoding='utf-8', errors='replace')
orig = s

s = s.replace('safe_add_screen(sm, Main(name="main"))', 'safe_add_screen(sm, MasterMenu(name="main"))')
s = s.replace("safe_add_screen(sm, Main(name='main'))", "safe_add_screen(sm, MasterMenu(name='main'))")

if s != orig:
    p.write_text(s, encoding='utf-8')
    print('OK patched:', p)
else:
    print('NO CHANGE needed:', p)
PY
}

patch_main main.py
patch_main apk_stage/main.py

cat > .github/workflows/android.yml <<'YAML'
name: Build APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Java 17
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install system packages
        run: |
          sudo apt-get update
          sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip python3-setuptools python3-wheel autoconf libtool pkg-config zlib1g-dev libncurses5 libstdc++6

      - name: Install Python build tools
        run: |
          python -m pip install --upgrade pip setuptools wheel
          python -m pip install buildozer cython==0.29.36

      - name: Prepare build logs
        run: |
          mkdir -p ci_logs
          echo "Workflow ready" > ci_logs/build_info.txt
          echo "Commit: $GITHUB_SHA" >> ci_logs/build_info.txt
          python --version >> ci_logs/build_info.txt
          java -version 2>> ci_logs/build_info.txt || true

      - name: Prepare fixed debug keystore if present
        run: |
          mkdir -p ~/.android
          if [ -f keystore/autobot-debug.keystore ]; then
            cp keystore/autobot-debug.keystore ~/.android/debug.keystore
            chmod 600 ~/.android/debug.keystore
            keytool -list -keystore ~/.android/debug.keystore -storepass android -alias androiddebugkey || true
            echo "Fixed debug keystore installed" | tee -a ci_logs/build_info.txt
          else
            echo "No fixed debug keystore in repo; buildozer default debug key will be used" | tee -a ci_logs/build_info.txt
          fi

      - name: Build APK with full log
        run: |
          mkdir -p ci_logs
          cd apk_stage
          set +e
          buildozer -v android debug 2>&1 | tee ../ci_logs/buildozer_full.log
          CODE=${PIPESTATUS[0]}
          echo "$CODE" > ../ci_logs/buildozer_exit_code.txt
          echo "=== ERROR SEARCH ===" | tee ../ci_logs/error_search.txt
          grep -niE "error:|failed|exception|traceback|no such file|command failed|stderr|fatal|could not|undefined|permission denied|undeclared|invalid workflow" ../ci_logs/buildozer_full.log | tail -180 | tee -a ../ci_logs/error_search.txt || true
          echo "=== LAST 300 LINES ===" | tee ../ci_logs/last_300_lines.txt
          tail -300 ../ci_logs/buildozer_full.log | tee -a ../ci_logs/last_300_lines.txt
          exit $CODE

      - name: Verify APK exists
        if: success()
        run: |
          cd apk_stage
          ls -lah bin || true
          find bin -type f -name "*.apk" -print

      - name: Upload APK
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: BinanceAutobot-APK
          path: apk_stage/bin/*.apk

      - name: Upload full log
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: build-logs
          path: ci_logs/
YAML

echo "=== Python compile ellenorzes ==="
python3 -m py_compile main.py demo_core_engine.py autobot_core.py ai_engine.py auth_manager.py version_manager.py make_apk_stage.py || exit 1
if [ -f apk_stage/main.py ]; then
  python3 -m py_compile apk_stage/main.py || exit 1
fi

echo "=== Gyors route/main ellenorzes ==="
grep -n "safe_add_screen(sm, MasterMenu(name=\"main\"))\|safe_add_screen(sm, MasterMenu(name='main'))" main.py apk_stage/main.py || true
grep -n "name: Build APK\|Prepare fixed debug keystore\|Build APK with full log\|Upload APK" .github/workflows/android.yml || true

cat > logs/PATCH_14_MAIN_MENU_WORKFLOW_FIX_REPORT.txt <<EOF
PATCH 14 OK
Date: $(date)
Fixek:
- main screen: MasterMenu aktiv
- regi Main grid nem aktiv
- GitHub workflow tiszta YAML
- keystore blokk opcionalis
- APK build nem indult
- Binance order nem tortent
EOF

echo "=== PATCH 14 KESZ ==="
echo "Jelentes: logs/PATCH_14_MAIN_MENU_WORKFLOW_FIX_REPORT.txt"
echo "APK build NEM indult. Commit NEM tortent."
