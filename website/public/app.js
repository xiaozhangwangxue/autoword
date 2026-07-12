const downloads = {
  android: {
    title: "Android",
    symbol: "A",
    href: "/downloads/AutoWord-android.apk",
    zh: "适用于 Android 7.0 及以上版本 · APK",
    en: "For Android 7.0 and later · APK",
  },
  macos: {
    title: "macOS",
    symbol: "⌘",
    href: "/downloads/AutoWord-macos.dmg",
    zh: "适用于 macOS 12 及以上版本 · 拖拽安装 DMG",
    en: "For macOS 12 and later · Drag-to-install DMG",
  },
  windows: {
    title: "Windows",
    symbol: "⊞",
    href: "/downloads/AutoWord-windows.zip",
    zh: "适用于 Windows 10 / 11 · ZIP",
    en: "For Windows 10 / 11 · ZIP",
  },
  linux: {
    title: "Linux",
    symbol: "L",
    href: "/downloads/AutoWord-linux.tar.gz",
    zh: "适用于 64 位 Linux · tar.gz",
    en: "For 64-bit Linux · tar.gz",
  },
};

function detectPlatform() {
  const ua = navigator.userAgent.toLowerCase();
  const platform = (navigator.userAgentData?.platform || navigator.platform || "").toLowerCase();
  if (/android/.test(ua)) return "android";
  if (/iphone|ipad|ipod/.test(ua) || (platform === "macintel" && navigator.maxTouchPoints > 1)) return "ios";
  if (/win/.test(platform) || /windows/.test(ua)) return "windows";
  if (/mac/.test(platform) || /macintosh/.test(ua)) return "macos";
  if (/linux|x11/.test(platform) || /linux/.test(ua)) return "linux";
  return "unknown";
}

let language = localStorage.getItem("autoword-language") || (navigator.language.startsWith("zh") ? "zh" : "en");
const detectedPlatform = detectPlatform();

const installGuides = {
  android: {
    symbol: "A",
    zh: { lead: "APK 来自官网直链。Android 可能会提醒你允许安装未知来源应用。", steps: ["下载完成后打开 APK 文件", "出现安全提示时，点“设置”并允许此来源", "返回安装页面，点“仍要安装”或“安装”"], note: "仅需为当前浏览器授权；安装完成后可以关闭这项权限。" },
    en: { lead: "This APK is served directly by the official site. Android may ask you to allow installs from this source.", steps: ["Open the downloaded APK", "On the security prompt, open Settings and allow this source", "Return and tap Install or Install anyway"], note: "You can turn this permission off again after installation." },
  },
  macos: {
    symbol: "⌘",
    zh: { lead: "当前版本尚未经过 Apple 公证，首次打开时 macOS 可能会拦截。", steps: ["打开 DMG，把 AutoWord 拖进 Applications（应用程序）", "在“应用程序”中按住 Control 点击 AutoWord，选择“打开”", "弹出确认框后再次点击“打开”"], note: "不要直接双击绕过提示；使用 Control 点击 → 打开，只需要操作一次。" },
    en: { lead: "This build is not yet Apple-notarized, so macOS may block the first launch.", steps: ["Open the DMG and drag AutoWord into Applications", "Control-click AutoWord in Applications and choose Open", "Confirm by clicking Open again"], note: "Control-click → Open is normally needed only once." },
  },
  windows: {
    symbol: "⊞",
    zh: { lead: "Windows SmartScreen 可能会显示“Windows 已保护你的电脑”。", steps: ["解压下载的 ZIP 文件", "启动 AutoWord.exe；出现提示时点“更多信息”", "点击“仍要运行”"], note: "请先完整解压，不要直接在 ZIP 压缩包中运行。" },
    en: { lead: "Windows SmartScreen may say that Windows protected your PC.", steps: ["Extract the downloaded ZIP", "Launch AutoWord.exe and choose More info if prompted", "Click Run anyway"], note: "Extract the whole archive before launching the app." },
  },
  linux: {
    symbol: "L",
    zh: { lead: "Linux 版本以压缩包提供，首次运行需要赋予执行权限。", steps: ["解压 tar.gz 文件", "右键主程序 → 属性 → 权限，允许作为程序执行", "双击启动；也可在终端运行 chmod +x AutoWord"], note: "不同桌面环境的按钮名称可能略有不同。" },
    en: { lead: "The Linux build is distributed as an archive and may need execute permission.", steps: ["Extract the tar.gz archive", "Open Properties → Permissions and allow executing as a program", "Launch it, or run chmod +x AutoWord in a terminal"], note: "Wording varies slightly between desktop environments." },
  },
};

