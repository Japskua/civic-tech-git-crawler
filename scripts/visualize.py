"""Generate publication-ready visualizations from crawled civic tech metrics.

Usage:
    uv run python scripts/visualize.py [--output-dir ./output] [--repo OWNER/REPO]
"""

import argparse
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

# Consistent style
plt.style.use("seaborn-v0_8-whitegrid")
COLORS = {
    "primary": "#2563eb",
    "secondary": "#dc2626",
    "tertiary": "#16a34a",
    "active": "#16a34a",
    "departed": "#dc2626",
    "additions": "#2563eb",
    "deletions": "#dc2626",
}
DPI = 150


def _safe_slug(repo: str) -> str:
    """Convert 'owner/repo' to 'owner_repo' for filenames."""
    return repo.replace("/", "_")


def _short_name(repo: str) -> str:
    """Get short repo name for chart titles."""
    return repo.split("/")[-1] if "/" in repo else repo


# ---------------------------------------------------------------------------
# Plot 1: Project Growth (cumulative commits & contributors)
# ---------------------------------------------------------------------------


def plot_project_growth(df: pd.DataFrame, repo: str, out: Path) -> Path | None:
    rdf = df[df["repo_full_name"] == repo].copy()
    if rdf.empty:
        return None

    rdf["week_start"] = pd.to_datetime(rdf["week_start"])
    rdf = rdf.sort_values("week_start")

    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(
        rdf["week_start"], rdf["cumulative_commits"],
        color=COLORS["primary"], linewidth=1.5, label="Cumulative commits",
    )
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Cumulative Commits", color=COLORS["primary"])
    ax1.tick_params(axis="y", labelcolor=COLORS["primary"])

    ax2 = ax1.twinx()
    ax2.plot(
        rdf["week_start"], rdf["cumulative_contributors"],
        color=COLORS["secondary"], linewidth=1.5, label="Cumulative contributors",
    )
    ax2.set_ylabel("Cumulative Contributors", color=COLORS["secondary"])
    ax2.tick_params(axis="y", labelcolor=COLORS["secondary"])

    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.autofmt_xdate()

    fig.suptitle(f"Project Growth — {_short_name(repo)}", fontsize=14, fontweight="bold")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    filepath = out / f"{_safe_slug(repo)}_growth.png"
    fig.savefig(filepath, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return filepath


# ---------------------------------------------------------------------------
# Plot 2: Weekly Commit Activity
# ---------------------------------------------------------------------------


def plot_weekly_activity(df: pd.DataFrame, repo: str, out: Path) -> Path | None:
    rdf = df[df["repo_full_name"] == repo].copy()
    if rdf.empty:
        return None

    rdf["week_start"] = pd.to_datetime(rdf["week_start"])
    rdf = rdf.sort_values("week_start")

    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.bar(
        rdf["week_start"], rdf["total_commits"],
        width=6, color=COLORS["primary"], alpha=0.6, label="Commits",
    )
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Commits per Week", color=COLORS["primary"])
    ax1.tick_params(axis="y", labelcolor=COLORS["primary"])

    ax2 = ax1.twinx()
    ax2.plot(
        rdf["week_start"], rdf["unique_contributors"],
        color=COLORS["secondary"], linewidth=1.2, label="Unique contributors",
    )
    ax2.set_ylabel("Unique Contributors", color=COLORS["secondary"])
    ax2.tick_params(axis="y", labelcolor=COLORS["secondary"])

    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.autofmt_xdate()

    fig.suptitle(
        f"Weekly Commit Activity — {_short_name(repo)}", fontsize=14, fontweight="bold",
    )
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    filepath = out / f"{_safe_slug(repo)}_weekly_activity.png"
    fig.savefig(filepath, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return filepath


# ---------------------------------------------------------------------------
# Plot 3: Contributor Lifecycle Gantt Chart
# ---------------------------------------------------------------------------


def plot_contributor_lifecycle(df: pd.DataFrame, repo: str, out: Path) -> Path | None:
    rdf = df[df["repo_full_name"] == repo].copy()
    if rdf.empty:
        return None

    rdf["first_commit_date"] = pd.to_datetime(rdf["first_commit_date"])
    rdf["last_commit_date"] = pd.to_datetime(rdf["last_commit_date"])

    # Top 30 by total_commits, sorted by first_commit_date
    rdf = rdf.nlargest(30, "total_commits").sort_values("first_commit_date")

    fig, ax = plt.subplots(figsize=(12, max(6, len(rdf) * 0.35)))

    for i, (_, row) in enumerate(rdf.iterrows()):
        color = COLORS["active"] if row["status"] == "active" else COLORS["departed"]
        start = row["first_commit_date"]
        duration = row["last_commit_date"] - start
        ax.barh(
            i, duration.days, left=start,
            color=color, alpha=0.7, height=0.6,
        )

    labels = rdf["contributor_id"].tolist()
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Date")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.autofmt_xdate()

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS["active"], alpha=0.7, label="Active"),
        Patch(facecolor=COLORS["departed"], alpha=0.7, label="Departed"),
    ]
    ax.legend(handles=legend_elements, loc="lower right")

    fig.suptitle(
        f"Contributor Lifecycles (Top 30) — {_short_name(repo)}",
        fontsize=14, fontweight="bold",
    )

    filepath = out / f"{_safe_slug(repo)}_lifecycle.png"
    fig.savefig(filepath, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return filepath


# ---------------------------------------------------------------------------
# Plot 4: New Contributor Rate
# ---------------------------------------------------------------------------


def plot_new_contributor_rate(df: pd.DataFrame, repo: str, out: Path) -> Path | None:
    rdf = df[df["repo_full_name"] == repo].copy()
    if rdf.empty:
        return None

    rdf["week_start"] = pd.to_datetime(rdf["week_start"])
    rdf = rdf.sort_values("week_start")

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(
        rdf["week_start"], rdf["new_contributors"],
        width=6, color=COLORS["tertiary"], alpha=0.6, label="New contributors",
    )

    # Rolling 4-week average
    rolling = rdf["new_contributors"].rolling(4, min_periods=1).mean()
    ax.plot(
        rdf["week_start"], rolling,
        color=COLORS["secondary"], linewidth=2, label="4-week rolling avg",
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("New Contributors per Week")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.autofmt_xdate()
    ax.legend(loc="upper left")

    fig.suptitle(
        f"New Contributor Rate — {_short_name(repo)}", fontsize=14, fontweight="bold",
    )

    filepath = out / f"{_safe_slug(repo)}_new_contributors.png"
    fig.savefig(filepath, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return filepath


# ---------------------------------------------------------------------------
# Plot 5: Issue Open/Close Trends
# ---------------------------------------------------------------------------


def plot_issue_trends(df: pd.DataFrame, repo: str, out: Path) -> Path | None:
    rdf = df[df["repo_full_name"] == repo].copy()
    if rdf.empty:
        return None

    rdf["created_at"] = pd.to_datetime(rdf["created_at"], utc=True).dt.tz_localize(None)
    rdf["closed_at"] = pd.to_datetime(rdf["closed_at"], utc=True).dt.tz_localize(None)

    # Group by month
    rdf["created_month"] = rdf["created_at"].dt.to_period("M")
    opened_per_month = rdf.groupby("created_month").size()

    closed = rdf.dropna(subset=["closed_at"]).copy()
    closed["closed_month"] = closed["closed_at"].dt.to_period("M")
    closed_per_month = closed.groupby("closed_month").size()

    # Align on same index
    all_months = opened_per_month.index.union(closed_per_month.index).sort_values()
    opened_per_month = opened_per_month.reindex(all_months, fill_value=0)
    closed_per_month = closed_per_month.reindex(all_months, fill_value=0)

    # Cumulative open = cumulative opened - cumulative closed
    cum_open = (opened_per_month.cumsum() - closed_per_month.cumsum())

    dates = all_months.to_timestamp()

    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(dates, opened_per_month.values, color=COLORS["secondary"],
             linewidth=1.2, label="Opened / month")
    ax1.plot(dates, closed_per_month.values, color=COLORS["tertiary"],
             linewidth=1.2, label="Closed / month")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Issues per Month")
    ax1.legend(loc="upper left")

    ax2 = ax1.twinx()
    ax2.fill_between(dates, cum_open.values, alpha=0.15, color=COLORS["primary"])
    ax2.plot(dates, cum_open.values, color=COLORS["primary"],
             linewidth=1, linestyle="--", label="Cumulative open")
    ax2.set_ylabel("Cumulative Open Issues", color=COLORS["primary"])
    ax2.tick_params(axis="y", labelcolor=COLORS["primary"])
    ax2.legend(loc="upper right")

    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.autofmt_xdate()

    fig.suptitle(
        f"Issue Trends — {_short_name(repo)}", fontsize=14, fontweight="bold",
    )

    filepath = out / f"{_safe_slug(repo)}_issue_trends.png"
    fig.savefig(filepath, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return filepath


# ---------------------------------------------------------------------------
# Plot 6: Top Contributors Bar Chart
# ---------------------------------------------------------------------------


def plot_top_contributors(df: pd.DataFrame, repo: str, out: Path) -> Path | None:
    rdf = df[df["repo_full_name"] == repo].copy()
    if rdf.empty:
        return None

    rdf = rdf.nlargest(15, "num_commits").sort_values("num_commits")

    labels = rdf.apply(
        lambda r: (
            str(r["login"]) if pd.notna(r.get("login")) and r["login"]
            else str(r["name"]) if pd.notna(r.get("name")) and r["name"]
            else "unknown"
        ),
        axis=1,
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.barh(labels, rdf["additions"], color=COLORS["additions"], alpha=0.8, label="Additions")
    ax.barh(labels, -rdf["deletions"], color=COLORS["deletions"], alpha=0.8, label="Deletions")

    ax.set_xlabel("Lines of Code")
    ax.legend(loc="lower right")
    ax.axvline(0, color="black", linewidth=0.5)

    # Add commit count annotations
    for i, (_, row) in enumerate(rdf.iterrows()):
        ax.annotate(
            f"  {int(row['num_commits'])} commits",
            xy=(max(row["additions"], 0), i),
            va="center", fontsize=8, color="gray",
        )

    fig.suptitle(
        f"Top 15 Contributors — {_short_name(repo)}", fontsize=14, fontweight="bold",
    )

    filepath = out / f"{_safe_slug(repo)}_top_contributors.png"
    fig.savefig(filepath, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return filepath


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate visualizations from crawled civic tech metrics",
    )
    parser.add_argument(
        "--output-dir", default="./output",
        help="Directory containing CSV files (default: ./output)",
    )
    parser.add_argument(
        "--repo", default=None,
        help="Generate plots for a single repo (e.g., owner/repo)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    plots_dir = output_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Load CSVs
    csv_files = {
        "weekly_snapshots": output_dir / "weekly_snapshots.csv",
        "contributor_lifecycles": output_dir / "contributor_lifecycles.csv",
        "issue_records": output_dir / "issue_records.csv",
        "person_metrics": output_dir / "person_metrics.csv",
    }

    dfs: dict[str, pd.DataFrame] = {}
    for name, path in csv_files.items():
        if path.exists():
            dfs[name] = pd.read_csv(path)
            print(f"  Loaded {name}.csv ({len(dfs[name])} rows)")
        else:
            print(f"  Warning: {path.name} not found, skipping related plots")

    # Determine repos to plot
    if args.repo:
        repos = [args.repo]
    else:
        # Get unique repos from whichever CSV has data
        repo_sets = [set(df["repo_full_name"].unique()) for df in dfs.values() if len(df) > 0]
        repos = sorted(set().union(*repo_sets)) if repo_sets else []

    if not repos:
        print("No repositories found in CSV data.")
        return

    print(f"\nGenerating plots for {len(repos)} repositories...")

    generated = 0
    for repo in repos:
        print(f"\n  {repo}:")

        plot_funcs = [
            ("weekly_snapshots", plot_project_growth, "growth"),
            ("weekly_snapshots", plot_weekly_activity, "weekly activity"),
            ("contributor_lifecycles", plot_contributor_lifecycle, "lifecycle"),
            ("weekly_snapshots", plot_new_contributor_rate, "new contributors"),
            ("issue_records", plot_issue_trends, "issue trends"),
            ("person_metrics", plot_top_contributors, "top contributors"),
        ]

        for csv_name, func, label in plot_funcs:
            if csv_name in dfs:
                result = func(dfs[csv_name], repo, plots_dir)
                if result:
                    print(f"    {label}: {result.name}")
                    generated += 1
                else:
                    print(f"    {label}: no data")

    print(f"\nDone! Generated {generated} plots in {plots_dir}/")


if __name__ == "__main__":
    main()
