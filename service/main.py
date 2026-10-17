import json
import math
import os
import time
from plyer import gps
import requests

# ---------------------------------------------------------
# TELEGRAM KONFIGURATION
# ---------------------------------------------------------
TELEGRAM_BOT_TOKEN = "8413301731:AAHRM32xA2CkAkrrcf85sqYDR88YK14k3bs"
TELEGRAM_CHAT_ID = "8941361378"

# ---------------------------------------------------------
# PFADE FÜR ANDROID (Sicher & Ohne JNI/autoclass Absturz)
# ---------------------------------------------------------
FILES_DIR = os.path.expanduser('~')
STATUS_FILE = os.path.join(FILES_DIR, "status.json")
COMMAND_FILE = os.path.join(FILES_DIR, "command.json")

is_shift_active = False
last_lat = None
last_lon = None
total_km = 0.0
telegram_connected = False


# ---------------------------------------------------------
# HELFERFUNKTIONEN
# ---------------------------------------------------------
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
      "telegram_ok": telegram_connected,
      "timestamp": time.time(),
  }

  try:
    with open(STATUS_FILE, "w") as f:
      json.dump(status_data, f)
  except Exception as e:
    print(f"Fehler beim Schreiben von status.json: {e}")


# ---------------------------------------------------------
# GPS CALLBACKS
# ---------------------------------------------------------
def on_location(**kwargs):
  global last_lat, last_lon, total_km, is_shift_active

  lat = kwargs.get("lat")
  lon = kwargs.get("lon")

  if lat and lon:
    if is_shift_active:
      if last_lat is not None and last_lon is not None:
        dist = calc_distance(last_lat, last_lon, lat, lon)
        if dist < 5.0:
          total_km += dist

      last_lat = lat
      last_lon = lon

    write_status(lat=lat, lon=lon)


def on_status(stype, status):
  print(f"GPS-Status-Event: {stype} - {status}")


# ---------------------------------------------------------
# MAIN EVENT LOOP
# ---------------------------------------------------------
if __name__ == "__main__":
  if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    telegram_connected = send_telegram_message(
        "🚛 *LKW Tracker Dienst gestartet*\nSystem ist bereit."
    )

  write_status()

  try:
    gps.configure(on_location=on_location, on_status=on_status)
    gps.start(minTime=1000, minDistance=3)
    print("GPS erfolgreich gestartet")
  except Exception as e:
    print(f"GPS-Initialisierungsfehler: {e}")

  while True:
    try:
      if os.path.exists(COMMAND_FILE):
        with open(COMMAND_FILE, "r") as f:
          cmd_data = json.load(f)

        cmd = cmd_data.get("command")

        if cmd == "START" and not is_shift_active:
          is_shift_active = True
          last_lat = None
          last_lon = None
          send_telegram_message("▶️ *Schicht gestartet!* Gute Fahrt.")
          write_status()

        elif cmd == "STOP" and is_shift_active:
          is_shift_active = False
          send_telegram_message(
              f"⏹ *Schicht beendet!*\nGesamtdistanz: {round(total_km, 2)} km"
          )
          write_status()

        os.remove(COMMAND_FILE)
    except Exception as e:
      print(f"Fehler in Befehlsschleife: {e}")

    time.sleep(1)
