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
    
    # FORCE DEBUG=True for presentation to see errors in browser
    # This overrides settings.py for this run script only
    os.environ["DEBUG"] = "True"

    # Fix for --windowed mode: Redirect stdout/stderr to a file instead of devnull
    # This lets us see why it crashes if it fails before the browser opens
    log_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else '.', 'debug.log')
    try:
        if sys.stdout is None:
            sys.stdout = open(log_path, "a")
        if sys.stderr is None:
            sys.stderr = open(log_path, "a")
    except Exception:
        pass # If we can't write logs, we just continue

    try:
        # Schedule the browser to open in 1.5 seconds
        Timer(1.5, open_browser).start()
        
        # Run the server. 
        sys.argv = [sys.argv[0], "runserver", "127.0.0.1:8000", "--noreload", "--insecure"]
        execute_from_command_line(sys.argv)
    except Exception as e:
        # Last ditch effort to catch startup crashes
        with open("CRITICAL_ERROR.txt", "w") as f:
            import traceback
            f.write(traceback.format_exc())
        raise
