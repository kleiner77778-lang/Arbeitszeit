[app]

# (str) Titel deiner Anwendung
title = LKW Tracker

# (str) Paketname (nur Kleinbuchstaben und Buchstaben, keine Sonderzeichen)
package.name = lkwtracker

# (str) Paket-Domain (Domain-Reverse-Notation)
package.domain = org.lkwtracker

# (list) Quelldateien, die eingeschlossen werden sollen
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Hauptverzeichnis mit dem Quellcode
source.dir = .

# (str) Anwendungsversion
version = 0.1

# (list) Python-Abhängigkeiten
requirements = python3,kivy,requests,plyer,jnius

# (str) Ausrichtung der App (portrait, landscape oder all)
orientation = portrait

# (list) Android-Berechtigungen
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# --- ANDROID 14+ KONFIGURATION ---

# Android-SDK-Lizenzen automatisch akzeptieren (ZWINGEND für CI/CD & GitHub Actions)
android.accept_sdk_license = True

# Target API Level (Android 14 = 34)
android.api = 34

# Minimum API Level (Android 14+ erfordert mindestens API 24)
android.minapi = 24

# NDK API Level (muss exakt mit minapi übereinstimmen)
android.ndk_api = 24

# NDK-Version für modernere NDK-Toolchains
android.ndk = 25b

# Feste Build-Tools-Version passend zu API 34
android.sdk_build_tools_version = 34.0.0

# Zielarchitektur für moderne Android-Smartphones (64-Bit)
android.archs = arm64-v8a

# Bootstrap für Kivy
p4a.bootstrap = sdl2

[buildozer]

# Log-Level (0 = info, 1 = debug, 2 = warning)
log_level = 2

# Warnung bei Ausführung als Root ignorieren (erforderlich für GitHub Runner)
warn_on_root = 1
