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
applyLanguage(language);
