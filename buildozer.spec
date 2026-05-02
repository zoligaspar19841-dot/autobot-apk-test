[app]

title = Autobot APK Test
package.name = autobottest
package.domain = org.zoligaspar

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

version = 0.2.4

requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, USE_BIOMETRIC, USE_FINGERPRINT
android.api = 35
android.minapi = 23
android.ndk = 25b
android.accept_sdk_license = True
android.numeric_version = 24

# Ha van icon.png a projekt gyökérben, ezt használja
icon.filename = icon.png

[buildozer]

log_level = 2
warn_on_root = 1
