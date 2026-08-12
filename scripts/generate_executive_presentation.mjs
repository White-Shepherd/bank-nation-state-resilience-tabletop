import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Presentation, PresentationFile } from "../tmp/presentation-build/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const payload = JSON.parse(await fs.readFile(path.join(root, "tmp/presentation-build/executive-deck.json"), "utf8"));
const tokens = JSON.parse(await fs.readFile(path.join(root, "brand/brand-tokens.json"), "utf8"));
const C = Object.fromEntries(Object.entries(tokens.colors).map(([key, value]) => [key, value.hex]));
const FONT = tokens.typography.font_family;
const OUTPUTS = {
  template: "presentations/templates/resilience-platform-template.pptx",
  executive: "presentations/board/executive-resilience-briefing.pptx",
  technical: "presentations/technical/resilience-architecture-briefing.pptx",
  tabletop: "presentations/tabletop/nation-state-exercise-facilitator.pptx",
  brand: "tmp/presentation-build/brand-guide.pptx",
};
const PREVIEW_ROOT = path.join(root, "tmp/presentation-build/renders");

const layoutNames = [
  "Minimal title", "Section divider", "Executive takeaway", "Claim plus evidence",
  "Full-width chart", "Chart plus interpretation", "Architecture diagram",
  "Service-dependency map", "Current state versus target state", "Risk concentration",
  "Scenario timeline", "Decision card", "Three-option comparison", "Investment roadmap",
  "KPI or KRI scorecard", "Before-and-after validation", "Table",
  "Quote or governing principle", "Closing recommendation", "Appendix detail",
  "Source and methodology",
];

function addText(surface, text, position, size, color = C.continuum_navy, bold = false, name) {
  const shape = surface.shapes.add({ geometry: "textbox", name, position, fill: "none", line: { style: "solid", fill: "none", width: 0 } });
  shape.text = text;
  shape.text.style = { fontSize: size, color, bold, fontFamily: FONT, verticalAlignment: "middle" };
  return shape;
}

function addRect(surface, position, fill = C.white, stroke = "#CBD7DE", width = 1, geometry = "rect") {
  return surface.shapes.add({ geometry, position, fill, line: { style: "solid", fill: stroke, width } });
}

function addWordmark(slide, dark = false) {
  const ink = dark ? C.white : C.continuum_navy;
  addRect(slide, { left: 72, top: 34, width: 5, height: 42 }, C.signal_teal, C.signal_teal, 0);
  addText(slide, "CONTINUUM", { left: 91, top: 30, width: 210, height: 28 }, 16, ink, true);
  addText(slide, "RESILIENCE", { left: 92, top: 54, width: 180, height: 22 }, 10, C.signal_teal, true);
}

function chrome(slide, section, page, options = {}) {
  const dark = options.dark || false;
  slide.background.fill = dark ? C.continuum_navy : C.paper;
  addWordmark(slide, dark);
  addText(slide, section.toUpperCase(), { left: 940, top: 38, width: 225, height: 24 }, 12, dark ? "#B8CBD6" : C.slate_blue, true);
  addText(slide, String(page).padStart(2, "0"), { left: 1170, top: 38, width: 38, height: 24 }, 12, dark ? C.white : C.continuum_navy, true);
  addText(slide, "SYNTHETIC EXERCISE DATA - NOT A REAL BANK", { left: 72, top: 682, width: 430, height: 16 }, 10, dark ? "#B8CBD6" : C.evidence);
}

function title(slide, claim, support = "", dark = false) {
  addText(slide, claim, { left: 72, top: 102, width: 1136, height: 92 }, 36, dark ? C.white : C.continuum_navy, true, "slide-title");
  if (support) addText(slide, support, { left: 72, top: 195, width: 1080, height: 52 }, 18, dark ? "#C8D7DF" : C.evidence);
}

