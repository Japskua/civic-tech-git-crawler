# syntax=docker/dockerfile:1
FROM python:3.13-slim

LABEL org.opencontainers.image.title="civic-tech-crawler"
LABEL org.opencontainers.image.description="GitHub repository metrics crawler for civic tech research"
LABEL org.opencontainers.image.source="https://github.com/Japskua/civic-tech-git-crawler"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Install dependencies first so source changes don't bust the dep cache.
COPY pyproject.toml README.md LICENSE.txt ./
COPY src ./src
RUN pip install --no-cache-dir .

# Resumable-crawl wrapper, the example config, and the per-snapshot analysis
# scripts are useful inside the image (the wrapper is the recommended way to
# run a long crawl). Copy them after the dependency install so they don't
# invalidate the cache.
COPY scripts ./scripts
COPY config.example.yaml ./

# Mount points: a host config dir at /config, a writable output dir at /output.
RUN mkdir -p /config /output
VOLUME ["/config", "/output"]

ENV PYTHONUNBUFFERED=1

# Default behaviour: run the CLI against /config/config.yaml writing to /output.
# Override CMD to pass extra flags (e.g. --help, --skip-chaoss). Override
# --entrypoint scripts/run_with_respawn.sh to use the auto-respawning wrapper.
ENTRYPOINT ["civic-tech-crawler"]
CMD ["--config", "/config/config.yaml", "--output-dir", "/output"]
