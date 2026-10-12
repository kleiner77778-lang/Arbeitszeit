import sys
import traceback
import os

# Fängt jeden ungesicherten Absturz ab und schreibt ihn in eine Datei
def global_exception_handler(exc_type, exc_value, exc_tb):
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        log_path = os.path.join(os.getcwd(), "crash_log.txt")
        with open(log_path, "w") as f:
            f.write(error_msg)
    except Exception:
            pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = global_exception_handler