function notes(slide, source = "Repository synthetic ecosystem YAML and assessment model.") {
  slide.speakerNotes.textFrame.setText(`[Sources]\n- ${source}\n- No external claim or asset. All values are synthetic.\n[/Sources]`);
  slide.speakerNotes.setVisible(true);
}

function bullets(slide, items, x = 96, y = 285, width = 1040, gap = 82) {
  items.forEach((item, index) => {
    const yy = y + index * gap;
    addRect(slide, { left: x, top: yy + 11, width: 12, height: 12 }, C.signal_teal, C.signal_teal, 0, "ellipse");
    addText(slide, item, { left: x + 38, top: yy, width, height: 46 }, 19);
  });
}

function bigStatement(slide, statement, implication) {
  addText(slide, statement, { left: 94, top: 270, width: 750, height: 150 }, 34, C.continuum_navy, true);
  addRect(slide, { left: 890, top: 270, width: 6, height: 190 }, C.copper, C.copper, 0);
  addText(slide, implication, { left: 930, top: 282, width: 255, height: 170 }, 20, C.slate_blue, true);
}

function concentrationChart(slide) {
  const top = payload.metrics.top_concentrations.slice(0, 6);
  slide.charts.add("bar", {
    position: { left: 84, top: 275, width: 760, height: 335 },
    categories: top.map(item => item.name.replace(" environment", "")),
    series: [{ name: "Critical relationships", values: top.map(item => item.critical_relationships), fill: C.copper }],
    hasLegend: false,
    dataLabels: { showValue: true, position: "outEnd" },
    xAxis: { title: "Declared critical relationships", majorGridlines: { style: "solid", fill: "#DDE5EA", width: 1 } },
    yAxis: { reverseOrder: true },
  });
  addRect(slide, { left: 900, top: 300, width: 6, height: 220 }, C.signal_teal, C.signal_teal, 0);
  addText(slide, "Identity is the largest modeled common-mode concentration. The count is evidence of dependency, not likelihood or loss.", { left: 940, top: 300, width: 245, height: 220 }, 20, C.continuum_navy, true);
}

function dependencyDiagram(slide) {
  const top = payload.metrics.top_concentrations.slice(0, 4);
  [210, 500, 790, 1080].forEach(x => addRect(slide, { left: x, top: 400, width: 3, height: 70 }, C.evidence, C.evidence, 0));
  addRect(slide, { left: 210, top: 468, width: 873, height: 3 }, C.evidence, C.evidence, 0);
  addRect(slide, { left: 645, top: 468, width: 3, height: 62 }, C.evidence, C.evidence, 0);
  ["Customer access", "Money movement", "Financial control", "Recovery"].forEach((label, index) => {
    const x = 92 + index * 290;
    addRect(slide, { left: x, top: 300, width: 238, height: 100 }, C.white, "#CBD7DE", 2, "roundRect");
    addText(slide, label, { left: x + 18, top: 325, width: 202, height: 50 }, 20, C.continuum_navy, true);
  });
  addRect(slide, { left: 420, top: 530, width: 455, height: 92 }, "#FFF7E8", C.copper, 3, "roundRect");
  addText(slide, `${top[0].name}: ${top[0].critical_relationships} declared critical relationships`, { left: 450, top: 548, width: 395, height: 54 }, 21, C.continuum_navy, true);
}

function timeline(slide) {
  const phases = ["Normal", "Warning", "Pre-position", "Disruption", "Integrity", "Containment", "Recovery", "Stabilize"];
  phases.forEach((label, index) => {
    const x = 68 + index * 147;
    if (index < phases.length - 1) addRect(slide, { left: x + 40, top: 373, width: 110, height: 5 }, "#A9BAC5", "#A9BAC5", 0);
    addRect(slide, { left: x, top: 355, width: 42, height: 42 }, index < 3 ? C.slate_blue : index < 6 ? C.amber : C.green, C.white, 2, "ellipse");
    addText(slide, label, { left: x - 30, top: 415, width: 110, height: 36 }, 13, C.continuum_navy, index === 5);
  });
  addRect(slide, { left: 330, top: 500, width: 620, height: 86 }, "#FFF7E8", C.amber, 2, "roundRect");
  addText(slide, "Containment decision: preserve payment availability or suspend channels while integrity is uncertain?", { left: 365, top: 516, width: 550, height: 54 }, 20, C.continuum_navy, true);
}

