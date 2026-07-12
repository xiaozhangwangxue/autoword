package com.xiaozhangwangxue.autoword;

import android.content.*;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.provider.OpenableColumns;
import android.text.InputType;
import android.view.*;
import android.widget.*;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import com.chaquo.python.android.AndroidPlatform;
import com.chaquo.python.Python;
import org.json.JSONObject;
import java.io.*;
import java.util.*;

public class MainActivity extends AppCompatActivity {
    private final List<Uri> files = new ArrayList<>();
    private TextView status;
    private EditText font, spacing, topMargin, bottomMargin, leftMargin, rightMargin;
    private Spinner punctuation;
    private CheckBox removeEmpty;
    private LinearLayout completedFiles;
    private ActivityResultLauncher<String[]> picker;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        if (!Python.isStarted()) Python.start(new AndroidPlatform(getApplicationContext()));
        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(root);
        final int padding = dp(18);
        ViewCompat.setOnApplyWindowInsetsListener(scroll, (view, insets) -> {
            Insets safe = insets.getInsets(WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.displayCutout());
            view.setPadding(padding + safe.left, padding + safe.top, padding + safe.right, padding + safe.bottom);
            return insets;
        });
        TextView title = new TextView(this); title.setText("AutoWord 离线排版"); title.setTextSize(24); root.addView(title);
        root.addView(label("所有文件只在本机处理，不会上传网络。"));
        Button github = new Button(this); github.setText("访问 GitHub 项目主页"); root.addView(github);
        Button choose = new Button(this); choose.setText("选择 DOCX 文件"); root.addView(choose);
        font = inputRow(root, "正文大小（pt）", "10.5");
        spacing = inputRow(root, "行间距（倍）", "1.0");
        root.addView(label("页边距（cm）"));
        topMargin = inputRow(root, "上边距", "0.7");
        bottomMargin = inputRow(root, "下边距", "0.7");
        leftMargin = inputRow(root, "左边距", "0.7");
        rightMargin = inputRow(root, "右边距", "0.7");
        punctuation = new Spinner(this); punctuation.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, new String[]{"转半角", "转全角", "保留标点"})); root.addView(punctuation);
        removeEmpty = new CheckBox(this); removeEmpty.setText("移除空段落"); removeEmpty.setChecked(true); root.addView(removeEmpty);
        Button process = new Button(this); process.setText("开始处理并保存到下载目录"); root.addView(process);
        status = label("尚未选择文件"); root.addView(status);
        completedFiles = new LinearLayout(this); completedFiles.setOrientation(LinearLayout.VERTICAL); root.addView(completedFiles);
        setContentView(scroll);
        ViewCompat.requestApplyInsets(scroll);
        picker = registerForActivityResult(new ActivityResultContracts.OpenMultipleDocuments(), uris -> { files.clear(); files.addAll(uris); status.setText("已选择 " + files.size() + " 个文件"); });
        choose.setOnClickListener(v -> picker.launch(new String[]{"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}));
        github.setOnClickListener(v -> startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/xiaozhangwangxue/autoword"))));
        process.setOnClickListener(v -> process());
    }

    private int dp(int value) { return Math.round(value * getResources().getDisplayMetrics().density); }
    private TextView label(String value) { TextView v = new TextView(this); v.setText(value); v.setPadding(0, dp(12), 0, dp(6)); return v; }
    private EditText inputRow(LinearLayout parent, String name, String value) {
        LinearLayout row = new LinearLayout(this); row.setGravity(Gravity.CENTER_VERTICAL); row.setPadding(0, dp(4), 0, dp(4));
        TextView label = new TextView(this); label.setText(name); label.setTextSize(15); row.addView(label, new LinearLayout.LayoutParams(dp(118), ViewGroup.LayoutParams.WRAP_CONTENT));
        EditText field = new EditText(this); field.setSingleLine(true); field.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL); field.setText(value);
        row.addView(field, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1)); parent.addView(row); return field;
    }

    private void process() {
        if (files.isEmpty()) { status.setText("请先选择 DOCX 文件"); return; }
        status.setText("正在离线处理…");
        new Thread(() -> { try {
            JSONObject o = new JSONObject(); o.put("font_size", Double.parseDouble(font.getText().toString())); o.put("line_spacing", Double.parseDouble(spacing.getText().toString()));
            o.put("space_before", 0); o.put("space_after", 0); o.put("top", Double.parseDouble(topMargin.getText().toString())); o.put("bottom", Double.parseDouble(bottomMargin.getText().toString())); o.put("left", Double.parseDouble(leftMargin.getText().toString())); o.put("right", Double.parseDouble(rightMargin.getText().toString()));
            o.put("punctuation", new String[]{"halfwidth", "fullwidth", "preserve"}[punctuation.getSelectedItemPosition()]); o.put("remove_empty", removeEmpty.isChecked()); o.put("footer_mode", "first_line");
            Python py = Python.getInstance(); int done = 0; List<OutputFile> outputs = new ArrayList<>();
            for (Uri uri : files) {
                File source = copy(uri); File result = new File(getCacheDir(), "formatted_" + (++done) + ".docx");
                py.getModule("formatter").callAttr("format_document", source.getPath(), result.getPath(), o.toString());
                String outputName = outputName(uri); outputs.add(new OutputFile(outputName, save(result, outputName)));
            }
            int total = done; runOnUiThread(() -> showOutputs(total, outputs));
        } catch (Exception e) { runOnUiThread(() -> status.setText("处理失败：" + e.getMessage())); } }).start();
    }
    private static class OutputFile { final String name; final Uri uri; OutputFile(String name, Uri uri) { this.name = name; this.uri = uri; } }
    private void showOutputs(int total, List<OutputFile> outputs) {
        status.setText("完成：" + total + " 个文件已保存到 Downloads/AutoWord"); completedFiles.removeAllViews(); completedFiles.addView(label("完成文件（点击打开）"));
        for (OutputFile output : outputs) { Button open = new Button(this); open.setText(output.name); open.setOnClickListener(v -> openOutput(output.uri)); completedFiles.addView(open); }
    }
    private void openOutput(Uri uri) { Intent intent = new Intent(Intent.ACTION_VIEW).setDataAndType(uri, "application/vnd.openxmlformats-officedocument.wordprocessingml.document").addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION); startActivity(Intent.createChooser(intent, "打开文件")); }
    private String outputName(Uri uri) { String original = displayName(uri); int dot = original.lastIndexOf('.'); String base = dot > 0 ? original.substring(0, dot) : original; return base + "*.docx"; }
    private String displayName(Uri uri) { try (Cursor cursor = getContentResolver().query(uri, new String[]{OpenableColumns.DISPLAY_NAME}, null, null, null)) { if (cursor != null && cursor.moveToFirst()) return cursor.getString(0); } return "document.docx"; }
    private File copy(Uri uri) throws IOException { File f = File.createTempFile("input_", ".docx", getCacheDir()); try (InputStream in = getContentResolver().openInputStream(uri); OutputStream out = new FileOutputStream(f)) { byte[] b = new byte[8192]; for (int n; (n = in.read(b)) > 0;) out.write(b, 0, n); } return f; }
    private Uri save(File file, String name) throws IOException { ContentValues v = new ContentValues(); v.put(MediaStore.Downloads.DISPLAY_NAME, name); v.put(MediaStore.Downloads.MIME_TYPE, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"); v.put(MediaStore.Downloads.RELATIVE_PATH, "Download/AutoWord"); Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v); if (uri == null) throw new IOException("无法创建下载文件"); try (OutputStream out = getContentResolver().openOutputStream(uri); InputStream in = new FileInputStream(file)) { byte[] b = new byte[8192]; for (int n; (n = in.read(b)) > 0;) out.write(b, 0, n); } return uri; }
}
