from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.utils import platform
import datetime
import requests

# Telegram Zugangsdaten
TELEGRAM_BOT_TOKEN = "8413301731:AAHRM32xA2CkAkrrcf85sqYDR88YK14k3bs"
TELEGRAM_CHAT_ID = "8941361378"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=5)
    except Exception as e:
        print(f"Telegram Fehler: {e}")

class LkwTrackerApp(App):
    def build(self.shift_active, self.start_time, self.total_secs = False, None, 0): # Clean init
        self.shift_active = False
        self.start_time = None
        self.total_secs = 0

        # Hauptlayout
        root = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 1. OBERES FENSTER: Dynamisches Verkehrs- & Stopp-Banner
        self.traffic_banner = Label(
            text='[b]VERKEHRS- & STOPP-INFO[/b]\nKeine Stau- oder Stoppmeldungen aktiv',
            markup=True,
            font_size=15,
            halign='center',
            valign='middle',
            size_hint=(1, 0.2),
            color=(0.2, 1, 0.3, 1) # Startet in sanftem Grün
        )
        self.traffic_banner.bind(size=self.traffic_banner.setter('text_size'))
        root.add_widget(self.traffic_banner)
        
        # 2. Status-Anzeige (Schicht & Timer)
        self.status_label = Label(
            text='Status: Keine Schicht aktiv\nBereit zur Abfahrt',
            markup=True,
            font_size=16,
            halign='center',
            valign='middle',
            size_hint=(1, 0.3)
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        root.add_widget(self.status_label)
        
        # 3. Pausen-Eingabebereich (erscheint nach Schicht-Ende)
        self.pause_box = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.12))
        self.pause_box.opacity = 0
        self.pause_box.disabled = True
        
        self.pause_label = Label(text='Pause (Minuten):', font_size=16, size_hint=(0.6, 1), halign='right')
        self.pause_input = TextInput(text='30', multiline=False, input_filter='int', font_size=18, size_hint=(0.4, 1))
        
        self.pause_box.add_widget(self.pause_label)
        self.pause_box.add_widget(self.pause_input)
        root.add_widget(self.pause_box)
        
        # 4. Zentraler Aktions-Button
        self.btn_action = Button(
            text='SCHICHT STARTEN',
            font_size=20,
            bold=True,
            background_color=(0.1, 0.7, 0.2, 1), 
            size_hint=(1, 0.25)
        )
        self.btn_action.bind(on_press=self.on_button_pressed)
        root.add_widget(self.btn_action)

        # Berechtigungen nach Start anfordern
        if platform == 'android':
            Clock.schedule_once(self.request_android_permissions, 1.5)

        # Timer für Schicht
        Clock.schedule_interval(self.update_timer, 1)
        
        # Test-Update für das Verkehrs-Banner (simuliert Live-Abfrage)
        # Hier kannst du später deine Stau-API oder Telegram-Befehle anbinden
        Clock.schedule_once(lambda dt: self.update_traffic_alert("⚠️ HINWEIS: Strecke frei. Keine Staus gemeldet.", level="normal"), 3)

        return root

    def update_traffic_alert(self, message, level="normal"):
        """Aktualisiert das obere Verkehrsfenster mit Stau- oder Stoppnachrichten"""
        if level == "stau":
            # Warnung bei Stau (Rot/Orange)
            self.traffic_banner.color = (1, 0.4, 0.2, 1)
            self.traffic_banner.text = f"[b]🔴 STAU-WARNUNG[/b]\n{message}"
        elif level == "stop":
            # Wichtige Stoppnachricht (Gelb/Rot)
            self.traffic_banner.color = (1, 0.9, 0.1, 1)
            self.traffic_banner.text = f"[b]🛑 STOPPNACHRICHT[/b]\n{message}"
        else:
            # Normal / Alles frei (Grün)
            self.traffic_banner.color = (0.2, 1, 0.3, 1)
            self.traffic_banner.text = f"[b]VERKEHRS- & STOPP-INFO[/b]\n{message}"

    def request_android_permissions(self, dt):
        try:
            from android.permissions import request_permissions, Permission
            def callback(permissions, results):
                pass
            request_permissions([
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION,
                Permission.INTERNET
            ], callback)
        except Exception as e:
            print(f"Permissions error: {e}")

    def update_timer(self, dt):
        if self.shift_active and self.start_time:
            now = datetime.datetime.now()
            delta = now - self.start_time
            secs = int(delta.total_seconds())
            h = secs // 3600
            m = (secs % 3600) // 60
            s = secs % 60
            self.status_label.text = f"[b]SCHICHT LÄUFT[/b]\nStart: {self.start_time.strftime('%H:%M:%S')}\nVerstrichen: {h:02d}:{m:02d}:{s:02d}"

    def on_button_pressed(self, instance):
        if not self.shift_active:
            if self.pause_box.disabled:
                # 1. Schicht starten
                self.shift_active = True
                self.start_time = datetime.datetime.now()
                self.btn_action.text = 'SCHICHT BEENDEN'
                self.btn_action.background_color = (0.8, 0.2, 0.2, 1)
                
                self.update_traffic_alert("Schicht aktiv – Route wird überwacht.", level="normal")
                send_telegram(f"🟢 LKW Schicht gestartet!\nStart: {self.start_time.strftime('%H:%M:%S')}")
            else:
                # 3. Pause bestätigen und Bericht senden
                try:
                    pause_min = int(self.pause_input.text)
                except ValueError:
                    pause_min = 0
                
                pause_secs = pause_min * 60
                net_secs = max(0, self.total_secs - pause_secs)
                
                tot_h = int(self.total_secs // 3600)
                tot_m = int((self.total_secs % 3600) // 60)
                net_h = int(net_secs // 3600)
                net_m = int((net_secs % 3600) // 60)
                
                start_str = self.start_time.strftime('%H:%M:%S')
                end_str = self.end_time.strftime('%H:%M:%S')
                
                report = (
                    f"📊 **LKW Schicht-Bericht**\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"⏱️ **Start:** {start_str}\n"
                    f"🏁 **Ende:** {end_str}\n"
                    f"⏳ **Gesamt (Brutto):** {tot_h}h {tot_m}m\n"
                    f"☕ **Pause:** {pause_min} Min.\n"
                    f"💼 **Arbeitszeit (Netto):** {net_h}h {net_m}m\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ An Telegram übermittelt."
                )
                
                send_telegram(report)
                
                self.status_label.text = f"[b]BERICHT GESENDET[/b]\nNetto: {net_h}h {net_m}m (Pause: {pause_min}m)"
                self.pause_box.opacity = 0
                self.pause_box.disabled = True
                self.btn_action.text = 'SCHICHT STARTEN'
                self.btn_action.background_color = (0.1, 0.7, 0.2, 1)
                self.start_time = None
                self.update_traffic_alert("Schicht beendet. Bereit für die nächste Tour.", level="normal")
        else:
            # 2. Schicht beenden -> Timer stoppen & Pausen-Eingabe anfordern
            self.shift_active = False
            self.end_time = datetime.datetime.now()
            total_delta = self.end_time - self.start_time
            self.total_secs = total_delta.total_seconds()
            
            tot_h = int(self.total_secs // 3600)
            tot_m = int((self.total_secs % 3600) // 60)
            
            self.status_label.text = f"[b]SCHICHT BEENDET[/b]\nBrutto: {tot_h}h {tot_m}m\nBitte Pausenzeit eintragen:"
            self.pause_box.opacity = 1
            self.pause_box.disabled = False
            self.btn_action.text = 'PAUSE BESTÄTIGEN & SENDEN'
            self.btn_action.background_color = (0.9, 0.5, 0.1, 1)
            self.update_traffic_alert("Warte auf Pausen-Bestätigung...", level="stop")

if __name__ == '__main__':
    LkwTrackerApp().run()