function integrityDecision(slide) {
  addRect(slide, { left: 115, top: 290, width: 430, height: 240 }, "#EAF4F3", C.signal_teal, 2, "roundRect");
  addText(slide, "KEEP CHANNEL OPEN", { left: 150, top: 318, width: 360, height: 34 }, 20, C.signal_teal, true);
  addText(slide, "Preserves access\n\nMay increase unreconciled transactions and customer harm if data cannot be trusted", { left: 150, top: 370, width: 340, height: 125 }, 18);
  addRect(slide, { left: 735, top: 290, width: 430, height: 240 }, "#FFF7E8", C.copper, 2, "roundRect");
  addText(slide, "SUSPEND CHANNEL", { left: 770, top: 318, width: 360, height: 34 }, 20, C.copper, true);
  addText(slide, "Limits questionable posting\n\nCreates immediate service disruption and manual-processing pressure", { left: 770, top: 370, width: 340, height: 125 }, 18);
  addText(slide, "Decision evidence: journal integrity, independent reconciliation, customer harm and settlement obligations", { left: 175, top: 570, width: 930, height: 40 }, 18, C.slate_blue, true);
}

function currentTarget(slide) {
  addText(slide, "CURRENT", { left: 100, top: 270, width: 420, height: 38 }, 18, C.red, true);
  addText(slide, "TARGET", { left: 760, top: 270, width: 420, height: 38 }, 18, C.green, true);
  ["Production identity", "Production DNS", "Replicated data", "Shared monitoring"].forEach((label, index) => {
    addRect(slide, { left: 100, top: 325 + index * 65, width: 390, height: 44 }, "#F9EBEB", C.red, 1);
    addText(slide, label, { left: 120, top: 330 + index * 65, width: 350, height: 34 }, 17);
  });
  ["Independent recovery identity", "Independent name resolution", "Offline integrity evidence", "Recovery-visible telemetry"].forEach((label, index) => {
    addRect(slide, { left: 760, top: 325 + index * 65, width: 390, height: 44 }, "#EAF3EE", C.green, 1);
    addText(slide, label, { left: 780, top: 330 + index * 65, width: 350, height: 34 }, 17);
  });
  addRect(slide, { left: 555, top: 405, width: 150, height: 50 }, C.continuum_navy, C.continuum_navy, 0, "rightArrow");
}

function roadmap(slide) {
  const stages = [
    ["0-90 DAYS", "Approve Tier 0\nFreeze unmanaged privilege\nValidate clean credentials"],
    ["NEXT 2 QUARTERS", "Independent recovery identity\nImmutable evidence\nManual payments test"],
    ["ONE YEAR", "Provider substitution\nCarrier diversity\nEnterprise reconciliation"],
  ];
  stages.forEach((item, index) => {
    const x = 85 + index * 390;
    addText(slide, item[0], { left: x, top: 275, width: 330, height: 30 }, 15, index === 0 ? C.copper : C.slate_blue, true);
    addRect(slide, { left: x, top: 325, width: 330, height: 225 }, index === 0 ? "#FFF7E8" : C.white, index === 0 ? C.copper : "#CBD7DE", 2, "roundRect");
    addText(slide, item[1], { left: x + 28, top: 350, width: 275, height: 170 }, 19, C.continuum_navy, true);
    if (index < 2) addRect(slide, { left: x + 340, top: 410, width: 40, height: 36 }, C.signal_teal, C.signal_teal, 0, "rightArrow");
  });
}

