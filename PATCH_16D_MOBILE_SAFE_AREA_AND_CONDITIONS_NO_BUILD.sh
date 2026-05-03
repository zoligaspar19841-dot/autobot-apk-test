#!/usr/bin/env bash
set -e

echo "=== PATCH 16D: MOBILE SAFE AREA + FELTÉTEL CHECKLIST - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, nem küld Binance ordert."

mkdir -p backups logs
TS=$(date +%Y%m%d_%H%M%S)

TARGET="webui/index.html"

if [ ! -f "$TARGET" ]; then
  echo "HIBA: nincs webui/index.html"
  exit 1
fi

cp "$TARGET" "backups/webui_index.html.bak_patch16d_$TS"

python3 - <<'PY'
from pathlib import Path

p = Path("webui/index.html")
s = p.read_text(encoding="utf-8")

css_marker = "/* === PATCH 16D MOBILE SAFE AREA START === */"
css_block = r'''
/* === PATCH 16D MOBILE SAFE AREA START === */
body{
  padding-bottom: max(90px, env(safe-area-inset-bottom));
}
.app{
  padding-bottom: 170px !important;
}
.card:last-child{
  margin-bottom: 120px;
}
.actions{
  margin-bottom: 18px;
}
.mobile-bottom-space{
  height: 130px;
}
.condition-grid{
  display:grid;
  grid-template-columns:1fr;
  gap:10px;
}
.condition-ok{
  border-left:5px solid #27d66b;
}
.condition-warn{
  border-left:5px solid #ffd84d;
}
.condition-stop{
  border-left:5px solid #ff3333;
}
.condition-title{
  font-weight:950;
  font-size:18px;
  margin-bottom:4px;
}
.condition-text{
  color:rgba(255,255,255,.78);
  font-size:15px;
  line-height:1.38;
}
@media(max-width:430px){
  .app{
    padding-bottom:190px !important;
  }
  .card:last-child{
    margin-bottom:150px;
  }
  .grid{
    gap:10px;
  }
  .kpi{
    min-height:104px;
  }
  .actions{
    gap:10px;
  }
  .btn{
    min-height:62px;
  }
}
/* === PATCH 16D MOBILE SAFE AREA END === */
'''

if css_marker not in s:
    s = s.replace("</style>", css_block + "\n</style>")

conditions_marker = "<!-- PATCH 16D CONDITIONS CARD -->"
conditions_card = r'''
    <!-- PATCH 16D CONDITIONS CARD -->
    <div class="card">
      <h2>🛡️ Feltételek / Biztonsági ellenőrzés</h2>
      <div class="condition-grid">

        <div class="item condition-ok">
          <div class="condition-title">✅ Demo mód</div>
          <div class="condition-text">
            Szimulált egyenleggel működik. Binance ár/adat előkészíthető, de éles pénzt nem használ.
          </div>
        </div>

        <div class="item condition-warn">
          <div class="condition-title">⚠️ Live mód</div>
          <div class="condition-text">
            Ugyanazt a dashboardot használja, mint a Demo. API nélkül csak előkészített nézet. Éles order külön engedély nélkül tiltva.
          </div>
        </div>

        <div class="item condition-stop">
          <div class="condition-title">⛔ Live order tiltás</div>
          <div class="condition-text">
            A web UI jelenlegi állapotban nem küld Binance ordert. Ez biztonsági kapu, amíg nincs teljes read-only teszt, API ellenőrzés és manuális jóváhagyás.
          </div>
        </div>

        <div class="item condition-ok">
          <div class="condition-title">✅ Egy Demo / Live vezérlés</div>
          <div class="condition-text">
            Nincs dupla Demo/Live kapcsoló. A fő navigáció: Demo / Live / Beállítások / Report.
          </div>
        </div>

        <div class="item condition-warn">
          <div class="condition-title">📈 Trend panel</div>
          <div class="condition-text">
            Demo és Live oldalon is van trend hely. Következő lépés: Binance klines, SMA9/21, profit trend, idősík szerinti részletezés.
          </div>
        </div>

        <div class="item condition-warn">
          <div class="condition-title">🔐 Beállítások / titkok</div>
          <div class="condition-text">
            Binance API, e-mail, OpenAI kulcsok helye előkészítve. Következő lépés: titkosított mentés creds.enc és email.enc fájlba.
          </div>
        </div>

        <div class="item condition-warn">
          <div class="condition-title">🧠 AI / Profit-Hold</div>
          <div class="condition-text">
            A Master lista szerint előkészítendő: Auto / Manuális jóváhagyás / Off, trailing take profit, profit erosion guard, cooldown.
          </div>
        </div>

        <div class="item condition-warn">
          <div class="condition-title">📊 Export / Report</div>
          <div class="condition-text">
            Report oldal megvan. Következő lépés: valódi trades.csv, profit_report.csv, audit_log.csv visszakötése.
          </div>
        </div>

      </div>
    </div>
'''

if conditions_marker not in s:
    # Report szekció végéhez illesztjük, a pageReport zárása elé
    s = s.replace("  </section>\n\n</div>", conditions_card + "\n  </section>\n\n</div>")

# extra alsó tér csak egyszer
bottom_marker = '<div class="mobile-bottom-space"></div>'
if bottom_marker not in s:
    s = s.replace("</div>\n\n<script>", bottom_marker + "\n</div>\n\n<script>")

p.write_text(s, encoding="utf-8")
print("OK patched:", p)
PY

echo "=== Ellenőrzés ==="
grep -nE "PATCH 16D|mobile-bottom-space|Feltételek|Live order tiltás|Demo mód|condition-grid" webui/index.html || true

python3 -m py_compile run_web_ui.py

cat > logs/PATCH_16D_MOBILE_SAFE_AREA_AND_CONDITIONS_REPORT.txt <<EOF
PATCH 16D OK
Date: $(date)

Javítás:
- mobil alsó safe-area hozzáadva
- böngészősáv miatti kitakarás ellen extra alsó hely
- Report oldal feltétel / safety checklist
- Demo mód feltétel megjelenítve
- Live mód figyelmeztetés megjelenítve
- Live order tiltás külön jelölve
- titkosítás / API / report / profit-hold következő lépésként jelölve
- APK build NEM indult
- Commit NEM történt
- Binance order NEM történt
EOF

echo "=== PATCH 16D KÉSZ ==="
echo "Jelentés: logs/PATCH_16D_MOBILE_SAFE_AREA_AND_CONDITIONS_REPORT.txt"
echo "APK build NEM indult. Commit NEM történt."
echo "Frissítsd a böngészőt: http://127.0.0.1:8080"
