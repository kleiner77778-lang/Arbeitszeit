[app]

title = LKW Tracker
package.name = lkwtracker
package.domain = org.lkwtracker

source.include_exts = py,png,jpg,kv,atlas,json
source.dir = .

version = 0.1

# Icon (wird im Workflow automatisch bereitgestellt)
icon.filename = %(source.dir)s/icon.png

# WICHTIG: cython<3 hier direkt als Requirement erzwingen!
requirements = python3,kivy==2.3.0,cython<3,requests,openssl,certifi,plyer,jnius

orientation = all

android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,FOREGROUND_SERVICE,FOREGROUND_SERVICE_LOCATION

services = lkwservice:service/main.py:foreground:sticky:foregroundServiceType=location

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
