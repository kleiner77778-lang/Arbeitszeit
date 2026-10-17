import json
import os
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

# Dateipfade für IPC mit dem Hintergrunddienst
STATUS_FILE = "status.json"
COMMAND_FILE = "command.json"


class LkwTrackerLayout(BoxLayout):

  def __init__(self, **kwargs):
    super(LkwTrackerLayout, self).__init__(**kwargs)
    self.orientation = "vertical"
    self.padding = 30
    self.spacing = 20

    # Titel
    self.add_widget(
        Label(
            text="LKW TRACKER",
            font_size="32sp",
            bold=True,
            halign="center",
            size_hint_y=None,
            height=80,
    )
    )

    # Status-Anzeige
    self.status_label = Label(
        text="Tracking gestoppt", font_size="22sp", halign="center"
    )
    self.add_widget(self.status_label)

    # GPS-Koordinaten / KM Anzeige
    self.info_label = Label(
        text="Warte auf GPS-Signal ...", font_size="18sp", halign="center"
    )
    self.add_widget(self.info_label)

    # Start / Stop Button
    self.toggle_btn = Button(
        text="Tracking starten",
        font_size="22sp",
        size_hint_y=None,
        height=70,
        background_color=(0.2, 0.6, 0.2, 1),
    )
    self.toggle_btn.bind(on_press=self.toggle_tracking)
    self.add_widget(self.toggle_btn)

    # Telegram Status Label
    self.telegram_label = Label(
        text="Telegram: Nicht konfiguriert",
        font_size="14sp",
        halign="center",
        size_hint_y=None,
        height=40,
    )
    self.add_widget(self.telegram_label)

    # Regelmäßiger Check der status.json vom Hintergrunddienst
    Clock.schedule_interval(self.update_from_service, 1.0)
    self.is_active = False

  def toggle_btn_style(self):
    if self.is_active:
      self.toggle_btn.text = "Tracking stoppen"
      self.toggle_btn.background_color = (0.8, 0.2, 0.2, 1)
    else:
      self.toggle_btn.text = "Tracking starten"
      self.toggle_btn.background_color = (0.2, 0.6, 0.2, 1)

  def toggle_tracking(self, instance):
    self.is_active = not self.is_active
    self.toggle_btn_style()

    # Befehl für den Hintergrunddienst schreiben
    cmd = "START" if self.is_active else "STOP"
    try:
      with open(COMMAND_FILE, "w") as f:
        json.dump({"command": cmd}, f)
    except Exception as e:
      print(f"Fehler beim Schreiben des Befehls: {e}")

  def update_from_service(self, dt):
    """Liest periodisch die status.json aus, die der Dienst aktualisiert."""
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
