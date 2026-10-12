import sys
import traceback
import os

# Automatischer Crash-Logger für die Haupt-App
def global_exception_handler(exc_type, exc_value, exc_tb):
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        log_path = os.path.join(os.getcwd(), "crash_log.txt")
        with open(log_path, "w") as f:
            f.write(error_msg)
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = global_exception_handler

import sqlite3
import datetime
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from plyer import gps
import requests

KV = '''
MDScreen:
    md_bg_color: 0.1, 0.1, 0.1, 1

    MDBoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15

        # Titel / Header
        MDBoxLayout:
            size_hint_y: None
            height: "50dp"
            MDLabel:
                text: "LKW Smart-GPS & Arbeitszeit Tracker"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                font_style: "H6"
                halign: "center"

        # Hauptbereich: 2 Spalten (Links: Steuerung, Rechts: Status & Logs)
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: 20

            # Linke Spalte: Schicht-Steuerung
            MDBoxLayout:
                orientation: 'vertical'
                spacing: 15
                
                MDRaisedButton:
                    text: "GPS Tracking Starten"
                    size_hint_x: 1
                    on_press: app.start_gps_tracking()
                    md_bg_color: 0.2, 0.6, 0.8, 1

                MDRaisedButton:
                    text: "Schicht Starten"
                    size_hint_x: 1
                    on_press: app.start_shift()
                    md_bg_color: 0.2, 0.7, 0.2, 1

                MDRaisedButton:
                    text: "Pause Machen"
                    size_hint_x: 1
                    on_press: app.start_break()
                    md_bg_color: 0.8, 0.6, 0.1, 1

                MDRaisedButton:
                    text: "Schicht Beenden"
                    size_hint_x: 1
                    on_press: app.end_shift()
                    md_bg_color: 0.8, 0.2, 0.2, 1

                MDRaisedButton:
                    text: "An Telegram senden"
                    size_hint_x: 1
                    on_press: app.send_to_telegram()
                    md_bg_color: 0.1, 0.5, 0.8, 1

            # Rechte Spalte: Info / Status-Anzeige
            MDBoxLayout:
                orientation: 'vertical'
                padding: 10
                md_bg_color: 0.15, 0.15, 0.15, 1
                
                MDLabel:
                    id: status_label
                    text: "Status: Bereit\\nGPS: Inaktiv\\nLetzte Bewegung: Keine"
                    theme_text_color: "Custom"
                    text_color: 0.9, 0.9, 0.9, 1
                    halign: "left"
                    valign: "top"
'''

class LKWTrackerApp(MDApp):
    def build(self):
        self.init_db()
        self.is_moving = True
        self.stopped_since = None
        self.last_lat = None
        self.last_lon = None
        return Builder.load_string(KV)

    def init_db(self):
        self.conn = sqlite3.connect("lkw_tracker.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                gps_data TEXT
            )
        ''')
        self.conn.commit()

    def log_event(self, event_type, details=""):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO work_logs (timestamp, event_type, gps_data) VALUES (?, ?, ?)", 
                            (now, event_type, details))
        self.conn.commit()
        self.root.ids.status_label.text = f"Status: {event_type}\nZeit: {now}\nInfo: {details}"

    def start_gps_tracking(self):
        try:
            gps.configure(on_location=self.on_gps_location, on_status=self.on_gps_status)
            gps.start(minTime=1000, minDistance=5)
            self.root.ids.status_label.text = "Status: GPS-Tracking aktiv..."
        except NotImplementedError:
            self.root.ids.status_label.text = "Status: GPS auf diesem Gerät nicht verfügbar."

    def on_gps_status(self, general_status, status_message):
        print(f"GPS Status: {general_status} - {status_message}")

    def on_gps_location(self, **kwargs):
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        speed = kwargs.get('speed', 0) or 0
        speed_kmh = speed * 3.6
        now = datetime.datetime.now()

        if speed_kmh < 5.0:
            if self.is_moving:
                if self.stopped_since is None:
                    self.stopped_since = now
                else:
                    if (now - self.stopped_since).total_seconds() > 180:
                        self.is_moving = False
                        self.log_event("Automatische Ankunft / Standzeit", f"Lat: {lat:.4f}, Lon: {lon:.4f}")
        else:
            if speed_kmh > 10.0 and not self.is_moving:
                self.is_moving = True
                self.stopped_since = None
                self.log_event("Automatische Weiterfahrt", f"Geschwindigkeit: {speed_kmh:.1f} km/h")
            elif self.is_moving:
                self.stopped_since = None

        self.last_lat = lat
        self.last_lon = lon

    def start_shift(self):
        self.log_event("Schicht gestartet")

    def start_break(self):
        self.log_event("Pause begonnen")

    def end_shift(self):
        self.log_event("Schicht beendet")

    def send_to_telegram(self):
        TOKEN = "DEIN_TELEGRAM_BOT_TOKEN"
        CHAT_ID = "DEINE_CHAT_ID"
        
        try:
            self.cursor.execute("SELECT timestamp, event_type, gps_data FROM work_logs ORDER BY id DESC LIMIT 5")
            rows = self.cursor.fetchall()
            message = "🚚 *LKW Auto-Protokoll*:\n" + "\n".join([f"{r[0]} - *{r[1]}* ({r[2]})" for r in rows])
            
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
            response = requests.post(url, json=payload, timeout=5)
            
            if response.status_code == 200:
                self.root.ids.status_label.text = "Status: Erfolgreich an Telegram gesendet!"
            else:
                self.root.ids.status_label.text = "Status: Telegram-Fehler beim Senden."
        except Exception as e:
            self.root.ids.status_label.text = f"Status: Fehler ({str(e)})"

if __name__ == '__main__':
    LKWTrackerApp().run()
