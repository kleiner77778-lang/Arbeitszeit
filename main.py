import json
import os
import sys
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

# Globaler Log-Buffer, der alle Ausgaben mitschreibt
global_log_content = "App wird initialisiert...\n"


class LogCollector:

  def __init__(self, original_stream):
    self.original_stream = original_stream

  def write(self, message):
    global global_log_content
    global_log_content += message
    if self.original_stream:
      try:
        self.original_stream.write(message)
      except Exception:
        pass

  def flush(self):
    if self.original_stream:
      try:
        self.original_stream.flush()
      except Exception:
        pass


# Ausgaben direkt umleiten
sys.stdout = LogCollector(sys.stdout)
sys.stderr = LogCollector(sys.stderr)

# Telegram-Konfiguration
TELEGRAM_BOT_TOKEN = "8903052918:AAHBnydKYckd-LHpV7Fi9f2oCifsLP25Irs"
TELEGRAM_CHAT_ID = "8941361378"


class AtlasApp(App):

  def build(self):
    # Basis-Layout
    root = BoxLayout(orientation="vertical", padding=15, spacing=10)

    # Titel
    root.add_widget(
        Label(
            text="ATLAS E-LKW TRACKER",
            font_size="22sp",
            bold=True,
            size_hint_y=None,
            height=40,
        )
    )

    # Status-Anzeige
    self.info_label = Label(
        text="Lade Status...",
        font_size="16sp",
        size_hint_y=None,
        height=60,
        halign="center",
        valign="middle",
    )
    self.info_label.bind(
        size=lambda s, w: setattr(s, "text_size", (w, None))
    )
    root.add_widget(self.info_label)

    # Buttons in einer Reihe (inklusive des neuen Extra-Logcat-Buttons)
    btn_layout = BoxLayout(
        orientation="horizontal", spacing=8, size_hint_y=None, height=55
    )

    btn_start = Button(text="START", background_color=(0, 0.7, 0, 1))
    btn_start.bind(on_press=self.on_start_click)
    btn_layout.add_widget(btn_start)

    btn_stop = Button(text="STOP", background_color=(0.8, 0, 0, 1))
    btn_stop.bind(on_press=self.on_stop_click)
    btn_layout.add_widget(btn_stop)

    # Der Extra Logcat-Button
    btn_logcat = Button(text="LOGCAT", background_color=(0, 0.4, 0.8, 1))
    btn_logcat.bind(on_press=self.show_logcat_popup)
    btn_layout.add_widget(btn_logcat)

    root.add_widget(btn_layout)

    # Hinweis für den Nutzer auf dem Hauptbildschirm
    root.add_widget(
        Label(
            text=(
                "Tippe jederzeit auf [LOGCAT], um die echten Fehlermeldungen"
                " zu sehen."
            ),
            font_size="13sp",
            halign="center",
            valign="middle",
        )
    )

    # Pfad-Ermittlung
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

    Clock.schedule_interval(self.check_status, 1.0)
    return root

  def show_logcat_popup(self, instance):
    global global_log_content
    # Erstelle ein großes Popup-Fenster für das Logcat
    content = BoxLayout(orientation="vertical", padding=10, spacing=10)

    log_input = TextInput(
        text=global_log_content,
        readonly=True,
        background_color=(0.05, 0.05, 0.05, 1),
        foreground_color=(0, 1, 0, 1),
        font_size="12sp",
    )

    scroll = ScrollView(size_hint=(1, 1))
    scroll.add_widget(log_input)
    content.add_widget(scroll)

    close_btn = Button(
        text="SCHLIESSEN",
        size_hint_y=None,
        height=50,
        background_color=(0.7, 0, 0, 1),
    )
    content.add_widget(close_btn)

    popup = Popup(
        title="Live Logcat / Terminal",
        content=content,
        size_hint=(0.95, 0.95),
    )
    close_btn.bind(on_press=popup.dismiss)
    popup.open()

  def send_command(self, cmd_data):
    try:
      with open(self.command_file, "w") as f:
        json.dump(cmd_data, f)
    except Exception as e:
      print(f"Befehls-Fehler: {e}")

  def on_start_click(self, instance):
    self.send_command({"command": "START"})

  def on_stop_click(self, instance):
    self.send_command({"command": "STOP", "pause_minuten": 45})

  def check_status(self, dt):
    if os.path.exists(self.status_file):
      try:
        with open(self.status_file, "r") as f:
          data = json.load(f)
        self.info_label.text = (
            f"Status: {data.get('status')} | KM: {data.get('km', 0.0)}"
        )
      except Exception as e:
        self.info_label.text = f"Status-Lesefehler: {e}"
    else:
        self.info_label.text = "Warte auf Hintergrunddienst (lkwservice)..."


if __name__ == "__main__":
  AtlasApp().run()
