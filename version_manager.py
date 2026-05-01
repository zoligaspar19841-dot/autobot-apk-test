import json, os, time

VERSIONS_FILE = "versions.json"

def _load():
    if not os.path.exists(VERSIONS_FILE):
        return {"current": "0.1.0", "versions": [{"version": "0.1.0", "name": "Első működő APK alap", "ts": int(time.time())}]}
    try:
        return json.load(open(VERSIONS_FILE, "r", encoding="utf-8"))
    except Exception:
        return {"current": "0.1.0", "versions": []}

def _save(d):
    with open(VERSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def list_versions():
    return _load()

def save_version(version, name):
    d = _load()
    d["current"] = version
    d.setdefault("versions", []).append({"version": version, "name": name, "ts": int(time.time())})
    _save(d)
    return d

def set_current(version):
    d = _load()
    d["current"] = version
    _save(d)
    return d