function scorecard(slide) {
  const rows = [
    ["Independent Tier 0 recovery", "UNVALIDATED", C.amber],
    ["Privilege-disable decision time", "MEASURE", C.evidence],
    ["Unreconciled transactions", "MONITOR", C.copper],
    ["Third-party substitution", "TEST", C.amber],
  ];
  rows.forEach((row, index) => {
    const y = 280 + index * 78;
    addText(slide, row[0], { left: 100, top: y, width: 570, height: 44 }, 20, C.continuum_navy, index === 0);
    addRect(slide, { left: 760, top: y, width: 240, height: 44 }, row[2], row[2], 0);
    addText(slide, row[1], { left: 790, top: y + 3, width: 180, height: 36 }, 16, C.white, true);
    addText(slide, "Owner + evidence + trend", { left: 1020, top: y + 3, width: 180, height: 36 }, 14, C.evidence);
  });
}

function decisionSlide(slide, decisions) {
  decisions.forEach((decision, index) => {
    const y = 270 + index * 105;
    addText(slide, String(index + 1).padStart(2, "0"), { left: 90, top: y, width: 48, height: 50 }, 25, C.copper, true);
    addText(slide, decision, { left: 165, top: y, width: 870, height: 50 }, 22, C.continuum_navy, true);
    addRect(slide, { left: 1075, top: y + 3, width: 110, height: 42 }, index === 0 ? C.copper : C.signal_teal, "none", 0);
    addText(slide, index === 0 ? "APPROVE" : "REQUIRE", { left: 1088, top: y + 6, width: 84, height: 34 }, 13, C.white, true);
  });
}

function buildLayouts(deck) {
  const master = deck.masters.add("Continuum Resilience Master");
  master.background.fill = C.paper;
  const layouts = {};
  for (const [index, name] of layoutNames.entries()) {
    const layout = deck.layouts.add(name);
    layout.setParentLayoutId(master.id);
    layout.placeholders.add({ type: "title", index: 0, geometry: "textbox", position: { left: 72, top: 90, width: 1136, height: 84 }, text: name });
    if (!["Minimal title", "Section divider"].includes(name)) layout.placeholders.add({ type: "body", index: 0, geometry: "textbox", position: { left: 72, top: 220, width: 1136, height: 390 }, text: "Editable content" });
    layout.placeholders.add({ type: "subtitle", index: 0, geometry: "textbox", position: { left: 72, top: 650, width: 600, height: 24 }, text: "Source note / synthetic-data footer" });
    layouts[name] = layout;
  }
  return layouts;
}

function createDeck() {
  const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });
  buildLayouts(deck);
  return deck;
}

function addSlide(deck, section, claim, support, visual, items = []) {
  const slide = deck.slides.add();
  chrome(slide, section, deck.slides.items.length);
  title(slide, claim, support);
  if (visual === "statement") bigStatement(slide, items[0], items[1]);
  else if (visual === "bullets") bullets(slide, items);
  else if (visual === "concentration") concentrationChart(slide);
  else if (visual === "dependency") dependencyDiagram(slide);
  else if (visual === "timeline") timeline(slide);
  else if (visual === "integrity") integrityDecision(slide);
  else if (visual === "target") currentTarget(slide);
  else if (visual === "roadmap") roadmap(slide);
  else if (visual === "scorecard") scorecard(slide);
  else if (visual === "decision") decisionSlide(slide, items);
  notes(slide);
  return slide;
}

function cover(deck, audience, context) {
  const slide = deck.slides.add();
  chrome(slide, audience, 1, { dark: true });
  addText(slide, "Cyber Operational Resilience\nDecision Intelligence", { left: 78, top: 185, width: 850, height: 150 }, 50, C.white, true);
  addRect(slide, { left: 80, top: 370, width: 150, height: 5 }, C.signal_teal, C.signal_teal, 0);
  addText(slide, context, { left: 80, top: 410, width: 820, height: 75 }, 22, "#C8D7DF");
  addText(slide, "HARBOR RIDGE BANK | FICTIONAL DEMONSTRATION CLIENT", { left: 80, top: 565, width: 760, height: 30 }, 14, C.copper, true);
  notes(slide);
}

