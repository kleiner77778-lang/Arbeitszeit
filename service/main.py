import json
import time
import os
from plyer import gps

print("LkwService gestartet")

SERVER_URL = "https://example.com/api/location"
STATUS_FILE = "status.json"


def save_status(lat, lon):
  try:
    data = {
        "lat": lat,
        "lon": lon,
        "timestamp": time.time(),
        "status": "GPS aktiv",
    }
    with open(STATUS_FILE, "w") as f:
      json.dump(data, f)
  except Exception as e:
    print(f"Fehler beim Speichern des Status: {e}")


def send_location(lat, lon):
  save_status(lat, lon)
  try:
    data = {"lat": lat, "lon": lon, "timestamp": time.time()}
    print(f"Standort gesendet: Lat={lat}, Lon={lon}")
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
