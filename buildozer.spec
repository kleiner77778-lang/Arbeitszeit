[app]

# (str) Title of your application
title = LKW Tracker

# (str) Package name
package.name = lkwtracker

# (str) Package domain (needed for android packaging)
package.domain = org.lkw

# (str) Source code where the application resides
source.dir = .

# (list) Source files to include (let it include python and png files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Source files to exclude (let it empty)
source.exclude_exts = spec

# (list) List of directory to exclude (let it empty)
source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
source.exclude_patterns = license,images/*.jpg

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# Feste Versionen für Kivy und Cython verhindern den config.pxi Fehler
requirements = python3,kivy==2.2.1,cython==0.29.33,sqlite3,plyer,jnius

# (list) Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android