function buildExecutive() {
  const deck = createDeck();
  cover(deck, "Board briefing", "A decision briefing on shared control planes, trusted transactions and independent recovery");
  addSlide(deck, "Executive summary", "Four choices determine whether disruption becomes customer harm", "Identity, transaction integrity, minimum viable payments and independent recovery form the decision frame.", "statement", ["Resilience is a management decision system, not a collection of tools.", "Approve authority, evidence thresholds and recovery independence before a timed crisis."]);
  addSlide(deck, "Critical services", "Sixteen critical services share a small set of control planes", "The service view connects customer and market need to explicitly declared dependencies.", "dependency");
  addSlide(deck, "Concentration", "Enterprise identity is the largest declared common-mode dependency", "Counts are critical relationships in the synthetic model, not probabilities or loss estimates.", "concentration");
  addSlide(deck, "Tier 0", "Tier 0 marks a recovery and decision boundary", "Nineteen dependencies have rationale and accountable ownership; designation remains institution-specific.", "bullets", ["Broad authority can create multi-service failure.", "Trusted recovery depends on identity, backup and integrity evidence.", "Human approval remains required after material change."]);
  addSlide(deck, "Scenario", "Ambiguous warning becomes a timed integrity dilemma", "Eight phases reveal modeled effects and deadlines without automatic attribution.", "timeline");
  addSlide(deck, "Integrity", "Availability can preserve access while increasing financial uncertainty", "The containment choice must consider independently reconciled evidence.", "integrity");
  addSlide(deck, "Recovery", "Production dependencies can follow the bank into recovery", "Clean-room restoration is credible only when authority, name resolution, telemetry and evidence are independent.", "bullets", ["Replication can reproduce corruption.", "Backup availability does not prove transaction integrity.", "Failover without monitoring reduces recovery confidence."]);
  addSlide(deck, "Target architecture", "Independent recovery removes the most consequential common modes", "The target state separates authority, infrastructure visibility and data validation from production.", "target");
  addSlide(deck, "Investment", "Sequence investment to remove recovery common modes first", "Priorities are qualitative and traceable to declared dependency paths.", "roadmap");
  addSlide(deck, "Oversight", "Board measures should test outcomes, not tool ownership", "Every measure needs an owner, evidence, threshold and trend.", "scorecard");
  addSlide(deck, "Decision", "Approve an evidence-led program with accountable owners", "Management should return with bounded milestones, validation criteria and residual-risk decisions.", "decision", ["Approve recovery-independence priorities", "Require quarterly evidence against service tolerances", "Revalidate Tier 0 after material change"]);
  return deck;
}

function buildBoard() {
  const deck = createDeck();
  cover(deck, "Board risk committee", "Approve resilience priorities for shared control planes and trusted recovery");
  addSlide(deck, "Decision frame", "Three approvals can materially improve recovery confidence", "Prioritize independent authority, financial integrity evidence and tested minimum viable payments.", "decision", ["Approve independent recovery identity", "Require transaction-integrity validation", "Fund tested carrier and provider substitution"]);
  addSlide(deck, "Service exposure", "Customer and payment services converge on shared authority", "The model contains sixteen critical services and 108 declared relationships.", "dependency");
  addSlide(deck, "Concentration", "Identity and backup dominate declared common-mode exposure", "The evidence supports prioritization, not a probability estimate.", "concentration");
  addSlide(deck, "Dilemma", "Payment availability is unsafe when posting integrity is uncertain", "A timed containment decision must preserve obligations without trusting ambiguous data.", "integrity");
  addSlide(deck, "Recovery", "A clean room is only independent when its prerequisites are independent", "Production credentials, DNS and monitoring cannot remain hidden recovery dependencies.", "target");
  addSlide(deck, "Roadmap", "The first 90 days establish authority and evidence", "Later phases expand substitution, diversity and reconciliation.", "roadmap");
  addSlide(deck, "Oversight", "Quarterly evidence should show whether resilience works", "Statuses are written as well as colored for accessible review.", "scorecard");
  addSlide(deck, "Approval", "Fund recovery independence and require evidence of outcomes", "No tool, backup or failover is treated as infallible.", "decision", ["Approve priorities and owners", "Require tolerance-based exercises", "Review residual uncertainty quarterly"]);
  return deck;
}

