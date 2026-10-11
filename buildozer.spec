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
requirements = python3,kivy==2.2.1,cython==0.29.33,sqlite3,plyer,jnius

# (list) Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Supported orientations: landscape (Querformat fürs Armaturenbrett)
orientation = landscape

# (str) The format used to package the app for release ('aab' or 'apk')
android.format = apk

# (str) Icon der App
icon.filename = icon.png

# (str) Vorschaubild / Ladebildschirm beim Start der App
presplash.filename = icon.png

#
# Python for android (p4a) specific
#

# (str) python-for-android branch to use (stabilisiert den Build-Prozess)
p4a.branch = release

# (bool) Indicate whether the application should be fullscreen or not
fullscreen = 1

# (string) Presplash background color (Hex code)
presplash.color = #000000
