const W = 1920;
const H = 1080;

function resolvePhoto(photos, key) {
  const spec = photos[key];
  if (!spec) return { src: "", label: "", caption: "", alt: "", fallback: true };
  return {
    src: spec.resolved || spec.fallback,
    label: spec.label,
    caption: spec.caption,
    alt: spec.alt,
    fallback: Boolean(spec.usingFallback),
    note: spec.placeholderNote,
  };
}

function el(html) {
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}

function brand(meta, light) {
  const emblem = light
    ? "../poster/assets/校徽_绿.svg"
    : "../poster/assets/校徽_反白.svg";
  const color = light ? "var(--green)" : "var(--cream)";
  return `
    <div class="brand" style="color:${color}">
      <img src="${emblem}" alt="中山大学校徽">
      <div>
        <div class="brand-name">${meta.university}</div>
        <div class="brand-en">${meta.universityEn}</div>
      </div>
    </div>`;
}

function topbar(meta, light, right) {
  return `
    <div class="topbar">
      ${brand(meta, light)}
      <div class="kicker" style="${light ? "color:var(--green)" : ""}">${right}</div>
    </div>`;
}

function footbar(meta, i, n, light) {
  const color = light ? "color:var(--muted)" : "";
  return `
    <div class="footbar" style="${color}">
      <span>${meta.motto}</span>
      <span>${String(i + 1).padStart(2, "0")} / ${String(n).padStart(2, "0")}</span>
    </div>`;
}

function renderCover(slide, meta, i, n) {
  return `
    <section class="slide slide-cover" data-id="${slide.id}" data-name="slide-${slide.id}">
      <div class="bg" style="background-image:url('${slide.background}')"></div>
      <div class="veil"></div>
      ${topbar(meta, false, slide.kicker)}
      <div class="cover-copy">
        <div class="gold-rule"></div>
        <h1 data-name="标题 1">${slide.title}</h1>
        <p class="subtitle" data-name="副标题">${slide.subtitle}</p>
        <p class="speaker" data-name="讲者">${slide.speaker}</p>
      </div>
      ${footbar(meta, i, n, false)}
    </section>`;
}

function renderQuote(slide, meta, i, n) {
  const points = slide.points
    .map((p, idx) => `<div class="point"><b>0${idx + 1}</b><span>${p}</span></div>`)
    .join("");
  return `
    <section class="slide slide-quote" data-id="${slide.id}">
      ${topbar(meta, true, slide.kicker)}
      <div class="inner">
        <div class="kicker" style="color:var(--gold)">${slide.kicker}</div>
        <h1>${slide.title}</h1>
        <p class="lead">${slide.body}</p>
        <div class="point-row">${points}</div>
      </div>
      ${footbar(meta, i, n, true)}
    </section>`;
}

function renderMap(slide, meta, i, n) {
  const cards = slide.cards
    .map(
      (c) => `
      <article class="map-card">
        <div class="photo" style="background-image:url('${c.photo}')"></div>
        <div class="shade"></div>
        <div class="txt">
          <div class="num">${c.num}</div>
          <h2>${c.title}</h2>
          <p class="line">${c.line}</p>
        </div>
      </article>`
    )
    .join("");
  return `
    <section class="slide slide-map" data-id="${slide.id}">
      ${topbar(meta, true, slide.kicker)}
      <div class="inner">
        <div class="kicker" style="color:var(--gold)">${slide.kicker}</div>
        <h1>${slide.title}</h1>
        <div class="map-grid">${cards}</div>
      </div>
      ${footbar(meta, i, n, true)}
    </section>`;
}

function photoCard(photo) {
  const badge = photo.fallback
    ? `<span class="using-fallback">校园氛围图 · 待换个人照片</span>`
    : "";
  return `
    <figure class="photo-card" data-name="${photo.name || "image"}">
      <img src="${photo.src}" alt="${photo.alt}">
      ${badge}
      <figcaption>
        <span class="label">${photo.label}</span>
        <span class="cap">${photo.caption}</span>
      </figcaption>
    </figure>`;
}

function renderExperience(slide, meta, photos, i, n) {
  const p1 = resolvePhoto(photos, slide.image1);
  const p2 = resolvePhoto(photos, slide.image2);
  return `
    <section class="slide slide-experience" data-id="${slide.id}">
      ${topbar(meta, true, meta.series + " · " + meta.year)}
      <div class="exp-layout">
        <div class="exp-copy">
          <h1 data-name="标题 1">${slide.title}</h1>
          <p class="green-title" data-name="文本框 25">${slide.greenTitle}</p>
          <div class="stats">
            <div class="stat"><b data-name="文本框 7">${slide.n1}</b><span data-name="文本框 10">${slide.l1}</span></div>
            <div class="stat"><b data-name="文本框 12">${slide.n2}</b><span data-name="文本框 13">${slide.l2}</span></div>
          </div>
          <div class="quote-card">
            <h2 data-name="文本框 22">${slide.whiteTitle}</h2>
            <p data-name="文本框 21">${slide.body}</p>
          </div>
        </div>
        <div class="exp-photos">
          ${photoCard({ ...p1, name: "图片 29" })}
          ${photoCard({ ...p2, name: "图片 23" })}
        </div>
      </div>
      ${footbar(meta, i, n, true)}
    </section>`;
}

