from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField

# (Füge das in deine LKWTrackerApp-Klasse in der main.py ein:)

    def end_shift_prompt(self):
        # Öffnet ein kleines Eingabefenster für die gemachte Pause beim Feierabend
        self.pause_input = MDTextField(
            hint_text="Pause in Minuten (z.B. 30)",
            input_filter="int",
            text="30"
        )
        
        self.dialog = MDDialog(
            title="Schicht beenden & Pause eintragen",
            text="Bitte gib an, wie viel Minuten Pause du insgesamt gemacht hast:",
            type="custom",
            content_style="box",
            content=self.pause_input,
            buttons=[
                MDFlatButton(
                    text="ABBRECHEN",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="BERECHNEN & SENDEN",
                    on_release=self.process_end_shift
                ),
            ],
        )
        self.dialog.open()

    def process_end_shift(self, instance):
        pause_min = int(self.pause_input.text) if self.pause_input.text else 0
        self.dialog.dismiss()
        
        # Schicht-Ende in DB loggen
        self.log_event("Schicht Beendet", f"Nachträgliche Pause: {pause_min} Minuten")
        
        # Gesamtauswertung aus der Datenbank holen und an Telegram senden
        self.generate_final_report_and_send(pause_min)

    def generate_final_report_and_send(self, pause_minutes):
        try:
            # Letzten Schichtstart und -ende auslesen (vereinfachtes Beispiel)
            self.cursor.execute("SELECT timestamp, event_type, gps_data FROM work_logs ORDER BY id DESC")
            rows = self.cursor.fetchall()
            
            # Bericht zusammenbauen
            report = f"📋 *LKW Tages- & Arbeitszeitbericht*\n"
            report += f"☕ Abgezogene Pause: {pause_minutes} Minuten\n\n"
            report += "Letzte Ereignisse:\n" + "\n".join([f"• {r[0]} - *{r[1]}* ({r[2]})" for r in rows[:6]])
            
            # An Telegram senden
            self.send_telegram_custom_message(report)
        except Exception as e:
            self.root.ids.status_label.text = f"Fehler beim Berichten: {str(e)}"
