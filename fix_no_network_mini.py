from pathlib import Path

p = Path("demo_core_engine.py")
s = p.read_text(encoding="utf-8")

start = s.find("def final_prebuild_audit_status():")
end = s.find("\ndef final_go_nogo_summary():", start)

if start == -1 or end == -1:
    raise SystemExit("HIBA: final_prebuild_audit_status blokk nem található")

new_fn = '''def final_prebuild_audit_status():
    """
    Final Prebuild Audit - NO NETWORK MINI.
    Csak lokális fájlokat ellenőriz.
    Nem kér élő árat.
    Nem hív Binance API-t.
    Nem buildel APK-t.
    """
    state = load_state()
    settings = state.get("settings", {})

    required_files = [
        "logs/full_system_status_report.json",
        "logs/health_report.json",
        "logs/firstrun_readiness_report.json",
        "logs/release_candidate_report.json",
        "logs/ui_route_report.json",
        "logs/apk_build_gate_report.json",
        "logs/apk_artifact_manifest.json",
    ]

    checks = []
    for path in required_files:
        exists = os.path.exists(path)
        checks.append({
            "key": path,
            "title": path,
            "required": True,
            "ok": exists,
            "detail": {
                "exists": exists,
                "size": os.path.getsize(path) if exists else 0,
            },
        })

    plain_secret_files = [
        "demo_core_secrets.json",
        "secrets.json",
        ".env",
        "creds.json",
        "email.json",
        "binance_api_key.txt",
        "openai_api_key.txt",
    ]

    plain_found = []
    for path in plain_secret_files:
        if os.path.exists(path):
            plain_found.append(path)

    secrets_ok = len(plain_found) == 0

    checks.append({
        "key": "plain_secrets",
        "title": "Plain secret fájl ne legyen",
        "required": True,
        "ok": secrets_ok,
        "detail": {"plain_found": plain_found},
    })

    required = [c for c in checks if c.get("required")]
    passed = [c for c in required if c.get("ok")]
    failed = [c for c in required if not c.get("ok")]

    score_pct = round((len(passed) / len(required)) * 100.0, 2) if required else 0.0
    min_score = float(settings.get("final_prebuild_min_score_pct", 90.0) or 90.0)

    go = score_pct >= min_score and not failed

    return {
        "ok": True,
        "no_network": True,
        "go_for_apk_build_later": go,
        "score_pct": score_pct,
        "min_score_pct": min_score,
        "passed_required": len(passed),
        "total_required": len(required),
        "failed_required": failed,
        "order_endpoint_flags": [],
        "checks": checks,
        "will_build_now": False,
        "apk_build_touched": False,
        "order_endpoint_used": False,
        "message": "Final prebuild audit NO NETWORK MINI kész. APK build nincs.",
    }
'''

s = s[:start] + new_fn + s[end:]
p.write_text(s, encoding="utf-8")

print("OK: final_prebuild_audit_status lecserélve NO NETWORK MINI verzióra")
