#!/usr/bin/env bash
set -e

echo "=== PATCH 17D: APK WEBUI NO-HTTP LOAD - APK BUILD NÉLKÜL ==="
echo "Nem buildel, nem pushol, nem küld Binance ordert."
echo "Cél: ne http://127.0.0.1:8080-t nyisson, hanem közvetlenül töltse be a tesztelt webui/index.html-t."

mkdir -p backups logs apk_stage/webui
TS=$(date +%Y%m%d_%H%M%S)

if [ ! -f webui/index.html ]; then
  echo "HIBA: nincs webui/index.html"
  exit 1
fi

if [ -f apk_stage/main.py ]; then
  cp apk_stage/main.py "backups/apk_stage_main.py.bak_patch17d_$TS"
fi

rm -rf apk_stage/webui
mkdir -p apk_stage/webui
cp -a webui/. apk_stage/webui/

cat > apk_stage/main.py <<'PY'
# PATCH 17D APK WEBUI NO-HTTP LAUNCHER
# Cél: az APK ugyanazt a tesztelt webui/index.html UI-t mutassa,
# de WebView-ben NEM http://127.0.0.1:8080-ról, hanem közvetlen HTML betöltéssel.
# Így nincs ERR_CLEARTEXT_NOT_PERMITTED.
# Biztonság: live order továbbra is tiltva.

import json
import time
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label


APP_DIR = Path(__file__).resolve().parent
WEB_FILE = APP_DIR / "webui" / "index.html"


MOCK_STATE = {
    "ok": True,
    "mode": "demo",
    "connected": True,
    "running": True,
    "strategy": "normal",
    "total_equity": 100.0,
    "today_pnl": 0.0,
    "realized_pnl": 0.0,
    "usdc_free": 100.0,
    "usdt_profit": 0.0,
    "open_positions": 0,
    "live_order_enabled": False,
    "warning": "APK demo mód. Live order tiltva.",
    "updated": int(time.time()),
}


def inject_apk_safety_layer(html: str) -> str:
    """
    WebView HTTP nélkül fut.
    Ha a web UI /api hívást próbálna, ezt helyben megfogjuk,
    hogy ne kelljen 127.0.0.1 cleartext.
    """
    state_json = json.dumps(MOCK_STATE, ensure_ascii=False)

    js = f"""
<script>
/* PATCH 17D APK NO-HTTP SAFETY LAYER */
window.__APK_MODE__ = true;
window.__AUTOBOT_STATE__ = {state_json};

(function(){{
  const originalFetch = window.fetch ? window.fetch.bind(window) : null;

  window.fetch = function(url, opts){{
    const u = String(url || "");
    if (u.startsWith("/api") || u.includes("127.0.0.1") || u.includes("localhost")) {{
      const body = JSON.stringify(Object.assign({{}}, window.__AUTOBOT_STATE__, {{
        ok: true,
        apk_no_http: true,
        blocked_live_order: true,
        message: "APK WebUI helyi mock válasz. Live order tiltva."
      }}));
      return Promise.resolve(new Response(body, {{
        status: 200,
        headers: {{ "Content-Type": "application/json" }}
      }}));
    }}
    if (originalFetch) return originalFetch(url, opts);
    return Promise.reject(new Error("fetch unavailable"));
  }};

  window.autobotSetMode = function(mode){{
    window.__AUTOBOT_STATE__.mode = (mode === "live") ? "live" : "demo";
    window.__AUTOBOT_STATE__.live_order_enabled = false;
    return window.__AUTOBOT_STATE__;
  }};

  window.autobotDemoReset = function(){{
    window.__AUTOBOT_STATE__.mode = "demo";
    window.__AUTOBOT_STATE__.running = false;
    window.__AUTOBOT_STATE__.total_equity = 100.0;
    window.__AUTOBOT_STATE__.today_pnl = 0.0;
    window.__AUTOBOT_STATE__.realized_pnl = 0.0;
    window.__AUTOBOT_STATE__.usdc_free = 100.0;
    window.__AUTOBOT_STATE__.usdt_profit = 0.0;
    window.__AUTOBOT_STATE__.open_positions = 0;
    return window.__AUTOBOT_STATE__;
  }};

  console.log("PATCH 17D APK no-http layer active");
}})();
</script>
"""

    if "</head>" in html:
        return html.replace("</head>", js + "\n</head>", 1)
    return js + "\n" + html


class AutobotWebUIApp(App):
    def build(self):
        root = FloatLayout()
        self.label = Label(
            text="[b]Autobot Trading System[/b]\n\nWeb UI betöltése APK módban...\nHTTP nélkül.\nLive order tiltva.",
            markup=True,
            halign="center",
            valign="middle",
            font_size="22sp",
        )
        self.label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        root.add_widget(self.label)
        return root

    def on_start(self):
        Clock.schedule_once(lambda dt: self.open_webview(), 0.5)

    def open_webview(self):
        if not WEB_FILE.exists():
            self.label.text = f"[b]HIBA[/b]\n\nNem találom:\n{WEB_FILE}"
            return

        html = WEB_FILE.read_text(encoding="utf-8", errors="ignore")
        html = inject_apk_safety_layer(html)

        if platform != "android":
            self.label.text = "[b]APK WebUI no-http mód[/b]\n\nAndroid APK-ban WebView nyitná meg a tesztelt UI-t."
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

                # NINCS http://127.0.0.1:8080
                # HTTPS base URL csak eredetnek kell, hálózati kérés nélkül.
                webview.loadDataWithBaseURL(
                    "https://autobot.local/",
                    html,
                    "text/html",
                    "UTF-8",
                    None
                )

                self.webview = webview

            show()

        except Exception as e:
            self.label.text = (
                "[b]WebView indítási hiba[/b]\n\n"
                f"{e}\n\n"
                "A HTTP nélküli APK betöltés nem indult."
            )


if __name__ == "__main__":
    AutobotWebUIApp().run()
PY

echo "=== Ellenőrzés ==="
python3 -m py_compile apk_stage/main.py

grep -nE "PATCH 17D|loadDataWithBaseURL|NO-HTTP|ERR_CLEARTEXT|blocked_live_order|127.0.0.1" apk_stage/main.py || true
ls -lah apk_stage/webui/index.html

cat > logs/PATCH_17D_APK_WEBUI_NO_HTTP_LOAD_REPORT.txt <<EOF
PATCH 17D OK
Date: $(date)

Javítás:
- APK WebView már NEM http://127.0.0.1:8080 címet nyit.
- webui/index.html közvetlenül WebView-be töltődik.
- ERR_CLEARTEXT_NOT_PERMITTED így kikerülve.
- /api hívások mock/fallback választ kapnak.
- Live order továbbra is tiltva.
- Binance order NEM történt.
- APK build NEM indult.
- Commit NEM történt.

Cél:
- Az APK ugyanazt a szép 16C/16D webes UI-t mutassa.
EOF

echo "=== PATCH 17D KÉSZ ==="
echo "Jelentés: logs/PATCH_17D_APK_WEBUI_NO_HTTP_LOAD_REPORT.txt"
echo "APK build NEM indult. Commit NEM történt."
