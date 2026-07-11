"""Launch AutoWord in a native desktop window, with no external browser."""
import threading
import socket

import webview
from werkzeug.serving import make_server

from app import app


def available_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    port = available_port()
    server = make_server("127.0.0.1", port, app)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    webview.create_window(
        "AutoWord 排版工厂",
        f"http://127.0.0.1:{port}",
        width=1100,
        height=800,
        min_size=(760, 600),
    )
    webview.start()
    server.shutdown()


if __name__ == "__main__":
    main()
