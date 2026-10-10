import os
import sqlite3
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

def get_db_path():
    try:
        app = App.get_running_app()
        if app and app.user_data_dir:
            if not os.path.exists(app.user_data_dir):
                os.makedirs(app.user_data_dir)
            return os.path.join(app.user_data_dir, 'arbeitszeiten_app.db')
    except Exception:
        pass
    return 'arbeitszeiten_app.db'

def init_db():
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schichten (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datum TEXT,
                start_zeit TEXT,
                ende_zeit TEXT,
                pause_min INTEGER DEFAULT 0,
                netto_min INTEGER DEFAULT 0,
                status TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stopps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schicht_id INTEGER,
                zeitstempel TEXT,
                typ TEXT,
                latitude REAL,
                longitude REAL
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Init Fehler: {e}")

class LkwTrackerApp(App):
    aktuelle_schicht_id = None

    def build(self):
        init_db()
        
        # Hauptlayout mit äußerem Abstand
        root_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Freiraum oben
        root_layout.add_widget(Widget(size_hint_y=0.1))

        # Titel
        root_layout.add_widget(Label(
            text="LKW Arbeitszeit & GPS Tracker",
            font_size='20sp',
            bold=True,
            size_hint_y=None,
            height='40dp',
            halign='center'
        ))

        # Statusanzeige
        self.status_label = Label(
            text="Status: Keine aktive Schicht",
            font_size='16sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height='35dp',
            halign='center'
        )
        root_layout.add_widget(self.status_label)
        
        root_layout.add_widget(Widget(size_hint_y=0.05))

        # Button-Container (kleinere, kompakte Buttons)
        btn_layout = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, height='270dp')

        btn_start = Button(text="SCHICHTSTART", font_size='16sp', bold=True, size_hint_y=None, height='45dp', background_color=(0.1, 0.6, 0.3, 1))
        btn_start.bind(on_release=lambda x: self.schicht_starten())
        btn_layout.add_widget(btn_start)

        btn_ankunft = Button(text="ANKUNFT / STOPP", font_size='16sp', bold=True, size_hint_y=None, height='45dp', background_color=(0.1, 0.4, 0.8, 1))
        btn_ankunft.bind(on_release=lambda x: self.stopp_erfassen("Ankunft"))
        btn_layout.add_widget(btn_ankunft)

        btn_weiterfahrt = Button(text="WEITERFAHRT", font_size='16sp', bold=True, size_hint_y=None, height='45dp', background_color=(0.8, 0.5, 0.1, 1))
        btn_weiterfahrt.bind(on_release=lambda x: self.stopp_erfassen("Weiterfahrt"))
        btn_layout.add_widget(btn_weiterfahrt)

        btn_feierabend = Button(text="FEIERABEND", font_size='16sp', bold=True, size_hint_y=None, height='45dp', background_color=(0.8, 0.2, 0.2, 1))
        btn_feierabend.bind(on_release=lambda x: self.feierabend_dialog_oeffnen())
        btn_layout.add_widget(btn_feierabend)

        btn_berichte = Button(text="SCHICHTBERICHTE", font_size='16sp', bold=True, size_hint_y=None, height='45dp', background_color=(0.4, 0.4, 0.4, 1))
        btn_berichte.bind(on_release=lambda x: self.schichtberichte_anzeigen())
        btn_layout.add_widget(btn_berichte)

        root_layout.add_widget(btn_layout)

        # Freiraum unten
        root_layout.add_widget(Widget(size_hint_y=0.1))

        return root_layout

    def get_gps_location(self):
        try:
            from plyer import gps
            gps.configure(on_location=self.on_gps_location)
            gps.start()
        except Exception:
            pass
        return 47.6970, 8.5786

    def on_gps_location(self, **kwargs):
        self.current_lat = kwargs.get('lat', 47.6970)
        self.current_lon = kwargs.get('lon', 8.5786)

    def schicht_starten(self):
        now = datetime.now()
        datum_str = now.strftime("%Y-%m-%d")
        start_str = now.strftime("%H:%M:%S")

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO schichten (datum, start_zeit, status) VALUES (?, ?, 'aktiv')",
            (datum_str, start_str)
        )
        self.aktuelle_schicht_id = cursor.lastrowid
        conn.commit()
        conn.close()

        self.status_label.text = f"Schicht aktiv seit {start_str[:5]} Uhr"

    def stopp_erfassen(self, typ):
        if not self.aktuelle_schicht_id:
            self.status_label.text = "Bitte zuerst Schicht starten!"
            return

        now_str = datetime.now().strftime("%H:%M:%S")
        lat, lon = self.get_gps_location()

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO stopps (schicht_id, zeitstempel, typ, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
            (self.aktuelle_schicht_id, now_str, typ, lat, lon)
        )
        conn.commit()
        conn.close()

        self.status_label.text = f"{typ} erfasst um {now_str[:5]} Uhr"

    def feierabend_dialog_oeffnen(self):
        if not self.aktuelle_schicht_id:
            self.status_label.text = "Keine aktive Schicht!"
            return

        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        content.add_widget(Label(text="Pausenminuten eingeben:", font_size='16sp'))
        
        self.pause_input = TextInput(text="45", font_size='18sp', multiline=False, input_filter='int')
        content.add_widget(self.pause_input)

        btn_layout = BoxLayout(size_hint_y=None, height='50dp', spacing=10)
        btn_abbrechen = Button(text="Abbrechen")
        btn_speichern = Button(text="Speichern", background_color=(0.1, 0.6, 0.3, 1))

        self.popup = Popup(title="Feierabend & Pause", content=content, size_hint=(0.8, 0.4))
        
        btn_abbrechen.bind(on_release=self.popup.dismiss)
        btn_speichern.bind(on_release=lambda x: self.schicht_beenden())

        btn_layout.add_widget(btn_abbrechen)
        btn_layout.add_widget(btn_speichern)
        content.add_widget(btn_layout)

        self.popup.open()

    def schicht_beenden(self):
        try:
            pause_min = int(self.pause_input.text) if self.pause_input.text else 0
        except ValueError:
            pause_min = 0

        now = datetime.now()
        ende_str = now.strftime("%H:%M:%S")

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute("SELECT start_zeit FROM schichten WHERE id = ?", (self.aktuelle_schicht_id,))
        row = cursor.fetchone()
        start_str = row[0] if row else "00:00:00"

        fmt = "%H:%M:%S"
        t_start = datetime.strptime(start_str, fmt)
        t_ende = datetime.strptime(ende_str, fmt)
        brutto_min = int((t_ende - t_start).total_seconds() / 60)
        netto_min = max(0, brutto_min - pause_min)

        cursor.execute(
            "UPDATE schichten SET ende_zeit = ?, pause_min = ?, netto_min = ?, status = 'beendet' WHERE id = ?",
            (ende_str, pause_min, netto_min, self.aktuelle_schicht_id)
        )
        conn.commit()
        conn.close()

        if self.popup:
            self.popup.dismiss()
            
        self.aktuelle_schicht_id = None
        
        h, m = divmod(netto_min, 60)
        self.status_label.text = f"Feierabend! Netto: {h}h {m}m"

    def schichtberichte_anzeigen(self):
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT datum, start_zeit, ende_zeit, netto_min, status FROM schichten ORDER BY id DESC LIMIT 10")
        schichten = cursor.fetchall()
        conn.close()

        bericht_text = "Letzte Schichten:\n\n"
        if not schichten:
        # Falls keine Daten vorhanden sind
            bericht_text += "Noch keine Schichten aufgezeichnet."
        else:
            for s in schichten:
                datum, start, ende, netto, status = s
                netto_h, netto_m = divmod(netto if netto else 0, 60)
                ende_zeit = ende[:5] if ende else "Aktiv"
                start_zeit = start[:5] if start else ""
                bericht_text += f"📅 {datum}\n⏱️ {start_zeit} - {ende_zeit} | Netto: {netto_h}h {netto_m}m\nStatus: {status}\n--------------------\n"

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        scroll = ScrollView(size_hint=(1, 0.8))
        lbl = Label(text=bericht_text, font_size='14sp', size_hint_y=None, halign='left', valign='top')
        lbl.bind(texture_size=lambda *x: setattr(lbl, 'height', lbl.texture_size[1]))
        scroll.add_widget(lbl)
        content.add_widget(scroll)

        btn_schliessen = Button(text="Schließen", size_hint_y=None, height='45dp')
        popup = Popup(title="Schichtberichte", content=content, size_hint=(0.9, 0.8))
        btn_schliessen.bind(on_release=popup.dismiss)
        content.add_widget(btn_schliessen)

        popup.open()

if __name__ == '__main__':
    LkwTrackerApp().run()
