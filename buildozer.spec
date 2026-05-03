[app]
title = Binance Autobot
package.name = binanceautobot
package.domain = org.autobot
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,csv
source.exclude_dirs = .git,.github,__pycache__,.pytest_cache,.mypy_cache,.buildozer,bin,logs,packages,backups,_chatgpt_export
source.exclude_exts = pyc,pyo,enc,key,keystore,apk,aab,zip,tar,gz,bak,sh
source.exclude_patterns = *.bak,*.bak_*,*.BROKEN_*,*secret*,*secrets*,*.enc,*.key,.env,logs/*,packages/*,_chatgpt_export/*
version = 0.7.2
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 35
android.minapi = 23
android.archs = arm64-v8a
android.accept_sdk_license = True
p4a.branch = master
log_level = 2
warn_on_root = 1
icon.filename = icon.png

[buildozer]
log_level = 2
warn_on_root = 1
