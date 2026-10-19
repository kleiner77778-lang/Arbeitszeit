[app]

# (str) Title of your application
title = LKW Tracker

# (str) Package name
package.name = lkwtracker

# (str) Package domain
package.domain = org.lkwtracker

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy,requests,plyer,jnius,urllib3,certifi,idna,charset_normalizer

# (str) Supported orientation ('all' lets the app rotate freely)
orientation = all

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions including Foreground Service for Android 14+
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, FOREGROUND_SERVICE, FOREGROUND_SERVICE_LOCATION

# (list) Services to declare (exakter Name 'lkwservice' passend zum Code)
services = lkwservice:service/main.py:foreground:sticky:foregroundServiceType=location

# (bool) Accept SDK license automatically
android.accept_sdk_license = True

# (int) Target Android API
android.api = 33

# (int) Minimum API supported
android.minapi = 24

# (int) NDK API version
android.ndk_api = 24

# (str) Android NDK version
android.ndk = 25b

# (str) SDK build tools version
android.sdk_build_tools_version = 33.0.2

# (list) Target architectures
android.archs = arm64-v8a

# (str) Bootstrap to use for p4a
p4a.bootstrap = sdl2

[buildozer]
# (int) Log level (1 = info, verhindert das Abschneiden der Logs auf GitHub)
log_level = 1

# (int) Warn on root user when building inside Docker
warn_on_root = 1
