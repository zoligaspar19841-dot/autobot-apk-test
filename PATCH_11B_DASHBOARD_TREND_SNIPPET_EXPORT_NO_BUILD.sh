#!/bin/bash
set -e

echo "=== PATCH 11B: DASHBOARD / TREND SNIPPET EXPORT - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, fő kódot nem módosít."

mkdir -p logs
REPORT="logs/PATCH_11B_DASHBOARD_TREND_SNIPPETS.txt"

{
echo "PATCH 11B DASHBOARD / TREND SNIPPETS"
echo "APK build: NEM indult"
echo "Commit: NEM történt"
echo ""

echo "============================================================"
echo "main.py fontos dashboard/trend rész"
echo "============================================================"
sed -n '1180,1535p' main.py

echo ""
echo "============================================================"
echo "main.py modern/demo dashboard rész"
echo "============================================================"
sed -n '1130,1175p' main.py
sed -n '1430,1535p' main.py

echo ""
echo "============================================================"
echo "apk_stage/main.py fontos dashboard/trend rész"
echo "============================================================"
sed -n '1180,1535p' apk_stage/main.py

echo ""
echo "============================================================"
echo "Compile check"
echo "============================================================"
python -m py_compile main.py demo_core_engine.py && echo "root compile OK"
python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py && echo "apk_stage compile OK"

} > "$REPORT"

echo "=== PATCH 11B KÉSZ ==="
echo "Jelentés: $REPORT"
echo "APK build NEM indult."
echo "Commit NEM történt."
echo ""
echo "Most ezt küldd be:"
echo "grep -nE 'class Trend|class Dashboard|class TrendCanvasWidget|class DemoCoreModernDashboardScreen|class DemoCoreTrendHistoryScreen|def __init__|def refresh|def set_values|Line\\(|Color\\(|Rectangle\\(|Label\\(|Button\\(' $REPORT | head -220"
