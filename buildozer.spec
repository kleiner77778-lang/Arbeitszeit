# (list) Application requirements
requirements = python3,kivy,kivymd,requests,plyer,jnius

# (list) List of services to declare
android.services = lkwtracker:service.py

# (list) Permissions (Inklusive Foreground-Service und Wake-Lock, damit das Handy nicht einschläft)
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, FOREGROUND_SERVICE, FOREGROUND_SERVICE_LOCATION, WAKE_LOCK
