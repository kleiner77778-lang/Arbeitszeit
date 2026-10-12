import time
import sqlite3
import datetime
from kivy.utils import platform
from plyer import gps

def log_to_db(event_type, details):
    try:
        conn = sqlite3.connect("lkw_tracker.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                gps_data TEXT
            )
        ''')
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO work_logs (timestamp, event_type, gps_data) VALUES (?, ?, ?)", 
                            (now, event_type, details))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Fehler im Hintergrund: {e}")

last_speed = 0
stopped_time = None
is_moving = True

def on_gps_location(**kwargs):
    global last_speed, stopped_time, is_moving
    speed = kwargs.get('speed', 0)
    if speed is None:
        speed = 0
    speed_kmh = speed * 3.6
    lat = kwargs.get('lat', 0)
    lon = kwargs.get('lon', 0)
    now = datetime.datetime.now()

    # Stau- und Standzeit-Erkennung im Hintergrund
    if speed_kmh < 5.0:
        if is_moving:
            if stopped_time is None:
                stopped_time = now
            else:
                if (now - stopped_time).total_seconds() > 180: # Länger als 3 Minuten unter 5 km/h
                    is_moving = False
                    log_to_db("Automatische Ankunft / Standzeit", f"Lat: {lat:.4f}, Lon: {lon:.4f}")
    else:
        if speed_kmh > 10.0 and not is_moving:
            is_moving = True
            stopped_time = None
            log_to_db("Automatische Weiterfahrt", f"Geschwindigkeit: {speed_kmh:.1f} km/h")
        elif is_moving:
            stopped_time = None

def main():
    log_to_db("Hintergrunddienst", "GPS-Dienst gestartet")
    
    if platform == 'android':
        from jnius import autoclass
        # Aktiviert den Foreground Service, damit Android die App nicht schlafen legt
        PythonService = autoclass('org.kivy.android.PythonService')
        service = PythonService.mService
        service.setAutoRestartService(True)
        
        try:
            gps.configure(on_location=on_gps_location)
            gps.start(minTime=1000, minDistance=5)
        except Exception as e:
            log_to_db("GPS Fehler", str(e))

    while True:
        time.sleep(10)

if __name__ == '__main__':
    main()
