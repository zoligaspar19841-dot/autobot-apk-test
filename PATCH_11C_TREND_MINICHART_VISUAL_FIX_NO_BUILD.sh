#!/bin/bash
set -e

echo "=== PATCH 11C: TREND MINI CHART VISUAL FIX - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, csak TrendMiniChart vizuális javítás."

TS=$(date +%Y%m%d_%H%M%S)

echo "=== 1) Biztonsági mentés ==="
cp main.py "main.py.bak_patch11c_trend_minichart_$TS"
cp apk_stage/main.py "apk_stage/main.py.bak_patch11c_trend_minichart_$TS"

echo "=== 2) TrendMiniChart osztály cseréje biztonságosan ==="

python - <<'PY'
from pathlib import Path
import re

FILES = [Path("main.py"), Path("apk_stage/main.py")]

NEW_CLASS = r'''class TrendMiniChart(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.values = [100.0, 100.0]
        self.bind(pos=lambda *_: self.redraw(), size=lambda *_: self.redraw())

    def set_values(self, values):
        try:
            vals = []
            for v in values or []:
                if v is None:
                    continue
                try:
                    vals.append(float(v))
                except Exception:
                    pass

            if len(vals) < 2:
                vals = [100.0, 100.0]

            self.values = vals[-60:]
        except Exception:
            self.values = [100.0, 100.0]

        self.redraw()

    def redraw(self):
        self.canvas.clear()

        vals = self.values or [100.0, 100.0]
        if len(vals) < 2:
            vals = [100.0, 100.0]

        with self.canvas:
            x, y = self.pos
            w, h = self.size

            # háttér
            Color(0.025, 0.025, 0.025, 1)
            Rectangle(pos=self.pos, size=self.size)

            pad_x = 10
            pad_y = 10
            gx0 = x + pad_x
            gy0 = y + pad_y
            gw = max(1, w - pad_x * 2)
            gh = max(1, h - pad_y * 2)

            # finom rács
            Color(0.16, 0.16, 0.16, 1)
            for i in range(1, 4):
                yy = gy0 + gh * i / 4
                Line(points=[gx0, yy, gx0 + gw, yy], width=1)

            for i in range(1, 4):
                xx = gx0 + gw * i / 4
                Line(points=[xx, gy0, xx, gy0 + gh], width=0.8)

            mn, mx = min(vals), max(vals)
            if abs(mx - mn) < 0.00001:
                mx = mn + 1.0

            pts = []
            for i, v in enumerate(vals):
                px = gx0 + (gw * i / max(1, len(vals) - 1))
                py = gy0 + ((v - mn) / (mx - mn)) * gh
                pts.extend([px, py])

            # trendvonal
            Color(1.0, 0.74, 0.10, 1)
            if len(pts) >= 4:
                Line(points=pts, width=2.2)

            # induló pont
            if len(pts) >= 2:
                Color(0.65, 0.65, 0.65, 1)
                sx, sy = pts[0], pts[1]
                Line(circle=(sx, sy, 3), width=1.3)

            # utolsó pont jelölés
            if len(pts) >= 2:
                Color(0.0, 0.86, 0.35, 1)
                px, py = pts[-2], pts[-1]
                Line(circle=(px, py, 4.5), width=2)

            # border
            Color(0.28, 0.28, 0.28, 1)
            Line(points=[x, y, x + w, y, x + w, y + h, x, y + h, x, y], width=1)
'''

def replace_class(src: str) -> str:
    pattern = re.compile(
        r"^class\s+TrendMiniChart\s*\(Widget\):.*?(?=^class\s+[A-Za-z_][A-Za-z0-9_]*\s*\(|\Z)",
        re.M | re.S
    )
    if not pattern.search(src):
        raise SystemExit("HIBA: TrendMiniChart class nem található")
    return pattern.sub(NEW_CLASS + "\n\n", src, count=1)

for p in FILES:
    s = p.read_text(encoding="utf-8", errors="replace")
    s2 = replace_class(s)
    p.write_text(s2, encoding="utf-8")
    print("OK patched:", p)
PY

echo "=== 3) Python compile teszt ==="
python -m py_compile main.py demo_core_engine.py
python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py
echo "OK: compile jó"

echo "=== 4) Ellenőrzés ==="
grep -n "class TrendMiniChart" main.py apk_stage/main.py
grep -n "TREND MINI CHART" PATCH_11C_TREND_MINICHART_VISUAL_FIX_NO_BUILD.sh

echo "=== 5) Git állapot - commit nincs, push nincs ==="
git status --short

echo "=== PATCH 11C KÉSZ ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Ha ez jó, írd: jó"
