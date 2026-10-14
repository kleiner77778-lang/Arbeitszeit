from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.utils import platform
import random
import datetime
import requests

# --- TELEGRAM KONFIGURATION (Bereits eingetragen) ---
TELEGRAM_BOT_TOKEN = "8413301731:AAHRM32xA2CkAkrrcf85sqYDR88YK14k3bs"
TELEGRAM_CHAT_ID = "8941361378"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=5)
    except Exception as e:
        print(f"Telegram Fehler: {e}")

class MatrixRainLabel(Label):
    """Stylischer Matrix-Regen Effekt für das Terminal-Design"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chars = "01010101010101010101LKWTRACKERFAHRPAUSEARBEITSZEIT"
        Clock.schedule_interval(self.update_matrix, 0.12)

    def update_matrix(self, dt):
        lines = []
        for _ in range(8):
            line = "".join(random.choice(self.chars) for _ in range(24))
            lines.append(line)
        self.text = "\n".join(lines)
        self.color = (0, 1, 0, 0.85)  # Neon-Grün
        self.font_size = 14

class LkwTrackerApp(App):
    def build(self):
        self.shift_active = False
        self.start_time = None
        
        root = BoxLayout(orientation='vertical', padding=15, spacing=12)
        sw = 1.0  # size_hint_x width helper
        
        # 1. Matrix-Display oben
        self.matrix_display = MatrixRainLabel(size_hint=(sw, 0.3))
        root.add_widget(self.matrix_display)
        
        # 2. Status-Anzeige
        self.status_label = Label(
            text='[b]LKW Tracker bereit[/b]\nStatus: Keine Schicht aktiv',
            markup=True,
            font_size=16,
            halign='center',
            valign='middle',
            size_hint=(sw, 0.25)
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        root.add_widget(self.status_label)
        
        # 3. Pausen-Eingabe (Minuten)
        pause_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(sw, 0.12))
        pause_layout.add_widget(Label(text='Pause (Min.):', font_size=14, size_hint=(0.4, 1)))
        
        self.pause_input = TextInput(
            text='30', 
            multiline=False, 
            input_filter='int', 
            font_size=16,
            size_hint=(0.6, 1)
        )
        pause_layout.add_widget(self.pause_input)
        root.add_widget(pause_layout)
        
        # 4. Schicht Start / Ende Buttons
        btn_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint=(sw, 0.22))
        
        self.btn_start = Button(
            text='Schicht\nStarten', 
            font_size=15, 
            background_color=(0, 0.7, 0, 1)
        )
        self.btn_start.bind(on_press=self.start_shift)
        btn_layout.add_widget(self.btn_start)
        
        self.btn_end = Button(
            text='Schicht\nBeenden', 
            font_size=15, 
            background_color=(0.7, 0, 1, 1), 
            disabled=True
        )
        self.btn_end.bind(on_press=self.end_shift)
        btn_layout.add_widget(self.btn_end)
        
        root.add_widget(btn_layout)
        
        return root

    def start_shift(self, instance):
        self.shift_active = True
        self.start_time = datetime.datetime.now()
        time_str = self.start_time.strftime("%H:%M:%S")
        
        self.status_label.text = f"[b]Schicht LÄUFT[/b]\nStart: {time_str}"
        self.btn_start.disabled = True
        self.btn_end.disabled = False
        
        # Telegram Nachricht bei Schichtstart
        send_telegram(f"🟢 LKW Schicht gestartet!\nStartzeit: {time_str}")

    def end_shift(self, instance):
        if not self.shift_active:
            return
        
        end_time = datetime.datetime.now()
        total_duration = end_time - self.start_time
        total_seconds = total_duration.seconds
        
        # Pause aus Eingabefeld auslesen (in Minuten)
        try:
            pause_minutes = int(self.pause_input.text)
        except ValueError:
            pause_minutes = 0
            
        pause_seconds = pause_minutes * 60
        net_seconds = max(0, total_seconds - pause_seconds)
        
        # Arbeitszeit formatieren
        tot_h = total_seconds // 3600
        tot_m = (total_seconds % 3600) // 60
        
        net_h = net_seconds // 3600
        net_m = (net_seconds % 3600) // 60
        
        start_str = self.start_time.strftime('%H:%M:%S')
        end_str = end_time.strftime('%H:%M:%S')
        
        # Ausführlicher Bericht für Telegram
        report = (
            f"📊 **LKW Schicht-Bericht**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"⏱️ **Start:** {start_str}\n"
            f"🏁 **Ende:** {end_str}\n"
            f"⏳ **Gesamtzeit (Brutto):** {tot_h} Std. {tot_m} Min.\n"
            f"☕ **Pause:** {pause_minutes} Min.\n"
            f"💼 **Arbeitszeit (Netto):** {net_h} Std. {net_m} Min.\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Schicht erfolgreich dokumentiert."
        )
        
        self.status_label.text = f"[b]Schicht beendet[/b]\nNetto: {net_h}h {net_m}m (Pause: {pause_minutes}m)\nBericht an Telegram gesendet."
        self.btn_start.disabled = False
        self.btn_end.disabled = True
        self.shift_active = False
        
        # Bericht an Telegram senden
        send_telegram(report)

if __name__ == '__main__':
    LkwTrackerApp().run()
