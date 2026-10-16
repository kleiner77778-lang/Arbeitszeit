import json
import os
import random
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

# Android-spezifische Berechtigungen prüfen/anfordern, falls verfügbar
try:
  from android.permissions import Permission, request_permissions

  ANDROID_PLATFORM = True
except ImportError:
  ANDROID_PLATFORM = False


# Klasse für den animierten Matrix-Code-Regen im Hintergrund
class MatrixRainWidget(Widget):

  def __init__(self, **kwargs):
    super(MatrixRainWidget, self).__init__(**kwargs)
    self.drops = []
    for _ in range(30):
      self.drops.append({
          "x": random.randint(0, 1000),
          "y": random.randint(0, 1200),
          "speed": random.randint(8, 20),
      })
    Clock.schedule_interval(self.update_rain, 0.05)

  def update_rain(self, dt):
    self.canvas.clear()
    with self.canvas:
      # Satter dunkler Cyberpunk-Hintergrund
      Color(0.0, 0.03, 0.01, 1)
      Rectangle(pos=self.pos, size=self.size)

      # Hellgrüne Matrix-Tropfen
      Color(0.1, 0.95, 0.2, 0.4)
      for drop in self.drops:
        drop["y"] -= drop["speed"]
        if drop["y"] < 0:
          drop["y"] = self.height + random.randint(0, 200)
          drop["x"] = random.randint(0, int(self.width or 800))

        Rectangle(pos=(drop["x"], drop["y"]), size=(6, 35))


