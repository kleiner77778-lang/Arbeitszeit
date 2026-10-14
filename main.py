from kivy.app import App
from kivy.uix.label import Label

class MinimalLkwApp(App):
    def build(self):
        return Label(
            text="LKW Tracker - Basis läuft!",
            font_size=24,
            halign='center'
        )

if __name__ == '__main__':
    MinimalLkwApp().run()
