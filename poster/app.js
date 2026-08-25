const $ = (sel, root = document) => root.querySelector(sel);

const ASSETS = {
  green: {
    emblem: "assets/校徽_绿.svg",
    name: "assets/校名_横式_绿.svg",
    haitang: "assets/海棠式洞窗_绿.svg",
    ornament: "assets/海棠装饰_空心_绿.svg",
    motto: "assets/校训.svg",
  },
  red: {
    emblem: "assets/校徽_红.svg",
    name: "assets/校名_横式_红.svg",
    haitang: "assets/海棠式洞窗_红.svg",
    ornament: "assets/海棠装饰_空心_红.svg",
    motto: "assets/校训.svg",
  },
  dark: {
    emblem: "assets/校徽_反白.svg",
    name: "assets/校名_横式_反白.svg",
    haitang: "assets/海棠式洞窗_反白.svg",
    ornament: "assets/海棠装饰_实心_反白.svg",
    motto: "assets/校训_反白.svg",
  },
};

const PRESETS = {
  lecture: {
    kicker: "学术活动",
    title: "逸仙学术讲座",
    subtitle: "面向未来的大学与社会",
    english: "Sun Yat-sen Distinguished Lecture",
    date: "2026年9月18日 星期四",
    time: "14:30–16:30",
    venue: "广州校区南校园\n梁銶琚堂",
    speaker: "特邀嘉宾",
    role: "中山大学教授",
    body: "本次讲座面向全校师生开放。请持校园卡提前十五分钟入场。讲座结束后开放交流环节。",
    organizer: "主办：中山大学\n承办：相关学院 / 部门",
    contact: "广州市海珠区新港西路135号  邮编 510275",
  },
  notice: {
    kicker: "通知公告",
    title: "开学典礼",
    subtitle: "欢迎新中大人",
    english: "Opening Ceremony",
    date: "2026年9月1日 星期二",
    time: "09:00",
    venue: "广州校区南校园\n运动场",
    speaker: "",
    role: "",
    body: "请全体新生准时出席。着装端庄得体，提前入场就座。如遇天气变化，请关注学校官方通知。",
    organizer: "主办：中山大学",
    contact: "广州市海珠区新港西路135号  邮编 510275",
  },
  ceremony: {
    kicker: "典礼仪式",
    title: "纪念大会",
    subtitle: "博学 审问 慎思 明辨 笃行",
    english: "Commemorative Assembly",
    date: "2026年11月12日",
    time: "09:30",
    venue: "中山大学\n怀士堂",
    speaker: "",
    role: "",
    body: "谨此恭请相关单位代表与师生出席。座位席次与流程以现场安排为准。",
    organizer: "主办：中山大学",
    contact: "广州市海珠区新港西路135号  邮编 510275",
  },
};

function currentPalette() {
  const theme = $("#theme").value;
  const paper = $("#paper").value;
  return paper === "dark" ? "dark" : theme;
}

function applyAssets() {
  const pack = ASSETS[currentPalette()];
  $(".emblem").src = pack.emblem;
  $(".nameplate").src = pack.name;
  $(".watermark").src = pack.haitang;
  document.querySelectorAll(".ornament").forEach((el) => (el.src = pack.ornament));
  $(".mottoMark").src = pack.motto;
}

function applyChrome() {
  const poster = $(".poster");
  poster.dataset.theme = $("#theme").value;
  poster.dataset.paper = $("#paper").value;
  poster.dataset.size = $("#size").value;
  poster.dataset.layout = $("#layout").value;
  applyAssets();
  fitPoster();
}

function bindFields() {
  const map = [
    ["kicker", ".kicker"],
    ["title", ".title"],
    ["subtitle", ".subtitle"],
    ["english", ".english"],
    ["date", "#dateValue"],
    ["time", "#timeValue"],
    ["venue", "#venueValue"],
    ["speaker", ".who"],
    ["role", ".role"],
    ["body", ".body-copy"],
    ["organizer", "#organizerValue"],
    ["contact", "#contactValue"],
  ];
  map.forEach(([id, sel]) => {
    const input = document.getElementById(id);
    const target = $(sel);
    const sync = () => {
      target.innerText = input.value;
    };
    input.addEventListener("input", sync);
    target.addEventListener("input", () => {
      input.value = target.innerText;
    });
  });
}

function loadPreset(name) {
  const data = PRESETS[name];
  Object.entries(data).forEach(([key, value]) => {
    const el = document.getElementById(key);
    if (el) el.value = value;
  });
  document.querySelectorAll("input, textarea").forEach((el) => el.dispatchEvent(new Event("input")));
  if (name === "lecture") $("#layout").value = "lecture";
  if (name === "notice") $("#layout").value = "classic";
  if (name === "ceremony") {
    $("#layout").value = "classic";
    $("#theme").value = "red";
  }
  applyChrome();
}

function fitPoster() {
  const poster = $("#poster");
  const stage = $("#stage");
  const wrap = $("#canvasWrap");
  const pad = 56;
  const scale = Math.min(
    (stage.clientWidth - pad) / poster.offsetWidth,
    (stage.clientHeight - pad) / poster.offsetHeight,
    1
  );
  wrap.style.transform = `scale(${scale})`;
  wrap.style.width = `${poster.offsetWidth * scale}px`;
  wrap.style.height = `${poster.offsetHeight * scale}px`;
}

function printPoster() {
  const size = $("#size").value;
  let page = "A3 portrait";
  if (size === "a4") page = "A4 portrait";
  if (size === "story") page = "1080px 1920px";
  let tag = document.getElementById("printPage");
  if (!tag) {
    tag = document.createElement("style");
    tag.id = "printPage";
    document.head.appendChild(tag);
  }
  tag.textContent = `@media print { @page { size: ${page}; margin: 0; } }`;
  window.print();
}

function downloadJson() {
  const data = {};
  document.querySelectorAll(".panel input, .panel textarea, .panel select").forEach((el) => {
    if (el.id) data[el.id] = el.value;
  });
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "sysu-poster.json";
  a.click();
}

function importJson(file) {
  const reader = new FileReader();
  reader.onload = () => {
    const data = JSON.parse(reader.result);
    Object.entries(data).forEach(([id, value]) => {
      const el = document.getElementById(id);
      if (el) el.value = value;
    });
    document.querySelectorAll("input, textarea, select").forEach((el) => el.dispatchEvent(new Event("input")));
    applyChrome();
  };
  reader.readAsText(file);
}

function customLogo(file) {
  const url = URL.createObjectURL(file);
  $(".emblem").src = url;
}

window.addEventListener("DOMContentLoaded", () => {
  bindFields();
  loadPreset("lecture");
  ["theme", "paper", "size", "layout"].forEach((id) => {
    document.getElementById(id).addEventListener("change", applyChrome);
  });
  document.querySelectorAll(".swatch").forEach((btn) => {
    btn.addEventListener("click", () => {
      $("#theme").value = btn.dataset.theme;
      document.querySelectorAll(".swatch").forEach((b) => b.classList.toggle("active", b === btn));
      applyChrome();
    });
  });
  $("#preset").addEventListener("change", (e) => loadPreset(e.target.value));
  $("#printBtn").addEventListener("click", printPoster);
  $("#saveBtn").addEventListener("click", downloadJson);
  $("#loadBtn").addEventListener("click", () => $("#jsonFile").click());
  $("#jsonFile").addEventListener("change", (e) => e.target.files[0] && importJson(e.target.files[0]));
  $("#logoFile").addEventListener("change", (e) => e.target.files[0] && customLogo(e.target.files[0]));
  window.addEventListener("resize", fitPoster);
  applyChrome();
});
