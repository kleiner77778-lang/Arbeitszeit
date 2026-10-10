[app]

# (str) Title of your application
title = LKW Tracker

# (str) Package name
package.name = lkwtracker

# (str) Package domain (needed for android packaging)
package.domain = org.lkw

# (list) Source files to include (let it include python and png files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusion patterns relative to the root dir
source.include_patterns = assets/*,images/*

# (list) Source files to exclude (let it empty)
source.exclude_exts = spec

# (list) List of directory to exclude (let it empty)
source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
source.exclude_patterns = license,images/*.jpg

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,sqlite3,plyer,jnius

# (str) Custom source folders for requirements
#requirements.source_root = 

# (list) Permissions
# GPS-Berechtigung für die Standorterfassung an den Haltepunkten
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android SDK version to use
# android.sdk = 20

# (str) Android NDK version to use
# android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your native code will compile against.
# android.ndk_api = 21

# (list) Graphic API to use (2 = OpenGL ES 2.0, 3 = OpenGL ES 3.0)
# android.graphics_api = 2.0

# (str) Supported orientations: landscape (perfekt fürs Armaturenbrett)
orientation = landscape

# (list) List of Java .jar files to add to the libs/ to use them.
# android.add_jars = foo.bar,bar.baz

# (list) List of Java files to add to the android project (can be java or a directory)
# android.add_src =

# (list) Gradle dependencies to add
# android.gradle_dependencies =

# (str) Transformation to apply on the AndroidManifest.xml
# android.manifest.xml = 

# (str) The format used to package the app for release ('aab' or 'apk')
android.format = apk

# (str) Icon der App (greift direkt auf dein hochgeladenes icon.png zu)
icon.filename = %(source.dir)s/icon.png

# (str) Vorschaubild / Ladebildschirm beim Start der App
presplash.filename = %(source.dir)s/icon.png

#
# Python for android (p4a) specific
#

# (str) python-for-android branch to use
p4a.branch = master

# (str) OUYA Console support
#supported_platforms = android

# (list) Experimental features to allow
#p4a.features = 

# (bool) Indicate whether the application should be fullscreen or not
fullscreen = 1

# (string) Presplash background color (Hex code)
presplash.color = #000000

# (string) Window background color (Hex code)
#window.background_color = #000000

# (list) list of service to declare
#services = 
