import json
import time
import os
from plyer import gps

print("LkwService gestartet")

SERVER_URL = "https://example.com/api/location"
STATUS_FILE = "status.json"
HISTORY_FILE = "track_history.json"


def save_to_history(lat, lon):
  try:
    history = []
    if os.path.exists(HISTORY_FILE):
      with open(HISTORY_FILE, "r") as f:
        try:
          history = json.load(f)
        except:
          history = []

    # Neuen Punkt anhängen (max. letzte 100 Punkte behalten)
    history.append({"lat": lat, "lon": lon, "timestamp": time.time()})
    if len(history) > 100:
      history.pop(0)

    with open(HISTORY_FILE, "w") as f:
      json.dump(history, f)
  except Exception as e:
    print(f"Fehler beim Speichern der Historie: {e}")


def save_status(lat, lon):
  try:
    data = {
        "lat": lat,
        "lon": lon,
        "timestamp": time.time(),
        "status": "GPS aktiv & loggt",
    }
    with open(STATUS_FILE, "w") as f:
      json.dump(data, f)
  except Exception as e:
    print(f"Fehler beim Speichern des Status: {e}")


def send_location(lat, lon):
  save_status(lat, lon)
  save_to_history(lat, lon)
  try:
    data = {"lat": lat, "lon": lon, "timestamp": time.time()}
    # response = requests.post(SERVER_URL, json=data, timeout=5)
    print(f"Standort verarbeitet & gespeichert: Lat={lat}, Lon={lon}")
  except Exception as e:
    print(f"Fehler beim Senden: {e}")


def on_location(**kwargs):
  lat = kwargs.get("lat")
  lon = kwargs.get("lon")
  if lat and lon:
    send_location(lat, lon)


def on_status(stype, status):
  print(f"GPS Status: {stype} - {status}")


try:
  gps.configure(on_location=on_location, on_status=on_status)
  gps.start(minTime=1000, minDistance=1)
  print("GPS gestartet")
except Exception as e:
  print(f"Fehler beim Starten von GPS: {e}")

# Initialen Status schreiben
try:
  with open(STATUS_FILE, "w") as f:
    json.dump(
        {
            "lat": 0.0,
            "lon": 0.0,
            "timestamp": time.time(),
            "status": "Dienst gestartet",
        },
        f,
    )
except:
  pass

while True:
  time.sleep(10)
