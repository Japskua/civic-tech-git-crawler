import logging

from github import Repository
from github.GithubException import GithubException

from civic_tech_crawler.client import GitHubClient
from civic_tech_crawler.models import RepoMetrics

logger = logging.getLogger(__name__)

DEFAULT_CLOUD_KEYWORDS: dict = {
    "topics": [
        "aws", "gcp", "azure", "cloud", "serverless", "kubernetes", "docker",
    ],
    "languages": ["HCL", "Dockerfile"],
    "files": [
        "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
        "cdk.json", "serverless.yml", "terraform.tf", "cloudbuild.yaml",
        "appspec.yml", "Procfile", ".buildpacks",
    ],
    "dependencies": [
        "boto3", "google-cloud", "azure", "aws-cdk", "pulumi",
    ],
}

DEFAULT_AI_ML_KEYWORDS: dict = {
    "topics": [
        "machine-learning", "deep-learning", "ai", "nlp",
        "computer-vision", "artificial-intelligence",
    ],
    "languages": ["Jupyter Notebook"],
    "files": [],
    "dependencies": [
        "tensorflow", "pytorch", "torch", "scikit-learn", "transformers",
        "keras", "xgboost", "lightgbm", "openai", "langchain",
        "huggingface", "spacy", "nltk",
    ],
}


def _extract_dependencies(client: GitHubClient, slug: str) -> list[str]:
    """Extract dependency names from common dependency files."""
    deps: list[str] = []

    # requirements.txt
    content = client.get_file_content(slug, "requirements.txt")
    if content:
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                # Parse "package>=1.0" -> "package"
                name = line.split(">=")[0].split("<=")[0].split("==")[0].split("~=")[0]
                name = name.split("[")[0].strip()
                if name:
                    deps.append(name.lower())

    # pyproject.toml dependencies
    content = client.get_file_content(slug, "pyproject.toml")
    if content:
        import tomllib

        try:
            data = tomllib.loads(content)
            for dep in data.get("project", {}).get("dependencies", []):
                name = dep.split(">=")[0].split("<=")[0].split("==")[0].split("~=")[0]
                name = name.split("[")[0].strip()
                if name:
                    deps.append(name.lower())
        except Exception:
            pass

    # package.json
    content = client.get_file_content(slug, "package.json")
    if content:
        import json

        try:
            data = json.loads(content)
            for section in ("dependencies", "devDependencies"):
                for dep_name in data.get(section, {}):
                    deps.append(dep_name.lower())
        except Exception:
            pass

    return deps


def _detect_signals(
    repo: Repository.Repository,
    client: GitHubClient,
    keywords: dict,
    root_files: list[str],
    deps: list[str],
    languages: dict[str, int],
) -> list[str]:
    """Check multi-signal detection against keyword config."""
    signals: list[str] = []
    try:
        topics = [t.lower() for t in repo.get_topics()]
    except GithubException as exc:
        logger.warning("get_topics failed for %s, skipping topic signals: %s", repo.full_name, exc)
        topics = []

    # Check topics
    for kw in keywords.get("topics", []):
        if kw.lower() in topics:
            signals.append(f"topic:{kw}")

    # Check languages
    for kw in keywords.get("languages", []):
        if kw in languages:
            signals.append(f"language:{kw}")

    # Check root files
    for kw in keywords.get("files", []):
        if kw.startswith("*."):
            ext = kw[1:]
            if any(f.endswith(ext) for f in root_files):
                signals.append(f"file:{kw}")
        elif kw in root_files:
            signals.append(f"file:{kw}")

    # Check dependencies
    for kw in keywords.get("dependencies", []):
        kw_lower = kw.lower()
        if any(kw_lower in dep for dep in deps):
            signals.append(f"dependency:{kw}")

    return signals


def run_detection(
    client: GitHubClient,
    repo: Repository.Repository,
    repo_metrics: RepoMetrics,
    cloud_keywords: dict | None = None,
    ai_ml_keywords: dict | None = None,
) -> None:
    """Run cloud and AI/ML detection, updating repo_metrics in-place."""
    slug = repo.full_name
    logger.info("Running detection for %s", slug)

    cloud_kw = cloud_keywords or DEFAULT_CLOUD_KEYWORDS
    ai_ml_kw = ai_ml_keywords or DEFAULT_AI_ML_KEYWORDS

    # Shared data fetches
    root_files = client.get_repo_contents_names(slug)
    deps = _extract_dependencies(client, slug)

    cloud_signals = _detect_signals(
        repo, client, cloud_kw, root_files, deps, repo_metrics.languages
    )
    ai_ml_signals = _detect_signals(
        repo, client, ai_ml_kw, root_files, deps, repo_metrics.languages
    )

    repo_metrics.cloud_detected = len(cloud_signals) > 0
    repo_metrics.cloud_signals = cloud_signals
    repo_metrics.ai_ml_detected = len(ai_ml_signals) > 0
    repo_metrics.ai_ml_signals = ai_ml_signals

    logger.info(
        "%s: cloud=%s (%d signals), ai_ml=%s (%d signals)",
        slug,
        repo_metrics.cloud_detected,
        len(cloud_signals),
        repo_metrics.ai_ml_detected,
        len(ai_ml_signals),
    )
