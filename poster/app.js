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

function el(id) {
  return document.getElementById(id);
}

function currentPalette() {
  const theme = el("theme") ? el("theme").value : "green";
  const paper = el("paper") ? el("paper").value : "cream";
  return paper === "dark" ? "dark" : theme;
}

function setSrc(node, src) {
  if (node && src) node.setAttribute("src", src);
}

function applyAssets() {
  const pack = ASSETS[currentPalette()];
  if (!pack) return;
  setSrc(el("emblem"), pack.emblem);
  setSrc(el("nameplate"), pack.name);
  setSrc(el("watermark"), pack.haitang);
  setSrc(el("mottoMark"), pack.motto);
  document.querySelectorAll(".ornament").forEach((img) => setSrc(img, pack.ornament));
}

function toggleSimpleFields() {
  const layout = el("layout");
  const fields = el("simpleFields");
  if (!layout || !fields) return;
  fields.hidden = layout.value === "reg-day" || layout.value === "reg-docs";
}

function applyChrome() {
  const poster = el("poster");
  const layout = el("layout");
  if (!poster || !layout) return;
  poster.setAttribute("data-theme", el("theme").value);
  poster.setAttribute("data-paper", el("paper").value);
  poster.setAttribute("data-size", el("size").value);
  poster.setAttribute("data-layout", layout.value);
  applyAssets();
  toggleSimpleFields();
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
    const input = el(id);
    const target = document.querySelector(sel);
    if (!input || !target) return;
    input.addEventListener("input", () => {
      target.innerText = input.value;
    });
    target.addEventListener("input", () => {
      input.value = target.innerText;
    });
  });
}

function fitPoster() {
  const poster = el("poster");
  const stage = el("stage");
  const wrap = el("canvasWrap");
  if (!poster || !stage || !wrap) return;
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
  const size = el("size").value;
  let page = "A3 portrait";
  if (size === "a4") page = "A4 portrait";
  if (size === "story") page = "1080px 1920px";
  let tag = el("printPage");
  if (!tag) {
    tag = document.createElement("style");
    tag.id = "printPage";
    document.head.appendChild(tag);
  }
  tag.textContent = `@media print { @page { size: ${page}; margin: 0; } }`;
  window.print();
}

function downloadJson() {
  const data = { layout: el("layout").value, theme: el("theme").value };
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
      const node = el(id);
      if (node) node.value = value;
    });
    applyChrome();
  };
  reader.readAsText(file);
}

function customLogo(file) {
  setSrc(el("emblem"), URL.createObjectURL(file));
}

window.applyChrome = applyChrome;
window.printPoster = printPoster;

window.addEventListener("DOMContentLoaded", () => {
  const layout = el("layout");
  const theme = el("theme");
  layout.addEventListener("change", applyChrome);
  ["theme", "paper", "size"].forEach((id) => {
    el(id).addEventListener("change", applyChrome);
  });
  document.querySelectorAll(".swatch").forEach((btn) => {
    btn.addEventListener("click", () => {
      theme.value = btn.dataset.theme;
      document.querySelectorAll(".swatch").forEach((b) => b.classList.toggle("active", b === btn));
      applyChrome();
    });
  });
  el("printBtn").addEventListener("click", printPoster);
  el("saveBtn").addEventListener("click", downloadJson);
  el("loadBtn").addEventListener("click", () => el("jsonFile").click());
  el("jsonFile").addEventListener("change", (e) => e.target.files[0] && importJson(e.target.files[0]));
  el("logoFile").addEventListener("change", (e) => e.target.files[0] && customLogo(e.target.files[0]));
  window.addEventListener("resize", fitPoster);
  bindFields();
  applyChrome();
});