function buildTechnical() {
  const deck = createDeck();
  cover(deck, "Technical architecture", "Explain service dependencies, control planes and trusted recovery design");
  addSlide(deck, "Architecture principle", "Critical services must be traced through authority and recovery", "Technical design starts with service tolerance, not infrastructure inventory.", "dependency");
  addSlide(deck, "Control planes", "Enterprise identity holds the broadest declared authority", "Seven critical relationships make identity the leading modeled concentration.", "concentration");
  addSlide(deck, "Tier 0", "Tier 0 dependencies require evidence-backed ownership", "Broad authority, multi-service effect and trusted recovery determine candidacy.", "bullets", ["Identity and privileged access", "DNS, certificates and time", "Network, cloud, virtualization and database management", "Backup and recovery orchestration"]);
  addSlide(deck, "Common mode", "Shared identity and administration can defeat component redundancy", "Redundant applications remain exposed when the same authority controls both paths.", "statement", ["Component redundancy is not control-plane independence.", "Test administrative separation and break-glass authority."]);
  addSlide(deck, "Telemetry", "A deployed tool is not the same as tested coverage", "Coverage progresses through configuration, telemetry, detection testing, response integration and recovery visibility.", "scorecard");
  addSlide(deck, "Integrity", "Recovery design must separate availability from trust", "Journal, ledger and reconciliation evidence determine whether restored service is safe.", "integrity");
  addSlide(deck, "Current architecture", "Production control planes remain implicit recovery prerequisites", "The current state can reproduce compromised authority or corrupted data.", "target");
  addSlide(deck, "Recovery sequence", "Clean authority must precede data restoration", "Independent DNS, offline evidence and recovery telemetry support trusted service restoration.", "roadmap");
  addSlide(deck, "Validation", "Architecture acceptance requires service-level evidence", "Each test must connect a dependency, control, result, limitation and owner.", "bullets", ["Recover with production identity unavailable.", "Investigate without the production monitoring plane.", "Validate the journal before service restoration.", "Demonstrate minimum viable payment capacity."]);
  addSlide(deck, "Action", "Design decisions should remove common modes before adding tools", "Prioritize isolation, independent evidence and tested substitution.", "decision", ["Approve target recovery architecture", "Assign technical owners and alternates", "Schedule evidence-based validation"]);
  return deck;
}

