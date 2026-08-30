/**
 * Artifact-tool compose script for the 2026 SYSU freshman-share deck.
 *
 * Run this in an environment that has @oai/artifact-tool. Do not import the
 * original Office file: it embeds 等线/DengXian as OTTO/CFF (scaler 0x4F54544F)
 * and the EOT family name "等线" does not match the SFNT name "DengXian".
 *
 * This script creates a new widescreen deck, composes named nodes, writes
 * speaker notes, then exports PNG + layout JSON for the visual QA loop.
 */
/** @jsxRuntime automatic */
import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const root = path.resolve(import.meta.dirname ?? ".", "..");
const outDir = path.join(root, "outputs");
const renderDir = path.join(outDir, "slides");
const pptxPath = path.join(outDir, "喜娜_中大本科新生分享_丰富经历照片终版_2026.pptx");

const GREEN = "#00561F";
const GREEN_DEEP = "#00220E";
const CREAM = "#F6F1E4";
const GOLD = "#D29865";
const INK = "#221F1B";
const PAPER = "#FBFAF6";
const WHITE = "#FFFFFF";
const MUTED = "#5C564C";

const FONT = { fontFamily: "Microsoft YaHei", eastAsiaFontFamily: "Microsoft YaHei" };
const SERIF = { fontFamily: "Noto Serif CJK SC", eastAsiaFontFamily: "Noto Serif CJK SC" };

type PhotoSpec = {
  slot: string;
  fallback: string;
  label: string;
  caption: string;
  alt: string;
};

const content = JSON.parse(await fs.readFile(path.join(root, "content.json"), "utf8"));

async function resolvePhoto(spec: PhotoSpec): Promise<string> {
  const slot = path.join(root, spec.slot);
  const fallback = path.resolve(root, spec.fallback);
  try {
    await fs.access(slot);
    return slot;
  } catch {
    return fallback;
  }
}

function slideFrame() {
  return { left: 0, top: 0, width: 960, height: 540 };
}

async function exportQa(p: InstanceType<typeof PresentationFile>, slide: any, index: number) {
  await fs.mkdir(renderDir, { recursive: true });
  const png = await p.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(`${renderDir}/slide-${String(index).padStart(2, "0")}.png`, new Uint8Array(await png.arrayBuffer()));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(`${renderDir}/slide-${String(index).padStart(2, "0")}.layout.json`, await layout.text());
}

async function addCover(p: InstanceType<typeof PresentationFile>, data: any, index: number) {
  const slide = p.slides.add();
  slide.background.fill = {
    type: "image",
    src: path.resolve(root, data.background),
    fit: "cover",
  };
  slide.compose(
    <column width="fill" height="fill" padding={40} gap={16}>
      <row width="fill" height={36} gap={12}>
        <paragraph name="校名" className="text-sm" style={{ color: CREAM, ...SERIF }}>
          {content.meta.university}
        </paragraph>
        <paragraph name="页眉" className="text-sm" style={{ color: GOLD }}>
          {data.kicker}
        </paragraph>
      </row>
      <box name="cover-spacer" width="fill" height="fill" fill="none" />
      <rule name="金线" stroke={GOLD} weight={3} />
      <paragraph name="标题 1" style={{ fontSize: 36, bold: true, color: CREAM, ...SERIF }}>
        {data.title}
      </paragraph>
      <paragraph name="副标题" style={{ fontSize: 16, color: GOLD, ...FONT }}>
        {data.subtitle}
      </paragraph>
      <paragraph name="讲者" style={{ fontSize: 16, color: CREAM, ...FONT }}>
        {data.speaker}
      </paragraph>
    </column>,
    { frame: { left: 40, top: 28, width: 880, height: 484 }, baseUnit: 8 },
  );
  slide.speakerNotes.textFrame.setText(data.notes);
  slide.speakerNotes.setVisible(true);
  await exportQa(p, slide, index);
}

