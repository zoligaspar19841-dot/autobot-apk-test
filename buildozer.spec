[app]

title = Binance Autobot
package.name = binanceautobot
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.2.5
requirements = python3,kivy

orientation = portrait

fullscreen = 0
android.api = 31
android.minapi = 21
android.ndk = 23b

android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 0

android.archs = arm64-v8a, armeabi-v7a

android.accept_sdk_license = True
