[app]

# (str) Titel deiner Anwendung
title = LKW Tracker

# (str) Paketname (nur Kleinbuchstaben, keine Sonderzeichen)
package.name = lkwtracker

# (str) Paket-Domain (Domain-Reverse-Notation)
package.domain = org.lkwtracker

# (list) Quelldateien, die eingeschlossen werden sollen (inkl. Schriften/ttf falls benötigt)
source.include_exts = py,png,jpg,kv,atlas,json,ttf

# (list) Hauptverzeichnis mit dem Quellcode
source.dir = .

# (str) Anwendungsversion
version = 0.1

# (list) Python-Abhängigkeiten (WICHTIG: Kein Cython hier, das läuft im GitHub-Workflow!)
requirements = python3,kivy,requests,plyer,jnius

# (str) Ausrichtung der App (erlaubt Hoch- und Querformat / Drehung)
orientation = all

# (list) Android-Berechtigungen (inkl. Foreground Service für Android 14+)
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,FOREGROUND_SERVICE,FOREGROUND_SERVICE_LOCATION

# Registrierung des Hintergrund-Dienstes
services = lkwservice:service/main.py:foreground:sticky:foregroundServiceType=location

# --- ANDROID 14+ KONFIGURATION ---

# Android-SDK-Lizenzen automatisch akzeptieren (ZWINGEND für GitHub Actions)
android.accept_sdk_license = True

# Target API Level (Android 14 = 34)
android.api = 34

# Minimum API Level (Android 14+ erfordert mindestens API 24)
android.minapi = 24

# NDK API Level (muss exakt mit minapi übereinstimmen)
android.ndk_api = 24

# NDK-Version
android.ndk = 25b

# Feste Build-Tools-Version passend zu API 34
android.sdk_build_tools_version = 34.0.0

# Zielarchitektur (64-Bit)
android.archs = arm64-v8a

# Bootstrap für Kivy
p4a.bootstrap = sdl2

[buildozer]

# Log-Level (0 = info, 1 = debug, 2 = warning)
log_level = 2

# Warnung bei Ausführung als Root auf dem Server ignorieren
warn_on_root = 1
