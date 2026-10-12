[app]

# (str) Title of your application
title = LKW Arbeitszeit Tracker

# (str) Package name
package.name = lkwtracker

# (str) Package domain (needed for android packaging)
package.domain = org.lkwtracker

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
# Wichtig: python3, kivy, kivymd, requests, plyer und jnius müssen hier stehen!
requirements = python3,kivy,kivymd,requests,plyer,jnius

# (str) Custom source folders for requirements
#requirements.source_dirs =

# (list) Perseus
#android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,FOREGROUND_SERVICE

# (list) Supported orientations
orientation = landscape

# (list) List of services to declare
# Bindet den Hintergrunddienst (
