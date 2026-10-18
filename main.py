import json
import os
import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label

# Telegram-Konfiguration
TELEGRAM_BOT_TOKEN = "8903052918:AAHBnydKYckd-LHpV7Fi9f2oCifsLP25Irs"
TELEGRAM_CHAT_ID = "8941361378"


def send_telegram_message(text):
  if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    return False
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
  try:
    res = requests.post(url, json=payload, timeout=8)
    return res.status_code == 200
  except Exception as e:
    print(f"Telegram-Fehler: {e}")
    return False


class AtlasApp(App):

  def build(self):
    # Ermittlung des internen Android-Pfads für Status & Commands
    try:
      from jnius import autoclass

      try:
        PythonService = autoclass("org.kivy.android.PythonService")
        context = PythonService.mService
        self.files_dir = context.getFilesDir().getAbsolutePath()
      except Exception:
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        context = PythonActivity.mActivity.getApplicationContext()
        self.files_dir = context.getFilesDir().getAbsolutePath()
    except Exception:
        self.files_dir = os.path.expanduser("~")

    self.status_file = os.path.join(self.files_dir, "status.json")
    self.command_file = os.path.join(self.files_dir, "command.json")

    # Hauptlayout
    root = BoxLayout(orientation="vertical", padding=10, spacing=10)

    # Titel
    root.add_widget(
        Label(
            text="ATLAS E-LKW TRACKER",
            font_size="20sp",
            size_hint_y=None,
            height=40,
        )
    )

    # Bild / Logo kleiner und rechteckig (proportional angepasst)
    self.img = Image(
        source="logo.png",
        size_hint_y=None,
        height=150,
        allow_stretch=True,
        keep_ratio=True,
    )
    root.add_widget(self.img)

    # Status-Anzeige (Textfeld für Live-Daten)
    self.status_label = Label(
        text="Lade Status...",
        font_size="16sp",
        halign="center",
        valign="middle",
    )
    root.add_widget(self.status_label)

    # Buttons in einer waagerechten Reihe nebeneinander, kompakter
    btn_layout = BoxLayout(
        orientation="horizontal", spacing=10, size_hint_y=None, height=50
    )

    self.btn_start = Button(text="START", background_color=(0, 0.7, 0, 1))
    self.btn_start.bind(on_press=self.on_start_click)
    btn_layout.add_widget(self.btn_start)

    self.btn_stop = Button(text="STOP", background_color=(0.8, 0, 0, 1))
    self.btn_stop.bind(on_press=self.on_stop_click)
    btn_layout.add_widget(self.btn_stop)

    self.btn_reset = Button(text="RESET", background_color=(0.5, 0.5, 0.5, 1))
    self.btn_reset.bind(on_press=self.on_reset_click)
    btn_layout.add_widget(self.btn_reset)

    root.add_widget(btn_layout)

    # Hintergrunddienst starten (Android)
    self.start_background_service()

    # Regelmäßiger Status-Check alle 1 Sekunde
    Clock.schedule_interval(self.update_status_display, 1.0)

    return root

  def start_background_service(self):
    try:
      from jnius import autoclass

      Activity = autoclass("org.kivy.android.PythonActivity")
      context = Activity.mActivity
      ServiceName = autoclass(
          "org.kivy.android.PythonService"
      ).mServiceClass
      intent = autoclass("android.content.Intent")(context, ServiceName)
      intent.putExtra("pythonServiceArgument", "service.py")
      context.startService(intent)
    except Exception as e:
      print(f"Service Start Fehler: {e}")

  def send_command(self, cmd_data):
    try:
      with open(self.command_file, "w") as f:
        json.dump(cmd_data, f)
    except Exception as e:
      print(f"Fehler beim Senden des Befehls: {e}")

  def on_start_click(self, instance):
    self.send_command({"command": "START"})
    send_telegram_message("▶️ *Schicht gestartet über App!* Gute Fahrt.")

  def on_stop_click(self, instance):
    self.send_command({"command": "STOP", "pause_minuten": 45})
    send_telegram_message("⏹ *Schicht beendet über App!*")

  def on_reset_click(self, instance):
    self.send_command({"command": "RESET"})

  def update_status_display(self, dt):
    if os.path.exists(self.status_file):
      try:
        with open(self.status_file, "r") as f:
          data = json.load(f)
        status_text = (
            f"Status: {data.get('status', 'Unbekannt')}\n"
            f"Distanz: {data.get('km', 0.0)} km\n"
            f"Lat: {data.get('lat', 0.0):.4f} | Lon:"
            f" {data.get('lon', 0.0):.4f}\n"
            f"Telegram: {'Verbunden' if data.get('telegram_ok') else 'Getrennt'}"
        )
        self.status_label.text = status_text
      except Exception:
        pass


if __name__ == "__main__":
  AtlasApp().run()
