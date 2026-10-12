import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.utils import platform
import subprocess

class LKWTrackerApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.label = Label(
            text="Klicke auf den Button, um den System-Fehler (Logcat) auszulesen:",
            size_hint_y=None,
            height="50dp",
            halign='center'
        )
        layout.add_widget(self.label)
        
        # Textfeld, das den echten Android-Fehler anzeigt
        self.log_output = TextInput(
            text="Noch keine Logs geladen...",
            readonly=True,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(0, 1, 0, 1)  # Grüner Hacker-Look
        )
        layout.add_widget(self.log_output)
        
        btn = Button(
            text="Fehler via Logcat auslesen",
            size_hint_y=None,
            height="60dp",
            background_color=(0.2, 0.6, 0.8, 1)
        )
        btn.bind(on_press=self.fetch_logs)
        layout.add_widget(btn)
        
        return layout

    def fetch_logs(self, instance):
        if platform == 'android':
            try:
                # Holt die letzten Python- und Laufzeitfehler aus dem Android-System
                cmd = ['logcat', '-d', '-s', 'python:V', 'AndroidRuntime:E', 'crontab:V']
                output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
                
                # Nur die letzten Zeilen anzeigen, damit es ins Display passt
                lines = output.splitlines()
                recent_logs = "\n".join(lines[-30:]) if len(lines) > 30 else output
                
                self.log_output.text = recent_logs if recent_logs.strip() else "Keine Fehler-Logs im Puffer gefunden."
            except Exception as e:
                self.log_output.text = f"Konnte Logcat nicht abrufen: {str(e)}"
        else:
            self.log_output.text = "Logcat funktioniert nur direkt auf dem Android-Gerät."

if __name__ == '__main__':
    LKWTrackerApp().run()
