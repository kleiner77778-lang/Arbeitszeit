[app]

# Name der Anwendung
title = LKW Tracker

# Paketname
package.name = lkwtracker

# Paket-Domain
package.domain = org.lkwtracker

# Dateiendungen, die eingebunden werden
source.include_exts = py,png,jpg,kv,atlas,json

# Zusätzliche Dateien und Ordner
source.include_patterns = assets/*,service/*

# Quellverzeichnis
source.dir = .

# Versionsnummer
version = 0.1

# Benötigte Python-Pakete
requirements = python3,kivy,requests,plyer,pyjnius,urllib3,certifi,idna,charset_normalizer

# Bildschirmorientierung
orientation = all

# Android-Berechtigungen
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,FOREGROUND_SERVICE,FOREGROUND_SERVICE_LOCATION

# GPS-Funktion
android.features = android.hardware.location.gps

# App-Symbol
icon.filename = icon.png

# Hintergrunddienst für die GPS-Ortung
services = lkwservice:service/main.py:foreground:sticky


# Android-Einstellungen

# Android Target SDK
android.api = 33

# Minimale Android-Version
android.minapi = 21

# Android SDK
android.sdk = 33

# Android NDK
android.ndk = 25b

# AndroidX aktivieren
android.androidx = True

# Python-for-Android
p4a.branch = master

# Unterstützte Prozessorarchitekturen
android.architectures = arm64-v8a, armeabi-v7a

# Android Auto Backup
android.backup = True

# APK erstellen
android.release_artifact = apk


[buildozer]

# Ausführliche Build-Ausgabe
log_level = 2

# Warnung bei Ausführung als Root
warn_root = 1
