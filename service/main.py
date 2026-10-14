from time import sleep
import json
import requests

# Endlosschleife für den Hintergrundbetrieb
while True:
    try:
        # Beispiel für Hintergrund-Datenverarbeitung oder API-Calls
        payload = {
            "status": "active",
            "module": "lkwservice"
        }
        
        # Beispiel (URL bei Bedarf anpassen):
        # requests.post("https://deine-api.de/update", json=payload, timeout=10)
        
        print("LKW Tracker Service: Hintergrund-Zyklus ausgeführt.")
    except Exception as e:
        print(f"Fehler im Hintergrund-Dienst: {e}")
    
    # Intervall einstellen (z. B. alle 30 Sekunden)
    sleep(30)