function buildTabletop() {
  const deck = createDeck();
  cover(deck, "Facilitator deck", "Run the synthetic nation-state disruption scenario and record accountable decisions");
  addSlide(deck, "Exercise objective", "Test decisions under ambiguity without assuming attribution", "Participants should protect customers and obligations while evidence remains incomplete.", "statement", ["The exercise tests governance, containment and recovery confidence.", "It does not teach intrusion methods or represent a real bank."]);
  addSlide(deck, "Rules", "Evidence is revealed progressively and decisions are recorded", "State assumptions, dissent, residual risk and evidence required for each action.", "bullets", ["Do not invent missing facts.", "Weak signals do not confirm nation-state activity.", "Legal and regulatory timing requires jurisdictional review.", "The facilitator does not automatically propagate undeclared failure."]);
  addSlide(deck, "Roles", "Decision ownership must remain explicit under time pressure", "Incident command coordinates business, technology, risk, legal and communications roles.", "bullets", ["Incident commander: integrates decisions", "Business owners: approve service consequences", "Technical teams: execute bounded actions", "Risk and legal: frame evidence and obligations"]);
  addSlide(deck, "Scenario", "Strategic warning evolves into coordinated disruption", "The eight-phase control moves from normal operations through stabilization.", "timeline");
  addSlide(deck, "Phase 1", "Strategic warning should change posture without proving attribution", "Review administrative privilege, external signals and decision readiness.", "bullets", ["Reveal government and sector warning.", "Ask whether to raise threat posture.", "Record evidence and dissent."]);
  addSlide(deck, "Phase 2", "Ambiguous pre-positioning tests escalation discipline", "Correlated but incomplete signals should reach accountable owners.", "bullets", ["Reveal identity and network anomalies.", "Test detecting tools and receiving teams.", "Start the configured decision timer."]);
  addSlide(deck, "Phase 3", "Coordinated disruption forces service prioritization", "Customer access and payment effects expose shared dependencies.", "dependency");
  addSlide(deck, "Phase 4", "Integrity uncertainty changes the meaning of availability", "Participants must decide whether a functioning channel is safe to operate.", "integrity");
  addSlide(deck, "Phase 5", "Containment trades immediate service for bounded uncertainty", "Record authority, deadline, selected action and operational consequence.", "decision", ["Isolate identity systems", "Suspend selected payment channels", "Invoke manual processing"]);
  addSlide(deck, "Phase 6", "Recovery begins with clean authority and trusted evidence", "Failover alone does not establish integrity.", "target");
  addSlide(deck, "Board update", "Executives need consequence, confidence and pending decisions", "Translate technical evidence into customer, payment, liquidity and recovery impact.", "scorecard");
  addSlide(deck, "After action", "Every gap needs an owner and validation criterion", "Capture decisions, evidence gaps, corrective actions and residual risk.", "roadmap");
  addSlide(deck, "Close", "The exercise ends when decisions and evidence are reviewable", "Do not convert facilitator observations into unsupported performance claims.", "decision", ["Confirm decision log", "Assign corrective-action owners", "Schedule validation and board follow-up"]);
  return deck;
}

function buildBrandGuide() {
  const deck = createDeck();
  cover(deck, "Brand system", "Continuum Resilience | Cyber Operational Resilience Decision Intelligence");
  addSlide(deck, "Positioning", "The brand makes evidence and decision authority visible", "Authoritative, controlled, technically credible and board appropriate.", "statement", ["Continuum connects sustained service with trusted recovery.", "Harbor Ridge Bank remains the fictional demonstration client."]);
  addSlide(deck, "Naming", "Continuum Resilience balances clarity and credibility", "No trademark availability claim is made.", "bullets", ["Continuum Resilience - selected", "ControlPoint Intelligence - clear but product-like", "Assurance Vector - credible but less self-explanatory"]);
  addSlide(deck, "Color", "A restrained palette separates brand, evidence and status", "Navy anchors authority; teal identifies the brand; copper marks decisions.", "scorecard");
  addSlide(deck, "Typography", "Aptos keeps PowerPoint portable on modern Windows", "Arial is the explicit fallback; minimum body copy is 16 px.", "statement", ["36 px slide title / 24 px callout / 18 px body / 13 px label", "Shorten content before reducing type."]);
  addSlide(deck, "Visual grammar", "Evidence, findings and decisions must look different", "Color is reinforced by labels, structure and reading order.", "integrity");
  addSlide(deck, "Layouts", "Twenty-one layouts support varied executive storytelling", "Data, diagram, comparison, timeline, decision and roadmap silhouettes share one grid.", "roadmap");
  addSlide(deck, "Usage", "Protect contrast, spacing and the distinction between product and client", "Never use hacker imagery, decorative gauges, fake 3D charts or low-contrast wordmarks.", "decision", ["Preserve wordmark safe area", "Use semantic colors with text", "Keep Harbor Ridge labeled fictional"]);
  return deck;
}

