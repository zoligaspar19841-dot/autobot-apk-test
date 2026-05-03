#!/bin/bash
set -e

echo "=== PATCH 01: Android target + ikon stabilizálás - APK BUILD NÉLKÜL ==="

TS=$(date +%Y%m%d_%H%M%S)

echo "=== 1) Biztonsági mentések ==="
cp buildozer.spec "buildozer.spec.bak_patch01_$TS" 2>/dev/null || true
cp apk_stage/buildozer.spec "apk_stage/buildozer.spec.bak_patch01_$TS" 2>/dev/null || true
cp main.py "main.py.bak_patch01_$TS" 2>/dev/null || true
cp apk_stage/main.py "apk_stage/main.py.bak_patch01_$TS" 2>/dev/null || true

echo "=== 2) Egyedi sötét/sárga ikon létrehozása ==="
python - <<'PY'
from pathlib import Path
import struct, zlib, math

def write_png(path, w, h, pixels):
    raw = b''
    for y in range(h):
        raw += b'\x00'
        for x in range(w):
            raw += bytes(pixels[y][x])
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t+d) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9))
    png += chunk(b'IEND', b'')
    Path(path).write_bytes(png)

def make_icon(path):
    w = h = 512
    bg = (5, 5, 7, 255)
    yellow = (246, 181, 35, 255)
    yellow2 = (255, 215, 80, 255)
    dark = (0, 0, 0, 255)

    pixels = [[bg for _ in range(w)] for __ in range(h)]

    cx = cy = 256

    # sárga rombusz/minta
    for y in range(h):
        for x in range(w):
            dx = abs(x - cx)
            dy = abs(y - cy)
            if dx + dy < 145:
                pixels[y][x] = yellow
            if dx + dy < 82:
                pixels[y][x] = dark

    # négy kisebb sárga rombusz, Binance-szerű, de saját
    centers = [(256, 118), (256, 394), (118, 256), (394, 256)]
    for ccx, ccy in centers:
        for y in range(max(0, ccy-70), min(h, ccy+71)):
            for x in range(max(0, ccx-70), min(w, ccx+71)):
                if abs(x-ccx) + abs(y-ccy) < 52:
                    pixels[y][x] = yellow2

    # középen B betű egyszerű blokkokból
    def rect(x1, y1, x2, y2, col):
        for yy in range(max(0,y1), min(h,y2)):
            for xx in range(max(0,x1), min(w,x2)):
                pixels[yy][xx] = col

    col = yellow2
    rect(205, 170, 235, 345, col)
    rect(235, 170, 295, 200, col)
    rect(235, 245, 300, 275, col)
    rect(235, 315, 295, 345, col)
    rect(295, 200, 325, 245, col)
    rect(300, 275, 330, 315, col)

    write_png(path, w, h, pixels)

for p in ["icon.png", "apk_stage/icon.png"]:
    make_icon(p)
    print("OK icon:", p)
PY

echo "=== 3) buildozer.spec javítása root + apk_stage ==="
python - <<'PY'
from pathlib import Path
import re

def set_key_in_app(text, key, value):
    lines = text.splitlines()
    out = []
    in_app = False
    done = False

    for line in lines:
        st = line.strip()

        if st.startswith("[") and st.endswith("]"):
            if in_app and not done:
                out.append(f"{key} = {value}")
                done = True
            in_app = (st == "[app]")

        if in_app and re.match(rf"\s*#?\s*{re.escape(key)}\s*=", line):
            if not done:
                out.append(f"{key} = {value}")
                done = True
            continue

        out.append(line)

    if in_app and not done:
        out.append(f"{key} = {value}")

    return "\n".join(out) + "\n"

