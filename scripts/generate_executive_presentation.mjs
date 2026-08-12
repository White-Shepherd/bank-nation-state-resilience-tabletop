import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Presentation, PresentationFile } from "../tmp/presentation-build/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const payload = JSON.parse(await fs.readFile(path.join(root, "tmp/presentation-build/executive-deck.json"), "utf8"));
const output = path.join(root, "output/presentation");
const previews = path.join(root, "tmp/presentation-build/previews");
await fs.mkdir(output, { recursive: true });
await fs.mkdir(previews, { recursive: true });

const C = payload.design.palette;
const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });

function addText(slide, text, position, fontSize, color = C.ink, bold = false, name = undefined) {
  const shape = slide.shapes.add({ geometry: "textbox", name, position, fill: "none", line: { style: "solid", fill: "none", width: 0 } });
  shape.text = text;
  shape.text.style = { fontSize, color, bold, fontFamily: "Aptos", verticalAlignment: "middle" };
  return shape;
}

function addRect(slide, position, fill = C.white, stroke = "#CCD8DF", width = 1, radius = "rounded-lg") {
  return slide.shapes.add({ geometry: "roundRect", position, fill, line: { style: "solid", fill: stroke, width }, borderRadius: radius });
}

function chrome(slide, item) {
  slide.background.fill = C.paper;
  slide.shapes.add({ geometry: "rect", position: { left: 0, top: 0, width: 1280, height: 10 }, fill: C.teal, line: { fill: "none", width: 0 } });
  addText(slide, `${item.section.toUpperCase()}   ${String(item.number).padStart(2, "0")}`, { left: 72, top: 32, width: 500, height: 28 }, 14, C.blue, true);
  addText(slide, item.title, { left: 72, top: 78, width: 1125, height: 96 }, 38, C.ink, true, `title-${item.number}`);
  addText(slide, item.subtitle, { left: 72, top: 174, width: 1080, height: 56 }, 19, C.slate, false);
  addText(slide, payload.synthetic_label, { left: 72, top: 681, width: 800, height: 18 }, 10, C.slate);
}

function bulletList(slide, bullets, top = 270) {
  bullets.forEach((bullet, index) => {
    const y = top + index * 82;
    slide.shapes.add({ geometry: "ellipse", position: { left: 88, top: y + 13, width: 14, height: 14 }, fill: C.teal, line: { fill: "none", width: 0 } });
    addText(slide, bullet, { left: 122, top: y, width: 1010, height: 52 }, 20, C.ink, false);
  });
}

function ecosystem(slide) {
  const groups = ["Customer access", "Money movement", "Control & record", "Crisis & recovery"];
  groups.forEach((label, index) => {
    const x = 72 + index * 288;
    addRect(slide, { left: x, top: 270, width: 248, height: 82 }, C.white);
    addText(slide, label, { left: x + 16, top: 286, width: 216, height: 48 }, 19, C.ink, true);
    slide.shapes.add({ geometry: "downArrow", position: { left: x + 104, top: 366, width: 40, height: 48 }, fill: "#6F8798", line: { fill: "none", width: 0 } });
  });
  const top = payload.metrics.top_concentrations.slice(0, 5);
  top.forEach((item, index) => {
    const x = 72 + index * 226;
    const displayName = item.name.replace(" environment", "");
    addRect(slide, { left: x, top: 440, width: 200, height: 122 }, C.white, index === 0 ? C.red : C.amber, index === 0 ? 4 : 2);
    addText(slide, displayName, { left: x + 14, top: 452, width: 172, height: 44 }, 15, C.ink, true);
    addText(slide, String(item.critical_relationships), { left: x + 14, top: 501, width: 52, height: 40 }, 30, index === 0 ? C.red : C.amber, true);
    addText(slide, "critical relationships", { left: x + 60, top: 506, width: 126, height: 32 }, 12, C.slate);
  });
}

