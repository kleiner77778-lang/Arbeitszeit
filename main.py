from kivy.app import App
from kivy.uix.label import Label

class LkwTrackerApp(App):
    def build(self):
        return Label(text='LKW Tracker MVP läuft!')

if __name__ == '__main__':
    LkwTrackerApp().run()
