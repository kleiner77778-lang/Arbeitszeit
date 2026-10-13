import time
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
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
        self.padding = 10
        self.spacing = 10

        self.green_color = get_color_from_hex('#00FF66')
        self.red_color = get_color_from_hex('#FF3333')
        self.yellow_color = get_color_from_hex('#FFFF33')

        # Scrollbarer Log-Bereich für Historie und Staus
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.log_label = Label(
            text="[MATRIX SYSTEM BEREIT]\nWarte auf Schichtstart...\n",
            font_size='14sp',
            halign='left',
            valign='top',
            color=self.green_color,
            markup=True,
            size_hint_y=None
        )
        self.log_label.bind(width=lambda s, w: setattr(s, 'text_size', (w, None)))
        self.log_label.bind(texture_size=lambda s, t: setattr(s, 'height', t[1]))
        
        self.scroll_view.add_widget(self.log_label)
        self.add_widget(self.scroll_view)

        # Kompakte Steuerungsleiste unten: START | STAU | BERICHT | ENDE
        control_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=45,
            spacing=8
        )

        # 1. START Button (Links)
        self.btn_start = Button(
            text="START",
            font_size='12sp',
            background_normal='',
            background_color=(0, 0.3, 0.1, 1),
            color=self.green_color
        )
        self.btn_start.bind(on_press=self.start_shift)

        # 2. STAU Button (Mitte-Links)
        self.btn_stop_event = Button(
            text="STAU",
            font_size='12sp',
            background_normal='',
            background_color=(0.2, 0.2, 0, 1),
            color=self.yellow_color
        )
        self.btn_stop_event.bind(on_press=self.log_stop_event)

        # 3. BERICHT Button (Mitte-Rechts)
        self.btn_report = Button(
            text="BERICHT",
            font_size='12sp',
            background_normal='',
            background_color=(0.1, 0.1, 0.1, 1),
            color=self.green_color
        )
        self.btn_report.bind(on_press=self.show_report)

        # 4. ENDE Button (Rechts)
        self.btn_stop = Button(
            text="ENDE",
            font_size='12sp',
            background_normal='',
            background_color=(0.3, 0, 0, 1),
            color=self.red_color
        )
        self.btn_stop.bind(on_press=self.stop_shift)

        control_layout.add_widget(self.btn_start)
        control_layout.add_widget(self.btn_stop_event)
        control_layout.add_widget(self.btn_report)
        control_layout.add_widget(self.btn_stop)

        self.add_widget(control_layout)

        self.is_active = False
        self.start_time = 0
        self.event_count = 0
        self.popup = None
        self.pause_input = None

    def add_log(self, text):
        timestamp = time.strftime("%H:%M:%S")
        new_entry = f"[{timestamp}] {text}\n"
        self.log_label.text += new_entry

    def start_shift(self, instance):
        if not self.is_active:
            self.is_active = True
            self.start_time = time.time()
            self.event_count = 0
            self.log_label.text = ""
            self.add_log("🟢 Schicht gestartet.")
            send_telegram("🟢 LKW-Schicht gestartet.")
        else:
            self.add_log("⚠️ Schicht läuft bereits.")

    def log_stop_event(self, instance):
        if self.is_active:
            self.event_count += 1
            event_msg = f"🛑 Stau / Haltepunkt #{self.event_count} protokolliert."
            self.add_log(event_msg)
            send_telegram(f"⚠️ {event_msg}")
        else:
            self.add_log("⚠️ Keine aktive Schicht.")

    def show_report(self, instance):
        if self.is_active:
            elapsed = int(time.time() - self.start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            report_msg = f"📊 Status: Aktiv | Zeit: {hours}h {minutes}m | Staus: {self.event_count}"
            self.add_log(report_msg)
            send_telegram(report_msg)
        else:
            self.add_log("ℹ️ Keine aktive Schicht.")

    def stop_shift(self, instance):
        if self.is_active:
            # Öffnet ein Eingabefenster (Popup), um die Pause abzufragen
            content = BoxLayout(orientation='vertical', padding=15, spacing=15)
            
            lbl = Label(
                text="Pausenzeit in Minuten eingeben (z.B. 45):",
                color=self.green_color,
                font_size='14sp',
                halign='center'
            )
            
            self.pause_input = TextInput(
                text="0",
                input_filter='int',
                multiline=False,
                font_size='22sp',
                size_hint_y=None,
                height=45
            )
            
            btn_confirm = Button(
                text="BESTÄTIGEN & ABSENDEN",
                font_size='14sp',
                background_normal='',
                background_color=(0, 0.3, 0.1, 1),
                color=self.green_color,
                size_hint_y=None,
                height=45
            )
            btn_confirm.bind(on_press=self.finalize_stop)
            
            content.add_widget(lbl)
            content.add_widget(self.pause_input)
            content.add_widget(btn_confirm)
            
            self.popup = Popup(
                title="Schicht beenden - Pause erfassen",
                content=content,
                size_hint=(0.85, 0.45),
                auto_dismiss=False
            )
            self.popup.open()
        else:
            self.add_log("ℹ️ Keine aktive Schicht zum Beenden.")

    def finalize_stop(self, instance):
        if self.popup:
            self.popup.dismiss()
            
        try:
            pause_minutes = int(self.pause_input.text)
        except (ValueError, TypeError):
            pause_minutes = 0

        self.is_active = False
        end_time = time.time()
        gross_elapsed = int(end_time - self.start_time)
        
        break_seconds = pause_minutes * 60
        net_elapsed = max(0, gross_elapsed - break_seconds)
        
        g_h, g_m = gross_elapsed // 3600, (gross_elapsed % 3600) // 60
        b_h, b_m = pause_minutes // 60, pause_minutes % 60
        n_h, n_m = net_elapsed // 3600, (net_elapsed % 3600) // 60

        self.add_log("🔴 Schicht beendet.")
        self.add_log(f"• Brutto: {g_h}h {g_m}m | Pause: {b_h}h {b_m}m")
        self.add_log(f"• Netto Arbeitszeit: {n_h}h {n_m}m")
        self.add_log(f"• Staus/Stopps: {self.event_count}")

        # Abschlussbericht an Telegram senden
        send_telegram(
            f"🛑 Schicht-Abschlussbericht:\n"
            f"Brutto: {g_h}h {g_m}m\n"
            f"Manuelle Pause: {b_h}h {b_m}m\n"
            f"Netto Arbeitszeit: {n_h}h {n_m}m\n"
            f"Protokollierte Staus/Stopps: {self.event_count}"
        )

class LkwTrackerApp(App):
    def build(self):
        return MatrixTrackerLayout()

    def on_pause(self):
        return True

    def on_resume(self):
        pass

if __name__ == '__main__':
    LkwTrackerApp().run()
