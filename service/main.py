import time
import requests
from plyer import gps

print("LkwService gestartet")

# Trage hier deine echte Server-URL ein
SERVER_URL = "https://example.com/api/location"


def send_location(lat, lon):
  try:
    data = {"lat": lat, "lon": lon, "timestamp": time.time()}
    response = requests.post(SERVER_URL, json=data, timeout=5)
    print(f"Standort gesendet: Lat={lat}, Lon={lon}, Status={response.status_code}")
  except requests.exceptions.RequestException as e:
    print(f"Netzwerkfehler beim Senden: {e}")
  except Exception as e:
    print(f"Unerwarteter Fehler beim Senden: {e}")


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

while True:
  time.sleep(10)
