import time
import os
import sqlite3
import datetime
import requests
from jnius import autoclass
from kivy.utils import platform

TELEGRAM_BOT_TOKEN = "DEIN_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "DEINE_CHAT_ID"

if platform == 'android':
    PythonService = autoclass('org.kivy.android.PythonService')
    service = PythonService.mService
    service.setAutoRestartService(True)

def get_db_connection():
    if platform == 'android':
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity
        files_dir = context.getFilesDir().getAbsolutePath()
    else:
        files_dir = os.getcwd()
    
    db_path = os.path.join(files_dir, "lkw_tracker.db")
    return sqlite3.connect(db_path)

def log_event_to_db(event_type, details):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO work_logs (timestamp, event_type, gps_data) VALUES (?, ?, ?)", 
                       (now, event_type, details))
        conn.commit()
        conn.close()
        
        # Sofortmeldung bei wichtigen Stopps/Staus an Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"🚚 *LKW Update*: {event_type}\n📍 {details}\n⏰ {now}", "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Service Log Fehler: {e}")

def main():
    log_event_to_db("Hintergrunddienst", "Service im Hintergrund gestartet.")
    
    is_moving = True
    stopped_since = None

    try:
        from plyer import gps
        def on_gps_location(**kwargs):
            nonlocal is_moving, stopped_since
            lat = kwargs.get('lat')
            lon = kwargs.get('lon')
            speed = kwargs.get('speed', 0) or 0
            speed_kmh = speed * 3.6
            now = datetime.datetime.now()

            if speed_kmh < 5.0:
                if is_moving:
                    if stopped_since is None:
                        stopped_since = now
                    else:
                        if (now - stopped_since).total_seconds() > 180:
                            is_moving = False
                            log_event_to_db("🛑 Stau / Haltepunkt erkannt", f"Lat: {lat:.4f}, Lon: {lon:.4f}")
            else:
                if speed_kmh > 10.0 and not is_moving:
                    is_moving = True
                    stopped_since = None
                    log_event_to_db("🚀 Fahrt fortgesetzt", f"Geschwindigkeit: {speed_kmh:.1f} km/h")
                elif is_moving:
                    stopped_since = None

        gps.configure(on_location=on_gps_location)
        gps.start(minTime=2000, minDistance=10)
    except Exception as e:
        print(f"Hintergrund GPS Fehler: {e}")

    while True:
        time.sleep(30)

if __name__ == '__main__':
    main()