class LKWTrackerApp(App):

  def build(self):
    self.title = "LKW Tracker - Zeiterfassung"

    # Beim Start direkt Berechtigungen anfordern (falls Android)
    self.check_and_request_permissions()

    from kivy.uix.floatlayout import FloatLayout

    root = FloatLayout()

    # 1. Hintergrund-Widget (Matrix-Regen)
    self.matrix_bg = MatrixRainWidget(
        size_hint=(1, 1), pos_hint={"x": 0, "y": 0}
    )
    root.add_widget(self.matrix_bg)

    # 2. Vordergrund-Layout (Inhalt der App) mit weniger Padding
    root_layout = BoxLayout(
        orientation="vertical", padding=10, spacing=10, size_hint=(1, 1)
    )

    # Lkw-Bild oben im Cockpit (feste Höhe, damit es nicht verschwindet)
    if os.path.exists("icon.png"):
      img_banner = Image(
          source="icon.png",
          size_hint=(1, 0.35),
          allow_stretch=True,
          keep_ratio=True,
      )
      root_layout.add_widget(img_banner)

    # Status-Bereich: JETZT RIESIG (font_size=55) für perfekte Lesbarkeit mit Brille!
    self.status_label = Label(
        text="Status: Bereit\nKilometer: 0.00 km",
        font_size=55,
        halign="center",
        valign="middle",
        bold=True,
        color=(0.9, 1.0, 0.9, 1),
        size_hint=(1, 0.35),
    )
    self.status_label.bind(size=self.status_label.setter("text_size"))
    root_layout.add_widget(self.status_label)

    # Unterer Bereich: 3 Buttons mit massiver Schrift (font_size=28)
    btn_layout = BoxLayout(
        orientation="horizontal", spacing=10, size_hint=(1, 0.25)
    )

    btn_start = Button(
        text="SCHICHT\nSTART",
        background_color=(0.1, 0.85, 0.3, 1),
        font_size=24,
        bold=True,
    )
    btn_start.bind(on_press=self.start_shift)

    btn_end = Button(
        text="FEIERABEND",
        background_color=(0.85, 0.2, 0.2, 1),
        font_size=24,
        bold=True,
    )
    btn_end.bind(on_press=self.prompt_feierabend)

    btn_logcat = Button(
        text="LOGCAT\n(FEHLER)",
        background_color=(0.1, 0.5, 0.9, 1),
        font_size=24,
        bold=True,
    )
    btn_logcat.bind(on_press=self.show_logcat_popup)

    btn_layout.add_widget(btn_start)
    btn_layout.add_widget(btn_end)
    btn_layout.add_widget(btn_logcat)

    root_layout.add_widget(btn_layout)
    root.add_widget(root_layout)

    # Regelmäßig Daten einlesen
    Clock.schedule_interval(self.check_status_file, 3)

    return root

  def check_and_request_permissions(self):
    if ANDROID_PLATFORM:
      try:
        request_permissions([
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION,
            Permission.FOREGROUND_SERVICE,
        ])
      except Exception as e:
        print(f"Fehler beim Anfordern der Berechtigungen: {e}")

  def start_shift(self, instance):
    self.update_command("START")
    self.status_label.text = "Status: Schicht aktiv!\nGPS zeichnet auf..."

  def prompt_feierabend(self, instance):
    content = BoxLayout(orientation="vertical", padding=20, spacing=15)

    lbl_popup = Label(
        text="FEIERABEND!\nPause in Minuten eintragen:",
        font_size=26,
        halign="center",
        bold=True,
    )
    lbl_popup.bind(size=lbl_popup.setter("text_size"))
    content.add_widget(lbl_popup)

    self.pause_input = TextInput(
        text="45", multiline=False, input_filter="int", font_size=32
    )
    content.add_widget(self.pause_input)

    btn_confirm = Button(
        text="Bestätigen & Beenden",
        background_color=(0.1, 0.5, 0.9, 1),
        font_size=24,
        size_hint=(1, 0.3),
        bold=True,
    )

    popup = Popup(
        title="Schicht beenden & Pause",
        content=content,
        size_hint=(0.9, 0.6),
        auto_dismiss=False,
    )

    btn_confirm.bind(on_press=lambda x: self.finish_shift(popup))
    content.add_widget(btn_confirm)

    popup.open()

  def finish_shift(self, popup):
    pause_min = self.pause_input.text
    popup.dismiss()
    self.update_command("STOP", pause=pause_min)
    self.status_label.text = (
        f"Status: Schicht beendet.\nPause: {pause_min} Min. eingetragen."
    )

  def show_logcat_popup(self, instance):
    content = BoxLayout(orientation="vertical", padding=15, spacing=10)

    log_text = "System-Logs / Berechtigungsstatus:\n"
    if ANDROID_PLATFORM:
      log_text += "Android-Plattform aktiv.\nBerechtigungen angefordert.\n"
    else:
      log_text += "Test-Modus (kein Android-Gerät).\n"

    lbl_log = Label(text=log_text, font_size=22, halign="left", valign="top")
    lbl_log.bind(size=lbl_log.setter("text_size"))
    content.add_widget(lbl_log)

    btn_close = Button(
        text="Schließen", size_hint=(1, 0.25), font_size=24, bold=True
    )
    popup = Popup(
        title="Logcat & Fehleranalyse",
        content=content,
        size_hint=(0.9, 0.7),
        auto_dismiss=True,
    )
    btn_close.bind(on_press=popup.dismiss)
    content.add_widget(btn_close)

    popup.open()

  def update_command(self, cmd, pause=0):
    cmd_file = "command.json"
    try:
      data = {
          "command": cmd,
          "pause_minutes": int(pause),
          "timestamp": time.time(),
      }
      with open(cmd_file, "w") as f:
        json.dump(data, f)
    except Exception as e:
      print(f"Fehler beim Schreiben des Befehls: {e}")

  def check_status_file(self, dt):
    status_file = "status.json"
    if os.path.exists(status_file):
      try:
        with open(status_file, "r") as f:
          data = json.load(f)
          status = data.get("status", "Inaktiv")
          km = data.get("km", 0.0)
          self.status_label.text = (
              f"Status: {status}\nKilometer: {km:.2f} km"
          )
      except:
        pass


if __name__ == "__main__":
  LKWTrackerApp().run()
