import os
import json
import shutil
import time
from pathlib import Path

SRC = Path(".").resolve()
DST = SRC / "apk_stage"
REPORT = SRC / "logs" / "apk_stage_report.json"

include_files = [
    "main.py",
    "demo_core_engine.py",
    "buildozer.spec",
]

optional_files = [
    "README.md",
    "README.txt",
    "requirements.txt",
]

blocked_exts = {
    ".enc", ".key", ".pyc", ".pyo", ".apk", ".aab", ".zip",
    ".tar", ".gz", ".bak",
}

blocked_names = {
    ".git", ".github", "__pycache__", ".buildozer", "bin", "logs",
    "packages", "backups", "apk_stage",
    ".env",
    "demo_core_secrets.json",
    "secrets.json",
    "creds.json",
    "email.json",
    "binance_api_key.txt",
    "openai_api_key.txt",
}

def blocked(path: Path):
    parts = set(path.parts)
    if parts & blocked_names:
        return True
    name = path.name.lower()
    if "secret" in name or "secrets" in name:
        return True
    if path.suffix.lower() in blocked_exts:
        return True
    if ".broken_" in name or ".bak" in name:
        return True
    return False

copied = []
missing = []
blocked_found = []

DST.mkdir(exist_ok=True)

for rel in include_files + optional_files:
    src = SRC / rel
    if src.exists() and not blocked(src):
        dst = DST / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(rel)
    elif src.exists() and blocked(src):
        blocked_found.append(rel)
    else:
        if rel in include_files:
            missing.append(rel)

# KV / képfájlok, ha vannak, de secrets nélkül
for ext in ["*.kv", "*.png", "*.jpg", "*.jpeg", "*.atlas"]:
    for src in SRC.glob(ext):
        if src.is_file() and not blocked(src):
            shutil.copy2(src, DST / src.name)
            copied.append(src.name)

# Stage tartalom ellenőrzés
# Fontos: itt már a STAGE relatív fájlnevet ellenőrizzük,
# nem az abszolút útvonalat, mert abban benne van az apk_stage mappanév.
stage_files = []
stage_blocked = []

def blocked_stage_file(rel: str):
    name = rel.lower()
    suffix = Path(rel).suffix.lower()
    parts = set(Path(rel).parts)

    stage_blocked_names = {
        ".git", ".github", "__pycache__", ".buildozer", "bin", "logs",
        "packages", "backups", ".env",
        "demo_core_secrets.json", "secrets.json", "creds.json", "email.json",
        "binance_api_key.txt", "openai_api_key.txt",
    }

    if parts & stage_blocked_names:
        return True
    if "secret" in name or "secrets" in name:
        return True
    if suffix in blocked_exts:
        return True
    if ".broken_" in name or ".bak" in name:
        return True
    return False

for fp in DST.rglob("*"):
    if fp.is_file():
        rel = str(fp.relative_to(DST))
        stage_files.append(rel)
        if blocked_stage_file(rel):
            stage_blocked.append(rel)

report = {
    "ok": not missing and not stage_blocked,
    "ts": int(time.time()),
    "stage_dir": str(DST),
    "no_build": True,
    "apk_build_touched": False,
    "order_endpoint_used": False,
    "copied": copied,
    "missing_required": missing,
    "stage_file_count": len(stage_files),
    "stage_files": stage_files,
    "blocked_found": blocked_found,
    "stage_blocked": stage_blocked,
    "message": "APK stage clean package kész. Build nem indult.",
}

REPORT.parent.mkdir(exist_ok=True)
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps(report, ensure_ascii=False, indent=2))

if not report["ok"]:
    raise SystemExit("HIBA: stage nem tiszta vagy hiányos")
