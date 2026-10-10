import os
import sqlite3
from datetime import datetime
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField

def get_db_path():
    try:
        app = MDApp.get_running_app()
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

KV = '''
MDScreen:
    md_bg_color: 0.1, 0.1, 0.1, 1

    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "15dp"

        MDLabel:
            text: "LKW Arbeitszeit & GPS Tracker"
            font_style: "H5"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            size_hint_y: None
            height: "40dp"

        MDLabel:
            id: status_label
            text: "Status: Bereitschaft"
            font_style: "Subtitle1"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0.8, 0.8, 0.8, 1
            size_hint_y: None
            height: "30dp"

        MDRaisedButton:
            text: "🟢 SCHICHTSTART"
            font_size: "18sp"
            size_hint: (1, 0.18)
            md_bg_color: 0.1, 0.7, 0.3, 1
            on_release: app.schicht_starten()

        MDRaisedButton:
            text: "📍 ANKUNFT / STOPP"
            font_size: "18sp"
            size_hint: (1, 0.18)
            md_bg_color: 0.2, 0.5, 0.9, 1
            on_release: app.stopp_erfassen("Ankunft")

        MDRaisedButton:
            text: "🚛 WEITERFAHRT"
            font_size: "18sp"
            size_hint: (1, 0.18)
            md_bg_color: 0.9, 0.6, 0.1, 1
            on_release: app.stopp_erfassen("Weiterfahrt")

        MDRaisedButton:
            text: "🔴 FEIERABEND"
            font_size: "18sp"
            size_hint: (1, 0.18)
            md_bg_color: 0.8, 0.2, 0.2, 1
            on_release: app.feierabend_dialog_oeffnen()
'''

class LkwTrackerApp(MDApp):
    dialog = None
    aktuelle_schicht_id = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        init_db()
        return Builder.load_string(KV)

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

        self.root.ids.status_label.text = f"Schicht aktiv seit {start_str[:5]} Uhr"

    def stopp_erfassen(self, typ):
        if not self.aktuelle_schicht_id:
            self.root.ids.status_label.text = "⚠️ Bitte zuerst Schicht starten!"
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

        self.root.ids.status_label.text = f"📍 {typ} erfasst um {now_str[:5]} Uhr"

    def feierabend_dialog_oeffnen(self):
        if not self.aktuelle_schicht_id:
            self.root.ids.status_label.text = "⚠️ Keine aktive Schicht!"
            return

        self.pause_input = MDTextField(
            hint_text="Pausenminuten eingeben (z. B. 45)",
            input_filter="int"
        )
        self.dialog = MDDialog(
            title="Feierabend & Pause",
            type="custom",
            content_cls=self.pause_input,
            buttons=[
                MDFlatButton(text="Abbrechen", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Speichern", on_release=lambda x: self.schicht_beenden())
            ],
        )
        self.dialog.open()

    def schicht_beenden(self):
        pause_min = int(self.pause_input.text) if self.pause_input.text and self.pause_input.text.isdigit() else 0
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

        self.dialog.dismiss()
        self.aktuelle_schicht_id = None
        
        h, m = divmod(netto_min, 60)
        self.root.ids.status_label.text = f"Feierabend! Netto-Arbeitszeit: {h}h {m}m"

if __name__ == '__main__':
    LkwTrackerApp().run()
