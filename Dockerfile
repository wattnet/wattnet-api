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

# Not root: the files above are only read. The id is fixed so that a deployment can ask for it (runAsUser).
RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin wattnet
USER 10001

# The commit of a snapshot, which the documentation shows as the version (a release leaves it empty and shows the version of the package).
ARG BUILD_COMMIT=""
ENV BUILD_COMMIT=$BUILD_COMMIT

EXPOSE 8000

ENTRYPOINT ["entrypoint.sh"]
