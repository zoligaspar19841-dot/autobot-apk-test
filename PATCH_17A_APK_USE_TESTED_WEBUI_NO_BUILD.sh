#!/usr/bin/env bash
set -e

echo "=== PATCH 17A: APK A TESZTELT WEB UI-T INDÍTSA - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, nem küld Binance ordert."

mkdir -p backups logs apk_stage/webui
TS=$(date +%Y%m%d_%H%M%S)

if [ ! -f webui/index.html ]; then
  echo "HIBA: nincs webui/index.html - ez kell, amit most teszteltünk."
  exit 1
fi

if [ -f apk_stage/main.py ]; then
  cp apk_stage/main.py "backups/apk_stage_main.py.bak_patch17a_$TS"
fi

if [ -f apk_stage/buildozer.spec ]; then
  cp apk_stage/buildozer.spec "backups/apk_stage_buildozer.spec.bak_patch17a_$TS"
fi

echo "=== 1) Tesztelt Web UI bemásolása APK stage-be ==="
rm -rf apk_stage/webui
mkdir -p apk_stage/webui
cp -a webui/. apk_stage/webui/

echo "=== 2) APK main.py átállítása WebUI launcher módra ==="
cat > apk_stage/main.py <<'PY'
# PATCH 17A APK WEBUI LAUNCHER
# Cél: az APK ugyanazt a webui/index.html felületet mutassa, mint amit Termuxban teszteltünk.
# Biztonság: live order tiltott; csak helyi demo API válaszok.

import os
import json
import time
import mimetypes
import threading
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

from kivy.app import App
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label


APP_DIR = Path(__file__).resolve().parent
WEB_DIR = APP_DIR / "webui"
HOST = "127.0.0.1"
PORT = 8080

STATE = {
    "mode": "demo",
    "connected": True,
    "running": True,
    "strategy": "normal",
    "total_equity": 100.0,
    "today_pnl": 0.0,
    "usdc_free": 100.0,
    "usdt_profit": 0.0,
    "open_positions": 0,
    "live_order_enabled": False,
    "warning": "Live order tiltva. Demo módban szimulált egyenleg.",
    "updated": int(time.time()),
}


def json_bytes(obj):
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")


class AutobotWebHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Csendesebb APK log.
        return

    def _send(self, code, data, content_type="application/json; charset=utf-8"):
        if isinstance(data, str):
            data = data.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self._send(200, b"OK", "text/plain")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/api/state", "/api/status", "/api/demo", "/api/live/status"):
            STATE["updated"] = int(time.time())
            self._send(200, json_bytes({"ok": True, "state": STATE, **STATE}))
            return

        if path in ("/api/health", "/health"):
            self._send(200, json_bytes({"ok": True, "service": "apk-webui", "live_order_enabled": False}))
            return

        if path == "/" or path == "":
            target = WEB_DIR / "index.html"
        else:
            target = (WEB_DIR / path.lstrip("/")).resolve()

        try:
            if not str(target).startswith(str(WEB_DIR.resolve())):
                self._send(403, "Forbidden", "text/plain")
                return

            if target.exists() and target.is_file():
                ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
                self._send(200, target.read_bytes(), ctype)
                return

            self._send(404, "Not found", "text/plain")
        except Exception as e:
            self._send(500, f"Server error: {e}", "text/plain")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b"{}"

        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            payload = {}

        # Általános UI akciók. Éles order továbbra is tiltva.
        if "mode" in payload:
            STATE["mode"] = "live" if str(payload["mode"]).lower() == "live" else "demo"

        if path.endswith("start") or payload.get("running") is True:
            STATE["running"] = True

        if path.endswith("stop") or payload.get("running") is False:
            STATE["running"] = False

        if "strategy" in payload:
            STATE["strategy"] = str(payload["strategy"]).lower()

        if "reset" in path or path.endswith("/demo/reset"):
            STATE.update({
                "mode": "demo",
                "running": False,
                "total_equity": 100.0,
                "today_pnl": 0.0,
                "usdc_free": 100.0,
                "usdt_profit": 0.0,
                "open_positions": 0,
                "warning": "Demo reset kész. Éles pénz nem mozdult.",
            })

        STATE["live_order_enabled"] = False
        STATE["updated"] = int(time.time())

        self._send(200, json_bytes({
            "ok": True,
            "blocked_live_order": True,
            "message": "APK WebUI demo API válasz. Live order tiltva.",
            "state": STATE,
            **STATE,
        }))


