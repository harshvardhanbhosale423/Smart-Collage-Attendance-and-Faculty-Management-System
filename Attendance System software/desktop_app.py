"""
Desktop (GUI window) launcher for the College Attendance System.

Starts the Flask app on a private local port in the background and shows it
inside a native desktop window (no browser needed, fully offline).

Run directly:   python desktop_app.py
Build an .exe:  double-click build_exe.bat (Windows)
"""
import socket
import threading
import time
import webbrowser

from werkzeug.serving import make_server

from app import app  # module-level Flask app


def _free_port(preferred=5000):
    for port in (preferred, 0):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", port))
            return s.getsockname()[1]
        except OSError:
            continue
        finally:
            s.close()
    raise RuntimeError("No free local port available.")


def main():
    port = _free_port(5000)
    server = make_server("127.0.0.1", port, app, threaded=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{port}"

    try:
        import webview  # pywebview: native window
    except ImportError:
        # Fallback: open the default browser and keep the server alive.
        webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        webview.create_window(
            "College Attendance System", url,
            width=1280, height=820, min_size=(900, 600),
        )
        webview.start()

    server.shutdown()


if __name__ == "__main__":
    main()
