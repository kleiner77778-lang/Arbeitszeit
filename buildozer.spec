[app]

# (str) Title of your application
title = ATLAS E-LKW TRACKER

# (str) Package name
package.name = lkwtracker

# (str) Package domain (needed for android/ios packaging)
package.domain = org.atlas

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
# WICHTIG: python3 zwingt Buildozer auf die stabile Python-Version 3.10
requirements = python3,kivy,plyer,requests,pyjnius

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, FOREGROUND_SERVICE, WAKE_LOCK

# (list) Services to declare
services = Serviceman:service/main.py

# (int) Target Android API
android.api = 33

# (int)
