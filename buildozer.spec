[app]

# (str) Title of your application
title = ATLAS E-LKW Tracker

# (str) Package name
package.name = lkwtracker

# (str) Package domain (needed for android packaging)
package.domain = org.atlas

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all files)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) List of inclusion & exclusion patterns for source files
source.include_patterns = assets/*,service/*.py

# (str) Application versioning
version = 1.0

# (list) Application requirements
requirements = python3,kivy,plyer,requests,urllib3,certifi,idna,charset_normalizer,pyjnius

# (list) Supported orientations
orientation = portrait

# (list) List of services to declare
services = tracker:service/main.py:on_boot:true

[android]

# (str) Supported Android architectures
android.archs = arm64-v8a

# (list) Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Enable AndroidX support
android.androidx = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (str) Path to build artifact storage
build_dir = .buildozer

# (str) Path to build output (binaries)
bin_dir = bin
