"""Launch AutoWord in a native desktop window, with no external browser."""
import threading
import time
from urllib.error import URLError
from urllib.request import urlopen

import webview
from werkzeug.serving import make_server

from app import app


def wait_for_server(url):
    for _ in range(30):
        try:
            with urlopen(url, timeout=0.2):
                return
        except URLError:
            time.sleep(0.1)
    raise RuntimeError("The local AutoWord service did not start.")


def main():
    server = make_server("127.0.0.1", 0, app)
    url = f"http://127.0.0.1:{server.server_port}"
    threading.Thread(target=server.serve_forever, daemon=True).start()
    wait_for_server(url)
    webview.create_window(
        "AutoWord 排版工厂",
        url,
        width=1100,
        height=800,
        min_size=(760, 600),
    )
    webview.start()
    server.shutdown()


if __name__ == "__main__":
    main()
