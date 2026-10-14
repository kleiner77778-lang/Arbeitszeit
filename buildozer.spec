[app]

title = LKW Tracker
package.name = lkwtracker
package.domain = org.lkwtracker

source.include_exts = py,png,jpg,kv,atlas,json
source.dir = .

version = 0.1

# Nur das absolute Minimum für den Start
requirements = python3,kivy

orientation = portrait

# Android 14+ Grundkonfiguration
android.accept_sdk_license = True
android.api = 34
android.minapi = 24
android.ndk_api = 24
android.ndk = 25b
android.sdk_build_tools_version = 34.0.0
android.archs = arm64-v8a

p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
