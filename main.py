from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform

if platform == 'android':
  from android.permissions import Permission, request_permissions
  import jnius

# Kivy Benutzeroberfläche (ohne den unnötigen Rechte-Button)
KV = """
BoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 20
    
    Label:
        text: "LKW GPS & Arbeitszeit-Tracker"
        font_size: 24
        halign: 'center'
        
    Button:
        text: "Schicht Starten"
        size_hint_y: None
        height: '50dp'
        
    Button:
        text: "Schicht Beenden"
        size_hint_y: None
        height: '50dp'
"""


class MainApp(App):

  def build(self):
    return Builder.load_string(KV)

  def on_start(self):
    # Wird sofort beim Start der App ausgeführt
    if platform == 'android':
      self.request_permissions_and_start()
    else:
      print('Desktop-Modus: Kein Android-Dienst aktiv.')

  def request_permissions_and_start(self):
    """Fordert automatisch alle notwendigen Berechtigungen an

    und startet danach den Dienst.
    """

    def permission_callback(permissions, results):
      # Dienst unabhängig davon starten, ob erteilt oder nicht,
      # damit der Service in jedem Fall anläuft.
      self.start_background_service()

    # Android-Laufzeitberechtigungen für den genauen und groben Standort abfragen
    request_permissions(
        [Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION],
        permission_callback,
    )

  def start_background_service(self):
    """Startet den Android-Hintergrunddienst im Hintergrund."""
    try:
      PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
      activity = PythonActivity.mActivity
      Context = jnius.autoclass('android.content.Context')
      Intent = jnius.autoclass('android.content.Intent')
      PythonService = jnius.autoclass('org.kivy.android.PythonService')

      # Dienst via Intent starten
      service_intent = Intent(activity, PythonService)
      service_intent.putExtra('android.intent.extra.TITLE', 'LKW Tracker')
      activity.startService(service_intent)
      print('Hintergrunddienst erfolgreich gestartet!')
    except Exception as e:
      print(f'Fehler beim Starten des Dienstes: {e}')


if __name__ == '__main__':
  MainApp().run()
