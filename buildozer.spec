[app]

title = LKW Arbeitszeit Tracker
package.name = lkwtracker
package.domain = org.lkwtracker
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_exts = spec
source.exclude_dirs = tests, bin, venv
version = 2.0

requirements = python3,kivy,requests,plyer,jnius

orientation = landscape,portrait
android.services = lkwtracker:service.py

fullscreen = 0
icon.filename = %(source.dir)s/icon.png
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, FOREGROUND_SERVICE

android.api = 34
android.minapi = 21
android.ndk = 25b
android.androidx = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0
