[app]

# (str) Titel deiner App
title = LKW Tracker

# (str) Paketname (ohne Leerzeichen/Sonderzeichen)
package.name = lkwtracker

# (str) Paket-Domain (Domain-Reverse-Notation)
package.domain = org.lkwtracker

# (list) Quellcode-Dateien, die eingeschlossen werden sollen
source.include_exts = py,png,jpg,kv,atlas

# (list) Verzeichnisse mit Quelldateien
source.dir = .

# (str) Anwendungsversion
version = 0.1

# (list) Python-Abhängigkeiten
requirements = python3,kivy,requests,plyer,jnius

# (str) Ausrichtung der App (portrait, landscape oder all)
orientation = portrait

# (list) Berechtigungen für Android
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# --- ANDROID 14+ EINSTELLUNGEN ---
# Target API level (Android 14)
android.api = 34

# Minimum API level (Android 14+ erfordert minapi 24)
android.minapi = 24

# NDK Version (muss zu API 34 / 24 passen)
android.ndk = 25b

# NDK API level (muss mit minapi übereinstimmen)
android.ndk_api = 24

# Zielarchitektur für moderne Geräte
android.archs = arm64-v8a

# (bool) Autostart bei Boot erlauben (optional)
# android.service_startup = False

[buildozer]

# Log-Level (0 = info, 1 = debug, 2 = warning)
log_level = 2

# Warnung bei Root-Ausführung ignorieren (wichtig für GitHub Actions)
warn_on_root = 1
