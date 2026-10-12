[app]

# (str) Title of your application
title = LKW Tracker

# (str) Package name
package.name = lkwtracker

# (str) Package domain
package.domain = org.oliver.lkwtracker

# (str) Source code directory
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy,kivymd,plyer,requests,urllib3,certifi,jnius

# (str) Supported orientation
orientation = landscape

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (list) Permissions (Wichtig: FOREGROUND_SERVICE verhindert das Einschlafen im Hintergrund)
android.permissions = ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, INTERNET, FOREGROUND_SERVICE

# (int) Target Android API
android.api = 33

# (int) Minimum API required
android.minapi = 24

# (str) Android NDK version
android.ndk = 25b

# (bool) Automatically accept sdk licenses
android.accept_sdk_license = True

# (str) The Android arch to build for
android.archs = arm64-v8a

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) App icon and presplash
icon.filename = icon.png
presplash.filename = icon.png

# (str) Background service configuration (Läuft absolut autark im Hintergrund weiter)
services = tracker:service.py

[buildozer]

# (int) Log level
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
