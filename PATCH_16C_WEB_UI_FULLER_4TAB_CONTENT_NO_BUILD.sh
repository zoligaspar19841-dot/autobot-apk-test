#!/usr/bin/env bash
set -e

echo "=== PATCH 16C: WEB UI 4 FÜL TARTALOM / DUPLA DEMO-LIVE TÖRLÉS - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, nem küld Binance ordert."

mkdir -p backups logs webui
TS=$(date +%Y%m%d_%H%M%S)

[ -f webui/index.html ] && cp webui/index.html "backups/webui_index.html.bak_patch16c_$TS"

cat > webui/index.html <<'HTML'
<!doctype html>
<html lang="hu">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Autobot Trading System</title>
<style>
:root{
  --bg:#0b0d12;
  --card:rgba(255,255,255,.14);
  --card2:rgba(255,255,255,.20);
  --text:#fff;
  --muted:rgba(255,255,255,.76);
  --yellow:#ffb51f;
  --orange:#ff8a00;
  --blue:#1677ff;
  --green:#27d66b;
  --red:#ff3333;
}
*{box-sizing:border-box}
body{
  margin:0;
  font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  color:var(--text);
  background:linear-gradient(145deg,#ffb51f,#ff7a1a);
  min-height:100vh;
}
body.live{
  background:linear-gradient(145deg,#10284d,#1765c7);
}
.app{
  max-width:760px;
  margin:0 auto;
  padding:14px;
  padding-bottom:40px;
}
.header{
  border:1px solid rgba(255,255,255,.22);
  border-radius:26px;
  padding:18px;
  background:rgba(255,255,255,.12);
  box-shadow:0 20px 50px rgba(0,0,0,.25);
}
h1{
  margin:0 0 8px;
  font-size:34px;
  line-height:1.1;
  text-shadow:0 3px 8px rgba(0,0,0,.35);
}
.sub{
  font-size:17px;
  color:var(--muted);
  line-height:1.35;
}
.status{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:10px;
  margin-top:14px;
}
.pill{
  border-radius:16px;
  padding:12px 10px;
  background:rgba(0,0,0,.22);
  text-align:center;
  font-weight:800;
  font-size:16px;
}
.ok{color:var(--green)}
.stop{color:#ffd84d}
.warn{color:#fff}
.tabs{
  margin:18px 0;
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:10px;
  background:rgba(255,255,255,.10);
  border-radius:24px;
  padding:10px;
}
.tab{
  border:0;
  border-radius:18px;
  padding:16px 8px;
  font-size:18px;
  font-weight:900;
  color:#fff;
  background:rgba(255,255,255,.12);
  box-shadow:0 10px 24px rgba(0,0,0,.18);
}
.tab.active{
  background:rgba(255,255,255,.30);
  transform:translateY(-1px);
}
.card{
  border:1px solid rgba(255,255,255,.22);
  border-radius:26px;
  padding:18px;
  background:rgba(255,255,255,.13);
  box-shadow:0 18px 45px rgba(0,0,0,.22);
  margin-bottom:18px;
}
h2{
  margin:0 0 16px;
  font-size:31px;
  text-shadow:0 3px 8px rgba(0,0,0,.34);
}
h3{
  margin:18px 0 10px;
  font-size:23px;
}
.grid{
  display:grid;
  grid-template-columns:repeat(2,1fr);
  gap:12px;
}
.kpi{
  min-height:110px;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  border-radius:22px;
  background:rgba(255,255,255,.14);
  border:1px solid rgba(255,255,255,.18);
}
.kpi .v{
  font-size:31px;
  font-weight:950;
  margin-bottom:8px;
  text-shadow:0 3px 8px rgba(0,0,0,.35);
}
.kpi .l{
  font-size:17px;
  color:var(--muted);
  text-align:center;
}
.actions{
  display:grid;
  grid-template-columns:repeat(2,1fr);
  gap:12px;
  margin-top:14px;
}
.btn{
  border:0;
  border-radius:18px;
  min-height:58px;
  padding:12px;
  color:#fff;
  font-size:19px;
  font-weight:950;
  box-shadow:0 14px 28px rgba(0,0,0,.22);
}
.start{background:linear-gradient(135deg,#2bd66f,#16a34a)}
.stopBtn{background:linear-gradient(135deg,#ff4a4a,#d60000)}
.orange{background:linear-gradient(135deg,#ffb100,#ff8500)}
.blue{background:linear-gradient(135deg,#1da1ff,#0057ff)}
.gray{background:rgba(0,0,0,.28)}
canvas{
  width:100%;
  height:230px;
  display:block;
  background:rgba(0,0,0,.22);
  border-radius:22px;
  border:1px solid rgba(255,255,255,.16);
}
.tf{
  display:grid;
  grid-template-columns:repeat(6,1fr);
  gap:8px;
  margin:12px 0;
}
.tf button{
  border:0;
  border-radius:13px;
  padding:11px 4px;
  font-size:15px;
  font-weight:900;
  color:#fff;
  background:rgba(0,0,0,.25);
}
.tf button.active{background:rgba(255,255,255,.30)}
.info{
  color:var(--muted);
  font-size:17px;
  line-height:1.45;
}
.warnbox{
  padding:13px;
  border-radius:18px;
  background:rgba(0,0,0,.25);
  border-left:5px solid #ffd84d;
  font-size:17px;
  line-height:1.45;
}
.field{
  margin:14px 0;
}
label{
  display:block;
  font-size:18px;
  font-weight:900;
  margin-bottom:6px;
}
.helper{
  font-size:15px;
  color:rgba(255,255,255,.76);
  line-height:1.35;
  margin:5px 0 8px;
}
input,select,textarea{
  width:100%;
  min-height:54px;
  border:0;
  border-radius:16px;
  padding:13px;
  font-size:18px;
  color:#fff;
  background:rgba(0,0,0,.28);
  outline:1px solid rgba(255,255,255,.12);
}
textarea{min-height:120px}
.list{
  display:grid;
  gap:10px;
}
.item{
  padding:13px;
  border-radius:17px;
  background:rgba(0,0,0,.20);
  font-size:17px;
  line-height:1.4;
}
.small{
  font-size:14px;
  color:rgba(255,255,255,.72);
}
.hidden{display:none}
@media(max-width:430px){
  .app{padding:10px}
  h1{font-size:29px}
  h2{font-size:28px}
  .tab{font-size:15px;padding:14px 4px}
  .kpi .v{font-size:28px}
  .btn{font-size:17px}
}
</style>
</head>
<body class="demo">
<div class="app">

  <div class="header">
    <h1>🤖 Autobot Trading System</h1>
    <div class="sub" id="modeText">DEMO: Binance ár előkészítve + szimulált egyenleg. Nem használ éles pénzt.</div>
    <div class="status">
      <div class="pill ok" id="conn">Connected</div>
      <div class="pill stop" id="run">Stopped</div>
      <div class="pill warn" id="strategy">Normal</div>
    </div>
  </div>

  <div class="tabs">
    <button class="tab active" id="tabDemo" onclick="openTab('demo')">Demo</button>
    <button class="tab" id="tabLive" onclick="openTab('live')">Live</button>
    <button class="tab" id="tabSettings" onclick="openTab('settings')">Beállítások</button>
    <button class="tab" id="tabReport" onclick="openTab('report')">Report</button>
  </div>

  <section id="pageDemo">
    <div class="card">
      <h2>📊 Demo Dashboard</h2>
      <div class="warnbox">Demo módban a felület ugyanaz, mint Live-ban, de az egyenleg szimulált. Ez a biztonságos teszt mód.</div>
      <div class="grid" style="margin-top:14px">
        <div class="kpi"><div class="v" id="equity">$100.00</div><div class="l">Total Equity</div></div>
        <div class="kpi"><div class="v" id="pnl">$0.00</div><div class="l">Today PnL</div></div>
        <div class="kpi"><div class="v" id="free">100.00</div><div class="l" id="freeLab">USDC Free</div></div>
        <div class="kpi"><div class="v" id="profit">0.00</div><div class="l">USDT Profit</div></div>
      </div>
      <div class="actions">
        <button class="btn start" onclick="start()">🚀 START BOT</button>
        <button class="btn stopBtn" onclick="stop()">⏹ STOP BOT</button>
        <button class="btn orange" onclick="resetDemo()" id="resetBtn">🔄 DEMO RESET</button>
        <button class="btn blue" onclick="exportCsv()">📊 EXPORT CSV</button>
      </div>
    </div>

    <div class="card">
      <h2 id="trendTitle">📈 Trend: BTCUSDT DEMO</h2>
      <div class="info">Idősík választható. Később ide kerül: SMA9/21, PnL trend, top coin mini-kártyák, crosshair pontadat.</div>
      <div class="tf">
        <button class="active" onclick="setTf('1m',this)">1m</button>
        <button onclick="setTf('5m',this)">5m</button>
        <button onclick="setTf('15m',this)">15m</button>
        <button onclick="setTf('1h',this)">1h</button>
        <button onclick="setTf('4h',this)">4h</button>
        <button onclick="setTf('1d',this)">1d</button>
      </div>
      <canvas id="chart" width="700" height="260"></canvas>
      <div class="small" id="pointInfo">Grafikon pontadat: érints rá a vonalra.</div>
    </div>
  </section>

  <section id="pageLive" class="hidden">
    <div class="card">
      <h2>🔵 Live Dashboard</h2>
      <div class="warnbox">Live módban ugyanaz a dashboard marad. API nélkül nincs saját Binance egyenleg. Éles order továbbra is tiltva, amíg külön nem engedélyezzük.</div>
      <div class="grid" style="margin-top:14px">
        <div class="kpi"><div class="v" id="liveEquity">$100.00</div><div class="l">Total Equity</div></div>
        <div class="kpi"><div class="v" id="livePnl">$0.00</div><div class="l">Today PnL</div></div>
        <div class="kpi"><div class="v" id="liveFree">100.00</div><div class="l">USDT/USDC Free</div></div>
        <div class="kpi"><div class="v" id="liveProfit">0.00</div><div class="l">USDT Profit</div></div>
      </div>
      <h3>Live állapot</h3>
      <div class="list">
        <div class="item">Binance API: <b id="apiReady">nincs bekötve / ellenőrizendő</b></div>
        <div class="item">Order engedély: <b>tiltva</b> — biztonsági kapu aktív.</div>
        <div class="item">Következő lépés: read-only balance + live klines bekötés.</div>
      </div>
    </div>

    <div class="card">
      <h2>📈 Live Trend helye</h2>
      <canvas id="chartLive" width="700" height="260"></canvas>
      <div class="small">Ugyanaz a trendlogika, később Binance klines adatokkal.</div>
    </div>
  </section>

  <section id="pageSettings" class="hidden">
    <div class="card">
      <h2>⚙️ Beállítások</h2>
      <div class="warnbox">Itt minden mezőhöz magyarázat kell. A kulcsok később titkosítva mennek: creds.enc, email.enc. Most még nem írunk ki titkot a képernyőre.</div>

      <h3>🔐 Binance API</h3>
      <div class="field">
        <label>Binance API key</label>
        <div class="helper">Binance.com → API Management. Első körben csak read-only ellenőrzéshez kell. Ne legyen withdrawal jog.</div>
        <input id="binanceKey" placeholder="API key">
      </div>
      <div class="field">
        <label>Binance API secret</label>
        <div class="helper">Csak titkosított mentéssel használjuk. A képernyőn ne jelenjen meg vissza.</div>
        <input id="binanceSecret" type="password" placeholder="API secret">
      </div>

      <h3>📧 E-mail értesítés</h3>
      <div class="field">
        <label>E-mail címzett</label>
        <div class="helper">Ide jönnek majd: trade esemény, hiba, healthcheck, launchpool figyelés.</div>
        <input id="emailTo" placeholder="példa@gmail.com">
      </div>
      <div class="field">
        <label>SMTP / Gmail app password</label>
        <div class="helper">Gmailnél alkalmazásjelszó kell, nem a normál Gmail jelszó.</div>
        <input id="emailPass" type="password" placeholder="app password">
      </div>

      <h3>🧠 AI / Profit-Hold</h3>
      <div class="field">
        <label>AI mód</label>
        <select id="aiMode">
          <option>Off</option>
          <option>Manuális jóváhagyás</option>
          <option>Auto</option>
        </select>
        <div class="helper">Auto csak később, safety guarddal. Először manuális jóváhagyás javasolt.</div>
      </div>
      <div class="field">
        <label>Profit-Hold mód</label>
        <select id="profitHold">
          <option>Off</option>
          <option>Fixed</option>
          <option>AI-Adaptive</option>
        </select>
        <div class="helper">Cél: felfutó profit tartása, majd optimális exit. Nem adótanácsadás.</div>
      </div>

      <button class="btn start" onclick="saveSettings()">💾 BEÁLLÍTÁSOK MENTÉSE</button>
      <div class="small" id="settingsMsg"></div>
    </div>
  </section>

  <section id="pageReport" class="hidden">
    <div class="card">
      <h2>📄 Report / Export</h2>
      <div class="list">
        <div class="item"><b>Trades export:</b> trades.csv, log.csv, profit_report.csv.</div>
        <div class="item"><b>PnL nézet:</b> Bruttó → Nettó fee után → adózás utáni irányadó HU 15%.</div>
        <div class="item"><b>Audit:</b> AI döntések, manuális jóváhagyások, Safe Mode események.</div>
        <div class="item"><b>Healthcheck:</b> Binance / Drive / E-mail / PC agent státusz.</div>
      </div>
      <div class="actions">
        <button class="btn blue" onclick="exportCsv()">📊 DEMO STATE CSV</button>
        <button class="btn gray" onclick="alert('Következő patch: teljes trades/report export.')">📁 REPORT HELY</button>
      </div>
    </div>

    <div class="card">
      <h2>✅ Master lista állapot</h2>
      <div class="list">
        <div class="item">1–4: Demo/Live dashboard alap: <b>részben kész</b></div>
        <div class="item">5–9: Schedules, Launchpool, Security: <b>régi patch-ekben megvan, új UI-ba vissza kell kötni</b></div>
        <div class="item">16–18: AI, multi-symbol, safety guards: <b>modul/patchek vannak, UI-integráció következik</b></div>
        <div class="item">23–24: Fee/Tax + Profit-Hold: <b>következő fejlesztési blokk</b></div>
      </div>
    </div>
  </section>

</div>

<script>
let mode="demo";
let data=[];
let timeframe="1m";

async function apiGet(path){
  const r=await fetch(path);
  return await r.json();
}
async function apiPost(path,data={}){
  const r=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
  return await r.json();
}
function setActiveTab(name){
  for(const id of ["Demo","Live","Settings","Report"]){
    document.getElementById("tab"+id)?.classList.remove("active");
  }
  const map={demo:"Demo",live:"Live",settings:"Settings",report:"Report"};
  document.getElementById("tab"+map[name])?.classList.add("active");
}
async function openTab(name){
  for(const id of ["pageDemo","pageLive","pageSettings","pageReport"]){
    document.getElementById(id).classList.add("hidden");
  }
  setActiveTab(name);
  if(name==="demo" || name==="live"){
    mode=name;
    document.body.className=name;
    await apiPost("/api/set-mode",{mode:name}).catch(()=>{});
    document.getElementById("modeText").textContent =
      name==="demo"
      ? "DEMO: Binance ár előkészítve + szimulált egyenleg. Nem használ éles pénzt."
      : "LIVE: ugyanaz a felület, de API nélkül csak előkészített nézet. Order tiltva.";
    document.getElementById(name==="demo"?"pageDemo":"pageLive").classList.remove("hidden");
    refreshState();
  } else {
    document.getElementById(name==="settings"?"pageSettings":"pageReport").classList.remove("hidden");
  }
}
function applyState(st){
  if(!st)return;
  document.getElementById("run").textContent=st.running?"Running":"Stopped";
  document.getElementById("run").className=st.running?"pill ok":"pill stop";
  document.getElementById("strategy").textContent=st.strategy||"Normal";
  const eq=Number(st.total_equity||0).toFixed(2);
  const pnl=Number(st.today_pnl||0).toFixed(2);
  const free=Number(st.usdc_free||0).toFixed(2);
  const prof=Number(st.usdt_profit||0).toFixed(2);
  for(const id of ["equity","liveEquity"]) document.getElementById(id).textContent="$"+eq;
  for(const id of ["pnl","livePnl"]) document.getElementById(id).textContent="$"+pnl;
  for(const id of ["free","liveFree"]) document.getElementById(id).textContent=free;
  for(const id of ["profit","liveProfit"]) document.getElementById(id).textContent=prof;
  document.getElementById("apiReady").textContent=st.live_api_ready?"OK":"nincs bekötve / ellenőrizendő";
  if(Array.isArray(st.trend)){data=st.trend; draw("chart"); draw("chartLive");}
}
async function refreshState(){
  try{
    const j=await apiGet("/api/demo-state");
    if(j.ok)applyState(j.state);
  }catch(e){}
}
async function start(){const j=await apiPost("/api/start"); if(j.ok)applyState(j.state);}
async function stop(){const j=await apiPost("/api/stop"); if(j.ok)applyState(j.state);}
async function resetDemo(){
  const j=await apiPost("/api/demo-reset");
  if(j.ok)applyState(j.state);
}
async function exportCsv(){
  const j=await apiGet("/api/export-csv");
  alert(j.message||"Export kész");
}
async function setTf(tf,btn){
  timeframe=tf;
  document.querySelectorAll(".tf button").forEach(b=>b.classList.remove("active"));
  btn.classList.add("active");
  await apiPost("/api/set-timeframe",{timeframe:tf}).catch(()=>{});
  refreshState();
}
function draw(id="chart"){
  const c=document.getElementById(id);
  if(!c || !data.length)return;
  const ctx=c.getContext("2d");
  const w=c.width,h=c.height;
  ctx.clearRect(0,0,w,h);
  ctx.fillStyle="rgba(0,0,0,.18)";
  ctx.fillRect(0,0,w,h);
  const vals=data.map(x=>Number(x.price));
  const mn=Math.min(...vals),mx=Math.max(...vals);
  ctx.strokeStyle="rgba(255,255,255,.18)";
  ctx.lineWidth=1;
  for(let i=1;i<5;i++){
    let y=i*h/5;
    ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();
  }
  ctx.strokeStyle=mode==="demo"?"#ffe25a":"#63b3ff";
  ctx.lineWidth=4;
  ctx.beginPath();
  data.forEach((d,i)=>{
    const x=i*(w/(data.length-1));
    const y=h-18-((d.price-mn)/(mx-mn||1))*(h-36);
    if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
  });
  ctx.stroke();
}
document.getElementById("chart").addEventListener("click",e=>{
  if(!data.length)return;
  const r=e.target.getBoundingClientRect();
  const x=e.clientX-r.left;
  const idx=Math.max(0,Math.min(data.length-1,Math.round(x/r.width*(data.length-1))));
  const p=data[idx];
  document.getElementById("pointInfo").textContent=`Pont: ${p.time} | ár: ${p.price} | PnL: ${p.pnl}`;
});
function saveSettings(){
  const msg=document.getElementById("settingsMsg");
  msg.textContent="Beállítások helyileg előkészítve. Következő patch: titkosított mentés creds.enc/email.enc.";
}
setInterval(refreshState,5000);
refreshState();
</script>
</body>
</html>
HTML

python3 -m py_compile run_web_ui.py

cat > logs/PATCH_16C_WEB_UI_FULLER_4TAB_CONTENT_REPORT.txt <<EOF
PATCH 16C OK
Date: $(date)

Javítás:
- dupla Demo/Live vezérlés kivéve
- csak 4 fő fül: Demo / Live / Beállítások / Report
- Demo és Live azonos dashboard logikára állítva
- nagyobb betűk, nagyobb gombok
- beállítások helper szövegekkel feltöltve
- Report oldal tartalommal feltöltve
- trend panel mind Demo, mind Live oldalon látható
- APK build nem indult
- Binance order nem történt
EOF

echo "=== PATCH 16C KÉSZ ==="
echo "Indítás: python3 run_web_ui.py"
echo "APK build NEM indult. Commit NEM történt."
