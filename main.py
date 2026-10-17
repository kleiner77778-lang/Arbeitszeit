import json
import os
import random
import subprocess
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from kivy.resources import resource_find
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout

# Sichere Pfadermittlung für Android & PC
FILES_DIR = os.path.expanduser('~')
STATUS_FILE = os.path.join(FILES_DIR, "status.json")
COMMAND_FILE = os.path.join(FILES_DIR, "command.json")


class MatrixRainOverlay(FloatLayout):
  """Zeichnet den animierten Matrix-Regen als transparentes Overlay"""

  def __init__(self, **kwargs):
    super(MatrixRainOverlay, self).__init__(**kwargs)
    self.drops = []
    for _ in range(45):
      self.drops.append({
          "x": random.randint(0, 600),
          "y": random.randint(0, 1000),
          "speed": random.randint(5, 15),
          "length": random.randint(8, 20),
      })

    Clock.schedule_interval(self.update_matrix, 0.03)

  def update_matrix(self, dt):
    self.canvas.after.clear()
    with self.canvas.after:
      for drop in self.drops:
        drop["y"] -= drop["speed"]
        if drop["y"] < 0:
          drop["y"] = self.height + random.randint(0, 300)
          drop["x"] = random.randint(0, int(self.width or 400))

        Color(0, 1, 0.3, 0.5)
        Line(
            points=[
                drop["x"],
                drop["y"],
                drop["x"],
                drop["y"] + drop["length"] * 10,
            ],
            width=1.5,
        )