async function addOpening(p: InstanceType<typeof PresentationFile>, data: any, index: number) {
  const slide = p.slides.add();
  slide.background.fill = PAPER;
  slide.compose(
    <column width="fill" height="fill" gap={20}>
      <paragraph name="页眉" style={{ fontSize: 12, color: GOLD, ...FONT }}>
        {data.kicker}
      </paragraph>
      <paragraph name="标题 1" style={{ fontSize: 32, bold: true, color: GREEN, ...SERIF }}>
        {data.title}
      </paragraph>
      <paragraph name="导语" style={{ fontSize: 16, color: INK, ...FONT }}>
        {data.body}
      </paragraph>
      <row width="fill" height="fill" gap={16}>
        {data.points.map((point: string, i: number) => (
          <box name={`要点底${i + 1}`} width="fill" height="fill" padding={16} fill={WHITE}>
            <column gap={8}>
              <paragraph name={`要点号${i + 1}`} style={{ fontSize: 14, color: GOLD, ...FONT }}>
                {`0${i + 1}`}
              </paragraph>
              <paragraph name={`要点${i + 1}`} style={{ fontSize: 16, color: INK, ...FONT }}>
                {point}
              </paragraph>
            </column>
          </box>
        ))}
      </row>
    </column>,
    { frame: { left: 40, top: 72, width: 880, height: 420 }, baseUnit: 8 },
  );
  slide.speakerNotes.textFrame.setText(data.notes);
  slide.speakerNotes.setVisible(true);
  await exportQa(p, slide, index);
}

