import datetime
import os
import sqlite3
import time
from jnius import autoclass
from kivy.utils import platform
import requests

# ---------------------------------------------------------
# Einstellungen & Konfiguration
# ---------------------------------------------------------
TELEGRAM_BOT_TOKEN = 'DEIN_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'DEINE_CHAT_ID'

global_wakelock = None


def setup_foreground_service():
  """Aktiviert Wakelock & Foreground Service mit permanenter Notification,

  damit Android den Prozess im Hintergrund nicht beendet.
  """
  global global_wakelock
  if platform != 'android':
    return

  try:
    PythonService = autoclass('org.kivy.android.PythonService')
    service = PythonService.mService

    # 1. CPU Wakelock aktivieren
    Context = autoclass('android.content.Context')
    PowerManager = autoclass('android.os.PowerManager')
    power_manager = service.getSystemService(Context.POWER_SERVICE)

    global_wakelock = power_manager.newWakeLock(
        PowerManager.PARTIAL_WAKE_LOCK, 'LKWTracker::WakelockTag'
    )
    global_wakelock.acquire()

    # Auto-Restart aktivieren
    service.setAutoRestartService(True)

    # 2. Benachrichtigungskanal für Android 8+ (API 26+) erstellen
    Notification = autoclass('android.app.Notification')
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationManager')
    Build = autoclass('android.os.Build')

    channel_id = 'lkw_tracker_channel'

    if Build.VERSION.SDK_INT >= 26:
      channel = NotificationChannel(
          channel_id,
          'LKW Tracker Dienst',
          NotificationManager.IMPORTANCE_LOW,
      )
      notification_manager = service.getSystemService(
          Context.NOTIFICATION_SERVICE
      )
      notification_manager.createNotificationChannel(channel)
      builder = NotificationBuilder(service, channel_id)
    else:
      builder = NotificationBuilder(service)

    # 3. Notification konfigurieren & Foreground Service starten
    builder.setContentTitle('LKW Tracker aktiv')
    builder.setContentText('GPS-Tracking und Stau-Erkennung laufen.')
    # Nutzt das Standard-App-Icon von Android
    builder.setSmallIcon(service.getApplicationInfo().icon)

    notification = builder.build()
    service.startForeground(1337, notification)
    print('Foreground Service & Wakelock erfolgreich gestartet.')

  except Exception as e:
    print(f'Fehler beim Starten des Foreground Service: {e}')


def get_db_connection():
  if platform == 'android':
    PythonService = autoclass('org.kivy.android.PythonService')
    service = PythonService.mService
    files_dir = service.getFilesDir().getAbsolutePath()
  else:
    files_dir = os.getcwd()

  db_path = os.path.join(files_dir, 'lkw_tracker.db')
  return sqlite3.connect(db_path)


def log_event_to_db(event_type, details):
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Tabelle anlegen, falls sie noch nicht existiert
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS work_logs (id INTEGER PRIMARY KEY'
        ' AUTOINCREMENT, timestamp TEXT, event_type TEXT, gps_data TEXT)'
    )

    cursor.execute(
        'INSERT INTO work_logs (timestamp, event_type, gps_data) VALUES (?,'
        ' ?, ?)',
        (now, event_type, details),
    )
    conn.commit()
    conn.close()

    # Meldung an Telegram senden
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': (
            f'🚚 *LKW Hintergrund-Info*: {event_type}\n📍'
            f' {details}\n⏰ {now}'
        ),
        'parse_mode': 'Markdown',
    }
    requests.post(url, json=payload, timeout=5)
  except Exception as e:
    print(f'Service Log Fehler: {e}')


def main():
  # Als Erstes den Vordergrunddienst initialisieren
  setup_foreground_service()

  log_event_to_db('Hintergrunddienst', 'GPS-Service im Hintergrund gestartet.')

  is_moving = True
  stopped_since = None

  try:
    from plyer import gps

    def on_gps_location(**kwargs):
      nonlocal is_moving, stopped_since
      lat = kwargs.get('lat')
      lon = kwargs.get('lon')
      speed = kwargs.get('speed', 0) or 0
      speed_kmh = speed * 3.6
      now = datetime.datetime.now()

      # Stau- / Stopp-Erkennung (< 5 km/h)
      if speed_kmh < 5.0:
        if is_moving:
          if stopped_since is None:
            stopped_since = now
          else:
            # Nach 3 Minuten Stillstand (180 Sekunden)
            if (now - stopped_since).total_seconds() > 180:
              is_moving = False
              log_event_to_db(
                  '🛑 Stau / Haltepunkt erkannt', f'Lat: {lat:.4f}, Lon: {lon:.4f}'
              )
      else:
        # Fahrt fortgesetzt (> 10 km/h)
        if speed_kmh > 10.0 and not is_moving:
          is_moving = True
          stopped_since = None
          log_event_to_db(
              '🚀 Fahrt fortgesetzt', f'Geschwindigkeit: {speed_kmh:.1f} km/h'
          )
        elif is_moving:
          stopped_since = None

    gps.configure(on_location=on_gps_location)
    gps.start(minTime=2000, minDistance=10)
  except Exception as e:
    print(f'Hintergrund GPS Fehler: {e}')

  # Endlosschleife, um den Service am Leben zu halten
  while True:
    time.sleep(30)


if __name__ == '__main__':
  main()