function renderAdvice(slide, meta, i, n) {
  const cards = slide.items
    .map(
      (it) => `
      <article class="advice-card">
        <div class="n">${it.n}</div>
        <h2>${it.title}</h2>
        <p>${it.body}</p>
      </article>`
    )
    .join("");
  return `
    <section class="slide slide-advice" data-id="${slide.id}">
      ${topbar(meta, true, slide.kicker)}
      <div class="inner">
        <div class="kicker" style="color:var(--gold)">${slide.kicker}</div>
        <h1>${slide.title}</h1>
        <div class="advice-grid">${cards}</div>
      </div>
      ${footbar(meta, i, n, true)}
    </section>`;
}

function renderClose(slide, meta, i, n) {
  return `
    <section class="slide slide-close" data-id="${slide.id}">
      <div class="bg" style="background-image:url('${slide.background}')"></div>
      <div class="veil"></div>
      ${topbar(meta, false, slide.kicker)}
      <div class="close-copy">
        <div class="gold-rule"></div>
        <h1>${slide.title}</h1>
        <p class="subtitle">${slide.body}</p>
        <p class="speaker">${slide.speaker}</p>
      </div>
      ${footbar(meta, i, n, false)}
    </section>`;
}

function renderSlide(slide, meta, photos, i, n) {
  switch (slide.kind) {
    case "cover":
      return renderCover(slide, meta, i, n);
    case "quote":
      return renderQuote(slide, meta, i, n);
    case "map":
      return renderMap(slide, meta, i, n);
    case "experience":
      return renderExperience(slide, meta, photos, i, n);
    case "advice":
      return renderAdvice(slide, meta, i, n);
    case "close":
      return renderClose(slide, meta, i, n);
    default:
      return `<section class="slide" data-id="${slide.id}"></section>`;
  }
}

function scaleStage() {
  const stage = document.querySelector(".stage");
  const s = Math.min(window.innerWidth / W, window.innerHeight / H);
  stage.style.transform = `scale(${s})`;
}

function setSlide(index, slides) {
  const max = slides.length - 1;
  const i = Math.max(0, Math.min(max, index));
  document.querySelectorAll(".slide").forEach((node, idx) => {
    node.classList.toggle("is-active", idx === i);
  });
  const notes = document.getElementById("notes");
  if (notes) notes.textContent = slides[i].notes || "";
  const counter = document.getElementById("counter");
  if (counter) counter.textContent = `${i + 1} / ${slides.length}`;
  const url = new URL(window.location.href);
  url.searchParams.set("slide", String(i + 1));
  history.replaceState(null, "", url);
  return i;
}

async function main() {
  const params = new URLSearchParams(location.search);
  if (params.get("shot") === "1") document.body.classList.add("shot");

  const data = await fetch("./content.json").then((r) => r.json());
  const resolved = await fetch("./resolved-photos.json")
    .then((r) => (r.ok ? r.json() : null))
    .catch(() => null);
  const photos = resolved || data.photos;
  const slides = data.slides;
  const meta = data.meta;

  const stage = document.querySelector(".stage");
  stage.innerHTML = slides
    .map((slide, i) => renderSlide(slide, meta, photos, i, slides.length))
    .join("");

  let index = Number(params.get("slide") || 1) - 1;
  index = setSlide(index, slides);

  document.getElementById("prev").onclick = () => {
    index = setSlide(index - 1, slides);
  };
  document.getElementById("next").onclick = () => {
    index = setSlide(index + 1, slides);
  };
  document.getElementById("toggle-notes").onclick = () => {
    document.getElementById("notes").classList.toggle("is-open");
  };

  window.addEventListener("keydown", (e) => {
    if (["ArrowRight", "PageDown", " ", "Enter"].includes(e.key)) {
      e.preventDefault();
      index = setSlide(index + 1, slides);
    } else if (["ArrowLeft", "PageUp", "Backspace"].includes(e.key)) {
      e.preventDefault();
      index = setSlide(index - 1, slides);
    } else if (e.key === "n") {
      document.getElementById("notes").classList.toggle("is-open");
    } else if (e.key === "Home") {
      index = setSlide(0, slides);
    } else if (e.key === "End") {
      index = setSlide(slides.length - 1, slides);
    }
  });

  scaleStage();
  window.addEventListener("resize", scaleStage);
}

main();
