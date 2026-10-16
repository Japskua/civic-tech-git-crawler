"""Render Fig. 1 — civic-tech-crawler architecture diagram for the MSR 2027 paper.

Output: fig1_architecture.pdf (vector, for the camera-ready) and fig1_architecture.png
(raster preview). Run from the repository root:

    uv run python msr_2027/figures/fig1_architecture.py

Sized for a single IEEE two-column width (~3.5 in / 88 mm). Nothing in the diagram
depends on live data; the architecture is read directly from the module layout
under src/civic_tech_crawler/collectors/.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT_DIR = Path(__file__).parent

# Colour palette — print-friendly, colour-blind safe, neutral enough for IEEE.
COLORS = {
    "entry": "#e8e8e8",
    "orchestrator": "#cfe2f3",
    "collector": "#d9ead3",
    "collector_new": "#fff2cc",
    "cache": "#f4cccc",
    "exporter": "#d9d2e9",
    "text": "#111111",
    "edge": "#555555",
}

BOX_LW = 1.0
ARROW_LW = 1.1


def box(ax, xy, size, label, fill, fontsize=8, bold=False) -> None:
    x, y = xy
    w, h = size
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=BOX_LW,
        edgecolor=COLORS["edge"],
        facecolor=fill,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h / 2,
        label,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=COLORS["text"],
        fontweight="bold" if bold else "normal",
    )


def arrow(ax, start, end) -> None:
    a = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=9,
        linewidth=ARROW_LW,
        color=COLORS["edge"],
        shrinkA=2,
        shrinkB=2,
    )
    ax.add_patch(a)


def main() -> None:
    # Figure sized for a single IEEE column (~3.5 in wide, slightly taller).
    fig, ax = plt.subplots(figsize=(3.5, 4.4), dpi=200)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 13)
    ax.set_aspect("equal")
    ax.axis("off")

    # ---- Row 1: inputs
    box(ax, (0.5, 11.6), (4.5, 1.0), "config.yaml\n(repo list + options)",
        COLORS["entry"], fontsize=7.5)
    box(ax, (7.0, 11.6), (4.5, 1.0), "GITHUB_TOKEN\n(env / --token / gh)",
        COLORS["entry"], fontsize=7.5)

    # ---- Row 2: orchestrator
    box(ax, (1.5, 10.0), (9.0, 1.0),
        "CLI / orchestrator  —  civic-tech-crawler",
        COLORS["orchestrator"], fontsize=8.5, bold=True)
    arrow(ax, (2.75, 11.6), (3.5, 11.0))
    arrow(ax, (9.25, 11.6), (8.5, 11.0))

    # ---- Rows 3-4: eight collectors (4 x 2), two-line labels so text fits.
    collectors = [
        ("repo\nmetrics", False),
        ("person\nmetrics", False),
        ("temporal\nmetrics", False),
        ("commit\nhistory", False),
        ("chaoss\nmetrics", False),
        ("issue\nanalytics", False),
        ("detection\n(cloud/ML)", False),
        ("ai_usage\n*new*", True),
    ]
    col_w, col_h = 2.4, 1.1
    col_x0, col_y0 = 0.6, 6.9
    col_dx, col_dy = 2.65, 1.3

    for i, (name, is_new) in enumerate(collectors):
        row = i // 4
        col = i % 4
        x = col_x0 + col * col_dx
        y = col_y0 + (1 - row) * col_dy
        fill = COLORS["collector_new"] if is_new else COLORS["collector"]
        box(ax, (x, y), (col_w, col_h), name, fill, fontsize=7.5,
            bold=is_new)

    # Single bus arrow from orchestrator to the collector grid.
    arrow(ax, (6.0, 10.0), (6.0, 9.3))

    # ---- Row 5: per-repo cache
    box(ax, (0.6, 5.1), (10.8, 1.0),
        "per-repo cache  —  crash recovery, incremental, --export-only",
        COLORS["cache"], fontsize=7.5)
    arrow(ax, (6.0, 6.9), (6.0, 6.1))

    # ---- Row 6: exporters
    box(ax, (0.6, 2.7), (5.1, 1.8),
        "CSV exporter\nrepo · person · chaoss\ntemporal · weekly · issues\n+ ai_usage",
        COLORS["exporter"], fontsize=6.8)
    box(ax, (6.3, 2.7), (5.1, 1.8),
        "JSON exporter\nfull_results.json\n(hierarchical,\nall fields nested)",
        COLORS["exporter"], fontsize=6.8)
    arrow(ax, (4.0, 5.1), (3.2, 4.5))
    arrow(ax, (8.0, 5.1), (8.8, 4.5))

    # ---- Row 7: output directory
    box(ax, (0.6, 0.6), (10.8, 1.4),
        "./output/\nhost-mounted via Docker:  -v $PWD/output:/output",
        COLORS["entry"], fontsize=7.5)
    arrow(ax, (3.2, 2.7), (4.5, 2.0))
    arrow(ax, (8.8, 2.7), (7.5, 2.0))

    plt.tight_layout(pad=0.1)

    pdf_out = OUT_DIR / "fig1_architecture.pdf"
    png_out = OUT_DIR / "fig1_architecture.png"
    fig.savefig(pdf_out, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(png_out, bbox_inches="tight", pad_inches=0.02, dpi=220)
    print(f"wrote {pdf_out.relative_to(Path.cwd())}")
    print(f"wrote {png_out.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
