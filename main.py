import json
import os
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

try:
  from android.permissions import Permission, request_permissions

  ANDROID_PLATFORM = True
except ImportError:
  ANDROID_PLATFORM = False


class LKWTrackerApp(App):

  def build(self):
    self.title = "LKW Tracker"
    self.check_and_request_permissions()

    # Reines, stabiles Layout mit einem satten Hintergrundfarbton per Label oder reinem BoxLayout
    root_layout = BoxLayout(orientation="vertical", padding=15, spacing=15)

    # 1. OBERER BEREICH: Das Lkw-Bild als Banner
    if os.path.exists("icon.png"):
      img_banner = Image(
          source="icon.png",
          size_hint=(1, 0.35),
          allow_stretch=True,
          keep_ratio=True,
      )
      root_layout.add_widget(img_banner)

    # 2. STATUS-BEREICH: Riesige Schrift, absolut minimalistisch
    self.status_label = Label(
        text="Status: Bereit\nKilometer: 0.00 km",
        font_size=50,
        halign="center",
        valign="middle",
        bold=True,
        color=(0.1, 1.0, 0.3, 1),
        size_hint=(1, 0.4),
    )
    self.status_label.bind(size=self.status_label.setter("text_size"))
    root_layout.add_widget(self.status_label)

    # 3. BUTTONS: Die 3 Hauptfunktionen unten
    btn_layout = BoxLayout(
        orientation="horizontal", spacing=10, size_hint=(1, 0.25)
    )

    btn_start = Button(
        text="SCHICHT\nSTART",
        background_color=(0.1, 0.8, 0.3, 1),
        font_size=22,
        bold=True,
    )
    btn_start.bind(on_press=self.start_shift)

    btn_end = Button(
        text="FEIERABEND",
        background_color=(0.8, 0.2, 0.2, 1),
        font_size=22,
        bold=True,
    )
    btn_end.bind(on_press=self.prompt_feierabend)

    btn_logcat = Button(
        text="LOGCAT\n(FEHLER)",
        background_color=(0.2, 0.5, 0.9, 1),
        font_size=22,
        bold=True,
    )
    btn_logcat.bind(on_press=self.show_logcat_popup)

    btn_layout.add_widget(btn_start)
    btn_layout.add_widget(btn_end)
    btn_layout.add_widget(btn_logcat)

    root_layout.add_widget(btn_layout)

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
      except:
        pass

  def start_shift(self, instance):
    self.update_command("START")
    self.status_label.text = "Status: Schicht aktiv!\nGPS zeichnet auf..."

  def prompt_feierabend(self, instance):
    content = BoxLayout(orientation="vertical", padding=20, spacing=15)
    lbl = Label(
        text="FEIERABEND!\nPause in Minuten:", font_size=24, bold=True
    )
    content.add_widget(lbl)

    self.pause_input = TextInput(
        text="45", multiline=False, input_filter="int", font_size=28
    )
    content.add_widget(self.pause_input)

    btn_confirm = Button(
        text="Bestätigen & Beenden",
        background_color=(0.2, 0.5, 0.9, 1),
        font_size=22,
        bold=True,
    )
    popup = Popup(
        title="Schicht beenden",
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
        f"Status: Schicht beendet.\nPause: {pause_min} Min."
    )

  def show_logcat_popup(self, instance):
    content = BoxLayout(orientation="vertical", padding=15, spacing=10)
    log_text = "Android System aktiv." if ANDROID_PLATFORM else "Testmodus."
    lbl = Label(text=log_text, font_size=20)
    content.add_widget(lbl)
    btn_close = Button(text="Schließen", font_size=22, bold=True)
    popup = Popup(
        title="Logcat", content=content, size_hint=(0.9, 0.7), auto_dismiss=True
    )
    btn_close.bind(on_press=popup.dismiss)
    content.add_widget(btn_close)
    popup.open()

  def update_command(self, cmd, pause=0):
    try:
      data = {
          "command": cmd,
          "pause_minutes": int(pause),
          "timestamp": time.time(),
      }
      with open("command.json", "w") as f:
        json.dump(data, f)
    except:
        pass

  def check_status_file(self, dt):
    if os.path.exists("status.json"):
      try:
        with open("status.json", "r") as f:
          data = json.load(f)
          self.status_label.text = f"Status: {data.get('status', 'Inaktiv')}\nKilometer: {data.get('km', 0.0):.2f} km"
      except:
        pass


if __name__ == "__main__":
  LKWTrackerApp().run()
