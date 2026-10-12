[app]

# (str) Title of your application
title = LKW Arbeitszeit Tracker

# (str) Package name
package.name = lkwtracker

# (str) Package domain (needed for android packaging)
package.domain = org.lkwtracker

# (str) Source where the app lives
source.dir = .

# (list) Source files to include (let empty to include all files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec

# (list) List of directory to exclude from distribution
source.exclude_dirs = tests, bin, venv

# (list) List of exclusions in source files
source.exclude_patterns = license,images/*.jpg

# (str) Application versioning
version = 1.0

# (list) Application requirements
requirements = python3,kivy,kivymd,requests,plyer,jnius

# (list) Supported orientations
orientation = landscape

# (list) List of services to declare
android.services = lkwtracker:service.py

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Icon of the application
icon.filename = %(source.dir)s/icon.png

# (list) Permissions
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, FOREGROUND_SERVICE, WAKE_LOCK

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (bool) Use Android X
android.androidx = True

# (list) The Android archs to build for
android.archs = arm64-v8a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildroot is in root directory (0 = False, 1 = True)
warn_on_root = 0