function concentration(slide) {
  const top = payload.metrics.top_concentrations.slice(0, 6);
  const max = Math.max(...top.map((item) => item.critical_relationships));
  top.forEach((item, index) => {
    const y = 260 + index * 59;
    addText(slide, item.name, { left: 72, top: y, width: 330, height: 36 }, 17, C.ink, index === 0);
    slide.shapes.add({ geometry: "rect", position: { left: 420, top: y + 7, width: 560, height: 22 }, fill: "#DCE5EA", line: { fill: "none", width: 0 } });
    slide.shapes.add({ geometry: "rect", position: { left: 420, top: y + 7, width: 560 * item.critical_relationships / max, height: 22 }, fill: index === 0 ? C.red : C.amber, line: { fill: "none", width: 0 } });
    addText(slide, String(item.critical_relationships), { left: 1000, top: y, width: 70, height: 36 }, 18, C.ink, true);
  });
  addText(slide, "Count of declared critical relationships; not a risk score", { left: 420, top: 625, width: 550, height: 24 }, 13, C.slate);
}

function timeline(slide) {
  const phases = ["Normal", "Warning", "Pre-position", "Disruption", "Integrity", "Containment", "Recovery", "Stabilize"];
  phases.forEach((label, index) => {
    const x = 66 + index * 145;
    slide.shapes.add({ geometry: "ellipse", position: { left: x, top: 348, width: 42, height: 42 }, fill: index < 3 ? C.blue : index < 6 ? C.amber : C.green, line: { fill: C.white, width: 2 } });
    if (index < phases.length - 1) slide.shapes.add({ geometry: "rect", position: { left: x + 42, top: 366, width: 103, height: 6 }, fill: "#AABBC6", line: { fill: "none", width: 0 } });
    addText(slide, label, { left: x - 30, top: 408, width: 105, height: 42 }, 13, C.ink, index === 5);
  });
  addRect(slide, { left: 315, top: 500, width: 650, height: 84 }, "#FFF7E8", C.amber, 2);
  addText(slide, "Containment decision: preserve payment availability or suspend channels while integrity is uncertain?", { left: 342, top: 516, width: 596, height: 52 }, 18, C.ink, true);
}

function recovery(slide) {
  const items = ["Clean credentials", "Independent DNS", "Offline evidence", "Recovery telemetry", "Ledger validation"];
  items.forEach((label, index) => {
    const x = 72 + index * 226;
    addRect(slide, { left: x, top: 300, width: 196, height: 90 }, C.white, index === 4 ? C.green : C.amber, 2);
    addText(slide, label, { left: x + 14, top: 316, width: 168, height: 54 }, 17, C.ink, true);
    if (index < items.length - 1) slide.shapes.add({ geometry: "rightArrow", position: { left: x + 198, top: 328, width: 26, height: 28 }, fill: "#6F8798", line: { fill: "none", width: 0 } });
  });
  addRect(slide, { left: 230, top: 470, width: 820, height: 92 }, C.ink, C.ink, 0);
  addText(slide, "Restore minimum viable service only after authority and transaction integrity are independently trusted.", { left: 268, top: 488, width: 744, height: 54 }, 21, C.white, true);
}

for (const item of payload.slides) {
  const slide = deck.slides.add();
  chrome(slide, item);
  if (item.visual === "title") {
    addRect(slide, { left: 72, top: 292, width: 1136, height: 238 }, C.ink, C.ink, 0);
    addText(slide, "CONTROL PLANE  →  SERVICE CONTINUITY  →  TRUSTED RECOVERY", { left: 118, top: 354, width: 1044, height: 58 }, 27, C.white, true);
    addText(slide, "A decision briefing for resilience investment and crisis governance", { left: 118, top: 430, width: 950, height: 42 }, 20, "#BFD1DB");
  } else if (item.visual === "ecosystem") ecosystem(slide);
  else if (item.visual === "concentration") concentration(slide);
  else if (item.visual === "timeline") timeline(slide);
  else if (item.visual === "recovery") recovery(slide);
  else bulletList(slide, item.bullets);
}

for (const [index, slide] of deck.slides.items.entries()) {
  const stem = `slide-${String(index + 1).padStart(2, "0")}`;
  const png = await deck.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(path.join(previews, `${stem}.png`), new Uint8Array(await png.arrayBuffer()));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(previews, `${stem}.layout.json`), await layout.text());
}
const montage = await deck.export({ format: "webp", montage: true, scale: 1 });
await fs.writeFile(path.join(previews, "deck-montage.webp"), new Uint8Array(await montage.arrayBuffer()));
const pptx = await PresentationFile.exportPptx(deck);
await pptx.save(path.join(output, "harbor-ridge-executive-resilience-briefing.pptx"));
