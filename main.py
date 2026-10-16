import json
import os
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

# Android-spezifische Berechtigungen prüfen/anfordern, falls verfügbar
try:
  from android.permissions import request_permissions, Permission
  ANDROID_PLATFORM = True
except ImportError:
  ANDROID_PLATFORM = False


class LKWTrackerApp(App):

  def build(self):
    self.title = "LKW Tracker - Zeiterfassung"

    # Beim Start direkt Berechtigungen anfordern (falls Android)
    self.check_and_request_permissions()

    # Hauptlayout
    root_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

    # 1. OBERER BEREICH: Extra große, fette Status-Anzeige für Brillenträger
    self.status_label = Label(
        text="Status: Bereit\nKilometer: 0.00 km",
        font_size=36,  # Nochmals deutlich vergrößert!
        halign='center',
        valign='middle',
        bold=True,
    )
    self.status_label.bind(size=self.status_label.setter('text_size'))
    root_layout.add_widget(self.status_label)

    # 2. UNTERER BEREICH: 3 Kompakte Buttons nebeneinander am Rand (größere Schrift)
    btn_layout = BoxLayout(
        orientation='horizontal', spacing=10, size_hint=(1, 0.25)
    )

    btn_start = Button(
        text="Schicht\nStart",
        background_color=(0.1, 0.6, 0.1, 1),
        font_size=20,  # Größere Button-Schrift
        bold=True,
    )
    btn_start.bind(on_press=self.start_shift)

    btn_end = Button(
        text="Feierabend",
        background_color=(0.8, 0.2, 0.2, 1),
        font_size=20,  # Größere Button-Schrift
        bold=True,
    )
    btn_end.bind(on_press=self.prompt_feierabend)

    btn_logcat = Button(
        text="Logcat\n(Fehler)",
        background_color=(0.2, 0.4, 0.8, 1),
        font_size=20,  # Größere Button-Schrift
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
    content = BoxLayout(orientation='vertical', padding=20, spacing=15)

    lbl_popup = Label(
        text="Feierabend!\nBitte Pause in Minuten eintragen:",
        font_size=22,
        halign='center',
        bold=True,
    )
    lbl_popup.bind(size=lbl_popup.setter('text_size'))
    content.add_widget(lbl_popup)

    self.pause_input = TextInput(
        text="45", multiline=False, input_filter="int", font_size=28
    )
    content.add_widget(self.pause_input)

    btn_confirm = Button(
        text="Bestätigen & Schicht beenden",
        background_color=(0.2, 0.4, 0.8, 1),
        font_size=20,
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
    content = BoxLayout(orientation='vertical', padding=15, spacing=10)

    log_text = "System-Logs / Berechtigungsstatus:\n"
    if ANDROID_PLATFORM:
      log_text += "Android-Plattform aktiv.\nBerechtigungen wurden angefordert.\n"
      log_text += (
          "Tipp: Für detaillierte Logs ADB / Logcat auf dem PC nutzen."
      )
    else:
      log_text += (
          "Läuft im Test-Modus (kein Android-Gerät erkannt).\nGPS/Logcat"
          " simuliert."
      )

    lbl_log = Label(text=log_text, font_size=18, halign='left', valign='top')
    lbl_log.bind(size=lbl_log.setter('text_size'))
    content.add_widget(lbl_log)

    btn_close = Button(
        text="Schließen", size_hint=(1, 0.25), font_size=20, bold=True
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
