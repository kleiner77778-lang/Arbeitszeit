import sys
import traceback
import os
import time
import sqlite3
import datetime
from kivy.utils import platform

# Automatischer Crash-Logger für den Hintergrunddienst
def service_exception_handler(exc_type, exc_value, exc_tb):
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        log_path = os.path.join(os.getcwd(), "service_crash.txt")
        with open(log_path, "w") as f:
            f.write(error_msg)
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = service_exception_handler

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
        print(f"DB Fehler: {e}")

def main():
    log_to_db("Dienst", "Hintergrunddienst gestartet")
    
    if platform == 'android':
        try:
            from plyer import gps
            from jnius import autoclass
            
            PythonService = autoclass('org.kivy.android.PythonService')
            service = PythonService.mService
            if service:
                service.setAutoRestartService(True)
            
            def on_gps_location(**kwargs):
                lat = kwargs.get('lat', 0)
                lon = kwargs.get('lon', 0)
                speed = kwargs.get('speed', 0) or 0
                if (speed * 3.6) < 5.0:
                    log_to_db("Standzeit / Stau", f"Lat: {lat:.4f}, Lon: {lon:.4f}")

            gps.configure(on_location=on_gps_location)
            gps.start(minTime=1000, minDistance=5)
        except Exception as e:
            log_to_db("GPS Initialisierungsfehler", str(e))

    while True:
        time.sleep(15)

if __name__ == '__main__':
    main()
