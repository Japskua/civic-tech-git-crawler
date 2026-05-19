// Slides for colleague briefing on the round-3 civic-tech landscape paper.
// Generates: colleague_briefing.pptx
//
// Narrative arc: civic tech matters → here's what we have →
//   six sustainability challenges → where we're going.
//
// Palette (Ocean / Teal, same family as the figures so the deck and the
// paper feel like one artefact):
//   Dark midnight   #0F172A  (sandwich slides + accents)
//   Teal primary    #0D9488
//   Teal light      #14B8A6
//   Amber accent    #F59E0B  (challenge badges + medians in figs)
//   Emerald result  #10B981  (positive evidence)
//   Slate-50 bg     #F8FAFC
//   Slate-800 text  #1E293B
//   Slate-500 muted #64748B

const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const {
  FaUsers,
  FaUserSlash,
  FaCubes,
  FaChartArea,
  FaInbox,
  FaHourglassHalf,
  FaProjectDiagram,
  FaGlobeAmericas,
  FaCalendarAlt,
  FaArrowRight,
} = require("react-icons/fa");

// ---------- helpers ----------
function renderIconSvg(IconComponent, color = "#000000", size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
}

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = renderIconSvg(IconComponent, color, size);
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}

const W = 13.3;
const H = 7.5;

const C = {
  dark: "0F172A",
  teal: "0D9488",
  tealLight: "14B8A6",
  tealPale: "CCFBF1",
  amber: "F59E0B",
  amberBg: "FEF3C7",
  emerald: "10B981",
  emeraldBg: "D1FAE5",
  bg: "F8FAFC",
  text: "1E293B",
  textMuted: "64748B",
  textLight: "94A3B8",
  white: "FFFFFF",
  border: "E2E8F0",
};

const FONT = {
  header: "Georgia",
  body: "Calibri",
};

const FIG_DIR = "../figures/";

// Top-left accent + page indicator on content slides
function addChrome(slide, pageNum, totalPages, sectionLabel) {
  slide.addShape("rect", {
    x: 0, y: 0, w: 0.35, h: 1.2,
    fill: { color: C.teal }, line: { type: "none" },
  });
  slide.addText(`${String(pageNum).padStart(2, "0")} / ${String(totalPages).padStart(2, "0")}`, {
    x: W - 1.5, y: 0.3, w: 1.2, h: 0.3,
    fontFace: FONT.body, fontSize: 10, color: C.textMuted,
    align: "right", valign: "top", charSpacing: 2, margin: 0,
  });
  if (sectionLabel) {
    slide.addText(sectionLabel.toUpperCase(), {
      x: W - 5, y: 0.55, w: 4.7, h: 0.3,
      fontFace: FONT.body, fontSize: 9, color: C.teal, bold: true,
      align: "right", valign: "top", charSpacing: 4, margin: 0,
    });
  }
}

// Challenge badge for the six challenge slides
function addChallengeBadge(slide, n) {
  slide.addShape("rect", {
    x: 0.7, y: 0.95, w: 1.45, h: 0.45,
    fill: { color: C.amberBg }, line: { color: C.amber, width: 1 },
  });
  slide.addText(`CHALLENGE ${String(n).padStart(2, "0")}`, {
    x: 0.7, y: 0.95, w: 1.45, h: 0.45,
    fontFace: FONT.body, fontSize: 10, color: "92400E", bold: true,
    charSpacing: 4, align: "center", valign: "middle", margin: 0,
  });
}

