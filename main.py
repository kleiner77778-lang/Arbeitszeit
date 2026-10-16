import json
import os
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class LKWTrackerApp(App):

  def build(self):
    self.title = "LKW Tracker"
    layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

    self.status_label = Label(
        text="LKW Tracker ist bereit\nWarte auf Status...",
        font_size=20,
        halign='center',
        valign='middle',
    )
    self.status_label.bind(size=self.status_label.setter('text_size'))

    btn_refresh = Button(
        text="Status aktualisieren", size_hint=(1, 0.3), font_size=18
    )
    btn_refresh.bind(on_press=self.update_status)

    layout.add_widget(self.status_label)
    layout.add_widget(btn_refresh)

    # Alle 3 Sekunden automatisch den Status einlesen
    Clock.schedule_interval(self.check_status_file, 3)

    return layout

  def check_status_file(self, dt):
    status_file = 'status.json'
    if os.path.exists(status_file):
      try:
        with open(status_file, 'r') as f:
          data = json.load(f)
          lat = data.get('lat', 0.0)
          lon = data.get('lon', 0.0)
          status = data.get('status', 'Unbekannt')
          self.status_label.text = (
              f'Status: {status}\nLat: {lat:.4f}\nLon: {lon:.4f}'
          )
      except Exception as e:
        pass

  def update_status(self, instance):
    self.check_status_file(0)


if __name__ == '__main__':
  LKWTrackerApp().run()
