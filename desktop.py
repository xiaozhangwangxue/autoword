"""Launch AutoWord as a self-contained desktop application."""
import threading
import webbrowser

from werkzeug.serving import make_server

from app import app


def main():
    server = make_server("127.0.0.1", 8080, app)
    threading.Timer(0.6, lambda: webbrowser.open("http://127.0.0.1:8080")).start()
    server.serve_forever()


if __name__ == "__main__":
    main()
