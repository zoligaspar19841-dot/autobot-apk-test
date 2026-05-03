[app]
title = Binance Autobot
package.name = binanceautobot
package.domain = org.autobot

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,md,csv
version = 0.2.5
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.api = 31
android.minapi = 21
android.ndk = 23b
android.permissions = INTERNET
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
[buildozer]
log_level = 2
warn_on_root = 1

android.archs = arm64-v8a, armeabi-v7a

android.accept_sdk_license = True

source.exclude_dirs = .git,.github,__pycache__,.pytest_cache,.mypy_cache,.buildozer,bin,logs,packages,backups

source.exclude_exts = pyc,pyo,enc,key,keystore,apk,aab,zip,tar,gz,bak

source.exclude_patterns = *.bak,*.bak_*,*.BROKEN_*,*secret*,*secrets*,*.enc,*.key,.env,logs/*,packages/*

p4a.branch = master
