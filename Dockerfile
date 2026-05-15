# syntax=docker/dockerfile:1
FROM python:3.13-slim

LABEL org.opencontainers.image.title="civic-tech-crawler"
LABEL org.opencontainers.image.description="GitHub repository metrics crawler for civic tech research"
LABEL org.opencontainers.image.source="https://github.com/Japskua/civic-tech-git-crawler"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

COPY pyproject.toml README.md LICENSE.txt ./
COPY src ./src

RUN pip install --no-cache-dir .

RUN mkdir -p /config /output
VOLUME ["/config", "/output"]

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["civic-tech-crawler", "--config", "/config/config.yaml", "--output-dir", "/output"]
CMD []
