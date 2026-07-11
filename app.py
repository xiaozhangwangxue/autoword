import io
import os
import zipfile
import uuid
import shutil
import json
import time
import threading
from flask import Flask, request, send_file, Response, stream_with_context
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml import OxmlElement, ns
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# --- 配置区 ---
UPLOAD_FOLDER = '/tmp/mac_pro_uploads'
MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE', 100 * 1024 * 1024))
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 7天自动清理
FILE_LIFETIME = 7 * 24 * 60 * 60
CLEANUP_INTERVAL = 3600

TRANS_TABLE = str.maketrans({
    '。': '.', '，': ',', '！': '!', '？': '?', '：': ':', '；': ';',
    '（': '(', '）': ')', '“': '"', '”': '"', '‘': "'", '’': "'",
    '【': '[', '】': ']', '、': ','
})

# --- 后台清理线程 ---
def auto_cleanup_task():
    while True:
        try:
            now = time.time()
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    if now - os.path.getmtime(file_path) > FILE_LIFETIME:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                except Exception: pass
        except Exception: pass
        time.sleep(CLEANUP_INTERVAL)

cleanup_thread = threading.Thread(target=auto_cleanup_task, daemon=True)
cleanup_thread.start()

# --- Word 处理逻辑 ---
def create_page_number_field(run):
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(ns.qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(ns.qn('xml:space'), 'preserve')
    instrText.text = "PAGE"
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(ns.qn('w:fldCharType'), 'end')
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)

def remove_empty_paragraphs(doc):
    count = 0
    for i in range(len(doc.paragraphs) - 1, -1, -1):
        p = doc.paragraphs[i]
        text = p.text.strip()
        has_image = p._element.xpath('.//w:drawing') or p._element.xpath('.//w:pict')
        if not text and not has_image:
            p._element.getparent().remove(p._element)
            count += 1
    return count

def process_paragraph(paragraph):
    paragraph.paragraph_format.line_spacing = 1.0
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    for run in paragraph.runs:
        if run.element.xpath('.//w:drawing') or run.element.xpath('.//w:pict'):
            continue
        if run.text:
            text = run.text.translate(TRANS_TABLE)
            while '\n\n' in text: text = text.replace('\n\n', '\n')
            while '\r\n\r\n' in text: text = text.replace('\r\n\r\n', '\r\n')
            run.text = text
        run.font.size = Pt(10.5)

def process_single_file_task(filepath, paper_size, job_id, filename):
    try:
        yield json.dumps({"status": "log", "msg": f"正在读取: {filename}..."}) + "\n"
        doc = Document(filepath)

        first_line_text = ""
        try:
            if len(doc.paragraphs) > 0:
                raw = doc.paragraphs[0].text.strip()
                first_line_text = raw.translate(TRANS_TABLE) if raw else ""
        except: pass

        yield json.dumps({"status": "log", "msg": f"  ↳ 智能去空行..."}) + "\n"
        remove_empty_paragraphs(doc)

        yield json.dumps({"status": "log", "msg": f"  ↳ 标准化排版..."}) + "\n"
        for p in doc.paragraphs: process_paragraph(p)
        for t in doc.tables:
            for r in t.rows:
                for c in r.cells:
                    for p in c.paragraphs: process_paragraph(p)

        yield json.dumps({"status": "log", "msg": f"  ↳ 应用页面设置..."}) + "\n"
        for section in doc.sections:
            section.header_distance = Cm(0)
            section.footer_distance = Cm(0.7)
            if paper_size == 'A4_STD':
                section.page_width = Cm(21); section.page_height = Cm(29.7)
                section.mirror_margins = True
                section.top_margin = Cm(0.5); section.bottom_margin = Cm(0.5)
                section.left_margin = Cm(1.5); section.right_margin = Cm(0.5)
            elif paper_size == 'A4_EQUAL':
                section.page_width = Cm(21); section.page_height = Cm(29.7)
                section.mirror_margins = False
                section.top_margin = Cm(0.7); section.bottom_margin = Cm(0.7)
                section.left_margin = Cm(0.7); section.right_margin = Cm(0.7)
            elif paper_size == 'B5':
                section.page_width = Cm(17.6); section.page_height = Cm(25)
                section.mirror_margins = False
                section.top_margin = Cm(0.7); section.bottom_margin = Cm(0.7)
                section.left_margin = Cm(0.7); section.right_margin = Cm(0.7)

            section.header.is_linked_to_previous = False
            section.footer.is_linked_to_previous = False
            for p in section.header.paragraphs: p.text = ""
            for p in section.footer.paragraphs: p.text = ""
            footer_para = section.footer.paragraphs[0]
            footer_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            run_text = footer_para.add_run(first_line_text + "  -  ")
            run_text.font.size = Pt(9)
            create_page_number_field(footer_para.add_run())

        yield json.dumps({"status": "log", "msg": f"  ↳ 完成！"}) + "\n"
        out_stream = io.BytesIO()
        doc.save(out_stream)
        out_stream.seek(0)

        name_part, ext_part = os.path.splitext(filename)
        new_name = f"{name_part}_formatted{ext_part}"
        yield {"filename": new_name, "data": out_stream.getvalue()}

    except Exception as e:
        yield json.dumps({"status": "error", "msg": f"❌ 失败: {filename}"}) + "\n"
        yield None

