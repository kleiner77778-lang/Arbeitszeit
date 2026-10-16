import json
import os
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

# Android-spezifische Berechtigungen prüfen/anfordern, falls verfügbar
try:
  from android.permissions import Permission, request_permissions

  ANDROID_PLATFORM = True
except ImportError:
  ANDROID_PLATFORM = False


class LKWTrackerApp(App):

  def build(self):
    self.title = "LKW Tracker - Zeiterfassung"

    # Beim Start direkt Berechtigungen anfordern (falls Android)
    self.check_and_request_permissions()

    # Hauptlayout mit dunklem Cyberpunk-Hintergrund per Canvas
    root_layout = BoxLayout(orientation="vertical", padding=15, spacing=15)

    with root_layout.canvas.before:
      # Satter, dunkler Cyberpunk-Hintergrund (Sehr dunkles Blau/Grün)
      Color(0.02, 0.08, 0.04, 1)
      self.bg_rect = Rectangle(size=root_layout.size, pos=root_layout.pos)

    root_layout.bind(size=self._update_bg, pos=self._update_bg)

    # 1. OBERER BEREICH: Dein Lkw-Bild (icon.png) als Banner
    if os.path.exists("icon.png"):
      img_banner = Image(
          source="icon.png",
          size_hint=(1, 0.35),
          allow_stretch=True,
          keep_ratio=True,
      )
      root_layout.add_widget(img_banner)

    # 2. MITTLERER BEREICH: RIESIGE, fette Status-Anzeige für Brillenträger
    self.status_label = Label(
        text="Status: Bereit\nKilometer: 0.00 km",
        font_size=52,  # Riesig und gut lesbar!
        halign="center",
        valign="middle",
        bold=True,
        color=(0.1, 1.0, 0.3, 1),  # Leuchtendes Matrix-Grün
        size_hint=(1, 0.35),
    )
    self.status_label.bind(size=self.status_label.setter("text_size"))
    root_layout.add_widget(self.status_label)

    # 3. UNTERER BEREICH: 3 Buttons mit großer Schrift
    btn_layout = BoxLayout(
        orientation="horizontal", spacing=10, size_hint=(1, 0.25)
    )

    btn_start = Button(
        text="SCHICHT\nSTART",
        background_color=(0.1, 0.85, 0.3, 1),
        font_size=22,
        bold=True,
    )
    btn_start.bind(on_press=self.start_shift)

    btn_end = Button(
        text="FEIERABEND",
        background_color=(0.85, 0.2, 0.2, 1),
        font_size=22,
        bold=True,
    )
    btn_end.bind(on_press=self.prompt_feierabend)

    btn_logcat = Button(
        text="LOGCAT\n(FEHLER)",
        background_color=(0.1, 0.5, 0.9, 1),
        font_size=22,
        bold=True,
    )
    btn_logcat.bind(on_press=self.show_logcat_popup)

    btn_layout.add_widget(btn_start)
    btn_layout.add_widget(btn_end)
    btn_layout.add_widget(btn_logcat)

    root_layout.add_widget(btn_layout)

    # Regelmäßig Daten einlesen
    Clock.schedule_interval(self.check_status_file, 3)

    return root_layout

  def _update_bg(self, instance, value):
    self.bg_rect.size = instance.size
    self.bg_rect.pos = instance.pos

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
        font_size=24,
        halign="center",
        bold=True,
    )
    lbl_popup.bind(size=lbl_popup.setter("text_size"))
    content.add_widget(lbl_popup)

    self.pause_input = TextInput(
        text="45", multiline=False, input_filter="int", font_size=28
    )
    content.add_widget(self.pause_input)

    btn_confirm = Button(
        text="Bestätigen & Beenden",
        background_color=(0.1, 0.5, 0.9, 1),
        font_size=22,
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

    lbl_log = Label(text=log_text, font_size=20, halign="left", valign="top")
    lbl_log.bind(size=lbl_log.setter("text_size"))
    content.add_widget(lbl_log)

    btn_close = Button(
        text="Schließen", size_hint=(1, 0.25), font_size=22, bold=True
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
