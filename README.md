# AutoWord 排版工厂

一个面向 `.docx` 文档的轻量级 Web 排版工具。上传一个或多个 Word 文件，选择纸张方案，即可批量生成统一排版后的压缩包。

> 当前界面名称为「排版工厂」。本项目不连接第三方服务，所有文档均在运行该服务的机器上处理。

## 功能

- 批量处理 `.docx` 文件并打包下载
- 移除空段落、统一正文为 10.5 pt 和单倍行距
- 将常见中文标点转换为对应的英文标点
- 支持 A4 标准边距、A4 等宽边距与 B5 小册子三种页面方案
- 在页脚添加首段文字与页码
- 自动清理超过 7 天的临时文件

## 快速开始

需要 Python 3.10 或更高版本。

```bash
git clone https://github.com/<你的用户名>/autoword.git
cd autoword
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

随后在浏览器打开 [http://127.0.0.1:8080](http://127.0.0.1:8080)。

## 生产运行

不要使用 Flask 自带的开发服务器对外提供服务。可使用 Gunicorn：

```bash
gunicorn --workers 2 --bind 127.0.0.1:8080 app:app
```

若要通过公网访问，请在反向代理层配置 HTTPS、访问控制和请求大小限制。默认单次请求上限为 100 MiB；可通过环境变量调整：

```bash
MAX_UPLOAD_SIZE=$((200 * 1024 * 1024)) gunicorn --workers 2 --bind 127.0.0.1:8080 app:app
```

## 使用方式

1. 打开网页并选择纸张规格。
2. 选择一个或多个 `.docx` 文件。
3. 点击“开始转换”，等待处理完成后浏览器会下载 `排版成品.zip`。

输出文件沿用原文件名并在扩展名前加上 `_formatted`，例如 `作业.docx` 会变为 `作业_formatted.docx`。

## 隐私与安全

- 上传的文件与生成结果会写入运行机器的临时目录 `/tmp/mac_pro_uploads`，并在 7 天后自动清理。
- 本项目不提供用户登录或访问控制，**不应直接暴露到公网**；公网部署请置于受保护的反向代理之后。
- 仅上传你有权处理的文档，尤其注意其中可能包含的个人信息或保密内容。

更多安全问题请参阅 [SECURITY.md](SECURITY.md)。

## 开发与测试

```bash
python -m unittest discover -s tests -v
```

GitHub Actions 会在每次推送和拉取请求时运行上述检查。

## 贡献

欢迎提交 issue 和 pull request。提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

本项目基于 [MIT License](LICENSE) 开源。
