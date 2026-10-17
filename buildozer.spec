[app]
# (str) Custom Java compile options
# android.add_compile_options =

# (str) Key parameters for signing release/debug builds
android.release = False
android.keystore = debug.keystore
android.keyalias = androiddebugkey
android.keystore_passthrough = True

title = LKW Tracker
package.name = lkwtracker
package.domain = org.lkwtracker

source.include_exts = py,png,jpg,kv,atlas,json
source.dir = .

version = 0.1

# Hier haben wir urllib3, certifi etc. ergänzt, damit Telegram-Nachrichten fehlerfrei rausgehen
requirements = python3,kivy,requests,plyer,jnius,urllib3,certifi,idna,charset_normalizer

# Geändert auf 'all', damit sich die App frei drehen kann
orientation = all

# Berechtigungen inkl. Foreground Service für Android 14+
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,FOREGROUND_SERVICE,FOREGROUND_SERVICE_LOCATION

# Registrierung des Hintergrund-Dienstes
services = lkwservice:service/main.py:foreground:sticky:foregroundServiceType=location

android.accept_sdk_license = True
android.api = 33
android.minapi = 24
android.ndk_api = 24
android.ndk = 25b
android.sdk_build_tools_version = 33.0.2
android.archs = arm64-v8a


p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
