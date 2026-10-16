import os
import threading
import time
import requests

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout

# GPS-Unterstützung
from plyer import gps


KV_CODE = """
<TrackerLayout>:
    orientation: "vertical"
    padding: "20dp"
    spacing: "15dp"

    Label:
        text: "LKW TRACKER"
        font_size: "26sp"
        bold: True
        size_hint_y: None
        height: "60dp"

    Label:
        text: root.status_text
        font_size: "17sp"
        halign: "center"
        valign: "middle"
        text_size: self.width, None

    Label:
        text: root.location_text
        font_size: "16sp"
        halign: "center"
        valign: "middle"
        text_size: self.width, None

    Button:
        text: "Tracking starten" if not root.tracking else "Tracking stoppen"
        size_hint_y: None
        height: "60dp"
        on_release: root.toggle_tracking()

    Label:
        text: "Telegram: " + root.telegram_status
        font_size: "14sp"
        size_hint_y: None
        height: "40dp"
"""


class TrackerLayout(BoxLayout):
    status_text = StringProperty("Bereit")
    location_text = StringProperty("Warte auf GPS-Standort ...")
    telegram_status = StringProperty("Nicht konfiguriert")
    tracking = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.latitude = None
        self.longitude = None
        self.accuracy = None

        self.last_send = 0
        self.send_interval = 60

        # Telegram-Daten hier eintragen
        self.telegram_token = ""
        self.telegram_chat_id = ""

        self.telegram_enabled = bool(
            self.telegram_token and self.telegram_chat_id
        )

        if self.telegram_enabled:
            self.telegram_status = "Konfiguriert"

        self._gps_started = False

    def toggle_tracking(self):
        if self.tracking:
            self.stop_tracking()
        else:
            self.start_tracking()

    def start_tracking(self):
        self.tracking = True
        self.status_text = "GPS wird gestartet ..."
        self.location_text = "Warte auf GPS-Signal ..."

        try:
            gps.configure(
                on_location=self.on_location,
                on_status=self.on_gps_status
            )

            gps.start(
                minTime=5000,
                minDistance=10
            )

            self._gps_started = True
            self.status_text = "Tracking aktiv"

        except NotImplementedError:
            self.status_text = "GPS auf diesem Gerät nicht verfügbar"

        except Exception as exc:
            self.status_text = f"GPS-Fehler: {exc}"
            self.tracking = False

    def stop_tracking(self):
        self.tracking = False

        if self._gps_started:
            try:
                gps.stop()
            except Exception:
                pass

            self._gps_started = False

        self.status_text = "Tracking gestoppt"

    def on_location(self, **kwargs):
        latitude = kwargs.get("lat")
        longitude = kwargs.get("lon")
        accuracy = kwargs.get("accuracy")

        if latitude is None or longitude is None:
            return

        Clock.schedule_once(
            lambda dt: self.update_location(
                latitude,
                longitude,
                accuracy
            )
        )

    def update_location(self, latitude, longitude, accuracy):
        self.latitude = latitude
        self.longitude = longitude
        self.accuracy = accuracy

        accuracy_text = (
            f"{accuracy:.1f} m"
            if isinstance(accuracy, (int, float))
            else "unbekannt"
        )

        self.location_text = (
            f"Breitengrad: {latitude:.6f}\n"
            f"Längengrad: {longitude:.6f}\n"
            f"Genauigkeit: {accuracy_text}"
        )

        self.status_text = "GPS-Position empfangen"

        if self.tracking:
            now = time.time()

            if now - self.last_send >= self.send_interval:
                self.last_send = now

                if self.telegram_enabled:
                    threading.Thread(
                        target=self.send_telegram_location,
                        daemon=True
                    ).start()

    def on_gps_status(self, stype, status):
        Clock.schedule_once(
            lambda dt: self.set_gps_status(stype, status)
        )

    def set_gps_status(self, stype, status):
        self.status_text = f"GPS: {status}"

    def send_telegram_location(self):
        if not self.telegram_enabled:
            return

        url = (
            "https://api.telegram.org/"
            f"bot{self.telegram_token}/sendLocation"
        )

        data = {
            "chat_id": self.telegram_chat_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

        try:
            response = requests.post(
                url,
                data=data,
                timeout=15
            )

            response.raise_for_status()
            result = response.json()

            if result.get("ok"):
                message = "Standort erfolgreich gesendet"
            else:
                message = "Telegram konnte Standort nicht senden"

        except Exception as exc:
            message = f"Telegram-Fehler: {exc}"

        Clock.schedule_once(
            lambda dt: self.set_telegram_status(message)
        )

    def set_telegram_status(self, message):
        self.telegram_status = message


class LKWTrackerApp(App):
    def build(self):
        Builder.load_string(KV_CODE)
        return TrackerLayout()

    def on_pause(self):
        # Android darf die App pausieren.
        # Ein echter Hintergrunddienst muss separat eingerichtet werden.
        return True

    def on_stop(self):
        # GPS im Hintergrund wird durch diese Hauptdatei allein
        # nicht garantiert.
        pass


if __name__ == "__main__":
    LKWTrackerApp().run()
