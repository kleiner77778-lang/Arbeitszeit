import json
import os
import sys
import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

# Telegram-Konfiguration
TELEGRAM_BOT_TOKEN = "8903052918:AAHBnydKYckd-LHpV7Fi9f2oCifsLP25Irs"
TELEGRAM_CHAT_ID = "8941361378"


# In-App Logcat Umleitung
class LogRedirector:

  def __init__(self, text_widget):
    self.text_widget = text_widget
    self.terminal = sys.stdout

  def write(self, message):
    self.terminal.write(message)
    Clock.schedule_once(lambda dt: self.append_log(message), 0)

  def flush(self):
    self.terminal.flush()

  def append_log(self, message):
    if message.strip():
      self.text_widget.text += message + "\n"


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
    # Android Laufzeit-Berechtigungen anfordern
    try:
      from android.permissions import Permission, request_permissions

      request_permissions([
          Permission.ACCESS_FINE_LOCATION,
          Permission.ACCESS_COARSE_LOCATION,
          Permission.FOREGROUND_SERVICE,
      ])
    except Exception as e:
      print(f"Berechtigungs-Hinweis: {e}")

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
    root = BoxLayout(orientation="vertical", padding=10, spacing=8)

    # Titel
    root.add_widget(
        Label(
            text="ATLAS E-LKW TRACKER",
            font_size="20sp",
            bold=True,
            size_hint_y=None,
            height=35,
        )
    )

    # Logo (falls vorhanden)
    logo_path = "logo.png" if os.path.exists("logo.png") else ""
    self.img = Image(
        source=logo_path,
        size_hint_y=None,
        height=100,
        allow_stretch=True,
        keep_ratio=True,
    )
    root.add_widget(self.img)

    # Status-Anzeige
    self.status_label = Label(
        text="Warte auf Status...",
        font_size="14sp",
        size_hint_y=None,
        height=60,
        halign="center",
        valign="middle",
    )
    root.add_widget(self.status_label)

    # Buttons
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

    # In-App Logcat-Konsole
    root.add_widget(
        Label(
            text="--- IN-APP LOGCAT ---",
            font_size="12sp",
            size_hint_y=None,
            height=20,
        )
    )

    self.log_text = TextInput(
        text="App gestartet...\n",
        readonly=True,
        background_color=(0.1, 0.1, 0.1, 1),
        foreground_color=(0, 1, 0, 1),
        font_size="12sp",
    )

    scroll = ScrollView(size_hint=(1, 1))
    scroll.add_widget(self.log_text)
    root.add_widget(scroll)

    # Umleitung aktivieren
    sys.stdout = LogRedirector(self.log_text)
    sys.stderr = LogRedirector(self.log_text)

    # Status-Check Intervall
    Clock.schedule_interval(self.update_status_display, 1.0)

    return root

  def send_command(self, cmd_data):
    try:
      with open(self.command_file, "w") as f:
        json.dump(cmd_data, f)
    except Exception as e:
      print(f"Befehls-Fehler: {e}")

  def on_start_click(self, instance):
    self.send_command({"command": "START"})
    send_telegram_message("▶️ *Schicht gestartet über App!*")

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
        self.status_label.text = (
            f"Status: {data.get('status', 'OK')} | Distanz:"
            f" {data.get('km', 0.0)} km"
        )
      except Exception as e:
        print(f"Status-Lesefehler: {e}")


if __name__ == "__main__":
  AtlasApp().run()
