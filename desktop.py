"""Launch AutoWord as a self-contained native desktop application."""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import webview

from app import UPLOAD_FOLDER, app


class DesktopApi:
    """Native bridge for choosing, exporting, and revealing output files."""

    def __init__(self):
        self.export_directory = str(Path.home() / "Downloads")

    def get_default_export_directory(self):
        Path(self.export_directory).mkdir(parents=True, exist_ok=True)
        return self.export_directory

    def choose_export_directory(self):
        result = webview.windows[0].create_file_dialog(
            webview.FOLDER_DIALOG,
            directory=self.export_directory,
        )
        if result:
            self.export_directory = str(Path(result[0]).expanduser().resolve())
        return self.export_directory

    def export_job(self, job_id, destination=None):
        if not re.fullmatch(r"[0-9a-f-]{36}", str(job_id)):
            return {"ok": False, "error": "Invalid job id"}
        output_dir = (Path(UPLOAD_FOLDER) / job_id / "output").resolve()
        upload_root = Path(UPLOAD_FOLDER).resolve()
        if upload_root not in output_dir.parents or not output_dir.is_dir():
            return {"ok": False, "error": "Output files are unavailable"}
        target_dir = Path(destination or self.export_directory).expanduser().resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        self.export_directory = str(target_dir)
        saved = []
        for source in sorted(output_dir.glob("*.docx")):
            target = target_dir / source.name
            counter = 2
            while target.exists():
                target = target_dir / f"{source.stem} ({counter}){source.suffix}"
                counter += 1
            shutil.copy2(source, target)
            saved.append({"name": target.name, "path": str(target)})
        return {"ok": bool(saved), "directory": str(target_dir), "files": saved}

    def open_export_directory(self, destination=None):
        target = str(Path(destination or self.export_directory).expanduser().resolve())
        if sys.platform == "darwin":
            subprocess.Popen(["open", target])
        elif os.name == "nt":
            os.startfile(target)
        else:
            subprocess.Popen(["xdg-open", target])
        return True


def main():
    # pywebview accepts a WSGI application directly and starts its internal
    # local server before loading the native window. This keeps the frontend
    # and backend in one lifecycle and removes the external-port race which
    # previously caused a connection-failed screen in packaged applications.
    webview.create_window(
        "AutoWord 排版工厂",
        app,
        js_api=DesktopApi(),
        width=1100,
        height=800,
        min_size=(760, 600),
        background_color="#07152f",
    )
    webview.start(private_mode=True)


if __name__ == "__main__":
    main()
