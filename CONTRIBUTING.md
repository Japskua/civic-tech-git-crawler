# Contributing to civic-tech-crawler

Thank you for your interest in contributing. This project collects repository-health metrics from GitHub for civic-technology research, and we welcome contributions from researchers, practitioners, and open-source maintainers.

## How to contribute

### Reporting issues

If you encounter a bug, have a question, or want to propose a new metric or feature, please open an issue on the [issue tracker](https://github.com/Japskua/civic-tech-git-crawler/issues). When reporting a bug, please include:

- The exact command you ran
- The relevant section of your `config.yaml` (with any tokens redacted)
- The error message or unexpected output
- Your Python version and operating system

### Proposing changes

1. Fork the repository and create a feature branch from `master`.
2. Make your changes, keeping commits focused and well-described.
3. Add or update tests where applicable.
4. Run `ruff check` and `pytest` locally before opening a pull request.
5. Open a pull request describing what your change does and why.

For non-trivial changes (new metrics, structural refactors, new data sources), please open an issue to discuss the approach before investing significant effort.

## Development setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency and environment management.

```bash
git clone https://github.com/Japskua/civic-tech-git-crawler
cd civic-tech-git-crawler
uv sync
GITHUB_TOKEN=$(gh auth token) uv run civic-tech-crawler --config config.example.yaml
```

## Code style

- Python 3.13+
- `ruff` is used for linting and formatting (line length 100, see `pyproject.toml`)
- Run `uv run ruff check` before committing

## Tests

Tests live in `tests/` and are run with `pytest`:

```bash
uv run pytest
```

## License

By contributing to this project, you agree that your contributions will be licensed under the [MIT License](LICENSE.txt).
