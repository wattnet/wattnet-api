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

| Category      | Links                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Documentation | [![API docs](https://img.shields.io/badge/API%20docs-api.wattnet.eu-2E63C2?logo=swagger&logoColor=white&labelColor=1E293B)](https://api.wattnet.eu/v1/docs) [![OpenAPI 3.1](https://img.shields.io/badge/OpenAPI-3.1-2E63C2?logo=openapiinitiative&logoColor=white&labelColor=1E293B)](https://api.wattnet.eu/v1/openapi.json)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Stack         | [![FastAPI](https://img.shields.io/badge/FastAPI-475569?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) [![Pydantic](https://img.shields.io/badge/Pydantic-475569?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Repository    | [![Contributors](https://img.shields.io/github/contributors/wattnet/wattnet-api?label=Contributors&color=1E293B&logo=github&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-api/graphs/contributors) [![Stars](https://img.shields.io/github/stars/wattnet/wattnet-api?style=flat&label=Stars&color=1E293B&logo=github&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-api/stargazers)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Testing & CI  | [![CI](https://img.shields.io/github/actions/workflow/status/wattnet/wattnet-api/ci.yml?branch=main&label=CI&logo=githubactions&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-api/actions/workflows/ci.yml) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-0F766E?logo=pre-commit&logoColor=white&labelColor=1E293B)](https://github.com/pre-commit/pre-commit)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   [![Ruff lint](https://img.shields.io/badge/Lint-Ruff-0F766E?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MTAgNjIyIj48cGF0aCBmaWxsPSIjZmZmIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMDcgMEwxOTYgMTBWNDFMMTg2IDUySDE1N0wxNDYgNjJWMTQ1TDEzNiAxNTZIMTA3TDk3IDE2NlYyMjNMODYgMjMzSDU3TDQ3IDI0NFYzMDFMMzYgMzExSDEwTDAgMzIxVjM1MkwxMCAzNjNIMTQ1TDE1NiAzNzNWNDMwTDE0NSA0NDFIMTE2TDEwNiA0NTFWNTA4TDk2IDUxOEg2Nkw1NiA1MjlWNjEyTDY2IDYyMkgxNTBMMTYwIDYxMlY1NzBIMjAyTDIxMiA1NjBWNTI5TDIyMiA1MThIMjUxTDI2MiA1MDhWNDc3TDI3MiA0NjZIMzAxTDMxMiA0NTZWNDI1TDMyMiA0MTVIMzUxTDM2MSA0MDRWMzczTDM3MiAzNjNINDAxTDQxMSAzNTJWMzIxTDQyMiAzMTFINDUxTDQ2MSAzMDFWMjE4TDQ1MSAyMDdINDIxTDQxMCAxOTdWMTY2TDQyMSAxNTZINDUwTDQ2MCAxNDVWMTE0TDQ3MSAxMDRINTAwTDUxMCA5M1YxMEw1MDAgMEgyMDdaTTE2OCA0NDFMMTU4IDQ1MVY1MDhMMTQ3IDUxOEgxMThMMTA4IDUyOVY1NjBMMTE4IDU3MEgxNjBWNTI5TDE3MCA1MThIMTk5TDIxMCA1MDhWNDc3TDIyMCA0NjZIMjQ5TDI2MCA0NTZWNDI1TDI3MCA0MTVIMjk5TDMxMCA0MDRWMzczTDMyMCAzNjNIMzQ5TDM1OSAzNTJWMzIxTDM3MCAzMTFIMzk5TDQwOSAzMDFWMjcwTDM5OSAyNTlIMzE5TDMwOCAyNDlWMjE4TDMxOSAyMDdIMzQ4TDM1OCAxOTdWMTY2TDM2OSAxNTZIMzk4TDQwOCAxNDVWMTE0TDQxOSAxMDRINDQ4TDQ1OCA5M1Y2Mkw0NDggNTJIMjA5TDE5OCA2MlYxNDVMMTg4IDE1NkgxNTlMMTQ5IDE2NlYyMjNMMTM4IDIzM0gxMDlMOTkgMjQ0VjMwMUwxMDkgMzExSDE5N0wyMDggMzIxVjQzMEwxOTcgNDQxSDE2OFoiLz48L3N2Zz4%3D&logoColor=white&labelColor=1E293B)](https://docs.astral.sh/ruff/linter/) |
| Release       | [![Release](https://img.shields.io/github/v/release/wattnet/wattnet-api?label=Release&color=3B5B8A&logo=github&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-api/releases) [![Publish](https://img.shields.io/github/actions/workflow/status/wattnet/wattnet-api/publish.yml?label=Publish&logo=githubactions&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-api/actions/workflows/publish.yml) [![Release Please](https://img.shields.io/github/actions/workflow/status/wattnet/wattnet-api/release-please.yml?branch=main&label=Release%20Please&logo=githubactions&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-api/actions/workflows/release-please.yml)                                                                                                                                                                                                                                                                     |
| Package       | [![PyPI](https://img.shields.io/pypi/v/wattnet-api?label=PyPI&color=9C5A32&logo=pypi&logoColor=white&labelColor=1E293B)](https://pypi.org/project/wattnet-api/) [![Python](https://img.shields.io/pypi/pyversions/wattnet-api?label=Python&color=9C5A32&logo=python&logoColor=white&labelColor=1E293B)](https://pypi.org/project/wattnet-api/) [![Downloads](https://img.shields.io/pepy/dt/wattnet-api?label=Downloads&color=9C5A32&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2ZmZiI%2BPHBhdGggZD0iTTExIDNoMnY5LjE3bDMuNTktMy41OEwxOCAxMGwtNiA2LTYtNiAxLjQxLTEuNDFMMTEgMTIuMTdWM3oiLz48cGF0aCBkPSJNNCAxOWgxNnYySDR6Ii8%2BPC9zdmc%2B&logoColor=white&labelColor=1E293B)](https://pepy.tech/projects/wattnet-api) [![Docker Hub](https://img.shields.io/docker/v/wattnet/wattnet-api?label=Docker%20Hub&sort=semver&color=9C5A32&logo=docker&logoColor=white&labelColor=1E293B)](https://hub.docker.com/r/wattnet/wattnet-api) |
| Quality       | [![Status](https://img.shields.io/badge/Status-Production%2FStable-4A8118?labelColor=1E293B)](https://pypi.org/project/wattnet-api/) [![Coverage](https://img.shields.io/codecov/c/github/wattnet/wattnet-api?label=Coverage&logo=codecov&logoColor=white&labelColor=1E293B)](https://codecov.io/gh/wattnet/wattnet-api)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    [![Ruff format](https://img.shields.io/badge/Format-Ruff-4A8118?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MTAgNjIyIj48cGF0aCBmaWxsPSIjZmZmIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMDcgMEwxOTYgMTBWNDFMMTg2IDUySDE1N0wxNDYgNjJWMTQ1TDEzNiAxNTZIMTA3TDk3IDE2NlYyMjNMODYgMjMzSDU3TDQ3IDI0NFYzMDFMMzYgMzExSDEwTDAgMzIxVjM1MkwxMCAzNjNIMTQ1TDE1NiAzNzNWNDMwTDE0NSA0NDFIMTE2TDEwNiA0NTFWNTA4TDk2IDUxOEg2Nkw1NiA1MjlWNjEyTDY2IDYyMkgxNTBMMTYwIDYxMlY1NzBIMjAyTDIxMiA1NjBWNTI5TDIyMiA1MThIMjUxTDI2MiA1MDhWNDc3TDI3MiA0NjZIMzAxTDMxMiA0NTZWNDI1TDMyMiA0MTVIMzUxTDM2MSA0MDRWMzczTDM3MiAzNjNINDAxTDQxMSAzNTJWMzIxTDQyMiAzMTFINDUxTDQ2MSAzMDFWMjE4TDQ1MSAyMDdINDIxTDQxMCAxOTdWMTY2TDQyMSAxNTZINDUwTDQ2MCAxNDVWMTE0TDQ3MSAxMDRINTAwTDUxMCA5M1YxMEw1MDAgMEgyMDdaTTE2OCA0NDFMMTU4IDQ1MVY1MDhMMTQ3IDUxOEgxMThMMTA4IDUyOVY1NjBMMTE4IDU3MEgxNjBWNTI5TDE3MCA1MThIMTk5TDIxMCA1MDhWNDc3TDIyMCA0NjZIMjQ5TDI2MCA0NTZWNDI1TDI3MCA0MTVIMjk5TDMxMCA0MDRWMzczTDMyMCAzNjNIMzQ5TDM1OSAzNTJWMzIxTDM3MCAzMTFIMzk5TDQwOSAzMDFWMjcwTDM5OSAyNTlIMzE5TDMwOCAyNDlWMjE4TDMxOSAyMDdIMzQ4TDM1OCAxOTdWMTY2TDM2OSAxNTZIMzk4TDQwOCAxNDVWMTE0TDQxOSAxMDRINDQ4TDQ1OCA5M1Y2Mkw0NDggNTJIMjA5TDE5OCA2MlYxNDVMMTg4IDE1NkgxNTlMMTQ5IDE2NlYyMjNMMTM4IDIzM0gxMDlMOTkgMjQ0VjMwMUwxMDkgMzExSDE5N0wyMDggMzIxVjQzMEwxOTcgNDQxSDE2OFoiLz48L3N2Zz4%3D&logoColor=white&labelColor=1E293B)](https://docs.astral.sh/ruff/formatter/) |
| Community     | [![Contributing](https://img.shields.io/badge/Contributing-guidelines-5374A7?logo=github&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-api/blob/main/CONTRIBUTING.md) [![Code of Conduct](https://img.shields.io/badge/Code%20of%20Conduct-3.0-5374A7?logo=contributorcovenant&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-api/blob/main/CODE_OF_CONDUCT.md) [![Security](https://img.shields.io/badge/Security-policy-5374A7?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2ZmZiI%2BPHBhdGggZD0iTTcgMTBWN2E1IDUgMCAwIDEgMTAgMHYzaDFhMiAyIDAgMCAxIDIgMnY4YTIgMiAwIDAgMS0yIDJINmEyIDIgMCAwIDEtMi0ydi04YTIgMiAwIDAgMSAyLTJoMXptMiAwaDZWN2EzIDMgMCAxIDAtNiAwdjN6Ii8%2BPC9zdmc%2B&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-api/blob/main/SECURITY.md) [![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-5374A7?logo=conventionalcommits&logoColor=white&labelColor=1E293B)](https://www.conventionalcommits.org/) |
| License       | [![License](https://img.shields.io/github/license/wattnet/wattnet-api?label=License&color=64748B&logo=opensourceinitiative&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-api/blob/main/LICENSE)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |

`wattnet-api` is the public-facing HTTP interface for the Wattnet platform. It exposes real-time, historical, and forecasted data on the carbon and water footprint of electricity consumption across Europe, fully documented with OpenAPI 3.1 and deployable as a Docker container.

## Purpose

Wattnet computes environmental metrics, carbon footprint, water impact, environmental scores, generation mix, from open electricity market data. `wattnet-api` makes all of these metrics available over HTTP so that dashboards, research tools, and third-party applications can query them without coupling to Wattnet's internal data pipeline.

The API is organized into five groups of endpoints:

| Group                     | Prefix                                                                       | Description                                                 |
| ------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **Zones**                 | `/v1/zones`                                                                  | Metadata and boundaries for supported electricity zones     |
| **Energy Metrics**        | `/v1/generation`, `/v1/load`, `/v1/imports`, `/v1/exports`, `/v1/mix`        | Electricity generation, consumption, and cross-border flows |
| **Environmental Metrics** | `/v1/footprints`, `/v1/impacts`, `/v1/environmental-score`                           | Carbon and water footprint, carbon impact, and environmental score  |
| **Shares Metrics**        | `/v1/flow-share`, `/v1/mix-share`, `/v1/footprint-share`, `/v1/impact-share` | Fractional attribution of flows, mix, footprint, and impact |
| **Factors**               | `/v1/factors`                                                                | Emission and consumption factors used in calculations       |

## Architecture

![API component diagram](https://github.com/wattnet/wattnet-software-architecture/blob/main/diagrams/png/structurizr-1-wattnet_api.png?raw=true)

For the full software architecture see the [wattnet-software-architecture](https://github.com/wattnet/wattnet-software-architecture) repository.

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

### With Docker

```bash
docker run -d \
  -p 8000:8000 \
  -e WATTNET_API_CLICKHOUSE_HOST=<host> \
  ghcr.io/wattnet/wattnet-api:latest
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

This work was developed within the [GreenDIGIT](https://greendigit-project.eu/) project, funded by the European Union's Horizon Europe research and innovation programme under grant agreement No. [101131207](https://cordis.europa.eu/project/id/101131207), and by the Swiss State Secretariat for Education, Research and Innovation (SERI).

<img src="https://github.com/wattnet/.github/raw/main/images/GreenDIGIT logo color horizontal2.png" alt="GreenDIGIT Logo" width="230" align="right"/>
<img src="https://github.com/wattnet/.github/raw/main/images/EN_FundedbytheEU_RGB_POS.png" alt="EU Funded Logo" width="260" align="left"/>
<img src="https://github.com/wattnet/.github/raw/main/images/Flag_of_Switzerland.svg" alt="Swiss State Secretariat for Education, Research and Innovation (SERI)" height="50" align="left"/>
<br clear="all"/>

##### © 2026 Spanish National Research Council (CSIC). All rights reserved.
