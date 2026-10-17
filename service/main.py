import json
import math
import os
import time
from plyer import gps
import requests

# Dein neuer Telegram Bot Token
TELEGRAM_BOT_TOKEN = "8903052918:AAHBnydKYckd-LHpV7Fi9f2oCifsLP25Irs"
TELEGRAM_CHAT_ID = "8941361378"

# 100% absturzsicherer Pfad für den Android-Hintergrunddienst
try:
  from jnius import autoclass
  try:
    PythonService = autoclass("org.kivy.android.PythonService")
    context = PythonService.mService
    FILES_DIR = context.getFilesDir().getAbsolutePath()
  except Exception:
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    context = PythonActivity.mActivity.getApplicationContext()
    FILES_DIR = context.getFilesDir().getAbsolutePath()
except Exception:
  FILES_DIR = os.path.expanduser('~')

STATUS_FILE = os.path.join(FILES_DIR, "status.json")
COMMAND_FILE = os.path.join(FILES_DIR, "command.json")

is_shift_active = False
last_lat = None
last_lon = None
total_km = 0.0
telegram_connected = False


def send_telegram_message(text):
  if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    return False
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
  try:
    res = requests.post(url, json=payload, timeout=8)
    return res.status_code == 200
  except Exception as e:
    print(f"Telegram-Fehler: {e}")
    return False


def calc_distance(lat1, lon1, lat2, lon2):
  R = 6371.0
  dlat = math.radians(lat2 - lat1)
  dlon = math.radians(lon2 - lon1)
  a = (
      math.sin(dlat / 2) ** 2
      + math.cos(math.radians(lat1))
      * math.cos(math.radians(lat2))
      * math.sin(dlon / 2) ** 2
  )
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  return R * c


def write_status(lat=None, lon=None):
  global is_shift_active, total_km, telegram_connected
  status_str = "Schicht aktiv" if is_shift_active else "Tracking gestoppt"
  status_data = {
      "status": status_str,
      "lat": lat if lat is not None else 0.0,
      "lon": lon if lon is not None else 0.0,
      "km": round(total_km, 2),
      "telegram_ok
