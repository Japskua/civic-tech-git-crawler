// Slides for colleague briefing on the ESEM 2026 measurement-coverage paper.
// Generates: colleague_briefing.pptx
//
// Palette: Ocean / Teal — feels appropriate for a data + methodology talk.
//   Dark midnight   #0F172A  (sandwich slides + accents)
//   Teal primary    #0D9488
//   Teal light      #14B8A6
//   Amber warning   #F59E0B  (the "claimed" / pilot side)
//   Emerald good    #10B981  (the "corrected" side)
//   Slate-50 bg     #F8FAFC
//   Slate-800 text  #1E293B
//   Slate-500 muted #64748B

const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const {
  FaDatabase,
  FaExclamationTriangle,
  FaCheckCircle,
  FaCircleNotch,
  FaProjectDiagram,
  FaTools,
  FaSearch,
  FaCompass,
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

// Common dimensions
const W = 13.3;
const H = 7.5;

// Palette constants
const C = {
  dark: "0F172A",
  teal: "0D9488",
  tealLight: "14B8A6",
  amber: "F59E0B",
  amberBg: "FEF3C7",
  emerald: "10B981",
  emeraldBg: "D1FAE5",
  bg: "F8FAFC",
  text: "1E293B",
  textMuted: "64748B",
  white: "FFFFFF",
  border: "E2E8F0",
};

const FONT = {
  header: "Georgia",
  body: "Calibri",
};

// Top-left accent block + page indicator that appears on every content slide
function addChrome(slide, pageNum, totalPages, sectionLabel) {
  // Teal accent block top-left
  slide.addShape("rect", {
    x: 0, y: 0, w: 0.35, h: 1.2,
    fill: { color: C.teal },
    line: { type: "none" },
  });
  // Page indicator top-right
  slide.addText(`${String(pageNum).padStart(2, "0")} / ${String(totalPages).padStart(2, "0")}`, {
    x: W - 1.5, y: 0.3, w: 1.2, h: 0.3,
    fontFace: FONT.body, fontSize: 10, color: C.textMuted,
    align: "right", valign: "top",
    charSpacing: 2,
    margin: 0,
  });
  // Section label below page indicator
  if (sectionLabel) {
    slide.addText(sectionLabel.toUpperCase(), {
      x: W - 4, y: 0.55, w: 3.7, h: 0.3,
      fontFace: FONT.body, fontSize: 9, color: C.teal, bold: true,
      align: "right", valign: "top",
      charSpacing: 4,
      margin: 0,
    });
  }
}

async function build() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";   // 13.3 x 7.5
  pres.title = "Coverage-Biased Correlations — colleague briefing";
  pres.author = "Anonymous";

  const TOTAL = 8;

  // Pre-render icons we'll use
  const icoDatabase  = await iconToBase64Png(FaDatabase,         "#" + C.teal,    256);
  const icoWarning   = await iconToBase64Png(FaExclamationTriangle, "#" + C.amber, 256);
  const icoCheck     = await iconToBase64Png(FaCheckCircle,      "#" + C.emerald, 256);
  const icoCycle     = await iconToBase64Png(FaCircleNotch,      "#" + C.tealLight,256);
  const icoDiagram   = await iconToBase64Png(FaProjectDiagram,   "#" + C.teal,    256);
  const icoTools     = await iconToBase64Png(FaTools,            "#" + C.teal,    256);
  const icoSearch    = await iconToBase64Png(FaSearch,           "#" + C.teal,    256);
  const icoCompass   = await iconToBase64Png(FaCompass,          "#" + C.teal,    256);

  // ======================================================================
  // Slide 1 — Title (dark)
  // ======================================================================
  const s1 = pres.addSlide();
  s1.background = { color: C.dark };
  // Decorative diagonal stripe (teal)
  s1.addShape("rect", {
    x: 0, y: 6.6, w: W, h: 0.07, fill: { color: C.teal }, line: { type: "none" },
  });
  s1.addShape("rect", {
    x: 0, y: 6.8, w: W * 0.25, h: 0.03, fill: { color: C.amber }, line: { type: "none" },
  });
  // Kicker
  s1.addText("ESEM 2026 — emerging-results submission · colleague briefing", {
    x: 0.7, y: 0.7, w: W - 1.4, h: 0.4,
    fontFace: FONT.body, fontSize: 14, color: C.tealLight,
    charSpacing: 4, bold: false, align: "left", valign: "top", margin: 0,
  });
  // Title
  s1.addText([
    { text: "Coverage-Biased Correlations", options: { breakLine: true } },
    { text: "in OSS Repository Health Studies" },
  ], {
    x: 0.7, y: 1.8, w: W - 1.4, h: 2.6,
    fontFace: FONT.header, fontSize: 48, color: C.white, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  // Subtitle / takeaway
  s1.addText("What we thought we found —", {
    x: 0.7, y: 4.5, w: W - 1.4, h: 0.55,
    fontFace: FONT.header, fontSize: 24, color: "9CA3AF", italic: true,
    align: "left", valign: "top", margin: 0,
  });
  s1.addText("and what was actually there.", {
    x: 0.7, y: 5.1, w: W - 1.4, h: 0.55,
    fontFace: FONT.header, fontSize: 24, color: C.tealLight, italic: true, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  // Footer line
  s1.addText("A 37-repository civic-tech panel · open-source toolchain · paired-design results", {
    x: 0.7, y: 6.95, w: W - 1.4, h: 0.4,
    fontFace: FONT.body, fontSize: 11, color: "94A3B8",
    align: "left", valign: "top", margin: 0,
  });

  // ======================================================================
  // Slide 2 — The problem in one number
  // ======================================================================
  const s2 = pres.addSlide();
  s2.background = { color: C.bg };
  addChrome(s2, 2, TOTAL, "The problem");
  // Title
  s2.addText("Your OSS health metrics depend on flaky endpoints.", {
    x: 0.7, y: 1.0, w: W - 1.4, h: 0.7,
    fontFace: FONT.header, fontSize: 30, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  // Stat — big number on left
  s2.addText("5 of 37", {
    x: 0.7, y: 2.1, w: 5.5, h: 1.8,
    fontFace: FONT.header, fontSize: 110, color: C.teal, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s2.addText("repositories returned populated", {
    x: 0.7, y: 4.0, w: 5.5, h: 0.5,
    fontFace: FONT.body, fontSize: 16, color: C.text,
    align: "left", valign: "top", margin: 0,
  });
  s2.addText("/stats/commit_activity   data on our initial crawl.", {
    x: 0.7, y: 4.4, w: 5.5, h: 0.5,
    fontFace: "Consolas", fontSize: 14, color: C.text,
    align: "left", valign: "top", margin: 0,
  });
  s2.addText("GitHub computes the rest asynchronously, then caches results only for repos with recent traffic.", {
    x: 0.7, y: 5.1, w: 5.5, h: 1.2,
    fontFace: FONT.body, fontSize: 13, color: C.textMuted, italic: true,
    align: "left", valign: "top", margin: 0,
  });

  // Right side: three-row failure-mode card
  // Card background
  s2.addShape("rect", {
    x: 7.0, y: 2.1, w: 5.6, h: 4.5,
    fill: { color: C.white }, line: { color: C.border, width: 1 },
    shadow: { type: "outer", color: "0F172A", blur: 12, offset: 3, angle: 90, opacity: 0.06 },
  });
  s2.addText("Why the missingness is non-random", {
    x: 7.3, y: 2.3, w: 5.0, h: 0.4,
    fontFace: FONT.header, fontSize: 14, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  // 3 rows
  const rows2 = [
    { ico: icoWarning, h: "Timeout under retry budget",
      b: "/stats/* returns HTTP 202 indefinitely for cold repos." },
    { ico: icoCycle, h: "Cache is warm for active repos",
      b: "Heavy API traffic → recent recomputation → populated response." },
    { ico: icoDatabase, h: "The 'populated' subset is biased",
      b: "And the bias correlates with the variables you care about." },
  ];
  rows2.forEach((r, i) => {
    const y = 2.85 + i * 1.18;
    s2.addImage({ data: r.ico, x: 7.3, y: y, w: 0.55, h: 0.55 });
    s2.addText(r.h, {
      x: 8.05, y: y - 0.05, w: 4.5, h: 0.4,
      fontFace: FONT.header, fontSize: 14, color: C.text, bold: true,
      align: "left", valign: "top", margin: 0,
    });
    s2.addText(r.b, {
      x: 8.05, y: y + 0.32, w: 4.5, h: 0.7,
      fontFace: FONT.body, fontSize: 12, color: C.textMuted,
      align: "left", valign: "top", margin: 0,
    });
  });

  // ======================================================================
  // Slide 3 — The discovery (before / after)
  // ======================================================================
  const s3 = pres.addSlide();
  s3.background = { color: C.bg };
  addChrome(s3, 3, TOTAL, "The discovery");
  s3.addText("A 'robust' correlation that vanished under triangulation", {
    x: 0.7, y: 1.0, w: W - 1.4, h: 0.7,
    fontFace: FONT.header, fontSize: 28, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s3.addText("burstiness  ↔  stale-issue ratio, across our 37-repo civic-tech panel", {
    x: 0.7, y: 1.7, w: W - 1.4, h: 0.4,
    fontFace: FONT.body, fontSize: 14, color: C.textMuted, italic: true,
    align: "left", valign: "top", margin: 0,
  });

  // LEFT card — what we thought
  s3.addShape("rect", {
    x: 0.7, y: 2.4, w: 5.7, h: 3.6,
    fill: { color: C.amberBg }, line: { color: C.amber, width: 1.5 },
  });
  s3.addText("PILOT  (n = 29)", {
    x: 0.95, y: 2.55, w: 5.2, h: 0.35,
    fontFace: FONT.body, fontSize: 11, color: "B45309", bold: true,
    charSpacing: 4, align: "left", valign: "top", margin: 0,
  });
  s3.addText("ρ = 0.685", {
    x: 0.95, y: 2.95, w: 5.2, h: 1.0,
    fontFace: FONT.header, fontSize: 56, color: "92400E", bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s3.addText("FDR-significant on n = 17 pairs", {
    x: 0.95, y: 4.05, w: 5.2, h: 0.4,
    fontFace: FONT.body, fontSize: 14, color: "78350F", bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s3.addText("Built on the subset of repos for which GitHub had pre-cached /stats/* results.", {
    x: 0.95, y: 4.55, w: 5.2, h: 1.3,
    fontFace: FONT.body, fontSize: 12, color: "78350F", italic: true,
    align: "left", valign: "top", margin: 0,
  });

  // Arrow (unicode glyph — most reliable across renderers)
  s3.addText("→", {
    x: 6.4, y: 3.7, w: 0.8, h: 0.9,
    fontFace: FONT.header, fontSize: 60, color: C.teal, bold: true,
    align: "center", valign: "middle", margin: 0,
  });

  // RIGHT card — what's actually there
  s3.addShape("rect", {
    x: 7.2, y: 2.4, w: 5.7, h: 3.6,
    fill: { color: C.emeraldBg }, line: { color: C.emerald, width: 1.5 },
  });
  s3.addText("CORRECTED  (n = 37, GraphQL triangulation)", {
    x: 7.45, y: 2.55, w: 5.2, h: 0.35,
    fontFace: FONT.body, fontSize: 11, color: "065F46", bold: true,
    charSpacing: 4, align: "left", valign: "top", margin: 0,
  });
  s3.addText("ρ = 0.444", {
    x: 7.45, y: 2.95, w: 5.2, h: 1.0,
    fontFace: FONT.header, fontSize: 56, color: "047857", bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s3.addText("not FDR-significant; n = 26 pairs", {
    x: 7.45, y: 4.05, w: 5.2, h: 0.4,
    fontFace: FONT.body, fontSize: 14, color: "065F46", bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s3.addText("Coverage 17/29 → 37/37 on burstiness via GraphQL bulk fetch.", {
    x: 7.45, y: 4.55, w: 5.2, h: 1.3,
    fontFace: FONT.body, fontSize: 12, color: "065F46", italic: true,
    align: "left", valign: "top", margin: 0,
  });

  // Takeaway band at the bottom
  s3.addShape("rect", {
    x: 0.7, y: 6.4, w: W - 1.4, h: 0.7,
    fill: { color: C.dark }, line: { type: "none" },
  });
  s3.addText("Same direction. Different population behind the number.", {
    x: 0.7, y: 6.4, w: W - 1.4, h: 0.7,
    fontFace: FONT.header, fontSize: 17, color: C.white, italic: true, bold: true,
    align: "center", valign: "middle", margin: 0,
  });

  // ======================================================================
  // Slide 4 — Why it generalises
  // ======================================================================
  const s4 = pres.addSlide();
  s4.background = { color: C.bg };
  addChrome(s4, 4, TOTAL, "Why it generalises");
  s4.addText("It's not about burstiness.", {
    x: 0.7, y: 1.0, w: W - 1.4, h: 0.6,
    fontFace: FONT.header, fontSize: 28, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s4.addText("It's about how aggregate endpoints behave under cache-driven coverage.", {
    x: 0.7, y: 1.6, w: W - 1.4, h: 0.5,
    fontFace: FONT.header, fontSize: 20, color: C.teal, italic: true,
    align: "left", valign: "top", margin: 0,
  });

  // Three-step flow
  const steps = [
    {
      n: "01",
      h: "Endpoint returns only what's cached",
      b: "Async aggregate endpoints serve repos GitHub has recently computed.",
    },
    {
      n: "02",
      h: "Caching correlates with activity",
      b: "Recent computation is triggered by external API traffic, which scales with popularity.",
    },
    {
      n: "03",
      h: "Correlations across the subset are biased",
      b: "Joined-subset correlations skew toward the very variables you wanted to measure independently.",
    },
  ];
  steps.forEach((s, i) => {
    const x = 0.7 + i * 4.2;
    s4.addShape("rect", {
      x: x, y: 2.6, w: 3.95, h: 3.6,
      fill: { color: C.white }, line: { color: C.border, width: 1 },
      shadow: { type: "outer", color: "0F172A", blur: 12, offset: 3, angle: 90, opacity: 0.06 },
    });
    s4.addShape("rect", {
      x: x, y: 2.6, w: 3.95, h: 0.1,
      fill: { color: C.teal }, line: { type: "none" },
    });
    s4.addText(s.n, {
      x: x + 0.3, y: 2.85, w: 1.2, h: 0.7,
      fontFace: FONT.header, fontSize: 42, color: C.teal, bold: true,
      align: "left", valign: "top", margin: 0,
    });
    s4.addText(s.h, {
      x: x + 0.3, y: 3.7, w: 3.4, h: 0.85,
      fontFace: FONT.header, fontSize: 16, color: C.text, bold: true,
      align: "left", valign: "top", margin: 0,
    });
    s4.addText(s.b, {
      x: x + 0.3, y: 4.7, w: 3.4, h: 1.4,
      fontFace: FONT.body, fontSize: 12, color: C.textMuted,
      align: "left", valign: "top", margin: 0,
    });
  });

  // Bottom callout
  s4.addText("Any OSS health study that joins an aggregate endpoint with a target metric is exposed to this failure mode.", {
    x: 0.7, y: 6.55, w: W - 1.4, h: 0.6,
    fontFace: FONT.header, fontSize: 14, color: C.text, italic: true,
    align: "center", valign: "top", margin: 0,
  });

  // ======================================================================
  // Slide 5 — Why our approach could work
  // ======================================================================
  const s5 = pres.addSlide();
  s5.background = { color: C.bg };
  addChrome(s5, 5, TOTAL, "Why this works");
  s5.addText("Two defences, not one.", {
    x: 0.7, y: 1.0, w: W - 1.4, h: 0.6,
    fontFace: FONT.header, fontSize: 28, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s5.addText("How we build studies that survive coverage problems.", {
    x: 0.7, y: 1.6, w: W - 1.4, h: 0.45,
    fontFace: FONT.body, fontSize: 14, color: C.textMuted, italic: true,
    align: "left", valign: "top", margin: 0,
  });

  // Two big cards
  const cards5 = [
    {
      x: 0.7,
      title: "Triangulate from independent sources",
      tag: "Engineering",
      body: [
        "GraphQL bulk-fetch as fallback to /stats/* timeouts",
        "Exponential backoff + warm-up pre-pass",
        "Per-metric coverage reported as first-class output",
      ],
      footer: "Result: burstiness coverage 5/37 → 37/37",
      ico: icoTools,
    },
    {
      x: 6.95,
      title: "Use paired-design metrics",
      tag: "Statistics",
      body: [
        "Within-repository Wilcoxon tests bypass coverage entirely",
        "Each pair is its own control — no joined-subset bias",
        "Robust at n=37 with large effect sizes",
      ],
      footer: "Result: two well-powered findings (next slide)",
      ico: icoCheck,
    },
  ];
  cards5.forEach(c => {
    s5.addShape("rect", {
      x: c.x, y: 2.4, w: 5.65, h: 4.6,
      fill: { color: C.white }, line: { color: C.border, width: 1 },
      shadow: { type: "outer", color: "0F172A", blur: 12, offset: 3, angle: 90, opacity: 0.06 },
    });
    s5.addShape("rect", {
      x: c.x, y: 2.4, w: 0.1, h: 4.6,
      fill: { color: C.teal }, line: { type: "none" },
    });
    s5.addImage({ data: c.ico, x: c.x + 0.4, y: 2.65, w: 0.55, h: 0.55 });
    s5.addText(c.tag.toUpperCase(), {
      x: c.x + 1.1, y: 2.7, w: 4.0, h: 0.3,
      fontFace: FONT.body, fontSize: 10, color: C.teal, bold: true,
      charSpacing: 4, align: "left", valign: "top", margin: 0,
    });
    s5.addText(c.title, {
      x: c.x + 0.4, y: 3.4, w: 5.0, h: 0.7,
      fontFace: FONT.header, fontSize: 19, color: C.text, bold: true,
      align: "left", valign: "top", margin: 0,
    });
    s5.addText(
      c.body.map((line, i) => ({
        text: line,
        options: { bullet: true, breakLine: i < c.body.length - 1 },
      })),
      {
        x: c.x + 0.4, y: 4.25, w: 5.0, h: 1.9,
        fontFace: FONT.body, fontSize: 13, color: C.text,
        align: "left", valign: "top",
        paraSpaceAfter: 6,
      }
    );
    // Footer line
    s5.addShape("line", {
      x: c.x + 0.4, y: 6.25, w: 5.0, h: 0,
      line: { color: C.border, width: 0.75 },
    });
    s5.addText(c.footer, {
      x: c.x + 0.4, y: 6.35, w: 5.0, h: 0.5,
      fontFace: FONT.body, fontSize: 12, color: C.teal, italic: true, bold: true,
      align: "left", valign: "top", margin: 0,
    });
  });

  // ======================================================================
  // Slide 6 — Evidence: two paired-design findings
  // ======================================================================
  const s6 = pres.addSlide();
  s6.background = { color: C.bg };
  addChrome(s6, 6, TOTAL, "Evidence");
  s6.addText("Two paired-design findings that ARE robust", {
    x: 0.7, y: 1.0, w: W - 1.4, h: 0.7,
    fontFace: FONT.header, fontSize: 28, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s6.addText("Each repository is its own control. Per-metric coverage doesn't enter the test.", {
    x: 0.7, y: 1.7, w: W - 1.4, h: 0.4,
    fontFace: FONT.body, fontSize: 14, color: C.textMuted, italic: true,
    align: "left", valign: "top", margin: 0,
  });

  const findings = [
    {
      x: 0.7,
      tag: "Bot filtering matters — selectively",
      stat: "p = 7 × 10⁻⁶",
      statLabel: "Wilcoxon signed-rank, HHI with-vs-without bots",
      lines: [
        "27 of 37 repositories change for HHI",
        "Only 4 of 37 change for bus factor",
        "Elephant factor: no repository changes",
      ],
      tail: "Recommendation: filter bots for HHI; include them for bus factor.",
    },
    {
      x: 6.95,
      tag: "Effort > activity, by construction",
      stat: "p = 4.8 × 10⁻⁵",
      statLabel: "Wilcoxon signed-rank, line-Gini vs commit-Gini",
      lines: [
        "Line-Gini exceeds commit-Gini in 27 of 37 repos",
        "Mean Δ = +0.052 (sign test p = 1.6 × 10⁻⁴)",
        "Commit counts systematically under-estimate effort concentration",
      ],
      tail: "Implication: lines-changed should accompany commit-count health metrics.",
    },
  ];
  findings.forEach(f => {
    s6.addShape("rect", {
      x: f.x, y: 2.4, w: 5.65, h: 4.6,
      fill: { color: C.white }, line: { color: C.border, width: 1 },
      shadow: { type: "outer", color: "0F172A", blur: 12, offset: 3, angle: 90, opacity: 0.06 },
    });
    s6.addShape("rect", {
      x: f.x, y: 2.4, w: 5.65, h: 0.1,
      fill: { color: C.emerald }, line: { type: "none" },
    });
    s6.addText(f.tag, {
      x: f.x + 0.4, y: 2.7, w: 5.0, h: 0.45,
      fontFace: FONT.header, fontSize: 16, color: C.text, bold: true,
      align: "left", valign: "top", margin: 0,
    });
    s6.addText(f.stat, {
      x: f.x + 0.4, y: 3.3, w: 5.0, h: 1.0,
      fontFace: FONT.header, fontSize: 36, color: C.emerald, bold: true,
      align: "left", valign: "top", margin: 0,
    });
    s6.addText(f.statLabel, {
      x: f.x + 0.4, y: 4.35, w: 5.0, h: 0.4,
      fontFace: FONT.body, fontSize: 11, color: C.textMuted, italic: true,
      align: "left", valign: "top", margin: 0,
    });
    s6.addText(
      f.lines.map((l, i) => ({
        text: l,
        options: { bullet: true, breakLine: i < f.lines.length - 1 },
      })),
      {
        x: f.x + 0.4, y: 4.8, w: 5.0, h: 1.5,
        fontFace: FONT.body, fontSize: 12, color: C.text,
        align: "left", valign: "top",
        paraSpaceAfter: 4,
      }
    );
    s6.addShape("line", {
      x: f.x + 0.4, y: 6.35, w: 5.0, h: 0,
      line: { color: C.border, width: 0.75 },
    });
    s6.addText(f.tail, {
      x: f.x + 0.4, y: 6.45, w: 5.0, h: 0.5,
      fontFace: FONT.body, fontSize: 11, color: C.teal, italic: true,
      align: "left", valign: "top", margin: 0,
    });
  });

  // ======================================================================
  // Slide 7 — What this paper offers + asks
  // ======================================================================
  const s7 = pres.addSlide();
  s7.background = { color: C.bg };
  addChrome(s7, 7, TOTAL, "What we offer");
  s7.addText("What this paper offers colleagues", {
    x: 0.7, y: 1.0, w: W - 1.4, h: 0.7,
    fontFace: FONT.header, fontSize: 28, color: C.text, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s7.addText("Reusable artefacts, a quantitative case study, and a research direction.", {
    x: 0.7, y: 1.7, w: W - 1.4, h: 0.4,
    fontFace: FONT.body, fontSize: 14, color: C.textMuted, italic: true,
    align: "left", valign: "top", margin: 0,
  });

  const offers = [
    { ico: icoTools,   h: "An open toolchain",      b: "Python crawler with the triangulation built in. Per-metric coverage reporting. MIT-licensed, Zenodo-archived." },
    { ico: icoSearch,  h: "A measurement-bias case study", b: "Quantitative decomposition of how a coverage bias produces an apparently 'robust' published correlation." },
    { ico: icoCompass, h: "A research direction",    b: "Systematic coverage-bias audit of CHAOSS-aligned metrics. Candidate intervention designs for civic-tech sustainability." },
  ];
  offers.forEach((o, i) => {
    const x = 0.7 + i * 4.2;
    s7.addShape("rect", {
      x: x, y: 2.4, w: 3.95, h: 3.5,
      fill: { color: C.white }, line: { color: C.border, width: 1 },
      shadow: { type: "outer", color: "0F172A", blur: 12, offset: 3, angle: 90, opacity: 0.06 },
    });
    // Circle for icon
    s7.addShape("ellipse", {
      x: x + 0.3, y: 2.65, w: 0.95, h: 0.95,
      fill: { color: "CCFBF1" }, line: { type: "none" },
    });
    s7.addImage({ data: o.ico, x: x + 0.5, y: 2.83, w: 0.55, h: 0.55 });
    s7.addText(o.h, {
      x: x + 0.3, y: 3.8, w: 3.4, h: 0.6,
      fontFace: FONT.header, fontSize: 17, color: C.text, bold: true,
      align: "left", valign: "top", margin: 0,
    });
    s7.addText(o.b, {
      x: x + 0.3, y: 4.45, w: 3.4, h: 1.4,
      fontFace: FONT.body, fontSize: 12, color: C.textMuted,
      align: "left", valign: "top", margin: 0,
    });
  });

  // Bottom ask box
  s7.addShape("rect", {
    x: 0.7, y: 6.25, w: W - 1.4, h: 0.85,
    fill: { color: C.dark }, line: { type: "none" },
  });
  s7.addText([
    { text: "Where I'd love your input:  ", options: { fontFace: FONT.body, fontSize: 13, color: C.tealLight, bold: true } },
    { text: "framing of the bias story · recent (2023–25) OSS-health refs · candidate metrics for the audit · second-coder for IRR", options: { fontFace: FONT.body, fontSize: 13, color: C.white } },
  ], {
    x: 0.95, y: 6.25, w: W - 1.9, h: 0.85,
    align: "left", valign: "middle", margin: 0,
  });

  // ======================================================================
  // Slide 8 — Timeline + closing ask (dark)
  // ======================================================================
  const s8 = pres.addSlide();
  s8.background = { color: C.dark };
  // Decorative stripe
  s8.addShape("rect", {
    x: 0, y: 0, w: W * 0.25, h: 0.07, fill: { color: C.teal }, line: { type: "none" },
  });
  // Page indicator (white)
  s8.addText("08 / 08", {
    x: W - 1.5, y: 0.3, w: 1.2, h: 0.3,
    fontFace: FONT.body, fontSize: 10, color: "94A3B8",
    align: "right", valign: "top", charSpacing: 2, margin: 0,
  });
  s8.addText("WHERE WE ARE", {
    x: W - 4, y: 0.55, w: 3.7, h: 0.3,
    fontFace: FONT.body, fontSize: 9, color: C.tealLight, bold: true,
    align: "right", valign: "top", charSpacing: 4, margin: 0,
  });

  s8.addText("Where we are + what's next", {
    x: 0.7, y: 1.0, w: W - 1.4, h: 0.7,
    fontFace: FONT.header, fontSize: 32, color: C.white, bold: true,
    align: "left", valign: "top", margin: 0,
  });
  s8.addText("ESEM 2026 abstract due May 22 · full submission May 29.", {
    x: 0.7, y: 1.7, w: W - 1.4, h: 0.4,
    fontFace: FONT.body, fontSize: 14, color: "94A3B8", italic: true,
    align: "left", valign: "top", margin: 0,
  });

  // Timeline
  const timelineY = 3.0;
  const timelineX = 0.9;
  const timelineW = W - 1.8;
  // Horizontal line
  s8.addShape("line", {
    x: timelineX, y: timelineY, w: timelineW, h: 0,
    line: { color: "334155", width: 2 },
  });
  const stops = [
    { x: 0.0,   label: "AUTUMN 2025", title: "Pilot phase",         body: "n = 29 crawl. Apparent FDR-significant finding.", color: C.amber },
    { x: 0.33,  label: "SPRING 2026", title: "Triangulation + panel expansion", body: "GraphQL fallback. n = 37 with 37/37 coverage on burstiness.", color: C.emerald },
    { x: 0.66,  label: "MAY 2026",    title: "ESEM submission",     body: "You are here. Feedback welcome.", color: C.tealLight },
    { x: 1.0,   label: "2026 – 2028", title: "L1 · L2 · L3",        body: "Longitudinal · platform replication · coverage-bias audit.", color: "94A3B8" },
  ];
  stops.forEach(s => {
    const cx = timelineX + s.x * timelineW;
    // Dot
    s8.addShape("ellipse", {
      x: cx - 0.12, y: timelineY - 0.12, w: 0.24, h: 0.24,
      fill: { color: s.color }, line: { color: C.dark, width: 2 },
    });
    // Label above
    s8.addText(s.label, {
      x: cx - 1.5, y: timelineY - 0.95, w: 3.0, h: 0.3,
      fontFace: FONT.body, fontSize: 10, color: s.color, bold: true,
      charSpacing: 3, align: "center", valign: "top", margin: 0,
    });
    s8.addText(s.title, {
      x: cx - 1.5, y: timelineY - 0.6, w: 3.0, h: 0.35,
      fontFace: FONT.header, fontSize: 14, color: C.white, bold: true,
      align: "center", valign: "top", margin: 0,
    });
    // Body below
    s8.addText(s.body, {
      x: cx - 1.5, y: timelineY + 0.3, w: 3.0, h: 1.2,
      fontFace: FONT.body, fontSize: 11, color: "CBD5E1",
      align: "center", valign: "top", margin: 0,
    });
  });

  // Closing line
  s8.addText("Thanks — questions, pushback, and replication ideas all very welcome.", {
    x: 0.7, y: 6.4, w: W - 1.4, h: 0.5,
    fontFace: FONT.header, fontSize: 18, color: C.tealLight, italic: true, bold: true,
    align: "center", valign: "middle", margin: 0,
  });

  // ----- write -----
  await pres.writeFile({ fileName: "colleague_briefing.pptx" });
  console.log("Wrote colleague_briefing.pptx");
}

build().catch(e => { console.error(e); process.exit(1); });
