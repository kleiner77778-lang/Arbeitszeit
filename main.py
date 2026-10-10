import os
import sqlite3
import random
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.clock import Clock

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

class MatrixRain(FloatLayout):
    """Echter Matrix-Digital-Rain im Hintergrund"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = []
        self.chars = "0123456789ABCDEFXYZ$#@*%&+-<>~"
        Clock.schedule_once(self.init_matrix, 0.5)

    def init_matrix(self, dt):
        self.clear_widgets()
        self.cols = []
        col_width = 30
        num_cols = int(self.width / col_width) if self.width > 0 else 30
        
        for i in range(num_cols):
            lbl = Label(
                text="",
                font_size='14sp',
                color=(0.1, 0.95, 0.3, 0.8),
                pos=(i * col_width, random.randint(0, 400)),
                size_hint=(None, None),
                size=(col_width, 400),
                halign='center',
                valign='top'
            )
            lbl.text_size = lbl.size
            self.add_widget(lbl)
            
            self.cols.append({
                'widget': lbl,
                'speed': random.uniform(2.0, 4.5),
                'chars_len': random.randint(10, 18),
                'y_pos': float(random.randint(0, 600))
            })
            
        Clock.schedule_interval(self.update_matrix, 0.05)

    def update_matrix(self, dt):
        for col in self.cols:
            text_lines = "".join(random.choice(self.chars) + "\n" for _ in range(col['chars_len']))
            col['widget'].text = text_lines
            
            col['y_pos'] -= col['speed']
            if col['y_pos'] < -300:
                col['y_pos'] = float(self.height + random.randint(30, 150))
                col['speed'] = random.uniform(2.0, 4.5)
            
            col['widget'].y = col['y_pos']

    def on_size(self, *args):
        if self.width > 0:
            self.init_matrix(0)

class LkwTrackerApp(App):
    aktuelle_schicht_id = None

    def build(self):
        init_db()
        self.start_background_service()
        
        root = FloatLayout()
        
        # 1. Matrix-Hintergrund als unterste Ebene
        matrix_bg = MatrixRain()
        root.add_widget(matrix_bg)

        # 2. Hauptlayout im Querformat (Vertikal aufgeteilt: Oben Info, Mitte Freiraum, Unten waagerechte Button-Leiste)
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # OBERER BEREICH: Titel & Status
        top_area = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=0.35)
        
        top_area.add_widget(Label(
            text="LKW TRACKER",
            font_size='20sp',
            bold=True,
            color=(0.1, 1.0, 0.4, 1),
            halign='left',
            valign='middle'
        ))

        self.status_label = Label(
            text="Status: Keine aktive Schicht",
            font_size='16sp',
            color=(0.8, 1.0, 0.8, 1),
            halign='right',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        top_area.add_widget(self.status_label)
        
        main_layout.add_widget(top_area)

        # Mittlerer Freiraum für den Matrix-Regen
        main_layout.add_widget(Widget(size_hint_y=0.15))

        # UNTERER BEREICH: Waagerechte Button-Leiste quer über den Bildschirm
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height='50dp')

        btn_start = Button(text="START", font_size='14sp', bold=True, background_color=(0.0, 0.7, 0.2, 1), color=(1, 1, 1, 1))
        btn_start.bind(on_release=lambda x: self.schicht_starten())
        btn_layout.add_widget(btn_start)

        btn_ankunft = Button(text="ANKUNFT", font_size='14sp', bold=True, background_color=(0.0, 0.4, 0.9, 1), color=(1, 1, 1, 1))
        btn_ankunft.bind(on_release=lambda x: self.stopp_erfassen("Ankunft"))
        btn_layout.add_widget(btn_ankunft)

        btn_weiterfahrt = Button(text="WEITER", font_size='14sp', bold=True, background_color=(0.9, 0.5, 0.0, 1), color=(1, 1, 1, 1))
        btn_weiterfahrt.bind(on_release=lambda x: self.stopp_erfassen("Weiterfahrt"))
        btn_layout.add_widget(btn_weiterfahrt)

        btn_feierabend = Button(text="FEIERABEND", font_size='14sp', bold=True, background_color=(0.9, 0.1, 0.2, 1), color=(1, 1, 1, 1))
        btn_feierabend.bind(on_release=lambda x: self.feierabend_dialog_oeffnen())
        btn_layout.add_widget(btn_feierabend)

        btn_berichte = Button(text="BERICHTE", font_size='14sp', bold=True, background_color=(0.3, 0.3, 0.5, 1), color=(1, 1, 1, 1))
        btn_berichte.bind(on_release=lambda x: self.schichtberichte_anzeigen())
        btn_layout.add_widget(btn_berichte)

        main_layout.add_widget(btn_layout)

        root.add_widget(main_layout)
        return root

    def start_background_service(self):
        try:
            from android.runnable import run_on_ui_thread
            @run_on_ui_thread
            def keep_screen_on():
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                window = activity.getWindow()
                WindowManager = autoclass('android.view.WindowManager$LayoutParams')
                window.addFlags(WindowManager.FLAG_KEEP_SCREEN_ON)
            keep_screen_on()
        except Exception as e:
            print(f"Dauerbetrieb-Hinweis: {e}")

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
            self.status_label.text = "⚠️ Zuerst Schicht starten!"
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

        self.status_label.text = f"{typ} erfasst ({now_str[:5]})"

    def feierabend_dialog_oeffnen(self):
        if not self.aktuelle_schicht_id:
            self.status_label.text = "⚠️ Keine aktive Schicht!"
            return

        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        content.add_widget(Label(text="Pausenminuten eingeben:", font_size='16sp'))
        
        self.pause_input = TextInput(text="45", font_size='18sp', multiline=False, input_filter='int')
        content.add_widget(self.pause_input)

        btn_layout = BoxLayout(size_hint_y=None, height='50dp', spacing=10)
        btn_abbrechen = Button(text="Abbrechen")
        btn_speichern = Button(text="Speichern", background_color=(0.0, 0.7, 0.2, 1))

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
        
        cursor.execute("SELECT start_zeit, datum FROM schichten WHERE id = ?", (self.aktuelle_schicht_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return
        
        start_str, datum_str = row
        fmt = "%H:%M:%S"
        t_start = datetime.strptime(start_str, fmt)
        t_ende = datetime.strptime(ende_str, fmt)
        
        brutto_min = int((t_ende - t_start).total_seconds() / 60)
        if brutto_min < 0:
            brutto_min += 24 * 60 
            
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
        cursor.execute("SELECT id, datum, start_zeit, ende_zeit, pause_min, netto_min, status FROM schichten ORDER BY id DESC LIMIT 10")
        schichten = cursor.fetchall()

        bericht_text = "Letzte Schichten:\n\n"
        if not schichten:
            bericht_text += "Noch keine Schichten aufgezeichnet."
        else:
            for s in schichten:
                schicht_id, datum, start, ende, pause, netto, status = s
                netto_h, netto_m = divmod(netto if netto else 0, 60)
                ende_zeit = ende[:5] if ende else "Aktiv"
                start_zeit = start[:5] if start else ""
                pause_zeit = pause if pause else 0
                
                bericht_text += f"📅 {datum}\n"
                bericht_text += f"⏱️ {start_zeit} - {ende_zeit} | Pause: {pause_zeit} min\n"
                bericht_text += f"👉 Netto-Arbeitszeit: {netto_h}h {netto_m}m\n"
                bericht_text += f"Status: {status}\n--------------------\n"

        conn.close()

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        scroll = ScrollView(size_hint=(1, 0.8))
        lbl = Label(text=bericht_text, font_size='14sp', size_hint_y=None, halign='left', valign='top')
        lbl.bind(texture_size=lambda *x: setattr(lbl, 'height', lbl.texture_size[1]))
        scroll.add_widget(lbl)
        content.add_widget(scroll)

        btn_schliessen = Button(text="Schließen", size_hint_y=None, height='45dp')
        popup = Popup(title="Schichtberichte & Arbeitszeit", content=content, size_hint=(0.9, 0.8))
        btn_schliessen.bind(on_release=popup.dismiss)
        content.add_widget(btn_schliessen)

        popup.open()

if __name__ == '__main__':
    LkwTrackerApp().run()
