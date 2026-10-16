[app]

# (str) Title of your application
title = LKW Tracker

# (str) Package name
package.name = lkwtracker

# (str) Package domain (needed for android packaging)
package.domain = org.lkwtracker

# (str) Source files to include (let it include json for our IPC)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Source files to include (let it include service folder)
source.include_patterns = assets/*,service/*

# (str) Application directory
source.dir = .

# (str) Version of the application
version = 0.1

# (list) Application requirements
# Wichtig: requests und alle SSL/Zertifikats-Abhängigkeiten für Telegram!
requirements = python3,kivy,requests,plyer,jnius,urllib3,certifi,idna,charset_normalizer

# (str) Supported orientations (geändert auf 'sensor', damit die App drehbar ist)
orientation = all

# (list) Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,FOREGROUND_SERVICE,FOREGROUND_SERVICE_LOCATION

# (list) Features
android.features = android.hardware.location.gps

# (str) Application Icon
icon.filename = icon.png

# (str) Presplash image
# presplash.filename = %(source.dir)s/data/presplash.png

# (list) List of services to declare
services = lkwservice:service/main.py:foreground:sticky

#
# Android specific
#

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use Android X
android.androidx = True

# (str) python-for-android branch to use
p4a.branch = master

# (str) OUYA Console support
# android.ouya.appui = False

# (str) XML extensions for manifest
# android.manifest.xml = 

# (str) extra xml to include in <application> tag
# android.manifest.application_xml = 

# (str) Android additional adb install args
# android.adb_install_args = 

# (list) The Android archs to build for,, and optionally optimzed as arm64-v8a
android.architectures = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (API >= 23)
android.backup = True

# (str) The format used to package the app for release ('aab' or 'apk')
android.release_artifact = apk

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_root = 1

# (str) Path to build artifact, storage for global sdcard
# bin_dir = ./bin

# (str) Path to build output, where py4a will be place
# build_output_dir = ./.build_output