function showInstallGuide(platform, href) {
  const guide = installGuides[platform];
  if (!guide) return;
  const copy = guide[language];
  document.getElementById("installSymbol").textContent = guide.symbol;
  document.getElementById("installSymbol").className = `dialog-platform ${platform}`;
  document.getElementById("installTitle").textContent = language === "zh" ? `安装 AutoWord ${downloads[platform].title} 版` : `Install AutoWord for ${downloads[platform].title}`;
  document.getElementById("installLead").textContent = copy.lead;
  document.getElementById("installSteps").innerHTML = copy.steps.map((step, index) => `<li><span>${index + 1}</span><p>${step}</p></li>`).join("");
  document.getElementById("installNote").textContent = `! ${copy.note}`;
  document.getElementById("installContinue").href = href;
  document.getElementById("installDialog").showModal();
}

function setRecommendedDownload() {
  const title = document.getElementById("recommendedTitle");
  const description = document.getElementById("recommendedDescription");
  const button = document.getElementById("recommendedButton");
  const buttonText = document.getElementById("recommendedButtonText");
  const symbol = document.getElementById("recommendedSymbol");

  document.querySelectorAll(".download-card").forEach((card) => card.classList.remove("is-recommended"));

  if (downloads[detectedPlatform]) {
    const item = downloads[detectedPlatform];
    title.textContent = `AutoWord for ${item.title}`;
    description.textContent = item[language];
    button.href = item.href;
    button.setAttribute("download", "");
    buttonText.textContent = language === "zh" ? `下载 ${item.title} 版本` : `Download for ${item.title}`;
    symbol.textContent = item.symbol;
    symbol.className = `platform-symbol ${detectedPlatform}`;
    document.querySelector(`[data-platform="${detectedPlatform}"]`)?.classList.add("is-recommended");
    return;
  }

  if (detectedPlatform === "ios") {
    title.textContent = language === "zh" ? "当前设备为 iPhone / iPad" : "You're on iPhone or iPad";
    description.textContent = language === "zh" ? "AutoWord 暂无 iOS 版本，请在 Android 或电脑上使用" : "AutoWord is not yet available for iOS. Use it on Android or desktop.";
    button.href = "#allDownloads";
    button.removeAttribute("download");
    buttonText.textContent = language === "zh" ? "查看全部版本" : "View all versions";
    symbol.textContent = "i";
    symbol.className = "platform-symbol macos";
    return;
  }

  title.textContent = language === "zh" ? "选择适合你的版本" : "Choose your version";
  description.textContent = language === "zh" ? "支持 Android、macOS、Windows 和 Linux" : "Available for Android, macOS, Windows and Linux";
  button.href = "#allDownloads";
  button.removeAttribute("download");
  buttonText.textContent = language === "zh" ? "查看全部版本" : "View all versions";
  symbol.textContent = "↓";
  symbol.className = "platform-symbol";
}

function applyLanguage(nextLanguage) {
  language = nextLanguage;
  localStorage.setItem("autoword-language", language);
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  document.title = language === "zh" ? "AutoWord — 离线 Word 文档智能排版" : "AutoWord — Offline Word document formatting";
  document.querySelectorAll("[data-zh][data-en]").forEach((element) => {
    element.textContent = element.dataset[language];
  });
  document.querySelectorAll("[data-zh-aria][data-en-aria]").forEach((element) => {
    element.setAttribute("aria-label", language === "zh" ? element.dataset.zhAria : element.dataset.enAria);
  });
  document.getElementById("languageButton").textContent = language === "zh" ? "EN" : "中";
  setRecommendedDownload();
}

document.getElementById("languageButton").addEventListener("click", () => applyLanguage(language === "zh" ? "en" : "zh"));
document.querySelectorAll(".download-card > a, #recommendedButton").forEach((link) => {
  link.addEventListener("click", (event) => {
    const platform = link.closest("[data-platform]")?.dataset.platform || detectedPlatform;
    if (!installGuides[platform] || !link.href.includes("/downloads/")) return;
    event.preventDefault();
    showInstallGuide(platform, link.href);
  });
});
document.getElementById("installClose").addEventListener("click", () => document.getElementById("installDialog").close());
document.getElementById("installCancel").addEventListener("click", () => document.getElementById("installDialog").close());
document.getElementById("installContinue").addEventListener("click", () => document.getElementById("installDialog").close());
applyLanguage(language);
