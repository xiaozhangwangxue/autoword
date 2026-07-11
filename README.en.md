# AutoWord Formatter

[简体中文](README.md)

AutoWord is a lightweight DOCX formatting tool. Select one or more Word documents, choose the rules you need, and download a ZIP file containing the formatted results.

> Documents are processed on the machine running AutoWord. The application does not use third-party services.

## Features

- Batch-process `.docx` files and download them as a ZIP archive.
- Configure font size, line spacing, spacing before/after paragraphs, and empty-paragraph removal.
- Convert punctuation to half-width or full-width, or preserve it unchanged.
- Choose A4 standard, A4 equal-margin, B5 booklet, or custom page margins.
- Add a first-paragraph footer with page number, page number only, or no footer.
- Switch the application interface between English and Simplified Chinese.
- Remove temporary files automatically after seven days.

## Quick start

Python 3.10 or newer is required.

```bash
git clone https://github.com/xiaozhangwangxue/autoword.git
cd autoword
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080) in a browser.

## Desktop and mobile downloads

Download macOS, Windows, Linux, and Android builds from [Releases](https://github.com/xiaozhangwangxue/autoword/releases). Desktop builds open in a native application window. The Android APK processes documents locally on the device.

## Security

Uploaded files and generated results are stored temporarily in `/tmp/mac_pro_uploads` and removed after seven days. Do not expose the web service directly to the public internet: it has no built-in authentication. See [SECURITY.en.md](SECURITY.en.md) for details.

## Development

```bash
python -m unittest discover -s tests -v
```

See [CONTRIBUTING.en.md](CONTRIBUTING.en.md) for contribution guidance. This project is licensed under the [MIT License](LICENSE).

## Support the project

If AutoWord is useful to you, you may support its maintenance with either QR code below. Donations are entirely optional — thank you for your support.

| WeChat Pay | Alipay |
| --- | --- |
| <img src="assets/donate/wechat.png" alt="WeChat Pay QR code" width="300"> | <img src="assets/donate/alipay.jpg" alt="Alipay QR code" width="300"> |
