from kivy.app import App
from kivy.uix.label import Label


class LKWTrackerApp(App):

  def build(self):
    return Label(text="LKW Tracker bereit", font_size=32)


if __name__ == "__main__":
  LKWTrackerApp().run()
