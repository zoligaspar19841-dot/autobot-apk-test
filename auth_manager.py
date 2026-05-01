import json, os, random, time

OTP_FILE = "auth_otp.json"
SESSION_FILE = "auth_session.json"
SESSION_SECONDS = 300

def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _load(path):
    if not os.path.exists(path):
        return {}
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except Exception:
        return {}

def generate_code(email=""):
    code = str(random.randint(10000, 99999))
    data = {"email": email, "code": code, "expires": int(time.time()) + SESSION_SECONDS}
    _save(OTP_FILE, data)

    sent = False
    try:
        from emailer import send_email
        r = send_email("Autobot belépési kód", f"A belépési kódod: {code}\nÉrvényes: 5 perc", email or None)
        sent = bool(r.get("ok"))
    except Exception:
        pass

    return {"ok": True, "code": code, "email_sent": sent, "expires_in": SESSION_SECONDS}

def verify_code(code):
    data = _load(OTP_FILE)
    if not data:
        return {"ok": False, "error": "Nincs generált kód"}
    if int(time.time()) > int(data.get("expires", 0)):
        return {"ok": False, "error": "Lejárt kód"}
    if str(code).strip() != str(data.get("code", "")):
        return {"ok": False, "error": "Hibás kód"}

    _save(SESSION_FILE, {"logged_in": True, "expires": int(time.time()) + SESSION_SECONDS})
    return {"ok": True, "expires_in": SESSION_SECONDS}

def session_valid():
    s = _load(SESSION_FILE)
    return bool(s.get("logged_in")) and int(time.time()) <= int(s.get("expires", 0))

def logout():
    _save(SESSION_FILE, {"logged_in": False, "expires": 0})
    return {"ok": True}