_server = None


def start_server():
    global _server
    if _server is not None:
        return
    _server = ThreadingHTTPServer((HOST, PORT), AutobotWebHandler)
    t = threading.Thread(target=_server.serve_forever, daemon=True)
    t.start()


class AutobotWebUIApp(App):
    def build(self):
        root = FloatLayout()
        self.label = Label(
            text="[b]Autobot Trading System[/b]\n\nWeb UI indítása...\nDemo biztonságos mód.\nLive order tiltva.",
            markup=True,
            halign="center",
            valign="middle",
            font_size="22sp",
        )
        self.label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        root.add_widget(self.label)
        return root

    def on_start(self):
        start_server()
        Clock.schedule_once(lambda dt: self.open_webview(), 0.8)

    def open_webview(self):
        url = f"http://{HOST}:{PORT}/"

        if platform != "android":
            self.label.text = f"[b]Autobot Trading System[/b]\n\nWeb UI fut:\n{url}"
            return

        try:
            from android.runnable import run_on_ui_thread
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            WebView = autoclass("android.webkit.WebView")
            WebViewClient = autoclass("android.webkit.WebViewClient")
            LayoutParams = autoclass("android.view.ViewGroup$LayoutParams")

            @run_on_ui_thread
            def show():
                activity = PythonActivity.mActivity
                webview = WebView(activity)
                settings = webview.getSettings()
                settings.setJavaScriptEnabled(True)
                settings.setDomStorageEnabled(True)
                settings.setAllowFileAccess(True)
                settings.setAllowContentAccess(True)
                webview.setWebViewClient(WebViewClient())
                activity.addContentView(webview, LayoutParams(-1, -1))
                webview.loadUrl(url)
                self.webview = webview

            show()

        except Exception as e:
            self.label.text = (
                "[b]WebView indítási hiba[/b]\n\n"
                f"{e}\n\n"
                f"A belső szerver fut:\n{url}\n\n"
                "Nyisd meg böngészőben."
            )


if __name__ == "__main__":
    AutobotWebUIApp().run()
PY

echo "=== 3) buildozer.spec webui fájlok engedélyezése ==="
python3 - <<'PY'
from pathlib import Path

p = Path("apk_stage/buildozer.spec")
if not p.exists():
    print("WARN: nincs apk_stage/buildozer.spec")
    raise SystemExit(0)

s = p.read_text(encoding="utf-8", errors="ignore")

def set_line(prefix, value):
    global s
    lines = s.splitlines()
    done = False
    out = []
    for line in lines:
        if line.strip().startswith(prefix):
            out.append(value)
            done = True
        else:
            out.append(line)
    if not done:
        out.append(value)
    s = "\n".join(out) + "\n"

set_line("source.include_exts", "source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,csv,html,css,js,svg,ico")
set_line("requirements", "requirements = python3,kivy")
set_line("android.permissions", "android.permissions = INTERNET")

p.write_text(s, encoding="utf-8")
print("OK patched:", p)
PY

echo "=== 4) Ellenőrzés ==="
python3 -m py_compile apk_stage/main.py

grep -nE "source.include_exts|requirements|android.permissions" apk_stage/buildozer.spec || true
ls -lah apk_stage/webui/index.html
grep -nE "PATCH 17A|ThreadingHTTPServer|WebView|live_order_enabled|blocked_live_order" apk_stage/main.py || true

cat > logs/PATCH_17A_APK_USE_TESTED_WEBUI_REPORT.txt <<EOF
PATCH 17A OK
Date: $(date)

Cél:
- APK a tesztelt webui/index.html felületet indítsa.
- APK belső 127.0.0.1:8080 szervert indít.
- Androidon WebView nyitja meg.
- Demo API válaszok vannak.
- Live order tiltva.
- Binance order NEM történt.
- APK build NEM indult.
- Commit NEM történt.

Módosított:
- apk_stage/main.py
- apk_stage/buildozer.spec
- apk_stage/webui/index.html másolat
EOF

echo "=== PATCH 17A KÉSZ ==="
echo "Jelentés: logs/PATCH_17A_APK_USE_TESTED_WEBUI_REPORT.txt"
echo "APK build NEM indult. Commit NEM történt."
