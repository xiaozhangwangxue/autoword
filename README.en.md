<div align="center">
  <img src="assets/icons/app-icon.png" alt="AutoWord icon" width="128" height="128">

  # AutoWord Formatter

  **Consistent Word formatting in one click · Fully offline · Cross-platform**

  [![Release](https://img.shields.io/github/v/release/xiaozhangwangxue/autoword?style=flat-square&color=1677ff)](https://github.com/xiaozhangwangxue/autoword/releases/latest)
  [![CI](https://img.shields.io/github/actions/workflow/status/xiaozhangwangxue/autoword/ci.yml?branch=main&style=flat-square&label=tests)](https://github.com/xiaozhangwangxue/autoword/actions/workflows/ci.yml)
  [![License](https://img.shields.io/github/license/xiaozhangwangxue/autoword?style=flat-square)](LICENSE)
  [![Platforms](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux%20%7C%20Android-30363d?style=flat-square)](#downloads-and-installation)

  [Official website](https://autoword.12323456.xyz) · [Download](https://autoword.12323456.xyz/#download) · [Release notes](https://github.com/xiaozhangwangxue/autoword/releases) · [简体中文](README.md)
</div>

---

AutoWord is a local formatter for `.docx` documents. Select your files and formatting rules to standardize font size, line spacing, paragraph spacing, page margins, footers, and Chinese/English punctuation in batches. Desktop builds save results to Downloads by default and also let you choose another export location.

> [!IMPORTANT]
> The document engine runs with the application. Files are not uploaded, no account is required, and conversion continues to work offline.

## Why AutoWord

| 🔒 Local and offline | 🧰 Flexible formatting | 📚 Batch processing | 💻 Cross-platform |
| --- | --- | --- | --- |
| Documents never leave your device | Customize text, spacing, margins, and footers | Process multiple `.docx` files at once | macOS, Windows, Linux, and Android |

## Highlights

- **Typography:** configure font size, line spacing, and spacing before or after paragraphs.
- **Page layout:** use A4, B5, equal-margin, 0.5/0.7 cm, mirrored-page, or fully custom margins.
- **Punctuation:** convert between full-width and half-width punctuation, or preserve the source.
- **Document cleanup:** optionally remove empty paragraphs that contain neither text nor images.
- **Footers:** combine first-paragraph text with page numbers, use page numbers only, or disable footers.
- **Clear exports:** choose a desktop output folder, review completed files, and reveal the folder in one click.
- **Bilingual UI:** switch between Simplified Chinese and English.

## Downloads and installation

The [official website](https://autoword.12323456.xyz/#download) detects your device, provides direct package downloads, and shows platform-specific installation guidance.

| Platform | Package | Requirements | Download |
| --- | --- | --- | --- |
| Android | APK | Android 7.0+ | [Official download](https://autoword.12323456.xyz/downloads/AutoWord-android.apk) |
| macOS | Drag-to-install DMG | macOS 12+ | [Official download](https://autoword.12323456.xyz/downloads/AutoWord-macos.dmg) |
| Windows | ZIP | Windows 10 / 11 | [Official download](https://autoword.12323456.xyz/downloads/AutoWord-windows.zip) |
| Linux | tar.gz | 64-bit Linux | [Official download](https://autoword.12323456.xyz/downloads/AutoWord-linux.tar.gz) |

<details>
<summary><strong>What if my system blocks the first installation?</strong></summary>

- **Android:** allow installs from the current browser or file manager, then choose Install anyway.
- **macOS:** drag AutoWord to Applications, Control-click the app, choose Open, and confirm once more.
- **Windows:** if SmartScreen appears, choose More info → Run anyway.
- **Linux:** extract the archive and grant the main executable permission before launching it.

</details>

## Format a document in three steps

1. Choose a paper preset and configure typography, spacing, margins, punctuation, and footer options.
2. Import one or more `.docx` files and select an export location.
3. Start formatting, then open completed documents from the result list.

Output names preserve the source name and add `_formatted` before the extension: `report.docx` → `report_formatted.docx`.

## Run from source

Python 3.10 or newer is required.

```bash
git clone https://github.com/xiaozhangwangxue/autoword.git
cd autoword
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080). On Windows, activate the environment with `.venv\Scripts\activate`.

<details>
<summary><strong>Production serving and configuration</strong></summary>

Use a WSGI server such as Gunicorn behind a reverse proxy with HTTPS and access control:

```bash
gunicorn --workers 2 --bind 127.0.0.1:8080 app:app
```

The default request limit is 100 MiB and can be changed with an environment variable:

```bash
MAX_UPLOAD_SIZE=$((200 * 1024 * 1024)) gunicorn --workers 2 --bind 127.0.0.1:8080 app:app
```

</details>

## Development and testing

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs tests on pushes and pull requests. Tags matching `v*` build and publish packages for every supported platform.

## Privacy and security

- Desktop and mobile builds process documents locally and do not connect to third-party document services.
- Web-mode temporary files are stored in `/tmp/mac_pro_uploads` and automatically removed after seven days.
- The Web service has no built-in account system and should not be exposed publicly without protection.
- Process only documents you are authorized to use, especially when they contain personal or confidential data.

See [SECURITY.en.md](SECURITY.en.md) for details.

## Contributing

Issues and pull requests are welcome. Read [CONTRIBUTING.en.md](CONTRIBUTING.en.md) before getting started.

AutoWord is available under the [MIT License](LICENSE).

## Support the project

If AutoWord saves you time, you may optionally support ongoing maintenance and cross-platform development. Thank you.

| WeChat Pay | Alipay |
| :---: | :---: |
| <img src="assets/donate/wechat.png" alt="WeChat Pay QR code" width="260"> | <img src="assets/donate/alipay.jpg" alt="Alipay QR code" width="260"> |

<div align="center">
  <sub>Made with care for cleaner documents.</sub>
</div>
