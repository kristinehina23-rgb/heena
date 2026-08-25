const ASSETS = {
  green: {
    emblem: "assets/校徽_绿.svg",
    emblemWhite: "assets/校徽_反白.svg",
    name: "assets/校名_横式_绿.svg",
    haitang: "assets/海棠式洞窗_绿.svg",
    ornament: "assets/海棠装饰_空心_绿.svg",
  },
  red: {
    emblem: "assets/校徽_红.svg",
    emblemWhite: "assets/校徽_反白.svg",
    name: "assets/校名_横式_红.svg",
    haitang: "assets/海棠式洞窗_红.svg",
    ornament: "assets/海棠装饰_空心_红.svg",
  },
};

function el(id) {
  return document.getElementById(id);
}

function applyAssets() {
  const theme = el("theme").value;
  const pack = ASSETS[theme] || ASSETS.green;
  document.querySelectorAll("[data-asset='emblem']").forEach((n) => n.setAttribute("src", pack.emblem));
  document.querySelectorAll("[data-asset='emblem-white']").forEach((n) => n.setAttribute("src", pack.emblemWhite));
  document.querySelectorAll("[data-asset='name']").forEach((n) => n.setAttribute("src", pack.name));
  document.querySelectorAll("[data-asset='haitang']").forEach((n) => n.setAttribute("src", pack.haitang));
  document.querySelectorAll("[data-asset='ornament']").forEach((n) => n.setAttribute("src", pack.ornament));
}

function applyChrome() {
  const theme = el("theme").value;
  const paper = el("paper").value;
  const size = el("size").value;
  const view = el("view").value;
  el("stage").setAttribute("data-view", view);
  document.querySelectorAll(".poster").forEach((poster) => {
    poster.setAttribute("data-theme", theme);
    poster.setAttribute("data-paper", paper);
    poster.setAttribute("data-size", size);
  });
  applyAssets();
  fitPosters();
}

function fitPosters() {
  const stage = el("stage");
  const view = stage.getAttribute("data-view") || "both";
  const sheets = {
    day: document.querySelector(".wrap-day"),
    docs: document.querySelector(".wrap-docs"),
  };
  const visible = (view === "both" ? [sheets.day, sheets.docs] : [sheets[view]]).filter(Boolean);
  const gap = 36;
  const extra = 48;
  visible.forEach((sheet) => {
    const poster = sheet.querySelector(".poster");
    const wrap = sheet.querySelector(".canvas-wrap");
    if (!poster || !wrap || poster.offsetWidth < 40 || poster.offsetHeight < 40) return;
    const count = visible.length;
    const availW = Math.max(260, (Math.max(stage.clientWidth, 320) - extra - (count - 1) * gap) / count);
    const availH = Math.max(420, Math.max(stage.clientHeight, 500) - 72);
    let scale = Math.min(availW / poster.offsetWidth, availH / poster.offsetHeight, 1);
    if (!isFinite(scale) || scale < 0.18) scale = 0.22;
    wrap.style.transform = `scale(${scale})`;
    wrap.style.width = `${poster.offsetWidth * scale}px`;
    wrap.style.height = `${poster.offsetHeight * scale}px`;
  });
}

function printPoster() {
  const size = el("size").value === "a4" ? "A4 portrait" : "A3 portrait";
  let tag = el("printPage");
  if (!tag) {
    tag = document.createElement("style");
    tag.id = "printPage";
    document.head.appendChild(tag);
  }
  tag.textContent = `@media print { @page { size: ${size}; margin: 0; } }`;
  window.print();
}

window.applyChrome = applyChrome;
window.printPoster = printPoster;

window.addEventListener("DOMContentLoaded", () => {
  el("view").addEventListener("change", applyChrome);
  ["theme", "paper", "size"].forEach((id) => el(id).addEventListener("change", applyChrome));
  document.querySelectorAll(".swatch").forEach((btn) => {
    btn.addEventListener("click", () => {
      el("theme").value = btn.dataset.theme;
      document.querySelectorAll(".swatch").forEach((b) => b.classList.toggle("active", b === btn));
      applyChrome();
    });
  });
  el("printBtn").addEventListener("click", printPoster);
  window.addEventListener("resize", fitPosters);
  const wanted = new URLSearchParams(location.search).get("view");
  if (wanted && el("view").querySelector(`option[value="${wanted}"]`)) {
    el("view").value = wanted;
  }
  applyChrome();
});
