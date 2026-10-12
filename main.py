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

class LKWTrackerApp(App):
    def build(self):
        # Hauptlayout im Querformat-tauglichen Design
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Titel
        title_label = Label(
            text="🚚 LKW GPS & Live-Logcat Tracker",
            size_hint_y=None,
            height="40dp",
            font_size='18sp',
            halign='center'
        )
        layout.add_widget(title_label)
        
        # Status / Logcat Textfeld (zeigt dir immer direkt an, was passiert)
        self.log_output = TextInput(
            text="App gestartet. Initialisiere...\n",
            readonly=True,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(0, 1, 0, 1)  # Grüner Matrix-Look
        )
        layout.add_widget(self.log_output)
        
        # Button-Leiste unten
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height="50dp", spacing=10)
        
        btn_logs = Button(
            text="Logs aktualisieren",
            background_color=(0.2, 0.6, 0.8, 1)
        )
        btn_logs.bind(on_press=self.fetch_logs)
        btn_layout.add_widget(btn_logs)
        
        btn_gps = Button(
            text="GPS Starten",
            background_color=(0.2, 0.7, 0.2, 1)
        )
        btn_gps.bind(on_press=self.start_gps_tracking)
        btn_layout.add_widget(btn_gps)
        
        layout.add_widget(btn_layout)
        
        # Berechtigungen direkt beim Start anfordern (mit kleiner Verzögerung/Sicherheit)
        self.request_permissions_on_startup()
        
        return layout

    def request_permissions_on_startup(self):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.ACCESS_FINE_LOCATION,
                    Permission.ACCESS_COARSE_LOCATION
                ])
                self.log_output.text += f"[{datetime.datetime.now().strftime('%H:%M:%S সিস্ট')}] Berechtigungen angefragt.\n"
            except Exception as e:
                self.log_output.text += f"Fehler bei Rechte-Anfrage: {str(e)}\n"
        else:
            self.log_output.text += "Läuft im Emulator / PC (Kein Android).\n"

    def fetch_logs(self, instance):
        if platform == 'android':
            try:
                cmd = ['logcat', '-d', '-s', 'python:V', 'AndroidRuntime:E']
                output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
                lines = output.splitlines()
                recent_logs = "\n".join(lines[-25:]) if len(lines) > 25 else output
                self.log_output.text = recent_logs if recent_logs.strip() else "Keine neuen Logs im Puffer."
            except Exception as e:
                self.log_output.text = f"Konnte Logcat nicht abrufen: {str(e)}"
        else:
            self.log_output.text = "Logcat ist nur auf dem Android-Gerät verfügbar."

    def start_gps_tracking(self, instance):
        self.log_output.text += f"[{datetime.datetime.now().strftime('%H:%M:%S')}] GPS-Tracking Button gedrückt.\n"
        try:
            from plyer import gps
            gps.configure(on_location=self.on_gps_location, on_status=self.on_gps_status)
            gps.start(minTime=1000, minDistance=5)
            self.log_output.text += "GPS erfolgreich initialisiert!\n"
        except NotImplementedError:
            self.log_output.text += "GPS wird von diesem Gerät nicht unterstützt.\n"
        except Exception as e:
            self.log_output.text += f"GPS-Fehler: {str(e)}\n"

    def on_gps_status(self, general_status, status_message):
        self.log_output.text += f"GPS Status: {general_status} - {status_message}\n"

    def on_gps_location(self, **kwargs):
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        speed = kwargs.get('speed', 0) or 0
        self.log_output.text += f"GPS Position -> Lat: {lat}, Lon: {lon}, Speed: {speed*3.6:.1f} km/h\n"

if __name__ == '__main__':
    LKWTrackerApp().run()