async function addMap(p: InstanceType<typeof PresentationFile>, data: any, index: number) {
  const slide = p.slides.add();
  slide.background.fill = PAPER;
  const title = slide.shapes.add({
    geometry: "textbox",
    name: "标题 1",
    position: { left: 40, top: 72, width: 880, height: 56 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  title.text = data.title;
  title.text.style = { fontSize: 30, bold: true, color: GREEN, ...SERIF };

  const cards = [];
  for (const [i, card] of data.cards.entries()) {
    const image = slide.images.add({
      name: `路线图${i + 1}`,
      src: path.resolve(root, card.photo),
      alt: card.title,
      fit: "cover",
      position: { left: 40 + i * 300, top: 140, width: 280, height: 340 },
    });
    cards.push(image);
    const label = slide.shapes.add({
      geometry: "textbox",
      name: `路线标题${i + 1}`,
      position: { left: 52 + i * 300, top: 400, width: 256, height: 60 },
      fill: "none",
      line: { style: "solid", fill: "none", width: 0 },
    });
    label.text = `${card.num}  ${card.title}\n${card.line}`;
    label.text.style = { fontSize: 16, bold: true, color: CREAM, ...SERIF };
  }
  slide.autoLayout(cards, {
    direction: "horizontal",
    frame: { left: 40, top: 140, width: 880, height: 340 },
    align: "topLeft",
    horizontalGap: 20,
  });
  slide.speakerNotes.textFrame.setText(data.notes);
  slide.speakerNotes.setVisible(true);
  await exportQa(p, slide, index);
}

async function addExperience(p: InstanceType<typeof PresentationFile>, data: any, index: number) {
  const slide = p.slides.add();
  slide.background.fill = PAPER;
  const photo1 = await resolvePhoto(content.photos[data.image1]);
  const photo2 = await resolvePhoto(content.photos[data.image2]);

  slide.compose(
    <row width="fill" height="fill" gap={20}>
      <column width={400} height="fill" gap={12}>
        <paragraph name="标题 1" style={{ fontSize: 22, bold: true, color: GREEN, ...SERIF }}>
          {data.title}
        </paragraph>
        <paragraph name="文本框 25" style={{ fontSize: 13, color: GREEN, ...FONT }}>
          {data.greenTitle}
        </paragraph>
        <row width="fill" gap={12}>
          <box name="统计1底" width="fill" padding={12} fill={WHITE}>
            <column gap={4}>
              <paragraph name="文本框 7" style={{ fontSize: 28, bold: true, color: GREEN, ...SERIF }}>
                {data.n1}
              </paragraph>
              <paragraph name="文本框 10" style={{ fontSize: 12, color: MUTED, ...FONT }}>
                {data.l1}
              </paragraph>
            </column>
          </box>
          <box name="统计2底" width="fill" padding={12} fill={WHITE}>
            <column gap={4}>
              <paragraph name="文本框 12" style={{ fontSize: 28, bold: true, color: GREEN, ...SERIF }}>
                {data.n2}
              </paragraph>
              <paragraph name="文本框 13" style={{ fontSize: 12, color: MUTED, ...FONT }}>
                {data.l2}
              </paragraph>
            </column>
          </box>
        </row>
        <box name="引言底" width="fill" height="fill" padding={16} fill={GREEN}>
          <column gap={10}>
            <paragraph name="文本框 22" style={{ fontSize: 16, bold: true, color: CREAM, ...SERIF }}>
              {data.whiteTitle}
            </paragraph>
            <paragraph name="文本框 21" style={{ fontSize: 13, color: CREAM, ...FONT }}>
              {data.body}
            </paragraph>
          </column>
        </box>
      </column>
      <row width="fill" height="fill" gap={12}>
        <box name="图片 29 框" width="fill" height="fill" fill={GREEN_DEEP} />
        <box name="图片 23 框" width="fill" height="fill" fill={GREEN_DEEP} />
      </row>
    </row>,
    { frame: { left: 28, top: 56, width: 904, height: 448 }, baseUnit: 8 },
  );

  const leftPhoto = slide.images.add({
    name: "图片 29",
    src: photo1,
    alt: content.photos[data.image1].alt,
    fit: "cover",
  });
  const rightPhoto = slide.images.add({
    name: "图片 23",
    src: photo2,
    alt: content.photos[data.image2].alt,
    fit: "cover",
  });
  slide.autoLayout([leftPhoto, rightPhoto], {
    direction: "horizontal",
    frame: { left: 448, top: 56, width: 484, height: 448 },
    align: "topLeft",
    horizontalGap: 12,
  });

  slide.speakerNotes.textFrame.setText(data.notes);
  slide.speakerNotes.setVisible(true);
  await exportQa(p, slide, index);
}

async function addAdvice(p: InstanceType<typeof PresentationFile>, data: any, index: number) {
  const slide = p.slides.add();
  slide.background.fill = PAPER;
  slide.compose(
    <column width="fill" height="fill" gap={20}>
      <paragraph name="页眉" style={{ fontSize: 12, color: GOLD, ...FONT }}>
        {data.kicker}
      </paragraph>
      <paragraph name="标题 1" style={{ fontSize: 28, bold: true, color: GREEN, ...SERIF }}>
        {data.title}
      </paragraph>
      <row width="fill" height="fill" gap={16}>
        {data.items.map((item: any, i: number) => (
          <box name={`建议底${i + 1}`} width="fill" height="fill" padding={20} fill={WHITE}>
            <column gap={10}>
              <paragraph name={`建议号${i + 1}`} style={{ fontSize: 14, color: GOLD, ...FONT }}>
                {item.n}
              </paragraph>
              <paragraph name={`建议标题${i + 1}`} style={{ fontSize: 18, bold: true, color: GREEN, ...SERIF }}>
                {item.title}
              </paragraph>
              <paragraph name={`建议正文${i + 1}`} style={{ fontSize: 14, color: INK, ...FONT }}>
                {item.body}
              </paragraph>
            </column>
          </box>
        ))}
      </row>
    </column>,
    { frame: { left: 40, top: 72, width: 880, height: 420 }, baseUnit: 8 },
  );
  slide.speakerNotes.textFrame.setText(data.notes);
  slide.speakerNotes.setVisible(true);
  await exportQa(p, slide, index);
}

async function main() {
  const p = await PresentationFile.create({ width: 960, height: 540 });
  let index = 1;
  for (const slide of content.slides) {
    if (slide.kind === "cover" || slide.kind === "close") {
      const data = slide.kind === "close"
        ? { ...slide, subtitle: slide.body, kicker: slide.kicker }
        : slide;
      await addCover(p, data, index++);
    } else if (slide.kind === "quote") {
      await addOpening(p, slide, index++);
    } else if (slide.kind === "map") {
      await addMap(p, slide, index++);
    } else if (slide.kind === "experience") {
      await addExperience(p, slide, index++);
    } else if (slide.kind === "advice") {
      await addAdvice(p, slide, index++);
    }
  }

  const inspect = await p.inspect({
    kind: "slide,textbox,shape,image,notes",
    maxChars: 500000,
  });
  await fs.mkdir(outDir, { recursive: true });
  await fs.writeFile(`${pptxPath}.inspect.ndjson`, inspect.ndjson);
  const out = await PresentationFile.exportPptx(p);
  await out.save(pptxPath);
  console.log(pptxPath);
}

await main();
