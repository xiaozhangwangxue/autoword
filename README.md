<div align="center">
  <img src="assets/icons/app-icon.png" alt="AutoWord 图标" width="128" height="128">

  # AutoWord 排版工厂

  **一键统一 Word 文档排版 · 完全离线 · 跨平台使用**

  [![Release](https://img.shields.io/github/v/release/xiaozhangwangxue/autoword?style=flat-square&color=1677ff)](https://github.com/xiaozhangwangxue/autoword/releases/latest)
  [![CI](https://img.shields.io/github/actions/workflow/status/xiaozhangwangxue/autoword/ci.yml?branch=main&style=flat-square&label=tests)](https://github.com/xiaozhangwangxue/autoword/actions/workflows/ci.yml)
  [![License](https://img.shields.io/github/license/xiaozhangwangxue/autoword?style=flat-square)](LICENSE)
  [![Platforms](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux%20%7C%20Android-30363d?style=flat-square)](#下载与安装)

  [官方网站](https://autoword.12323456.xyz) · [下载最新版](https://autoword.12323456.xyz/#download) · [更新记录](https://github.com/xiaozhangwangxue/autoword/releases) · [English](README.en.md)
</div>

---

AutoWord 是一个专注于 `.docx` 文档的本地排版工具。选择文件和排版规则后，即可批量统一字体大小、行间距、段落间距、页边距、页脚与中英文标点。桌面版默认将成品保存到系统“下载”文件夹，也可以自行选择导出位置。

> [!IMPORTANT]
> 文档处理引擎随应用一起运行，不需要上传文件、登录账号或连接第三方服务；断网后仍可正常转换。

## 为什么选择 AutoWord

| 🔒 本机离线 | 🧰 灵活排版 | 📚 批量处理 | 💻 跨平台 |
| --- | --- | --- | --- |
| 文档不会上传到云端 | 字号、行距、段距和页边距均可设置 | 一次选择多个 `.docx` 文件 | 支持 macOS、Windows、Linux 与 Android |

## 核心功能

- **正文格式**：设置字体大小、行间距、段前与段后距离。
- **页面布局**：支持 A4、B5、等宽边距、0.5/0.7 cm 预设、对称页和自定义四边页边距。
- **标点转换**：一键转换全角、半角标点，也可保持原样。
- **文档清理**：按需移除没有文字或图片的空段落。
- **页脚设置**：可使用首段文字与页码、仅页码或不添加页脚。
- **明确导出**：桌面版可选择保存目录，完成后显示文件列表并直接打开所在文件夹。
- **双语界面**：应用与文档均提供简体中文和英文版本。

## 下载与安装

中国大陆用户可通过[官方网站](https://autoword.12323456.xyz/#download)直接下载，无需访问 GitHub。网站会自动识别设备，并在下载前显示对应的安装步骤。

| 平台 | 安装包 | 系统要求 | 下载 |
| --- | --- | --- | --- |
| Android | APK | Android 7.0+ | [官网下载](https://autoword.12323456.xyz/downloads/AutoWord-android.apk) |
| macOS | 拖拽安装 DMG | macOS 12+ | [官网下载](https://autoword.12323456.xyz/downloads/AutoWord-macos.dmg) |
| Windows | ZIP | Windows 10 / 11 | [官网下载](https://autoword.12323456.xyz/downloads/AutoWord-windows.zip) |
| Linux | tar.gz | 64 位 Linux | [官网下载](https://autoword.12323456.xyz/downloads/AutoWord-linux.tar.gz) |

<details>
<summary><strong>首次安装被系统拦截怎么办？</strong></summary>

- **Android**：在系统提示中允许当前浏览器或文件管理器安装未知来源应用，然后选择“仍要安装”。
- **macOS**：将 AutoWord 拖入“应用程序”，按住 Control 点击应用并选择“打开”，再确认一次。
- **Windows**：若 SmartScreen 出现提示，请选择“更多信息”→“仍要运行”。
- **Linux**：解压后为主程序添加执行权限，再启动应用。

</details>

## 三步完成排版

1. 选择纸张方案并设置正文、间距、页边距、标点和页脚。
2. 导入一个或多个 `.docx` 文件，并选择导出位置。
3. 点击“开始转换”，完成后从文件列表直接打开成品。

生成文件沿用原文件名，并在扩展名前添加 `_formatted`。例如：`作业.docx` → `作业_formatted.docx`。

## 从源码运行

需要 Python 3.10 或更高版本。

```bash
git clone https://github.com/xiaozhangwangxue/autoword.git
cd autoword
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

随后打开 [http://127.0.0.1:8080](http://127.0.0.1:8080)。Windows 用户可使用 `.venv\Scripts\activate` 激活虚拟环境。

<details>
<summary><strong>生产运行与配置</strong></summary>

请使用 Gunicorn 等 WSGI 服务器，并通过带有 HTTPS 与访问控制的反向代理提供服务：

```bash
gunicorn --workers 2 --bind 127.0.0.1:8080 app:app
```

默认单次请求上限为 100 MiB，可通过环境变量调整：

```bash
MAX_UPLOAD_SIZE=$((200 * 1024 * 1024)) gunicorn --workers 2 --bind 127.0.0.1:8080 app:app
```

</details>

## 开发与测试

```bash
python -m unittest discover -s tests -v
```

GitHub Actions 会在推送与拉取请求中自动运行测试；推送 `v*` 标签后会构建并发布四个平台的安装包。

## 隐私与安全

- 桌面端与移动端均在设备本机处理文档，不连接第三方文档服务。
- Web 模式的临时文件保存在 `/tmp/mac_pro_uploads`，并在 7 天后自动清理。
- Web 服务没有内置账户系统，不应未经保护直接暴露到公网。
- 仅处理你有权使用的文档，注意其中可能包含的个人或保密信息。

详细说明见 [SECURITY.md](SECURITY.md)（[English](SECURITY.en.md)）。

## 参与项目

欢迎提交 [Issue](https://github.com/xiaozhangwangxue/autoword/issues) 与 Pull Request。开始前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)（[English](CONTRIBUTING.en.md)）。

AutoWord 基于 [MIT License](LICENSE) 开源。

## 捐款支持

如果 AutoWord 帮你节省了时间，可以自愿支持项目的持续维护与跨平台适配。感谢你的认可。

| 微信支付 | 支付宝 |
| :---: | :---: |
| <img src="assets/donate/wechat.png" alt="微信支付收款码" width="260"> | <img src="assets/donate/alipay.jpg" alt="支付宝收款码" width="260"> |

<div align="center">
  <sub>Made with care for cleaner documents.</sub>
</div>