def clean_duplicate_app_keys(text):
    keep_keys = {
        "title",
        "package.name",
        "package.domain",
        "source.dir",
        "source.include_exts",
        "source.exclude_dirs",
        "source.exclude_exts",
        "source.exclude_patterns",
        "version",
        "requirements",
        "orientation",
        "fullscreen",
        "icon.filename",
        "android.permissions",
        "android.api",
        "android.minapi",
        "android.archs",
        "android.accept_sdk_license",
        "p4a.branch",
        "log_level",
        "warn_on_root",
    }

    seen = set()
    out = []
    in_app = False

    for line in text.splitlines():
        st = line.strip()

        if st.startswith("[") and st.endswith("]"):
            in_app = (st == "[app]")
            out.append(line)
            continue

        if in_app and "=" in line and not st.startswith("#"):
            key = line.split("=", 1)[0].strip()
            if key in keep_keys:
                if key in seen:
                    continue
                seen.add(key)

        out.append(line)

    return "\n".join(out) + "\n"

def fix_spec(path):
    p = Path(path)
    if not p.exists():
        print("HIÁNYZIK:", path)
        return

    s = p.read_text(encoding="utf-8", errors="replace")

    if "[app]" not in s:
        s = "[app]\n" + s

    s = clean_duplicate_app_keys(s)

    # Fontos: package maradjon stabil, hogy később frissíthető legyen.
    values = [
        ("title", "Binance Autobot"),
        ("package.name", "binanceautobot"),
        ("package.domain", "org.autobot"),
        ("source.dir", "."),
        ("source.include_exts", "py,png,jpg,jpeg,kv,atlas,json,txt,md,csv"),
        ("source.exclude_dirs", ".git,.github,__pycache__,.pytest_cache,.mypy_cache,.buildozer,bin,logs,packages,backups"),
        ("source.exclude_exts", "pyc,pyo,enc,key,keystore,apk,aab,zip,tar,gz,bak"),
        ("source.exclude_patterns", "*.bak,*.bak_*,*.BROKEN_*,*secret*,*secrets*,*.enc,*.key,.env,logs/*,packages/*"),
        ("version", "0.7.1"),
        ("requirements", "python3,kivy"),
        ("orientation", "portrait"),
        ("fullscreen", "0"),
        ("icon.filename", "icon.png"),
        ("android.permissions", "INTERNET"),
        ("android.api", "35"),
        ("android.minapi", "23"),
        ("android.archs", "arm64-v8a"),
        ("android.accept_sdk_license", "True"),
        ("p4a.branch", "master"),
        ("log_level", "2"),
        ("warn_on_root", "1"),
    ]

    for k, v in values:
        s = set_key_in_app(s, k, v)

    # [buildozer] rész legyen, de ne duplázzon
    if "[buildozer]" not in s:
        s += "\n[buildozer]\nlog_level = 2\nwarn_on_root = 1\n"
    else:
        s = re.sub(r"(?m)^\s*#?\s*log_level\s*=.*$", "log_level = 2", s)
        s = re.sub(r"(?m)^\s*#?\s*warn_on_root\s*=.*$", "warn_on_root = 1", s)

    p.write_text(s, encoding="utf-8")
    print("OK spec:", path)

fix_spec("buildozer.spec")
fix_spec("apk_stage/buildozer.spec")
PY

echo "=== 4) Ellenőrzés: nincs duplikált icon.filename / android.api ==="
python - <<'PY'
from pathlib import Path
from collections import Counter

for fn in ["buildozer.spec", "apk_stage/buildozer.spec"]:
    s = Path(fn).read_text(encoding="utf-8", errors="replace")
    keys = []
    in_app = False
    for line in s.splitlines():
        st = line.strip()
        if st.startswith("[") and st.endswith("]"):
            in_app = (st == "[app]")
            continue
        if in_app and "=" in line and not st.startswith("#"):
            keys.append(line.split("=",1)[0].strip())
    c = Counter(keys)
    dup = {k:v for k,v in c.items() if v > 1}
    print(fn, "DUP:", dup)
    assert "icon.filename" not in dup
    assert "android.api" not in dup
    assert "android.minapi" not in dup
PY

echo "=== 5) Python compile teszt - build nélkül ==="
python -m py_compile main.py demo_core_engine.py
python -m py_compile apk_stage/main.py apk_stage/demo_core_engine.py

echo "=== 6) Git állapot - csak ellenőrzés, commit nincs ==="
git status --short

echo "=== PATCH 01 KÉSZ ==="
echo "APK build NEM indult."
echo "Commit NEM történt."
echo "Ha az ellenőrzés jó, írd: jó"