class LkwTrackerLayout(MatrixRainOverlay):

  def __init__(self, **kwargs):
    super(LkwTrackerLayout, self).__init__(**kwargs)

    # Hintergrundbild sicher über Kivy Resource Finder laden
    bg_path = resource_find("background.png") or resource_find("78903.jpg")
    if not bg_path:
      bg_path = ""  # Fallback, falls kein Bild gefunden wird

    self.bg_image = Image(
        source=bg_path,
        allow_stretch=True,
        keep_ratio=False,
        size_hint=(1, 1),
        pos=(0, 0),
    )
    self.add_widget(self.bg_image)

    # Haupt-Inhalt als vertikales Layout im Vordergrund
    content_layout = BoxLayout(
        orientation="vertical",
        padding=25,
        spacing=15,
        size_hint=(1, 1),
        pos_hint={"x": 0, "y": 0},
    )

    if platform == "android":
      Clock.schedule_once(self.request_gps_permissions, 1)

    # Titel
    content_layout.add_widget(
        Label(
            text="ATLAS E-LKW TRACKER",
            font_size="26sp",
            bold=True,
            halign="center",
            color=(0.9, 1, 0.9, 1),
            size_hint_y=None,
            height=60,
        )
    )

    # Status-Anzeige
    self.status_label = Label(
        text="Tracking gestoppt",
        font_size="20sp",
        halign="center",
        color=(1, 1, 1, 1),
    )
    content_layout.add_widget(self.status_label)

    # GPS-Koordinaten / KM Anzeige
    self.info_label = Label(
        text="Warte auf GPS-Signal ...",
        font_size="16sp",
        halign="center",
        color=(0.9, 1, 0.9, 1),
    )
    content_layout.add_widget(self.info_label)

    # Haupt Start / Stop Button
    self.toggle_btn = Button(
        text="Tracking starten",
        font_size="20sp",
        size_hint_y=None,
        height=60,
        background_color=(0.1, 0.6, 0.1, 1),
    )
    self.toggle_btn.bind(on_press=self.toggle_tracking)
    content_layout.add_widget(self.toggle_btn)

    # Untere Layout-Leiste für Extra-Buttons
    extra_layout = BoxLayout(
        orientation="horizontal", size_hint_y=None, height=55, spacing=10
    )

    self.btn_extra_start = Button(
        text="Dienst Reset",
        font_size="16sp",
        background_color=(0.1, 0.4, 0.8, 1),
    )
    self.btn_extra_start.bind(on_press=self.send_service_ping)
    extra_layout.add_widget(self.btn_extra_start)

    self.btn_logcat = Button(
        text="🔍 Logcat Fehler",
        font_size="16sp",
        background_color=(0.8, 0.4, 0.1, 1),
    )
    self.btn_logcat.bind(on_press=self.show_logcat_popup)
    extra_layout.add_widget(self.btn_logcat)

    content_layout.add_widget(extra_layout)

    # Telegram Status Label
    self.telegram_label = Label(
        text="Telegram: Nicht konfiguriert",
        font_size="13sp",
        halign="center",
        color=(0.8, 1, 0.8, 1),
        size_hint_y=None,
        height=35,
    )
    content_layout.add_widget(self.telegram_label)

    self.add_widget(content_layout)

    Clock.schedule_interval(self.update_from_service, 1.0)
    self.is_active = False

  def request_gps_permissions(self, dt):
    try:
      from android.permissions import Permission, request_permissions
      permissions = [
          Permission.ACCESS_FINE_LOCATION,
          Permission.ACCESS_COARSE_LOCATION,
      ]
      request_permissions(permissions, self.permission_callback)
    except Exception as e:
      print(f"Fehler bei Berechtigungsanfrage: {e}")

  def permission_callback(self, permissions, results):
    if all(results):
      print("Alle Standort-Berechtigungen erteilt!")
    else:
      print("Standort-Berechtigungen teilweise abgelehnt.")

  def toggle_btn_style(self):
    if self.is_active:
      self.toggle_btn.text = "Tracking stoppen"
      self.toggle_btn.background_color = (0.8, 0.1, 0.1, 1)
    else:
      self.toggle_btn.text = "Tracking starten"
      self.toggle_btn.background_color = (0.1, 0.6, 0.1, 1)

  def toggle_tracking(self, instance):
    self.is_active = not self.is_active
    self.toggle_btn_style()

    cmd = "START" if self.is_active else "STOP"
    try:
      with open(COMMAND_FILE, "w") as f:
        json.dump({"command": cmd}, f)
    except Exception as e:
      print(f"Fehler beim Schreiben des Befehls: {e}")

  def send_service_ping(self, instance):
    try:
      with open(COMMAND_FILE, "w") as f:
        json.dump({"command": "PING"}, f)
      self.status_label.text = "Status: Dienst-Ping gesendet"
    except Exception as e:
      print(f"Ping Fehler: {e}")

  def show_logcat_popup(self, instance):
    log_text = "Keine Logs verfügbar."
    try:
      result = subprocess.run(
          ["logcat", "-d", "-t", "50", "*:S", "python:D"],
          capture_output=True,
          text=True,
      )
      if result.stdout:
        log_text = result.stdout
      else:
        res_fallback = subprocess.run(
            ["logcat", "-d", "-t", "30"], capture_output=True, text=True
        )
        log_text = (
            res_fallback.stdout
            if res_fallback.stdout
            else "Logcat leer oder gesperrt."
        )
    except Exception as e:
      log_text = f"Fehler beim Abrufen von Logcat: {e}"

    popup_layout = BoxLayout(orientation="vertical", padding=15, spacing=10)

    scroll = ScrollView(size_hint=(1, 0.85))
    lbl_logs = Label(
        text=log_text,
        font_size="12sp",
        size_hint_x=1,
        size_hint_y=None,
        halign="left",
        valign="top",
    )
    lbl_logs.bind(
        texture_size=lambda *args: setattr(lbl_logs, "height", lbl_logs.texture_size[1])
    )
    scroll.add_widget(lbl_logs)
    popup_layout.add_widget(scroll)

    close_btn = Button(
        text="Schließen", size_hint_y=None, height=50, background_color=(0.5, 0.5, 0.5, 1)
    )
    popup_layout.add_widget(close_btn)

    popup = Popup(
        title="Android Logcat (Fehlerdiagnose)",
        content=popup_layout,
        size_hint=(0.9, 0.9),
    )
    close_btn.bind(on_press=popup.dismiss)
    popup.open()

  def update_from_service(self, dt):
    if os.path.exists(STATUS_FILE):
      try:
        with open(STATUS_FILE, "r") as f:
          data = json.load(f)

        status = data.get("status", "Bereit")
        lat = data.get("lat", 0.0)
        lon = data.get("lon", 0.0)
        km = data.get("km", 0.0)
        telegram_ok = data.get("telegram_ok", False)

        self.status_label.text = f"Status: {status}"
        if lat != 0.0 and lon != 0.0:
          self.info_label.text = (
              f"Lat: {lat:.4f}\nLon: {lon:.4f}\nGesamt: {km} km"
          )
        else:
          self.info_label.text = (
              f"Warte auf GPS-Signal ...\nGesamt: {km} km"
          )

        if telegram_ok:
          self.telegram_label.text = "Telegram: Verbunden & Bereit"
        else:
          self.telegram_label.text = "Telegram: Nicht konfiguriert"

      except Exception as e:
        print(f"Fehler beim Lesen von status.json: {e}")


class LkwTrackerApp(App):

  def build(self):
    return LkwTrackerLayout()


if __name__ == "__main__":
  LkwTrackerApp().run()
