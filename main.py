import kivy
kivy.require('2.3.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.utils import platform
import subprocess
import datetime
import os
import sqlite3
import requests

class LKWTrackerApp(App):
    def build(self):
        self.title = "LKW Arbeitszeit Tracker"
        self.init_db()
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        title_label = Label(
            text="🚚 LKW GPS & Arbeitszeit-Tracker (Pro)",
            size_hint_y=None,
            height="40dp",
            font_size='18sp'
        )
        layout.add_widget(title_label)
        
        self.log_output = TextInput(
            text="System auf modernem Stand initialisiert...\n",
            readonly=True,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(0, 1, 0, 1)
        )
        layout.add_widget(self.log_output)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height="50dp", spacing=10)
        
        btn_start = Button(text="Schicht Starten", background_color=(0.2, 0.7, 0.2, 1))
        btn_start.bind(on_press=self.start_shift)
        btn_layout.add_widget(btn_start)
        
        btn_end = Button(text="Schicht Beenden", background_color=(0.8, 0.2, 0.2, 1))
        btn_end.bind(on_press=self.end_shift)
        btn_layout.add_widget(btn_end)
        
        layout.add_widget(btn_layout)
        
        self.request_permissions_and_service()
        
        return layout

    def init_db(self):
        try:
            db_path = os.path.join(self.user_data_dir, "lkw_tracker.db")
            self.conn = sqlite3.connect(db_path)
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
        except Exception as e:
            print(f"DB Init Fehler: {e}")

    def log_event(self, event_type, details=""):
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("INSERT INTO work_logs (timestamp, event_type, gps_data) VALUES (?, ?, ?)", 
                                (now, event_type, details))
            self.conn.commit()
            self.log_output.text += f"[{now}] {event_type}\n"
        except Exception as e:
            print(f"Log Fehler: {e}")

    def request_permissions_and_service(self):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.ACCESS_FINE_LOCATION,
                    Permission.ACCESS_COARSE_LOCATION,
                    Permission.FOREGROUND_SERVICE,
                    Permission.FOREGROUND_SERVICE_LOCATION
                ])
                
                from jnius import autoclass
                PythonService = autoclass('org.kivy.android.PythonService')
                mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
                PythonService.start(mActivity, '')
                self.log_output.text += "Hintergrunddienst erfolgreich gestartet.\n"
            except Exception as e:
                self.log_output.text += f"Rechte/Dienst-Fehler: {str(e)}\n"

    def start_shift(self, instance):
        self.log_event("Schicht gestartet", "Tour aktiv")

    def end_shift(self, instance):
        self.log_event("Schicht Beendet", "Bericht wird gesendet")
        self.send_telegram_report()

    def send_telegram_report(self):
        TOKEN = "DEIN_TELEGRAM_BOT_TOKEN"
        CHAT_ID = "DEINE_CHAT_ID"
        try:
            self.cursor.execute("SELECT timestamp, event_type, gps_data FROM work_logs ORDER BY id DESC LIMIT 5")
            rows = self.cursor.fetchall()
            
            message = "📋 *LKW Tagesbericht (Modern)*\n\n" + "\n".join([f"• {r[0]} - *{r[1]}*" for r in rows])
            
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
            requests.post(url, json=payload, timeout=5)
            self.log_output.text += "Telegram Bericht erfolgreich gesendet!\n"
        except Exception as e:
            self.log_output.text += f"Telegram Fehler: {str(e)}\n"

if __name__ == '__main__':
    LKWTrackerApp().run()
