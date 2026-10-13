import kivy
kivy.require('2.3.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import platform
import subprocess
import datetime
import os
import sqlite3
import requests

class LKWTrackerApp(App):
    # Telegram Konfiguration fest hinterlegt
    TELEGRAM_TOKEN = "8413301731:AAHRM32xA2CkAkrrcf85sqYDR88YK14k3bs"
    TELEGRAM_CHAT_ID = "8941361378"

    def build(self):
        self.title = "LKW Arbeitszeit Tracker"
        self.init_db()
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        title_label = Label(
            text="🚚 LKW GPS & Arbeitszeit-Tracker",
            size_hint_y=None,
            height="35dp",
            font_size='18sp'
        )
        layout.add_widget(title_label)
        
        self.log_output = TextInput(
            text="App gestartet. System bereit...\n",
            readonly=True,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(0, 1, 0, 1)
        )
        layout.add_widget(self.log_output)
        
        # Button-Leiste
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height="50dp", spacing=10)
        
        btn_start = Button(text="Schicht Starten", background_color=(0.2, 0.7, 0.2, 1))
        btn_start.bind(on_press=self.start_shift)
        btn_layout.add_widget(btn_start)
        
        btn_perms = Button(text="Rechte & GPS", background_color=(0.8, 0.6, 0.1, 1))
        btn_perms.bind(on_press=self.request_permissions_and_service)
        btn_layout.add_widget(btn_perms)
        
        btn_logcat = Button(text="Logcat senden", background_color=(0.2, 0.5, 0.8, 1))
        btn_logcat.bind(on_press=self.send_logcat_to_telegram)
        btn_layout.add_widget(btn_logcat)
        
        btn_end = Button(text="Schicht Beenden", background_color=(0.8, 0.2, 0.2, 1))
        btn_end.bind(on_press=self.end_shift_prompt)
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

    def request_permissions_and_service(self, instance=None):
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
                self.log_output.text += "Berechtigungen angefordert & Dienst gestartet.\n"
            except Exception as e:
                self.log_output.text += f"Rechte-Fehler: {str(e)}\n"
        else:
            self.log_output.text += "Läuft im PC-Modus (Kein Android).\n"

    def start_shift(self, instance):
        self.log_event("Schicht gestartet", "Tour aktiv")

    def send_logcat_to_telegram(self, instance):
        if platform == 'android':
            try:
                cmd = ['logcat', '-d', '-s', 'python:V', 'AndroidRuntime:E']
                output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
                lines = output.splitlines()
                log_text = "\n".join(lines[-30:]) if len(lines) > 30 else output
            except Exception as e:
                log_text = f"Konnte Logcat nicht lesen: {str(e)}"
        else:
            log_text = "Logcat ist nur auf dem Android-Gerät verfügbar."
            
        try:
            url = f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/sendMessage"
            payload = {
                "chat_id": self.TELEGRAM_CHAT_ID, 
                "text": f"🛠 *LKW Logcat Debug-Report*\n```\n{log_text[-3500:]}\n```", 
                "parse_mode": "Markdown"
            }
            requests.post(url, json=payload, timeout=5)
            self.log_output.text += "Logcat an Telegram gesendet!\n"
        except Exception as e:
            self.log_output.text += f"Sende-Fehler: {str(e)}\n"

    def end_shift_prompt(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text="Pause in Minuten eingeben:"))
        
        self.pause_input = TextInput(text="30", input_filter="int", multiline=False, size_hint_y=None, height="40dp")
        content.add_widget(self.pause_input)
        
        btn_box = BoxLayout(orientation='horizontal', size_hint_y=None, height="40dp", spacing=10)
        btn_ok = Button(text="Berechnen & Senden", background_color=(0.2, 0.7, 0.2, 1))
        btn_cancel = Button(text="Abbrechen", background_color=(0.8, 0.2, 0.2, 1))
        
        btn_box.add_widget(btn_ok)
        btn_box.add_widget(btn_cancel)
        content.add_widget(btn_box)
        
        self.popup = Popup(title="Schicht beenden & Pause", content=content, size_hint=(0.8, 0.6))
        
        btn_ok.bind(on_press=self.process_end_shift)
        btn_cancel.bind(on_press=lambda x: self.popup.dismiss())
        self.popup.open()

    def process_end_shift(self, instance):
        try:
            pause_min = int(self.pause_input.text) if self.pause_input.text else 0
        except ValueError:
            pause_min = 0
            
        self.popup.dismiss()
        self.log_event("Schicht Beendet", f"Nachträgliche Pause: {pause_min} Minuten")
        self.generate_final_report_and_send(pause_min)

    def generate_final_report_and_send(self, pause_minutes):
        try:
            self.cursor.execute("SELECT timestamp, event_type, gps_data FROM work_logs ORDER BY id DESC LIMIT 10")
            rows = self.cursor.fetchall()
            
            message = f"📋 *LKW Tages- & Arbeitszeitbericht*\n"
            message += f"☕ Abgezogene Pause: {pause_minutes} Minuten\n\n"
            message += "Protokoll:\n" + "\n".join([f"• {r[0]} - *{r[1]}* ({r[2]})" for r in rows])
            
            url = f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": self.TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
            requests.post(url, json=payload, timeout=5)
            
            self.log_output.text += "Schichtbericht an Telegram gesendet!\n"
        except Exception as e:
            self.log_output.text += f"Telegram-Fehler: {str(e)}\n"

    def on_stop(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == '__main__':
    LKWTrackerApp().run()
