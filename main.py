from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from jnius import autoclass

class LkwTrackerApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        self.label = Label(
            text='LKW Tracker\nAndroid 14+ bereit', 
            font_size=22, 
            halign='center'
        )
        layout.add_widget(self.label)
        
        btn_start = Button(
            text='Hintergrund-Dienst starten', 
            font_size=18, 
            size_hint=(1, 0.25)
        )
        btn_start.bind(on_press=self.start_tracking_service)
        layout.add_widget(btn_start)
        
        # Berechtigungen beim App-Start automatisch anfordern
        if platform == 'android':
            self.request_android_permissions()
            
        return layout

    def request_android_permissions(self):
        def callback(permissions, results):
            if all(results):
                self.label.text = "Alle Berechtigungen erteilt!\nBereit zum Start."
            else:
                self.label.text = "Achtung: Berechtigungen\nwurden abgelehnt!"

        request_permissions([
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION,
            Permission.INTERNET
        ], callback)

    def start_tracking_service(self, instance):
        if platform == 'android':
            try:
                # Start des Python Foreground Services über python-for-android
                PYTHON_SERVICE_CLASS = 'org.kivy.android.PythonService'
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                Intent = autoclass('android.content.Intent')
                
                service_intent = Intent(activity, autoclass(PYTHON_SERVICE_CLASS))
                service_intent.putExtra('android.app.inctype', 'service')
                service_intent.putExtra('python.service.argument', '')
                
                # Für Android 14+ zwingend als Foreground Service starten
                if hasattr(activity, 'startForegroundService'):
                    activity.startForegroundService(service_intent)
                else:
                    activity.startService(service_intent)
                    
                self.label.text = "Hintergrund-Dienst\nerfolgreich gestartet!"
            except Exception as e:
                self.label.text = f"Fehler beim Start:\n{str(e)}"
        else:
            self.label.text = "Desktop-Modus:\nForeground-Service läuft nur auf Android."

if __name__ == '__main__':
    LkwTrackerApp().run()
