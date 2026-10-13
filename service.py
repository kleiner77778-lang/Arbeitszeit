import time
import requests

TELEGRAM_TOKEN = "8413301731:AAHRM32xA2CkAkrrcf85sqYDR88YK14k3bs"
CHAT_ID = "8941361378"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Service Telegram Error: {e}")

if __name__ == '__main__':
    send_telegram("⚙️ LKW Hintergrund-Service gestartet.")
    while True:
        # Hier läuft der dauerhafte Hintergrund-Tracker (GPS / Schichtzeit)
        time.sleep(300)  # Alle 5 Minuten Status-Heartbeat oder Tracking-Logik
