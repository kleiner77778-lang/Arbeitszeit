[app]

# (str) Title of your application
title = LKW Arbeitszeit Tracker

# (str) Package name
package.name = lkwtracker

# (str) Package domain (needed for android packaging)
package.domain = org.lkwtracker

# (str) Source where the app lives
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (list) Source files to exclude
source.exclude_exts = spec
source.exclude_dirs = tests, bin, venv

# (str) Application versioning
version = 1.1

# (list) Application requirements (Neueste kompatible Versionen)
requirements = python3,kivy,kivymd,requests,plyer,jnius

# (list) Supported orientations
orientation = landscape

# (list) List of services to declare
android.services = lkwtracker:service.py

#
# Android specific
#

fullscreen = 0

# (string) Icon of the application
icon.filename = %(source.dir)s/icon.png

# (list) Permissions (Inklusive moderner Foreground-Service Berechtigungen für Android 14)
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, FOREGROUND_SERVICE, FOREGROUND_SERVICE_LOCATION, WAKE_LOCK

# (int) Target Android API
android.api = 34

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version (Modernster Standard)
android.ndk = 25b

# (bool) Use Android X
android.androidx = True

# (list) The Android archs to build for
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0
