import os
import sys
import webbrowser
from threading import Timer
from django.core.management import execute_from_command_line

def open_browser():
    # Give the server a moment to start, then open the page
    webbrowser.open_new("http://127.0.0.1:8000")

if __name__ == "__main__":
    # Point to the settings file
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edithunt.settings")

    # Fix for --windowed mode (no console) causing crash when Django writes to stdout
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")
    
    # Schedule the browser to open in 1.5 seconds
    Timer(1.5, open_browser).start()
    
    # Run the server. 
    # --noreload is CRITICAL for .exe files (autoloader breaks them)
    # --insecure allows serving static files without DEBUG=True
    sys.argv = [sys.argv[0], "runserver", "127.0.0.1:8000", "--noreload", "--insecure"]
    
    execute_from_command_line(sys.argv)
