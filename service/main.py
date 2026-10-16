import json
import math
import os
import time
from plyer import gps
import requests

print("LkwService gestartet")

STATUS_FILE = "status.json"
COMMAND_FILE = "command.json"
HISTORY_FILE = "track_history.json"

TELEGRAM_TOKEN = "8413301731:AAHRM32xA2CkAkrrcf85sqYDR88YK14k3bs"
TELEGRAM_CHAT_ID = "8941361378"

# Statusvariablen für den Dienst
is_shift_active = False
shift_start_time = 0.0
total_km = 0.0
last_lat = None
last_lon = None


def send_telegram(message):
  try:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, json=payload, timeout=5)
    print(f"Telegram gesendet, Status: {response.status_code}")
  except Exception as e:
    print(f"Fehler beim Telegram-Versand: {e}")


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


def check_commands():
  global is_shift_active, shift_start_time, total_km, last_lat, last_lon
  if os.path.exists(COMMAND_FILE):
    try:
      with open(COMMAND_FILE, "r") as f:
        data = json.load(f)
        cmd = data.get("command")
        pause_min = data.get("pause_minutes", 0)

        if cmd == "START" and not is_shift_active:
          is_shift_active = True
          shift_start_time = time.time()
          total_km = 0.0
          last_lat = None
          last_lon = None
          send_telegram(
              "🚛 Schicht gestartet!\nGPS-Tracking und Kilometererfassung"
              " aktiv."
          )
          print("Schicht gestartet per Befehl.")

        elif cmd == "STOP" and is_shift_active:
          is_shift_active = False
          duration_seconds = time.time() - shift_start_time
          duration_hours = duration_seconds / 3600.0

          msg = (
              f"🛑 Feierabend-Bericht:\n"
              f"⏱️ Schichtdauer: {duration_hours:.2f} Stunden\n"
              f"☕ Eingetragene Pause: {pause_min} Minuten\n"
              f"🛣️ Gefahrene Strecke: {total_km:.2f} km"
          )
          send_telegram(msg)
          print("Schicht beendet per Befehl.")

      os.remove(COMMAND_FILE)
    except Exception as e:
      print(f"Fehler beim Verarbeiten von command.json: {e}")


def on_location(**kwargs):
  global last_lat, last_lon, total_km
  lat = kwargs.get("lat")
  lon = kwargs.get("lon")

  if lat and lon and is_shift_active:
    if last_lat is not None and last_lon is not None:
      dist = calc_distance(last_lat, last_lon, lat, lon)
      # Unplausible GPS-Sprünge (> 5km auf einmal) ignorieren
      if dist < 5.0:
        total_km += dist

    last_lat = lat
    last_lon = lon

    # Status für die App aktualisieren
    try:
      status_data = {
          "status": "Schicht aktiv",
          "lat": lat,
          "lon": lon,
          "km": total_km,
          "timestamp": time.time(),
      }
      with open(STATUS_FILE, "w") as f:
        json.dump(status_data, f)
    except:
      pass


def on_status(stype, status):
  print(f"GPS Status: {stype} - {status}")


try:
  gps.configure(on_location=on_location, on_status=on_status)
  gps.start(minTime=1000, minDistance=5)
  print("GPS gestartet im Hintergrund")
except Exception as e:
  print(f"Fehler beim Starten von GPS: {e}")

# Endlosschleife zur Befehlsprüfung
while True:
  check_commands()
  time.sleep(2)
