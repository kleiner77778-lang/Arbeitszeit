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


class LKWTrackerApp(App):

  def build(self):
    self.title = "LKW Tracker - Zeiterfassung"
    layout = BoxLayout(orientation='vertical', padding=25, spacing=15)

    # Status-Anzeige
    self.status_label = Label(
        text=(
            "Lkw Tracker bereit\nStatus: Schicht inaktiv\nGefahrene km: 0.0"
        ),
        font_size=18,
        halign='center',
        valign='middle',
    )
    self.status_label.bind(size=self.status_label.setter('text_size'))
    layout.add_widget(self.status_label)

    # Steuerungs-Buttons
    btn_start = Button(
        text="Schicht Start",
        background_color=(0.1, 0.6, 0.1, 1),
        font_size=18,
    )
    btn_start.bind(on_press=self.start_shift)
    layout.add_widget(btn_start)

    btn_end = Button(
        text="Feierabend", background_color=(0.8, 0.2, 0.2, 1), font_size=18
    )
    btn_end.bind(on_press=self.prompt_feierabend)
    layout.add_widget(btn_end)

    # Regelmäßig Daten einlesen
    Clock.schedule_interval(self.check_status_file, 3)

    return layout

  def start_shift(self, instance):
    self.update_command("START")
    self.status_label.text = "Schicht gestartet! GPS zeichnet auf..."

  def prompt_feierabend(self, instance):
    content = BoxLayout(orientation='vertical', padding=20, spacing=15)
    content.add_widget(
        Label(
            text="Feierabend! Bitte Pause in Minuten eintragen:", font_size=16
        )
    )

    self.pause_input = TextInput(
        text="45", multiline=False, input_filter="int", font_size=20
    )
    content.add_widget(self.pause_input)

    btn_confirm = Button(
        text="Bestätigen & Schicht beenden",
        background_color=(0.2, 0.4, 0.8, 1),
        font_size=16,
    )

    popup = Popup(
        title="Schicht beenden & Pause",
        content=content,
        size_hint=(0.8, 0.5),
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
        f"Schicht beendet.\nPause von {pause_min} Min. eingetragen."
    )

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
              f"Status: {status}\nGefahrene km: {km:.2f}"
          )
      except:
        pass


if __name__ == "__main__":
  LKWTrackerApp().run()
