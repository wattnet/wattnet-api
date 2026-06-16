FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir gunicorn uvicorn[standard]

COPY dist/wattnet_api-*.whl .
RUN pip install --no-cache-dir wattnet_api-*.whl \
    && rm -f wattnet_api-*.whl

COPY data /app/data
COPY scripts/docker-entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["entrypoint.sh"]
