FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir gunicorn uvicorn[standard]

COPY dist/wattnet_api-*.whl .
# git is only needed while wattnet-storage comes from a git address (pyproject.toml); when it is a released version again, this is the plain pip install.
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && pip install --no-cache-dir wattnet_api-*.whl \
    && rm -f wattnet_api-*.whl \
    && apt-get purge -y --auto-remove git \
    && rm -rf /var/lib/apt/lists/*

COPY data /app/data
COPY scripts/docker-entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["entrypoint.sh"]
