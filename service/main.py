import time
from plyer import gps

print("LkwService gestartet")


def on_location(**kwargs):
  # Hier kommt später deine Logik hin, wenn GPS-Daten empfangen werden
  lat = kwargs.get("lat")
  lon = kwargs.get("lon")
  print(f"Standort erhalten: Lat={lat}, Lon={lon}")


def on_status(stype, status):
  print(f"GPS Status: {stype} - {status}")


try:
  gps.configure(on_location=on_location, on_status=on_status)
  gps.start(minTime=1000, minDistance=1)
  print("GPS gestartet")
except Exception as e:
  print(f"Fehler beim Starten von GPS: {e}")

while True:
  # Der Dienst läuft im Hintergrund weiter
  time.sleep(10)
