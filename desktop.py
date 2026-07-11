"""Launch AutoWord in a native desktop window, with no external browser."""
import threading

import webview
from werkzeug.serving import make_server

from app import app


def main():
    server = make_server("127.0.0.1", 8080, app)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    webview.create_window(
        "AutoWord 排版工厂",
        "http://127.0.0.1:8080",
        width=1100,
        height=800,
        min_size=(760, 600),
    )
    webview.start()
    server.shutdown()


if __name__ == "__main__":
    main()
