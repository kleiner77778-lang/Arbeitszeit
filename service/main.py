import json
import os
import time
from plyer import gps

# Globale Variablen
is_shift_active = False
last_lat = None
last_lon = None
total_km = 0.0
STATUS_FILE = "status.json"
COMMAND_FILE = "command.json"


def on_location(**kwargs):
  global last_lat, last_lon, total_km, is_shift_active
  lat = kwargs.get("lat")
  lon = kwargs.get("lon")

  if lat and lon and is_shift_active:
    if last_lat is not None and last_lon is not None:
      dist = calc_distance(last_lat, last_lon, lat, lon)
      if dist < 5.0:  # Unplausible Sprünge filtern
        total_km += dist

    last_lat = lat
    last_lon = lon

    # Status für die App schreiben
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


def calc_distance(lat1, lon1, lat2, lon2):
  # Einfache Distanzberechnung (kann deine bestehende sein)
  import math

  R = 6371.0
  dlat = math.radians(lat2 - lat1)
  dlon = math.radians(lon2 - lon1)
  a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(
      math.radians(lat2)
  ) * math.sin(dlon / 2) ** 2
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  return R * c


if __name__ == "__main__":
  # GPS initialisieren
  try:
    gps.configure(on_location=on_location, on_status=on_status)
    gps.start(minTime=1000, minDistance=5)
    print("GPS gestartet im Hintergrund")
  except Exception as e:
    print(f"GPS Fehler: {e}")

  # WICHTIG: Die Endlosschleife hält den Dienst am Leben und liest Befehle aus der App!
  while True:
    try:
      if os.path.exists(COMMAND_FILE):
        with open(COMMAND_FILE, "r") as f:
          cmd_data = json.load(f)
          if cmd_data.get("command") == "START":
            is_shift_active = True
          elif cmd_data.get("command") == "STOP":
            is_shift_active = False
            # Eventuell hier Telegram-Bericht senden
    except:
        pass

    time.sleep(1)
