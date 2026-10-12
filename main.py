import kivy
kivy.require('2.1.0')

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

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField

class LKWTrackerApp(MDApp):
    def build(self):
        self.title = "LKW Arbeitszeit Tracker"
        self.init_db()
        
        # Hauptlayout im Querformat-tauglichen Design
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Titel
        title_label = Label(
            text="🚚 LKW GPS & Arbeitszeit-Tracker",
            size_hint_y=None,
            height="40dp",
            font_size='18sp',
            halign='center'
        )
        layout.add_widget(title_label)
        
        # Status / Logcat Textfeld
        self.log_output = TextInput(
            text="App gestartet. Initialisiere...\n",
            readonly=True,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(0, 1, 0, 1)  # Grüner Matrix-Look
        )
        layout.add_widget(self.log_output)
        
        # Button-Leiste unten
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height="50dp", spacing=10)
        
        btn_start_shift = Button(
            text="Schicht Starten",
            background_color=(0.2, 0.7, 0.2, 1)
        )
        btn_start_shift.bind(on_press=self.start_shift)
        btn_layout.add_widget(btn_start_shift)
        
        btn_end_shift = Button(
            text="Schicht Beenden",
            background_color=(0.8, 0.2, 0.2, 1)
        )
        btn_end_shift.bind(on_press=lambda x: self.end_shift_prompt())
        btn_layout.add_widget(btn_end_shift)
        
        btn_logs = Button(
            text="Logs aktualisieren",
            background_color=(0.2, 0.6, 0.8, 1)
        )
        btn_logs.bind(on_press=self.fetch_logs)
        btn_layout.add_widget(btn_logs)
        
        layout.add_widget(btn_layout)
        
        # Berechtigungen und Hintergrunddienst starten
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
            self.log_output.text += f"[{now}] {event_type}: {details}\n"
        except Exception as e:
            print(f"Log Fehler: {e}")

    def request_permissions_and_service(self):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.ACCESS_FINE_LOCATION,
                    Permission.ACCESS_COARSE_LOCATION,
                    Permission.FOREGROUND_SERVICE
                ])
                
                # Hintergrunddienst starten
                from jnius import autoclass
                PythonService = autoclass('org.kivy.android.PythonService')
                mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
                PythonService.start(mActivity, '')
                self.log_output.text += "Hintergrunddienst erfolgreich gestartet.\n"
            except Exception as e:
                self.log_output.text += f"Fehler bei Start/Rechten: {str(e)}\n"
        else:
            self.log_output.text += "Läuft im Emulator / PC (Kein Android).\n"

    def start_shift(self, instance):
        self.log_event("Schicht gestartet", "Bereit für Tour")

    def end_shift_prompt(self):
        # Eingabefenster für die Pause beim Schichtende
        self.pause_input = MDTextField(
            hint_text="Pause in Minuten (z.B. 30)",
            input_filter="int",
            text="30"
        )
        
        self.dialog = MDDialog(
            title="Schicht beenden & Pause eintragen",
            text="Bitte gib an, wie viel Minuten Pause du insgesamt gemacht hast:",
            type="custom",
            content_style="box",
            content=self.pause_input,
            buttons=[
                MDFlatButton(
                    text="ABBRECHEN",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="BERECHNEN & SENDEN",
                    on_release=self.process_end_shift
                ),
            ],
        )
        self.dialog.open()

    def process_end_shift(self, instance):
        pause_min = int(self.pause_input.text) if self.pause_input.text else 0
        self.dialog.dismiss()
        
        self.log_event("Schicht Beendet", f"Nachträgliche Pause: {pause_min} Minuten")
        self.generate_final_report_and_send(pause_min)

    def generate_final_report_and_send(self, pause_minutes):
        TOKEN = "DEIN_TELEGRAM_BOT_TOKEN"
        CHAT_ID = "DEINE_CHAT_ID"
        
        try:
            self.cursor.execute("SELECT timestamp, event_type, gps_data FROM work_logs ORDER BY id DESC LIMIT 10")
            rows = self.cursor.fetchall()
            
            message = f"📋 *LKW Tages- & Arbeitszeitbericht*\n"
            message += f"☕ Abgezogene Pause: {pause_minutes} Minuten\n\n"
            message += "Protokoll:\n" + "\n".join([f"• {r[0]} - *{r[1]}* ({r[2]})" for r in rows])
            
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
            requests.post(url, json=payload, timeout=5)
            
            self.log_output.text += "Bericht erfolgreich an Telegram gesendet!\n"
        except Exception as e:
            self.log_output.text += f"Telegram-Fehler: {str(e)}\n"

    def fetch_logs(self, instance):
        if platform == 'android':
            try:
                cmd = ['logcat', '-d', '-s', 'python:V', 'AndroidRuntime:E']
                output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
                lines = output.splitlines()
                recent_logs = "\n".join(lines[-20:]) if len(lines) > 20 else output
                self.log_output.text = recent_logs if recent_logs.strip() else "Keine neuen Logs im Puffer."
            except Exception as e:
                self.log_output.text = f"Konnte Logcat nicht abrufen: {str(e)}"
        else:
            self.log_output.text = "Logcat ist nur auf dem Android-Gerät verfügbar."

if __name__ == '__main__':
    LKWTrackerApp().run()
