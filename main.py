import threading
import time
import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex

TELEGRAM_TOKEN = "8413301731:AAHRM32xA2CkAkrrcf85sqYDR88YK14k3bs"
CHAT_ID = "8941361378"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram Error: {e}")

class MatrixTrackerLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MatrixTrackerLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 30
        self.spacing = 20

        # Matrix Farben: Schwarz & Neon-Grün
        self.bg_color = get_color_from_hex('#000000')
        self.green_color = get_color_from_hex('#00FF66')

        # Status Label
        self.status_label = Label(
            text="SYSTEM BEREIT\nWarte auf Schichtstart...",
            font_size='22sp',
            halign='center',
            valign='middle',
            color=self.green_color
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        self.add_widget(self.status_label)

        # Start Button
        self.btn_start = Button(
            text="SCHICHT STARTEN",
            font_size='20sp',
            background_normal='',
            background_color=(0, 0.2, 0.1, 1),
            color=self.green_color
        )
        self.btn_start.bind(on_press=self.start_shift)
        self.add_widget(self.btn_start)

        # Stop Button
        self.btn_stop = Button(
            text="SCHICHT BEENDEN",
            font_size='20sp',
            background_normal='',
            background_color=(0.2, 0, 0, 1),
            color=get_color_from_hex('#FF3333')
        )
        self.btn_stop.bind(on_press=self.stop_shift)
        self.add_widget(self.btn_stop)

        self.is_active = False

    def start_shift(self, instance):
        if not self.is_active:
            self.is_active = True
            self.status_label.text = "SCHICHT LÄUFT\nGPS & Hintergrunddienst aktiv..."
            threading.Thread(target=self.shift_loop, daemon=True).start()
            send_telegram("🟢 LKW-Schicht gestartet (Matrix Tracker v2.0)")

    def stop_shift(self, instance):
        if self.is_active:
            self.is_active = False
            self.status_label.text = "SCHICHT BEENDET"
            send_telegram("🔴 LKW-Schicht beendet.")

    def shift_loop(self):
        counter = 0
        while self.is_active:
            counter += 1
            # Hier läuft die zyklische Überprüfung
            time.sleep(60)

class LkwTrackerApp(App):
    def build(self):
        return MatrixTrackerLayout()

if __name__ == '__main__':
    LkwTrackerApp().run()