function buildTemplate() {
  const deck = createDeck();
  for (const [index, name] of layoutNames.entries()) {
    const slide = deck.slides.add();
    slide.setLayout(deck.layouts.getById(deck.layouts.items.find(item => item.name === name).id));
    slide.background.fill = index === 1 ? C.continuum_navy : C.paper;
    const titlePlaceholder = slide.placeholders.getItem("title");
    titlePlaceholder.text = "";
    if (!["Minimal title", "Section divider"].includes(name)) {
      const body = slide.placeholders.getItem("body");
      body.text = "";
    }
    const footer = slide.placeholders.getItem("subtitle");
    footer.text = "";
    addWordmark(slide, index === 1);
    addText(slide, `${String(index + 1).padStart(2, "0")} | ${name}`, { left: 72, top: 110, width: 1136, height: 70 }, index < 2 ? 44 : 36, index === 1 ? C.white : C.continuum_navy, true);
    if (!["Minimal title", "Section divider"].includes(name)) {
      addRect(slide, { left: 72, top: 235, width: 1136, height: 335 }, index === 1 ? "#173C5C" : C.white, index === 1 ? "#557386" : "#CBD7DE", 2, "roundRect");
      addText(slide, "EDITABLE CONTENT REGION", { left: 102, top: 270, width: 420, height: 36 }, 18, index === 1 ? C.white : C.slate_blue, true);
      addText(slide, "Use this silhouette for one audience-facing claim and its supporting evidence. Replace sample content; preserve the grid, footer and notes structure.", { left: 102, top: 330, width: 920, height: 100 }, 20, index === 1 ? "#C8D7DF" : C.continuum_navy);
    }
    addText(slide, "SOURCE NOTE SUPPORT | SYNTHETIC-DATA FOOTER OPTION | PAGE MARKER", { left: 72, top: 662, width: 650, height: 20 }, 10, index === 1 ? "#B8CBD6" : C.evidence);
    addText(slide, String(index + 1).padStart(2, "0"), { left: 1170, top: 662, width: 38, height: 20 }, 11, index === 1 ? C.white : C.continuum_navy, true);
    notes(slide, "Template layout catalog; no external source.");
  }
  return deck;
}

async function exportDeck(deck, relativePath, key) {
  const finalPath = path.join(root, relativePath);
  const previewDir = path.join(PREVIEW_ROOT, key);
  await fs.mkdir(path.dirname(finalPath), { recursive: true });
  await fs.mkdir(previewDir, { recursive: true });
  for (const [index, slide] of deck.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    const png = await deck.export({ slide, format: "png", scale: 1 });
    await fs.writeFile(path.join(previewDir, `${stem}.png`), new Uint8Array(await png.arrayBuffer()));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(path.join(previewDir, `${stem}.layout.json`), await layout.text());
  }
  const montage = await deck.export({ format: "webp", montage: true, scale: 1 });
  await fs.writeFile(path.join(previewDir, "contact-sheet.webp"), new Uint8Array(await montage.arrayBuffer()));
  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(finalPath);
  const inspect = await deck.inspect({ kind: "slide,layout,notes,chart,shape,textbox", maxChars: 30000 });
  await fs.writeFile(path.join(previewDir, "inspect.ndjson"), inspect.ndjson);
}

await exportDeck(buildTemplate(), OUTPUTS.template, "template");
await exportDeck(buildExecutive(), OUTPUTS.executive, "executive");
await exportDeck(buildTechnical(), OUTPUTS.technical, "technical");
await exportDeck(buildTabletop(), OUTPUTS.tabletop, "tabletop");
await exportDeck(buildBrandGuide(), OUTPUTS.brand, "brand-guide");
