import argparse
import logging
import sys
from datetime import datetime, timezone

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from civic_tech_crawler.cache import (
    is_cached,
    load_all_cached,
    load_repo_cache,
    save_repo_cache,
)
from civic_tech_crawler.client import GitHubClient
from civic_tech_crawler.collectors.chaoss_metrics import collect_chaoss_metrics
from civic_tech_crawler.collectors.detection import run_detection
from civic_tech_crawler.collectors.person_metrics import collect_person_metrics
from civic_tech_crawler.collectors.repo_metrics import collect_repo_metrics
from civic_tech_crawler.collectors.temporal_metrics import collect_temporal_metrics
from civic_tech_crawler.config import load_config
from civic_tech_crawler.exporters.csv_exporter import export_csv
from civic_tech_crawler.exporters.json_exporter import export_json
from civic_tech_crawler.models import RepositoryData

console = Console(stderr=True)
logger = logging.getLogger("civic_tech_crawler")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="civic-tech-crawler",
        description="GitHub repository metrics crawler for civic tech research",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to YAML configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="GitHub personal access token (overrides GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--repos",
        default=None,
        help="Comma-separated list of repos (e.g., owner/repo1,owner/repo2)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: ./output)",
    )
    parser.add_argument("--skip-chaoss", action="store_true", help="Skip CHAOSS metrics")
    parser.add_argument(
        "--skip-temporal", action="store_true", help="Skip temporal metrics (PRs, tags)"
    )
    parser.add_argument(
        "--skip-detection", action="store_true", help="Skip cloud/AI-ML detection"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-crawl all repos even if cached data exists",
    )
    parser.add_argument(
        "--export-only",
        action="store_true",
        help="Skip crawling; regenerate CSV/JSON from cached per-repo data",
    )
    return parser.parse_args()


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, show_time=True, show_path=False)],
    )


def crawl_repository(
    client: GitHubClient,
    slug: str,
    config,
    progress: Progress,
    task_id,
) -> RepositoryData:
    """Crawl a single repository and collect all metrics."""
    repo = client.get_repo(slug)

    # Step 1: Repo metrics
    progress.update(task_id, description=f"[bold blue]{slug}[/] - repo metrics")
    repo_metrics = collect_repo_metrics(client, repo)

    # Step 2: Person metrics
    progress.update(task_id, description=f"[bold blue]{slug}[/] - person metrics")
    person_metrics = collect_person_metrics(client, repo)

    # Step 3: Detection (cloud/AI/ML)
    temporal_metrics = None
    if not config.skip_detection:
        progress.update(task_id, description=f"[bold blue]{slug}[/] - detection")
        run_detection(
            client,
            repo,
            repo_metrics,
            cloud_keywords=config.cloud_keywords or None,
            ai_ml_keywords=config.ai_ml_keywords or None,
        )

    # Step 4: Temporal metrics (PRs, tags, releases)
    if not config.skip_temporal:
        progress.update(task_id, description=f"[bold blue]{slug}[/] - temporal metrics")
        temporal_metrics = collect_temporal_metrics(client, repo)

    # Step 5: CHAOSS metrics
    chaoss_metrics = None
    if not config.skip_chaoss:
        progress.update(task_id, description=f"[bold blue]{slug}[/] - CHAOSS metrics")
        chaoss_metrics = collect_chaoss_metrics(
            client,
            repo,
            person_metrics,
            temporal_metrics,
        )

    return RepositoryData(
        repo_metrics=repo_metrics,
        person_metrics=person_metrics,
        temporal_metrics=temporal_metrics,
        chaoss_metrics=chaoss_metrics,
        crawled_at=datetime.now(timezone.utc),
    )


def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)

    try:
        repos_override = args.repos.split(",") if args.repos else None
        config = load_config(
            config_path=args.config,
            token_override=args.token,
            repos_override=repos_override,
            output_dir_override=args.output_dir,
            skip_chaoss=args.skip_chaoss,
            skip_temporal=args.skip_temporal,
            skip_detection=args.skip_detection,
        )
    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        sys.exit(1)

    output_dir = config.output_dir

    # --export-only mode: rebuild CSV/JSON from existing cache, no crawling
    if args.export_only:
        console.print("[bold green]Civic Tech Git Crawler[/bold green] - export-only mode")
        all_data = load_all_cached(output_dir)
        if not all_data:
            console.print("[red]No cached data found in[/red] " + output_dir)
            sys.exit(1)
        console.print(f"  Loaded {len(all_data)} repositories from cache")
        export_csv(all_data, output_dir)
        export_json(all_data, output_dir)
        console.print(
            f"\n[bold green]Done![/bold green] Exported {len(all_data)} repositories "
            f"to {output_dir}/"
        )
        return

    # Normal crawl mode
    client = GitHubClient(
        token=config.token,
        max_retries=config.max_retries,
        retry_delay=config.retry_delay,
        rate_limit_buffer=config.rate_limit_buffer,
    )

    console.print(
        f"[bold green]Civic Tech Git Crawler[/bold green] - "
        f"crawling {len(config.repositories)} repositories"
    )
    console.print(f"Rate limit remaining: {client.rate_limit_remaining}")

    all_data: list[RepositoryData] = []
    crawled_count = 0
    cached_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        overall = progress.add_task(
            "[bold]Crawling repositories...", total=len(config.repositories)
        )
        for slug in config.repositories:
            # Check cache first (unless --force)
            if not args.force and is_cached(slug, output_dir):
                cached_data = load_repo_cache(slug, output_dir)
                if cached_data is not None:
                    progress.update(
                        overall,
                        description=f"[dim]{slug}[/dim] - loaded from cache",
                    )
                    all_data.append(cached_data)
                    cached_count += 1
                    progress.advance(overall)
                    continue
                # Cache file was corrupt — fall through to re-crawl

            try:
                repo_data = crawl_repository(client, slug, config, progress, overall)
                # Persist immediately (crash protection)
                save_repo_cache(repo_data, output_dir)
                all_data.append(repo_data)
                crawled_count += 1
            except Exception as e:
                logger.error("Failed to crawl %s: %s", slug, e)
                if args.verbose:
                    logger.exception("Full traceback:")
            progress.advance(overall)

    # Export results (from all data: cached + freshly crawled)
    console.print("\n[bold]Exporting results...[/bold]")
    export_csv(all_data, output_dir)
    export_json(all_data, output_dir)

    # Summary
    console.print(f"\n[bold green]Done![/bold green] Results written to {output_dir}/")
    console.print(
        f"  Repositories: {len(all_data)} total "
        f"({crawled_count} crawled, {cached_count} from cache)"
    )
    if len(all_data) < len(config.repositories):
        failed = len(config.repositories) - len(all_data)
        console.print(f"  [red]Failed: {failed}[/red]")
    total_contributors = sum(len(rd.person_metrics) for rd in all_data)
    console.print(f"  Total contributors: {total_contributors}")
    console.print(f"  Rate limit remaining: {client.rate_limit_remaining}")

    client.close()