@app.route('/', methods=['GET'])
def index():
    return '''
    <!doctype html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Mac Pro 排版工厂</title>
        <style>
            /* 全局重置，适配移动端 */
            * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
            body {
                background-color: #f2f2f7;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                margin: 0;
                padding: 20px 0;
                color: #1c1c1e;
                display: flex;
                justify-content: center;
                min-height: 100vh;
            }

            .card {
                background: white;
                border-radius: 18px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                padding: 24px;
                width: 92%; /* 移动端占满宽度 */
                max-width: 500px; /* 桌面端限制宽度 */
                margin: auto;
                transition: transform 0.3s ease;
            }

            h2 {
                margin-top: 0;
                font-weight: 700;
                text-align: center;
                margin-bottom: 25px;
                font-size: 22px;
            }
            .badge {
                background: #007aff;
                color: white;
                padding: 3px 8px;
                border-radius: 6px;
                font-size: 12px;
                vertical-align: middle;
                margin-left: 5px;
            }

            label {
                display: block;
                font-weight: 600;
                margin-bottom: 10px;
                color: #3a3a3c;
                font-size: 15px;
            }

            /* 大触控区域优化 */
            select, input[type=file] {
                width: 100%;
                padding: 14px;
                margin-bottom: 20px;
                border: 1px solid #e5e5ea;
                border-radius: 12px;
                font-size: 16px; /* 防止iOS缩放 */
                background-color: #f9f9fa;
                appearance: none; /* 去除原生样式 */
                outline: none;
            }

            /* 按钮优化 */
            button {
                background-color: #0071e3;
                color: white;
                border: none;
                padding: 16px;
                font-size: 17px;
                font-weight: 600;
                border-radius: 12px;
                cursor: pointer;
                width: 100%;
                box-shadow: 0 4px 12px rgba(0,113,227,0.3);
                transition: all 0.2s;
            }
            button:active { transform: scale(0.97); opacity: 0.9; }
            button:disabled { background-color: #aeaeb2; box-shadow: none; }

            /* 进度面板优化 */
            #progressPanel { display: none; margin-top: 25px; border-top: 1px solid #f2f2f7; padding-top: 20px; }
            .progress-header { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px; color: #8e8e93; font-weight: 500; }
            .progress-bar-bg { background: #e5e5ea; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 15px; }
            .progress-bar-fill { background: #34c759; height: 100%; width: 0%; transition: width 0.2s linear; }

            #logBox {
                background: #1c1c1e;
                color: #34c759;
                font-family: "Menlo", monospace;
                font-size: 11px;
                padding: 12px;
                border-radius: 10px;
                height: 180px;
                overflow-y: auto;
                line-height: 1.6;
                -webkit-overflow-scrolling: touch; /* iOS顺滑滚动 */
            }
            .log-line { margin: 0; border-bottom: 1px solid #2c2c2e; padding: 2px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .log-line.error { color: #ff453a; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>排版工厂 <span class="badge">v16.0 移动版</span></h2>

            <form id="uploadForm">
                <label>1. 纸张规格</label>
                <select id="paperSize" name="paper_size">
                    <option value="A4_STD">A4 标准 (内1.5 / 外0.5)</option>
                    <option value="A4_EQUAL">A4 等宽 (四边0.7) ✨</option>
                    <option value="B5">B5 小册子 (四边0.7)</option>
                </select>

                <label>2. 选择文件 (多选)</label>
                <input type="file" id="fileInput" name="file" multiple accept=".docx" required>

                <button type="submit" id="startBtn">🚀 开始转换</button>
            </form>

            <div id="progressPanel">
                <div class="progress-header">
                    <span id="progressText">准备中...</span>
                    <span id="percentText">0%</span>
                </div>
                <div class="progress-bar-bg">
                    <div id="progressFill" class="progress-bar-fill"></div>
                </div>
                <div id="logBox"></div>
            </div>
        </div>

        <script>
            const form = document.getElementById('uploadForm');
            const startBtn = document.getElementById('startBtn');
            const logBox = document.getElementById('logBox');
            const progressPanel = document.getElementById('progressPanel');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            const percentText = document.getElementById('percentText');

            form.addEventListener('submit', async function(e) {
                e.preventDefault();

                const files = document.getElementById('fileInput').files;
                if (files.length === 0) { alert("请先选择文件！"); return; }

                startBtn.disabled = true;
                startBtn.textContent = "处理中...";
                progressPanel.style.display = 'block';
                logBox.innerHTML = '<div class="log-line">> 连接服务器...</div>';

                const formData = new FormData(form);

                try {
                    const response = await fetch('/process_stream', { method: 'POST', body: formData });
                    if (!response.ok) throw new Error("连接失败");

                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let buffer = '';

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;

                        buffer += decoder.decode(value, { stream: true });
                        const lines = buffer.split('\\n');
                        buffer = lines.pop();

                        for (const line of lines) {
                            if (!line.trim()) continue;
                            try {
                                const data = JSON.parse(line);

                                if (data.status === 'log') {
                                    const div = document.createElement('div');
                                    div.className = 'log-line';
                                    div.textContent = "> " + data.msg;
                                    logBox.appendChild(div);
                                    logBox.scrollTop = logBox.scrollHeight;
                                }
                                else if (data.status === 'progress') {
                                    const pct = Math.round(data.val * 100);
                                    progressFill.style.width = pct + '%';
                                    percentText.textContent = pct + '%';
                                    progressText.textContent = data.msg;
                                }
                                else if (data.status === 'done') {
                                    const div = document.createElement('div');
                                    div.className = 'log-line';
                                    div.style.color = '#34c759';
                                    div.textContent = "> ✅ 完成，正在下载...";
                                    logBox.appendChild(div);

                                    window.location.href = "/download/" + data.job_id;

                                    startBtn.textContent = "转换完成";
                                    startBtn.style.backgroundColor = "#34c759";
                                }
                                else if (data.status === 'error') {
                                    const div = document.createElement('div');
                                    div.className = 'log-line error';
                                    div.textContent = data.msg;
                                    logBox.appendChild(div);
                                }
                            } catch (err) { }
                        }
                    }
                } catch (error) {
                    alert("错误: " + error.message);
                    startBtn.disabled = false;
                    startBtn.textContent = "重试";
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/process_stream', methods=['POST'])
def process_stream():
    uploaded_files = request.files.getlist('file')
    paper_size = request.form.get('paper_size', 'A4_STD')

    valid_files = [f for f in uploaded_files if f.filename and f.filename.lower().endswith('.docx')]

    if not valid_files:
        return Response(json.dumps({"status": "error", "msg": "❌ 无有效docx文件"}) + "\n", mimetype='application/json')

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    os.makedirs(job_dir, exist_ok=True)

    def generate():
        total = len(valid_files)
        processed_files = []

        local_paths = []
        for f in valid_files:
            # Browsers normally provide a plain filename, but never trust it as a path.
            filename = os.path.basename(f.filename.replace('\\', '/'))
            if not filename or filename in {'.', '..'} or '\x00' in filename:
                continue
            # Prefix the temporary name so files with the same browser filename
            # never overwrite each other; keep the original name for the output.
            path = os.path.join(job_dir, f"{len(local_paths)}_{filename}")
            f.save(path)
            local_paths.append((path, filename))

        for i, (path, filename) in enumerate(local_paths):
            yield json.dumps({"status": "progress", "val": i / total, "msg": f"处理 {i+1}/{total}"}) + "\n"

            gen = process_single_file_task(path, paper_size, job_id, filename)

            file_data = None
            file_name = None
            for item in gen:
                if isinstance(item, str): yield item
                elif isinstance(item, dict):
                    file_name = item['filename']
                    file_data = item['data']

            if file_data:
                processed_files.append((file_name, file_data))
                yield json.dumps({"status": "progress", "val": (i + 0.9) / total, "msg": f"完成: {filename}"}) + "\n"

        yield json.dumps({"status": "log", "msg": "正在打包..."}) + "\n"

        zip_path = os.path.join(job_dir, f"result_{job_id}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for fname, fdata in processed_files:
                zf.writestr(fname, fdata)

        yield json.dumps({"status": "progress", "val": 1.0, "msg": "完成"}) + "\n"
        yield json.dumps({"status": "done", "job_id": job_id}) + "\n"

    return Response(stream_with_context(generate()), mimetype='application/x-ndjson')

@app.route('/download/<job_id>')
def download_result(job_id):
    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    zip_path = os.path.join(job_dir, f"result_{job_id}.zip")
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True, download_name=f'排版成品.zip')
    else:
        return "Expired", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
