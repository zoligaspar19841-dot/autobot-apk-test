import os
import json
import shutil
import time
from pathlib import Path

PROJECT = Path(".").resolve()
SPEC = PROJECT / "buildozer.spec"
REPORT = PROJECT / "logs" / "apk_build_dry_run_plan.json"

def read_spec():
    out = {}
    if not SPEC.exists():
        return out
    for line in SPEC.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip()
    return out

def exists(path):
    return (PROJECT / path).exists()

def file_size(path):
    p = PROJECT / path
    return p.stat().st_size if p.exists() else 0

spec = read_spec()

required_files = [
    "main.py",
    "demo_core_engine.py",
    "buildozer.spec",
]

secret_patterns = [
    ".env",
    "demo_core_secrets.json",
    "secrets.json",
    "creds.json",
    "email.json",
    "secrets.enc",
    "demo_core_secret.key",
    "binance_api_key.txt",
    "openai_api_key.txt",
]

plain_secrets_found = [p for p in secret_patterns if exists(p)]

tools = {
    "python": shutil.which("python"),
    "pip": shutil.which("pip"),
    "buildozer": shutil.which("buildozer"),
    "java": shutil.which("java"),
    "git": shutil.which("git"),
    "zip": shutil.which("zip"),
    "unzip": shutil.which("unzip"),
}

files = []
for f in required_files:
    files.append({
        "path": f,
        "exists": exists(f),
        "size": file_size(f),
    })

build_command = "buildozer android debug"
safe_recommended_command = "buildozer -v android debug"

warnings = []
if not spec:
    warnings.append("buildozer.spec nincs vagy nem olvasható.")
if not tools["buildozer"]:
    warnings.append("buildozer nincs telepítve.")
if not tools["java"]:
    warnings.append("java nincs telepítve.")
if plain_secrets_found:
    warnings.append("Plain secret fájl található, APK build előtt tilos.")
if not exists("main.py"):
    warnings.append("main.py hiányzik.")
if not exists("demo_core_engine.py"):
    warnings.append("demo_core_engine.py hiányzik.")

report = {
    "ok": len(warnings) == 0,
    "ts": int(time.time()),
    "project": str(PROJECT),
    "no_build": True,
    "apk_build_touched": False,
    "order_endpoint_used": False,
    "tools": tools,
    "spec": {
        "title": spec.get("title"),
        "package.name": spec.get("package.name"),
        "package.domain": spec.get("package.domain"),
        "requirements": spec.get("requirements"),
        "source.include_exts": spec.get("source.include_exts"),
        "source.exclude_dirs": spec.get("source.exclude_dirs"),
        "source.exclude_exts": spec.get("source.exclude_exts"),
        "source.exclude_patterns": spec.get("source.exclude_patterns"),
        "android.permissions": spec.get("android.permissions"),
        "android.api": spec.get("android.api"),
        "android.minapi": spec.get("android.minapi"),
        "android.archs": spec.get("android.archs"),
    },
    "required_files": files,
    "plain_secrets_found": plain_secrets_found,
    "build_command_preview": build_command,
    "safe_recommended_command_preview": safe_recommended_command,
    "warnings": warnings,
}

REPORT.parent.mkdir(exist_ok=True)
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps(report, ensure_ascii=False, indent=2))