async function build() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
  pres.title = "The Civic-Tech OSS Landscape — colleague briefing";
  pres.author = "Anonymous";

  const TOTAL = 9;

  // Pre-render icons
  const icoUsers     = await iconToBase64Png(FaUsers,         "#" + C.teal,    256);
  const icoUserSlash = await iconToBase64Png(FaUserSlash,     "#" + C.amber,   256);
  const icoCubes     = await iconToBase64Png(FaCubes,         "#" + C.teal,    256);
  const icoChart     = await iconToBase64Png(FaChartArea,     "#" + C.teal,    256);
  const icoInbox     = await iconToBase64Png(FaInbox,         "#" + C.amber,   256);
  const icoHourglass = await iconToBase64Png(FaHourglassHalf, "#" + C.teal,    256);
  const icoProject   = await iconToBase64Png(FaProjectDiagram,"#" + C.teal,    256);
  const icoGlobe     = await iconToBase64Png(FaGlobeAmericas, "#" + C.teal,    256);
  const icoCalendar  = await iconToBase64Png(FaCalendarAlt,   "#" + C.teal,    256);

  // ======================================================================
  // 1 — Title (dark)
  // ======================================================================
  const s1 = pres.addSlide();
  s1.background = { color: C.dark };
  s1.addShape("rect", { x: 0, y: 6.6, w: W, h: 0.07, fill: { color: C.teal }, line: { type: "none" } });
  s1.addShape("rect", { x: 0, y: 6.8, w: W * 0.25, h: 0.03, fill: { color: C.amber }, line: { type: "none" } });

  s1.addText("ESEM 2026 — emerging-results submission · colleague briefing", {
    x: 0.7, y: 0.7, w: W - 1.4, h: 0.4,
    fontFace: FONT.body, fontSize: 14, color: C.tealLight,
    charSpacing: 4, align: "left", valign: "top", margin: 0,
  });
  s1.addText([
    { text: "The Civic-Tech", options: { breakLine: true } },
    { text: "Open-Source Landscape" },
  ], {
    x: 0.7, y: 1.7, w: W - 1.4, h: 2.6,
    fontFace: FONT.header, fontSize: 54, color: C.white, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s1.addText("Sustainability challenges across 37 projects.", {
    x: 0.7, y: 4.6, w: W - 1.4, h: 0.6,
    fontFace: FONT.header, fontSize: 26, color: C.tealLight, italic: true,
    align: "left", valign: "top", margin: 0,
  });
  // Stat strip footer
  s1.addText(
    "37 repos  ·  16 organisations  ·  6 continents  ·  15 years  ·  178k commits  ·  2,506 contributor records",
    {
      x: 0.7, y: 6.95, w: W - 1.4, h: 0.4,
      fontFace: FONT.body, fontSize: 12, color: C.textLight,
      align: "left", valign: "top", margin: 0,
    }
  );

  // ======================================================================
  // 2 — Why this matters
  // ======================================================================
  const s2 = pres.addSlide();
  s2.background = { color: C.bg };
  addChrome(s2, 2, TOTAL, "Why this matters");
  s2.addText("Civic tech is public infrastructure.", {
    x: 0.7, y: 1.0, w: W - 1.4, h: 0.7,
    fontFace: FONT.header, fontSize: 30, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s2.addText("We don't actually know how it's holding up.", {
    x: 0.7, y: 1.7, w: W - 1.4, h: 0.5,
    fontFace: FONT.header, fontSize: 22, color: C.teal, italic: true,
    align: "left", valign: "top", margin: 0,
  });

  // Two-column body
  // LEFT — what it is
  s2.addText("WHAT CIVIC TECH ACTUALLY IS", {
    x: 0.7, y: 2.7, w: 5.7, h: 0.3,
    fontFace: FONT.body, fontSize: 10, color: C.teal, bold: true,
    charSpacing: 4, align: "left", valign: "top", margin: 0,
  });
  s2.addText(
    [
      { text: "Elections and voter information", options: { bullet: true, breakLine: true } },
      { text: "Government services and benefits portals", options: { bullet: true, breakLine: true } },
      { text: "Freedom-of-information platforms", options: { bullet: true, breakLine: true } },
      { text: "Environmental monitoring", options: { bullet: true, breakLine: true } },
      { text: "Federated social infrastructure", options: { bullet: true, breakLine: true } },
      { text: "Civic mapping, deliberation, transparency tools", options: { bullet: true } },
    ],
    {
      x: 0.7, y: 3.05, w: 5.7, h: 2.5,
      fontFace: FONT.body, fontSize: 13, color: C.text,
      align: "left", valign: "top", paraSpaceAfter: 4,
    }
  );

  // RIGHT — the gap
  s2.addText("WHY MEASURE IT", {
    x: 7.0, y: 2.7, w: 5.6, h: 0.3,
    fontFace: FONT.body, fontSize: 10, color: C.teal, bold: true,
    charSpacing: 4, align: "left", valign: "top", margin: 0,
  });
  s2.addText(
    "Mostly volunteer-led. Intermittently funded. Small non-profit teams. When a project fails, the cost falls on democratic participation and public-service delivery — not on private customers.",
    {
      x: 7.0, y: 3.05, w: 5.6, h: 1.6,
      fontFace: FONT.body, fontSize: 13, color: C.text,
      align: "left", valign: "top", margin: 0,
    }
  );
  s2.addText(
    "Existing literature is qualitative civic-tech work or quantitative OSS-health work on commercial flagships. No quantitative landscape of civic-tech specifically.",
    {
      x: 7.0, y: 4.65, w: 5.6, h: 1.5,
      fontFace: FONT.body, fontSize: 13, color: C.textMuted, italic: true,
      align: "left", valign: "top", margin: 0,
    }
  );

  // Bottom takeaway band
  s2.addShape("rect", { x: 0.7, y: 6.3, w: W - 1.4, h: 0.8, fill: { color: C.dark }, line: { type: "none" } });
  s2.addText(
    "Our question:  what does the civic-tech OSS landscape look like, and where are its sustainability stresses?",
    {
      x: 0.7, y: 6.3, w: W - 1.4, h: 0.8,
      fontFace: FONT.header, fontSize: 16, color: C.white, italic: true, bold: true,
      align: "center", valign: "middle", margin: 0,
    }
  );

  // ======================================================================
  // 3 — What we have (the dataset)
  // ======================================================================
  const s3 = pres.addSlide();
  s3.background = { color: C.bg };
  addChrome(s3, 3, TOTAL, "What we have");
  s3.addText("A purposive sample covering scale, age, and topic.", {
    x: 0.7, y: 1.0, w: W - 1.4, h: 0.7,
    fontFace: FONT.header, fontSize: 28, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s3.addText("All artefacts open-source under CC-BY 4.0 / MIT; Zenodo-archived.", {
    x: 0.7, y: 1.7, w: W - 1.4, h: 0.4,
    fontFace: FONT.body, fontSize: 14, color: C.textMuted, italic: true,
    align: "left", valign: "top", margin: 0,
  });

  // Four big stat cards
  const stats = [
    { n: "37", lbl: "repositories",       sub: "from 16 organisations" },
    { n: "6",  lbl: "continents",         sub: "Pan-African, EU, US, JP, AR, AU" },
    { n: "15", lbl: "years of history",   sub: "earliest commit 2011-04" },
    { n: "2,506", lbl: "contributor records", sub: "22,486 contributor-weeks" },
  ];
  stats.forEach((s, i) => {
    const x = 0.7 + i * 3.1;
    s3.addShape("rect", {
      x: x, y: 2.5, w: 2.9, h: 2.0,
      fill: { color: C.white }, line: { color: C.border, width: 1 },
      shadow: { type: "outer", color: "0F172A", blur: 12, offset: 3, angle: 90, opacity: 0.06 },
    });
    s3.addShape("rect", { x: x, y: 2.5, w: 2.9, h: 0.08, fill: { color: C.teal }, line: { type: "none" } });
    s3.addText(s.n, {
      x: x, y: 2.7, w: 2.9, h: 0.95,
      fontFace: FONT.header, fontSize: 44, color: C.teal, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s3.addText(s.lbl, {
      x: x, y: 3.65, w: 2.9, h: 0.35,
      fontFace: FONT.body, fontSize: 13, color: C.text, bold: true,
      align: "center", valign: "top", margin: 0,
    });
    s3.addText(s.sub, {
      x: x, y: 4.0, w: 2.9, h: 0.4,
      fontFace: FONT.body, fontSize: 10, color: C.textMuted, italic: true,
      align: "center", valign: "top", margin: 0,
    });
  });

  // Inclusion criteria strip below
  s3.addText("INCLUSION CRITERIA  (C1–C3, applied by two coders)", {
    x: 0.7, y: 4.95, w: W - 1.4, h: 0.3,
    fontFace: FONT.body, fontSize: 10, color: C.teal, bold: true,
    charSpacing: 4, align: "left", valign: "top", margin: 0,
  });
  const criteria = [
    { n: "C1", t: "Public-interest design intent",       d: "Civic mission at project inception, not incidental use" },
    { n: "C2", t: "Public-interest steward",             d: "Non-profit, government, academic, or civic collective" },
    { n: "C3", t: "Open development",                     d: "Public Git forge with public commit history" },
  ];
  criteria.forEach((c, i) => {
    const x = 0.7 + i * 4.2;
    s3.addText([
      { text: c.n + "   ", options: { fontFace: FONT.header, bold: true, color: C.amber, fontSize: 14 } },
      { text: c.t,        options: { fontFace: FONT.header, bold: true, color: C.text,  fontSize: 14 } },
    ], { x: x, y: 5.3, w: 4.0, h: 0.4, align: "left", valign: "top", margin: 0 });
    s3.addText(c.d, {
      x: x, y: 5.7, w: 4.0, h: 0.7,
      fontFace: FONT.body, fontSize: 11, color: C.textMuted,
      align: "left", valign: "top", margin: 0,
    });
  });

  // Bottom band — funnel
  s3.addShape("rect", { x: 0.7, y: 6.55, w: W - 1.4, h: 0.6, fill: { color: C.dark }, line: { type: "none" } });
  s3.addText("64 candidate repositories  →  21 failed C1  ·  6 failed C3  →  37 in sample", {
    x: 0.7, y: 6.55, w: W - 1.4, h: 0.6,
    fontFace: FONT.body, fontSize: 14, color: C.white, bold: true,
    align: "center", valign: "middle", margin: 0,
  });

  // ======================================================================
  // 4 — Challenge 01: drive-by contributors
  // ======================================================================
  const s4 = pres.addSlide();
  s4.background = { color: C.bg };
  addChrome(s4, 4, TOTAL, "Drive-by contribution");
  addChallengeBadge(s4, 1);
  s4.addText("More than half of contributors never come back.", {
    x: 0.7, y: 1.55, w: W - 1.4, h: 0.7,
    fontFace: FONT.header, fontSize: 28, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });

  // LEFT — big stat
  s4.addText("52%", {
    x: 0.7, y: 2.55, w: 5.5, h: 1.8,
    fontFace: FONT.header, fontSize: 130, color: C.amber, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s4.addText("of 2,506 human contributor records made a single commit and never returned.", {
    x: 0.7, y: 4.45, w: 5.5, h: 0.9,
    fontFace: FONT.body, fontSize: 15, color: C.text,
    align: "left", valign: "top", margin: 0,
  });
  // Sub-stats
  const sub = [
    { v: "73%", l: "within 3 months of first commit" },
    { v: "2.4%", l: "sustain activity > 5 years" },
    { v: "11.5 : 1", l: "departed-to-active ratio (humans)" },
  ];
  sub.forEach((r, i) => {
    const y = 5.5 + i * 0.42;
    s4.addText(r.v, {
      x: 0.7, y: y, w: 1.4, h: 0.35,
      fontFace: FONT.header, fontSize: 16, color: C.teal, bold: true,
      align: "left", valign: "middle", margin: 0,
    });
    s4.addText(r.l, {
      x: 2.15, y: y, w: 4.1, h: 0.35,
      fontFace: FONT.body, fontSize: 12, color: C.textMuted,
      align: "left", valign: "middle", margin: 0,
    });
  });

  // RIGHT — figure
  s4.addImage({ path: FIG_DIR + "fig_contributor_duration.png", x: 6.6, y: 2.4, w: 6.2, h: 3.5 });
  s4.addText(
    "Why it matters: the 'total contributors' number on a repo's landing page is a poor proxy for current engagement. Drive-by patches are valuable — but they don't sustain a project.",
    {
      x: 6.6, y: 6.05, w: 6.2, h: 1.1,
      fontFace: FONT.body, fontSize: 12, color: C.textMuted, italic: true,
      align: "left", valign: "top", margin: 0,
    }
  );

  // ======================================================================
  // 5 — Challenge 02: high-concentration cores
  // ======================================================================
  const s5 = pres.addSlide();
  s5.background = { color: C.bg };
  addChrome(s5, 5, TOTAL, "Concentration");
  addChallengeBadge(s5, 2);
  s5.addText("Cores are dangerously thin.", {
    x: 0.7, y: 1.55, w: W - 1.4, h: 0.7,
    fontFace: FONT.header, fontSize: 28, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });

  // Big stat
  s5.addText("46%", {
    x: 0.7, y: 2.5, w: 5.5, h: 1.5,
    fontFace: FONT.header, fontSize: 110, color: C.amber, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s5.addText("of repositories have bus factor 1.", {
    x: 0.7, y: 4.1, w: 5.5, h: 0.5,
    fontFace: FONT.body, fontSize: 16, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s5.addText("A single developer accounts for ≥50% of project commits.", {
    x: 0.7, y: 4.55, w: 5.5, h: 0.7,
    fontFace: FONT.body, fontSize: 13, color: C.textMuted, italic: true,
    align: "left", valign: "top", margin: 0,
  });

  // RIGHT — three stat cards
  const conc = [
    { n: "2",       lbl: "median bus factor",                          ico: icoUsers },
    { n: "96.6%",   lbl: "median per-repo elephant-week share",       ico: icoCubes },
    { n: "p=7×10⁻⁶", lbl: "bots inflate HHI (Wilcoxon paired, n=37)", ico: icoChart },
  ];
  conc.forEach((r, i) => {
    const y = 2.5 + i * 1.5;
    s5.addShape("rect", {
      x: 7.0, y: y, w: 5.6, h: 1.3,
      fill: { color: C.white }, line: { color: C.border, width: 1 },
      shadow: { type: "outer", color: "0F172A", blur: 12, offset: 3, angle: 90, opacity: 0.06 },
    });
    s5.addImage({ data: r.ico, x: 7.2, y: y + 0.35, w: 0.55, h: 0.55 });
    s5.addText(r.n, {
      x: 7.9, y: y + 0.1, w: 4.6, h: 0.65,
      fontFace: FONT.header, fontSize: 28, color: C.teal, bold: true,
      align: "left", valign: "top", margin: 0,
    });
    s5.addText(r.lbl, {
      x: 7.9, y: y + 0.78, w: 4.6, h: 0.4,
      fontFace: FONT.body, fontSize: 12, color: C.textMuted,
      align: "left", valign: "top", margin: 0,
    });
  });

  s5.addText(
    "For half the 37 repositories, almost every active week is dominated by a single contributor.",
    {
      x: 0.7, y: 6.6, w: W - 1.4, h: 0.5,
      fontFace: FONT.header, fontSize: 16, color: C.text, italic: true,
      align: "center", valign: "top", margin: 0,
    }
  );

  // ======================================================================
  // 6 — Challenge 03: effort > activity concentration
  // ======================================================================
  const s6 = pres.addSlide();
  s6.background = { color: C.bg };
  addChrome(s6, 6, TOTAL, "Effort vs activity");
  addChallengeBadge(s6, 3);
  s6.addText("Counting commits hides how concentrated effort actually is.", {
    x: 0.7, y: 1.55, w: W - 1.4, h: 0.7,
    fontFace: FONT.header, fontSize: 28, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });

  // LEFT — explanation
  s6.addText("THE TEST", {
    x: 0.7, y: 2.5, w: 5.5, h: 0.3,
    fontFace: FONT.body, fontSize: 10, color: C.teal, bold: true,
    charSpacing: 4, align: "left", valign: "top", margin: 0,
  });
  s6.addText(
    "Per repo, two Ginis: commits-per-contributor (activity) and lines-changed-per-contributor (effort). Paired Wilcoxon across the 37 repos — within-repository design, robust to coverage problems.",
    {
      x: 0.7, y: 2.85, w: 5.5, h: 1.6,
      fontFace: FONT.body, fontSize: 13, color: C.text,
      align: "left", valign: "top", margin: 0,
    }
  );

  // Big result box
  s6.addShape("rect", {
    x: 0.7, y: 4.7, w: 5.5, h: 2.2,
    fill: { color: C.emeraldBg }, line: { color: C.emerald, width: 1.5 },
  });
  s6.addText("RESULT", {
    x: 0.95, y: 4.85, w: 5.0, h: 0.3,
    fontFace: FONT.body, fontSize: 10, color: "065F46", bold: true,
    charSpacing: 4, align: "left", valign: "top", margin: 0,
  });
  s6.addText("p = 4.8 × 10⁻⁵", {
    x: 0.95, y: 5.2, w: 5.0, h: 0.9,
    fontFace: FONT.header, fontSize: 40, color: "047857", bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s6.addText(
    "Effort-Gini exceeds commit-Gini in 27 of 37 repositories (Wilcoxon W = 53.0). Mean Δ = +0.052.",
    {
      x: 0.95, y: 6.1, w: 5.0, h: 0.75,
      fontFace: FONT.body, fontSize: 12, color: "065F46",
      align: "left", valign: "top", margin: 0,
    }
  );

  // RIGHT — figure
  s6.addImage({ path: FIG_DIR + "fig_effort_gini_clean.png", x: 6.6, y: 2.4, w: 6.2, h: 4.0 });
  s6.addText(
    "At flagship scale the line-Gini saturates near 1 while the commit-Gini stays at 0.76–0.95 — large refactor commits dominate effort even when commit counts look balanced.",
    {
      x: 6.6, y: 6.5, w: 6.2, h: 0.7,
      fontFace: FONT.body, fontSize: 11, color: C.textMuted, italic: true,
      align: "left", valign: "top", margin: 0,
    }
  );

  // ======================================================================
  // 7 — Challenges 04 + 05: backlogs + survivor paradox
  // ======================================================================
  const s7 = pres.addSlide();
  s7.background = { color: C.bg };
  addChrome(s7, 7, TOTAL, "Backlogs · Survival");
  // Two badges side by side
  s7.addShape("rect", { x: 0.7, y: 0.95, w: 1.45, h: 0.45, fill: { color: C.amberBg }, line: { color: C.amber, width: 1 } });
  s7.addText("CHALLENGE 04", { x: 0.7, y: 0.95, w: 1.45, h: 0.45, fontFace: FONT.body, fontSize: 10, color: "92400E", bold: true, charSpacing: 4, align: "center", valign: "middle", margin: 0 });
  s7.addShape("rect", { x: 2.25, y: 0.95, w: 1.45, h: 0.45, fill: { color: C.amberBg }, line: { color: C.amber, width: 1 } });
  s7.addText("CHALLENGE 05", { x: 2.25, y: 0.95, w: 1.45, h: 0.45, fontFace: FONT.body, fontSize: 10, color: "92400E", bold: true, charSpacing: 4, align: "center", valign: "middle", margin: 0 });

  s7.addText("Backlogs accumulate. Survivors intensify.", {
    x: 0.7, y: 1.55, w: W - 1.4, h: 0.7,
    fontFace: FONT.header, fontSize: 28, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });

  // LEFT — backlogs card
  s7.addShape("rect", {
    x: 0.7, y: 2.5, w: 5.7, h: 4.5,
    fill: { color: C.white }, line: { color: C.border, width: 1 },
    shadow: { type: "outer", color: "0F172A", blur: 12, offset: 3, angle: 90, opacity: 0.06 },
  });
  s7.addShape("rect", { x: 0.7, y: 2.5, w: 0.1, h: 4.5, fill: { color: C.amber }, line: { type: "none" } });
  s7.addImage({ data: icoInbox, x: 1.0, y: 2.75, w: 0.55, h: 0.55 });
  s7.addText("BACKLOGS", {
    x: 1.7, y: 2.85, w: 4.5, h: 0.35,
    fontFace: FONT.body, fontSize: 11, color: C.amber, bold: true,
    charSpacing: 4, align: "left", valign: "top", margin: 0,
  });
  s7.addText("0.98", {
    x: 1.0, y: 3.5, w: 5.0, h: 0.9,
    fontFace: FONT.header, fontSize: 48, color: C.amber, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s7.addText("median stale-issue ratio (n=26 repos with open issues).", {
    x: 1.0, y: 4.45, w: 5.0, h: 0.4,
    fontFace: FONT.body, fontSize: 13, color: C.text,
    align: "left", valign: "top", margin: 0,
  });
  s7.addShape("line", { x: 1.0, y: 4.95, w: 4.9, h: 0, line: { color: C.border, width: 0.5 } });
  s7.addText("AND  no release discipline:", {
    x: 1.0, y: 5.1, w: 5.0, h: 0.35,
    fontFace: FONT.body, fontSize: 11, color: C.teal, bold: true,
    charSpacing: 2, align: "left", valign: "top", margin: 0,
  });
  s7.addText("20 of 37 repositories (54%) have never tagged a release.", {
    x: 1.0, y: 5.45, w: 5.2, h: 0.45,
    fontFace: FONT.body, fontSize: 14, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s7.addText(
    "Including five projects more than 9 years old — a 15-year-old FOI platform, an 11-year-old polling-station service.",
    {
      x: 1.0, y: 5.95, w: 5.2, h: 0.95,
      fontFace: FONT.body, fontSize: 12, color: C.textMuted, italic: true,
      align: "left", valign: "top", margin: 0,
    }
  );

  // RIGHT — survivor paradox card
  s7.addShape("rect", {
    x: 6.9, y: 2.5, w: 5.7, h: 4.5,
    fill: { color: C.white }, line: { color: C.border, width: 1 },
    shadow: { type: "outer", color: "0F172A", blur: 12, offset: 3, angle: 90, opacity: 0.06 },
  });
  s7.addShape("rect", { x: 6.9, y: 2.5, w: 0.1, h: 4.5, fill: { color: C.teal }, line: { type: "none" } });
  s7.addImage({ data: icoCalendar, x: 7.2, y: 2.75, w: 0.55, h: 0.55 });
  s7.addText("THE SURVIVOR PARADOX", {
    x: 7.9, y: 2.85, w: 4.5, h: 0.35,
    fontFace: FONT.body, fontSize: 11, color: C.teal, bold: true,
    charSpacing: 4, align: "left", valign: "top", margin: 0,
  });
  s7.addImage({ path: FIG_DIR + "fig_activity_vs_age.png", x: 7.2, y: 3.45, w: 5.2, h: 2.5 });
  s7.addText(
    "Median weekly commits rise with project age — but the projects that died aren't in this sample. Survivor bias, not health.",
    {
      x: 7.2, y: 6.05, w: 5.2, h: 0.9,
      fontFace: FONT.body, fontSize: 11, color: C.textMuted, italic: true,
      align: "left", valign: "top", margin: 0,
    }
  );

  // ======================================================================
  // 8 — Challenge 06: thin cross-project ecosystem
  // ======================================================================
  const s8 = pres.addSlide();
  s8.background = { color: C.bg };
  addChrome(s8, 8, TOTAL, "Cross-project ecosystem");
  addChallengeBadge(s8, 6);
  s8.addText("The civic-tech ecosystem is thin and umbrella-bounded.", {
    x: 0.7, y: 1.55, w: W - 1.4, h: 0.7,
    fontFace: FONT.header, fontSize: 28, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });

  // LEFT — stat chain: 5.5% → 8.9% → 0.5%
  s8.addText("5.5%", {
    x: 0.7, y: 2.4, w: 5.5, h: 1.3,
    fontFace: FONT.header, fontSize: 90, color: C.amber, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s8.addText("of unique humans contribute to ≥ 2 of our 37 repositories.", {
    x: 0.7, y: 3.7, w: 5.5, h: 0.5,
    fontFace: FONT.body, fontSize: 14, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s8.addText("112 of 2,055 humans, after bot filtering.", {
    x: 0.7, y: 4.15, w: 5.5, h: 0.35,
    fontFace: FONT.body, fontSize: 11, color: C.textMuted, italic: true,
    align: "left", valign: "top", margin: 0,
  });

  // Sensitivity-check chain
  s8.addShape("rect", {
    x: 0.7, y: 4.7, w: 5.5, h: 2.3,
    fill: { color: C.tealPale }, line: { color: C.teal, width: 1 },
  });
  s8.addText("THE SENSITIVITY CHECK", {
    x: 0.9, y: 4.85, w: 5.1, h: 0.3,
    fontFace: FONT.body, fontSize: 10, color: "065F46", bold: true,
    charSpacing: 4, align: "left", valign: "top", margin: 0,
  });
  s8.addText([
    { text: "of those 112 multi-repo humans, only ", options: { fontFace: FONT.body, fontSize: 12, color: "065F46" } },
    { text: "8.9% (10)", options: { fontFace: FONT.header, fontSize: 14, color: "047857", bold: true } },
    { text: " span ≥ 2 distinct organisations.", options: { fontFace: FONT.body, fontSize: 12, color: "065F46", breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Across the whole sample that leaves ", options: { fontFace: FONT.body, fontSize: 12, color: "065F46" } },
    { text: "≈ 0.5%", options: { fontFace: FONT.header, fontSize: 14, color: "047857", bold: true } },
    { text: " of all humans across the 37 repositories as genuinely cross-organisational. Invariant to umbrella over-representation in our frame.", options: { fontFace: FONT.body, fontSize: 12, color: "065F46" } },
  ], {
    x: 0.9, y: 5.2, w: 5.1, h: 1.7,
    align: "left", valign: "top", margin: 0,
  });

  // RIGHT — figure
  s8.addImage({ path: FIG_DIR + "fig_cross_project_v2.png", x: 6.6, y: 2.4, w: 6.2, h: 4.5 });
  s8.addText(
    "Implication: the cross-project contributor pool is small AND umbrella-bounded. Sustainability interventions assuming cross-cutting volunteer flow don't have that flow to work with.",
    {
      x: 6.6, y: 6.95, w: 6.2, h: 0.4,
      fontFace: FONT.body, fontSize: 11, color: C.textMuted, italic: true,
      align: "left", valign: "top", margin: 0,
    }
  );

  // ======================================================================
  // 9 — What's next + ask (dark)
  // ======================================================================
  const s9 = pres.addSlide();
  s9.background = { color: C.dark };
  s9.addShape("rect", { x: 0, y: 0, w: W * 0.25, h: 0.07, fill: { color: C.teal }, line: { type: "none" } });
  s9.addText("09 / 09", {
    x: W - 1.5, y: 0.3, w: 1.2, h: 0.3,
    fontFace: FONT.body, fontSize: 10, color: C.textLight,
    align: "right", valign: "top", charSpacing: 2, margin: 0,
  });
  s9.addText("WHAT'S NEXT", {
    x: W - 5, y: 0.55, w: 4.7, h: 0.3,
    fontFace: FONT.body, fontSize: 9, color: C.tealLight, bold: true,
    align: "right", valign: "top", charSpacing: 4, margin: 0,
  });

  s9.addText("Three axes for the longer-term programme.", {
    x: 0.7, y: 1.0, w: W - 1.4, h: 0.7,
    fontFace: FONT.header, fontSize: 30, color: C.white, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s9.addText("ESEM 2026 abstract due May 22 · full submission May 29.", {
    x: 0.7, y: 1.7, w: W - 1.4, h: 0.4,
    fontFace: FONT.body, fontSize: 14, color: C.textLight, italic: true,
    align: "left", valign: "top", margin: 0,
  });

  const axes = [
    {
      tag: "L1",
      title: "Longitudinal tracking",
      body: "Quarterly recrawls of the 37 repositories over 24 months. Change-over-time on the six challenges. Event-study designs around governance changes.",
    },
    {
      tag: "L2",
      title: "Replication & extension",
      body: "Non-GitHub hosts (GitLab, Codeberg, self-hosted Gitea). Larger civic-tech population (target n ≥ 100). Cross-platform consistency checks.",
    },
    {
      tag: "L3",
      title: "Failed-projects comparison",
      body: "Parallel sample of civic-tech repositories that ceased activity. Convert survivor observations into causal claims about lifecycle.",
    },
  ];
  axes.forEach((a, i) => {
    const x = 0.7 + i * 4.2;
    s9.addShape("rect", {
      x: x, y: 2.5, w: 3.95, h: 3.3,
      fill: { color: "1E293B" }, line: { color: C.teal, width: 1 },
    });
    s9.addShape("rect", { x: x, y: 2.5, w: 3.95, h: 0.1, fill: { color: C.teal }, line: { type: "none" } });
    s9.addText(a.tag, {
      x: x + 0.3, y: 2.75, w: 1.5, h: 0.7,
      fontFace: FONT.header, fontSize: 36, color: C.tealLight, bold: true,
      align: "left", valign: "top", margin: 0,
    });
    s9.addText(a.title, {
      x: x + 0.3, y: 3.55, w: 3.4, h: 0.5,
      fontFace: FONT.header, fontSize: 16, color: C.white, bold: true,
      align: "left", valign: "top", margin: 0,
    });
    s9.addText(a.body, {
      x: x + 0.3, y: 4.15, w: 3.4, h: 1.6,
      fontFace: FONT.body, fontSize: 12, color: C.textLight,
      align: "left", valign: "top", margin: 0,
    });
  });

  // Ask band
  s9.addShape("rect", { x: 0.7, y: 6.15, w: W - 1.4, h: 0.95, fill: { color: C.teal }, line: { type: "none" } });
  s9.addText([
    { text: "Where I'd love your input:  ", options: { fontFace: FONT.body, fontSize: 14, color: C.white, bold: true } },
    { text: "framing of the six challenges  ·  candidates for L1/L2/L3  ·  ", options: { fontFace: FONT.body, fontSize: 14, color: C.white } },
    { text: "recent (2023–25) OSS-health refs", options: { fontFace: FONT.body, fontSize: 14, color: "FEF3C7", bold: true } },
  ], {
    x: 0.95, y: 6.15, w: W - 1.9, h: 0.95,
    align: "left", valign: "middle", margin: 0,
  });

  // ----- write -----
  await pres.writeFile({ fileName: "colleague_briefing.pptx" });
  console.log("Wrote colleague_briefing.pptx (9 slides)");
}

build().catch(e => { console.error(e); process.exit(1); });
