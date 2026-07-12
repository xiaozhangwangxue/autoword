"""Launch AutoWord as a self-contained native desktop application."""
import webview

from app import app


def main():
    # pywebview accepts a WSGI application directly and starts its internal
    # local server before loading the native window. This keeps the frontend
    # and backend in one lifecycle and removes the external-port race which
    # previously caused a connection-failed screen in packaged applications.
    webview.create_window(
        "AutoWord 排版工厂",
        app,
        width=1100,
        height=800,
        min_size=(760, 600),
        background_color="#07152f",
    )
    webview.start(private_mode=True)


if __name__ == "__main__":
    main()
