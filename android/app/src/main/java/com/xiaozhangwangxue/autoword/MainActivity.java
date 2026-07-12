package com.xiaozhangwangxue.autoword;

import android.content.*;
import android.database.Cursor;
import android.graphics.Color;
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
import com.google.android.material.button.MaterialButton;
import com.google.android.material.card.MaterialCardView;
import com.google.android.material.textfield.TextInputEditText;
import com.google.android.material.textfield.TextInputLayout;
import org.json.JSONObject;
import java.io.*;
import java.util.*;

public class MainActivity extends AppCompatActivity {
    private final List<Uri> files = new ArrayList<>();
    private TextView status;
    private EditText font, spacing, topMargin, bottomMargin, leftMargin, rightMargin;
    private Spinner punctuation, marginPreset;
    private CheckBox removeEmpty;
    private LinearLayout completedFiles;
    private ActivityResultLauncher<String[]> picker;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        if (!Python.isStarted()) Python.start(new AndroidPlatform(getApplicationContext()));
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true); scroll.setBackgroundColor(Color.rgb(245, 247, 252));
        LinearLayout root = new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(root);
        final int padding = dp(18);
        ViewCompat.setOnApplyWindowInsetsListener(scroll, (view, insets) -> {
            Insets safe = insets.getInsets(WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.displayCutout());
            view.setPadding(padding + safe.left, padding + safe.top, padding + safe.right, padding + safe.bottom);
            return insets;
        });
        LinearLayout hero = addCard(root, true);
        TextView title = new TextView(this); title.setText("AutoWord"); title.setTextColor(Color.WHITE); title.setTextSize(28); hero.addView(title);
        TextView subtitle = new TextView(this); subtitle.setText("离线 DOCX 排版工具 · 文件不会上传网络"); subtitle.setTextColor(0xDFFFFFFF); subtitle.setTextSize(14); subtitle.setPadding(0, dp(4), 0, dp(12)); hero.addView(subtitle);
        MaterialButton github = button("访问 GitHub 项目主页", false); hero.addView(github);

        LinearLayout filesCard = addCard(root, false); filesCard.addView(sectionTitle("选择文档"));
        MaterialButton choose = button("选择 DOCX 文件", true); filesCard.addView(choose);
        status = label("尚未选择文件"); filesCard.addView(status);

        LinearLayout textCard = addCard(root, false); textCard.addView(sectionTitle("文字与标点"));
        font = inputRow(textCard, "正文大小（pt）", "10.5");
        spacing = inputRow(textCard, "行间距（倍）", "1.0");
        punctuation = new Spinner(this); punctuation.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, new String[]{"转半角", "转全角", "保留标点"})); textCard.addView(punctuation);
        removeEmpty = new CheckBox(this); removeEmpty.setText("移除空段落"); removeEmpty.setChecked(true); textCard.addView(removeEmpty);

        LinearLayout marginCard = addCard(root, false); marginCard.addView(sectionTitle("页边距（cm）"));
        marginPreset = new Spinner(this); marginPreset.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, new String[]{"自定义", "四边都是 0.5 cm", "四边都是 0.7 cm", "对称页：内 1.5 cm，外/上下 0.7 cm"})); marginCard.addView(marginPreset);
        topMargin = inputRow(marginCard, "上边距", "0.7"); bottomMargin = inputRow(marginCard, "下边距", "0.7");
        leftMargin = inputRow(marginCard, "左边距", "0.7"); rightMargin = inputRow(marginCard, "右边距", "0.7");

        LinearLayout actionCard = addCard(root, false);
        MaterialButton process = button("开始处理并保存到下载目录", true); actionCard.addView(process);
        completedFiles = new LinearLayout(this); completedFiles.setOrientation(LinearLayout.VERTICAL); actionCard.addView(completedFiles);
        setContentView(scroll);
        ViewCompat.requestApplyInsets(scroll);
        picker = registerForActivityResult(new ActivityResultContracts.OpenMultipleDocuments(), uris -> { files.clear(); files.addAll(uris); status.setText("已选择 " + files.size() + " 个文件"); });
        choose.setOnClickListener(v -> picker.launch(new String[]{"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}));
        github.setOnClickListener(v -> startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/xiaozhangwangxue/autoword"))));
        marginPreset.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            @Override public void onNothingSelected(android.widget.AdapterView<?> parent) { }
            @Override public void onItemSelected(android.widget.AdapterView<?> parent, View view, int position, long id) {
                if (position == 1) setMargins("0.5", "0.5", "0.5", "0.5");
                else if (position == 2) setMargins("0.7", "0.7", "0.7", "0.7");
                else if (position == 3) setMargins("0.7", "0.7", "1.5", "0.7");
            }
        });
        marginPreset.setSelection(2);
        process.setOnClickListener(v -> process());
    }

    private int dp(int value) { return Math.round(value * getResources().getDisplayMetrics().density); }
    private LinearLayout addCard(LinearLayout parent, boolean hero) {
        MaterialCardView card = new MaterialCardView(this); card.setRadius(dp(22)); card.setCardElevation(dp(hero ? 6 : 2)); card.setCardBackgroundColor(hero ? 0xFF146CE5 : Color.WHITE);
        LinearLayout.LayoutParams cardParams = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT); cardParams.setMargins(0, 0, 0, dp(14)); parent.addView(card, cardParams);
        LinearLayout content = new LinearLayout(this); content.setOrientation(LinearLayout.VERTICAL); content.setPadding(dp(18), dp(16), dp(18), dp(16)); card.addView(content); return content;
    }
    private TextView sectionTitle(String value) { TextView v = new TextView(this); v.setText(value); v.setTextColor(0xFF172033); v.setTextSize(17); v.setPadding(0, 0, 0, dp(8)); return v; }
    private TextView label(String value) { TextView v = new TextView(this); v.setText(value); v.setTextColor(0xFF596275); v.setTextSize(14); v.setPadding(0, dp(8), 0, dp(4)); return v; }
    private MaterialButton button(String value, boolean primary) { MaterialButton button = new MaterialButton(this); button.setText(value); button.setCornerRadius(dp(14)); button.setAllCaps(false); if (!primary) { button.setTextColor(Color.WHITE); button.setStrokeColor(android.content.res.ColorStateList.valueOf(0x99FFFFFF)); button.setStrokeWidth(dp(1)); button.setBackgroundColor(Color.TRANSPARENT); } return button; }
    private EditText inputRow(LinearLayout parent, String name, String value) {
        LinearLayout row = new LinearLayout(this); row.setGravity(Gravity.CENTER_VERTICAL); row.setPadding(0, dp(3), 0, dp(3));
        TextView label = new TextView(this); label.setText(name); label.setTextColor(0xFF374151); label.setTextSize(14); row.addView(label, new LinearLayout.LayoutParams(dp(118), ViewGroup.LayoutParams.WRAP_CONTENT));
        TextInputLayout container = new TextInputLayout(this); container.setBoxBackgroundMode(TextInputLayout.BOX_BACKGROUND_OUTLINE); container.setBoxStrokeColor(0xFF3B82F6);
        TextInputEditText field = new TextInputEditText(this); field.setSingleLine(true); field.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL); field.setText(value); container.addView(field);
        row.addView(container, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1)); parent.addView(row); return field;
    }
    private void setMargins(String top, String bottom, String left, String right) { topMargin.setText(top); bottomMargin.setText(bottom); leftMargin.setText(left); rightMargin.setText(right); }

    private void process() {
        if (files.isEmpty()) { status.setText("请先选择 DOCX 文件"); return; }
        status.setText("正在离线处理…");
        new Thread(() -> { try {
            JSONObject o = new JSONObject(); o.put("font_size", Double.parseDouble(font.getText().toString())); o.put("line_spacing", Double.parseDouble(spacing.getText().toString()));
            o.put("space_before", 0); o.put("space_after", 0); o.put("top", Double.parseDouble(topMargin.getText().toString())); o.put("bottom", Double.parseDouble(bottomMargin.getText().toString())); o.put("left", Double.parseDouble(leftMargin.getText().toString())); o.put("right", Double.parseDouble(rightMargin.getText().toString())); o.put("mirror", marginPreset.getSelectedItemPosition() == 3);
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
