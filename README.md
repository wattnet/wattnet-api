<div align="left">
  <picture>
    <source media="(prefers-color-scheme: dark)"
            srcset="https://github.com/wattnet/.github/raw/main/images/wattnet-logo-full-dark-transparent-cropped.png" />
    <source media="(prefers-color-scheme: light)"
            srcset="https://github.com/wattnet/.github/raw/main/images/wattnet-logo-full-light-transparent-cropped.png" />
    <img src="https://github.com/wattnet/.github/raw/main/images/wattnet-logo-full-light-transparent-cropped.png"
         alt="Wattnet Logo"
         width="300" />
  </picture>
</div>

# RESTful API

[![CI](https://github.com/wattnet/wattnet-api/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/wattnet/wattnet-api/actions/workflows/ci.yml)
[![Publish](https://github.com/wattnet/wattnet-api/actions/workflows/publish.yml/badge.svg)](https://github.com/wattnet/wattnet-api/actions/workflows/publish.yml)
[![Release Please](https://github.com/wattnet/wattnet-api/actions/workflows/release-please.yml/badge.svg?branch=main)](https://github.com/wattnet/wattnet-api/actions/workflows/release-please.yml)
[![codecov](https://codecov.io/gh/wattnet/wattnet-api/graph/badge.svg)](https://codecov.io/gh/wattnet/wattnet-api)
[![GitHub stars](https://img.shields.io/github/stars/wattnet/wattnet-api?style=social)](https://github.com/wattnet/wattnet-api/stargazers)
[![PyPI version](https://img.shields.io/pypi/v/wattnet-api)](https://pypi.org/project/wattnet-api/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/wattnet-api?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/wattnet-api)
[![Python](https://img.shields.io/pypi/pyversions/wattnet-api)](https://pypi.org/project/wattnet-api/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121.1-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![OpenAPI 3.1](https://img.shields.io/badge/OpenAPI-3.1-6BA539?logo=openapiinitiative&logoColor=white)](https://www.openapis.org/)
[![Docker Hub](https://img.shields.io/docker/v/wattnet/wattnet-api?sort=semver&logo=docker&label=Docker%20Hub&color=2496ED)](https://hub.docker.com/r/wattnet/wattnet-api)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

`wattnet-api` is the public-facing HTTP interface for the Wattnet platform. It exposes real-time, historical, and forecasted data on the carbon and water footprint of electricity consumption across Europe, fully documented with OpenAPI 3.1 and deployable as a Docker container.

## Purpose

Wattnet computes environmental metrics — carbon footprint, water impact, green scores, generation mix — from open electricity market data. `wattnet-api` makes all of these metrics available over HTTP so that dashboards, research tools, and third-party applications can query them without coupling to Wattnet's internal data pipeline.

The API is organized into five groups of endpoints:

| Group                     | Prefix                                                                       | Description                                                 |
| ------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **Zones**                 | `/v1/zones`                                                                  | Metadata and boundaries for supported electricity zones     |
| **Energy Metrics**        | `/v1/generation`, `/v1/load`, `/v1/imports`, `/v1/exports`, `/v1/mix`        | Electricity generation, consumption, and cross-border flows |
| **Environmental Metrics** | `/v1/footprints`, `/v1/impacts`, `/v1/green-score`                           | Carbon and water footprint, carbon impact, and green score  |
| **Shares Metrics**        | `/v1/flow-share`, `/v1/mix-share`, `/v1/footprint-share`, `/v1/impact-share` | Fractional attribution of flows, mix, footprint, and impact |
| **Factors**               | `/v1/factors`                                                                | Emission and consumption factors used in calculations       |

## Architecture

![API component diagram](https://github.com/wattnet/wattnet-architecture/blob/main/diagrams/png/structurizr-1-wattnet_api.png?raw=true)

For the full system architecture see the [wattnet-architecture](https://github.com/wattnet/wattnet-architecture) repository.

`wattnet-api` is a [FastAPI](https://fastapi.tiangolo.com/) application served by [Uvicorn](https://www.uvicorn.org/). It reads energy metrics from `wattnet-storage` and zone/GeoJSON data from `wattnet-data`. The API is versioned; all current endpoints live under `/v1`.

## Requirements

- Python ≥ 3.10
- Docker (for containerised deployment)
- A running [wattnet-storage](https://github.com/wattnet/wattnet-storage) backend

## Installation

### From PyPI

Installs the `wattnet-api` server and its `wattnet-api` CLI entrypoint:

```bash
pip install wattnet-api
```

### From source

```bash
git clone --recurse-submodules https://github.com/wattnet/wattnet-api.git
cd wattnet-api
poetry install
```

### Docker

Pre-built images are published to [GHCR](https://github.com/wattnet/wattnet-api/pkgs/container/wattnet-api) and [DockerHub](https://hub.docker.com/r/wattnet/wattnet-api) for `linux/amd64` and `linux/arm64`. Images are tagged by full version, minor, major, and `latest`.

```bash
# Pull from GHCR
docker pull ghcr.io/wattnet/wattnet-api:latest

# Or from DockerHub
docker pull wattnet/wattnet-api:latest
```

Run the container:

```bash
docker run -p 8000:8000 --env-file config/.env.production ghcr.io/wattnet/wattnet-api:latest
```

## Configuration

The server reads settings from environment variables or a `.env` file. Copy the example and adjust as needed:

```bash
cp config/.env.example config/.env.development
```

| Variable                 | Default                                                 | Description                                             |
| ------------------------ | ------------------------------------------------------- | ------------------------------------------------------- |
| `WATTNET_ENV`            | `development`                                           | Active environment; selects `config/.env.<WATTNET_ENV>` |
| `API_HOST`               | `localhost`                                             | Bind address for the Uvicorn server                     |
| `API_PORT`               | `8000`                                                  | Listening port                                          |
| `API_DEBUG`              | `True`                                                  | Enable debug mode and verbose logging                   |
| `GEOJSON_PATH`           | _(bundled wattnet-data)_                                | Directory with GeoJSON zone boundary files              |
| `ZONES_FILE_PATH`        | _(bundled wattnet-data)_                                | Path to the zones YAML file                             |
| `CROSSBORDERS_FILE_PATH` | _(bundled wattnet-data)_                                | Path to the crossborders YAML file                      |
| `LOG_LEVEL`              | `INFO`                                                  | Logging level (`DEBUG`, `INFO`, `WARNING`, …)           |
| `LOG_HANDLERS`           | `["console"]`                                           | Log outputs: `"console"` and/or `"file"`                |
| `LOG_FILE`               | `./logs/wattnet-api.log`                                | Log file path (only used when `file` handler is active) |
| `STORAGE_DB_URL`         | `http://localhost:8123`                                 | URL for the wattnet-storage ClickHouse backend          |
| `ENTSOE_URL`             | `https://web-api.tp.entsoe.eu/api`                      | ENTSO-E Transparency Platform API endpoint              |
| `ELEXON_URL`             | `https://data.elexon.co.uk/bmrs/api/v1`                 | ELEXON Balancing Mechanism Reporting Service endpoint   |
| `EPIAS_URL`              | `https://seffaflik.epias.com.tr/electricity-service/v1` | EPIAS Electricity Market Transparency Platform endpoint |

## Running the API

### With Poetry

```bash
wattnet-api
```

Or directly with Uvicorn:

```bash
uvicorn wattnet.api.app:versioned_app --host 0.0.0.0 --port 8000 --reload
```

### With Docker Compose

```bash
docker compose up -d
```

## Interactive API Documentation

Once the server is running, explore endpoints, parameters, and responses interactively:

| Interface    | URL                                                                            |
| ------------ | ------------------------------------------------------------------------------ |
| Swagger UI   | [http://localhost:8000/v1/docs](http://localhost:8000/v1/docs)                 |
| ReDoc        | [http://localhost:8000/v1/redoc](http://localhost:8000/v1/redoc)               |
| OpenAPI JSON | [http://localhost:8000/v1/openapi.json](http://localhost:8000/v1/openapi.json) |

The production instance is available at **[https://api.wattnet.eu/docs](https://api.wattnet.eu/docs)**.

> The API is versioned. The current version is `v1`; the base URL is `https://api.wattnet.eu/v1/`.

### Health check

The `/v1/status` endpoint reports whether the API and its upstream dependencies (wattnet-storage, ENTSO-E, ELEXON, EPIAS) are reachable. Useful for readiness probes in containerised deployments:

```bash
curl http://localhost:8000/v1/status
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for environment setup, code style, and how to run the tests.

## License

This repository is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

See the [LICENSE](LICENSE) file for more details.

## Funding and Acknowledgments

This work is funded by the European Union's Horizon Europe research and innovation programme through the **[GreenDIGIT](https://greendigit-project.eu/)** project, under grant agreement **[101131207](https://cordis.europa.eu/project/id/101131207)**.

<div align="left">
  <img src="https://github.com/wattnet/.github/raw/main/images/EN_FundedbytheEU_RGB_POS.png" alt="EU Funded Logo" width="260"/>
  <img src="https://github.com/wattnet/.github/raw/main/images/GreenDIGIT%20logo%20color%20horizontal2.png" alt="GreenDIGIT Logo" width="230"/>
</div>

##### © 2026 Spanish National Research Council (CSIC). All rights reserved.
