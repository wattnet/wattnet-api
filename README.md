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
| Testing & CI  | [![CI](https://img.shields.io/github/actions/workflow/status/wattnet/wattnet-api/ci.yml?branch=main&label=CI&logo=githubactions&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-api/actions/workflows/ci.yml) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-0F766E?logo=pre-commit&logoColor=white&labelColor=1E293B)](https://github.com/pre-commit/pre-commit)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   [![Ruff lint](https://img.shields.io/badge/Lint-Ruff-0F766E?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTEwIiBoZWlnaHQ9IjYyMiIgdmlld0JveD0iMCAwIDUxMCA2MjIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI%2BPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMDYuNzAxIDBDMjAwLjk2NCAwIDE5Ni4zMTQgNC42NDEzMSAxOTYuMzE0IDEwLjM2NjdWNDEuNDY2N0MxOTYuMzE0IDQ3LjE5MiAxOTEuNjYzIDUxLjgzMzMgMTg1LjkyNyA1MS44MzMzSDE1Ni44NDNDMTUxLjEwNyA1MS44MzMzIDE0Ni40NTYgNTYuNDc0NiAxNDYuNDU2IDYyLjJWMTQ1LjEzM0MxNDYuNDU2IDE1MC44NTkgMTQxLjgwNiAxNTUuNSAxMzYuMDY5IDE1NS41SDEwNi45ODZDMTAxLjI0OSAxNTUuNSA5Ni41OTg4IDE2MC4xNDEgOTYuNTk4OCAxNjUuODY3VjIyMi44ODNDOTYuNTk4OCAyMjguNjA5IDkxLjk0ODQgMjMzLjI1IDg2LjIxMTggMjMzLjI1SDU3LjEyODNDNTEuMzkxNyAyMzMuMjUgNDYuNzQxMyAyMzcuODkxIDQ2Ljc0MTMgMjQzLjYxN1YzMDAuNjMzQzQ2Ljc0MTMgMzA2LjM1OSA0Mi4wOTA5IDMxMSAzNi4zNTQ0IDMxMUgxMC4zODdDNC42NTA0IDMxMSAwIDMxNS42NDEgMCAzMjEuMzY3VjM1Mi40NjdDMCAzNTguMTkyIDQuNjUwNCAzNjIuODMzIDEwLjM4NyAzNjIuODMzSDE0NS40MThDMTUxLjE1NCAzNjIuODMzIDE1NS44MDQgMzY3LjQ3NSAxNTUuODA0IDM3My4yVjQzMC4yMTdDMTU1LjgwNCA0MzUuOTQyIDE1MS4xNTQgNDQwLjU4MyAxNDUuNDE4IDQ0MC41ODNIMTE2LjMzNEMxMTAuNTk3IDQ0MC41ODMgMTA1Ljk0NyA0NDUuMjI1IDEwNS45NDcgNDUwLjk1VjUwNy45NjdDMTA1Ljk0NyA1MTMuNjkyIDEwMS4yOTcgNTE4LjMzMyA5NS41NjAxIDUxOC4zMzNINjYuNDc2NkM2MC43NCA1MTguMzMzIDU2LjA4OTYgNTIyLjk3NSA1Ni4wODk2IDUyOC43VjYxMS42MzNDNTYuMDg5NiA2MTcuMzU5IDYwLjc0IDYyMiA2Ni40NzY2IDYyMkgxNDkuNTcyQzE1NS4zMDkgNjIyIDE1OS45NTkgNjE3LjM1OSAxNTkuOTU5IDYxMS42MzNWNTcwLjE2N0gyMDEuNTA3QzIwNy4yNDQgNTcwLjE2NyAyMTEuODk0IDU2NS41MjUgMjExLjg5NCA1NTkuOFY1MjguN0MyMTEuODk0IDUyMi45NzUgMjE2LjU0NCA1MTguMzMzIDIyMi4yODEgNTE4LjMzM0gyNTEuMzY1QzI1Ny4xMDEgNTE4LjMzMyAyNjEuNzUyIDUxMy42OTIgMjYxLjc1MiA1MDcuOTY3VjQ3Ni44NjdDMjYxLjc1MiA0NzEuMTQxIDI2Ni40MDIgNDY2LjUgMjcyLjEzOCA0NjYuNUgzMDEuMjIyQzMwNi45NTkgNDY2LjUgMzExLjYwOSA0NjEuODU5IDMxMS42MDkgNDU2LjEzM1Y0MjUuMDMzQzMxMS42MDkgNDE5LjMwOCAzMTYuMjU5IDQxNC42NjcgMzIxLjk5NiA0MTQuNjY3SDM1MS4wNzlDMzU2LjgxNiA0MTQuNjY3IDM2MS40NjYgNDEwLjAyNSAzNjEuNDY2IDQwNC4zVjM3My4yQzM2MS40NjYgMzY3LjQ3NSAzNjYuMTE3IDM2Mi44MzMgMzcxLjg1MyAzNjIuODMzSDQwMC45MzdDNDA2LjY3MyAzNjIuODMzIDQxMS4zMjQgMzU4LjE5MiA0MTEuMzI0IDM1Mi40NjdWMzIxLjM2N0M0MTEuMzI0IDMxNS42NDEgNDE1Ljk3NCAzMTEgNDIxLjcxMSAzMTFINDUwLjc5NEM0NTYuNTMxIDMxMSA0NjEuMTgxIDMwNi4zNTkgNDYxLjE4MSAzMDAuNjMzVjIxNy43QzQ2MS4xODEgMjExLjk3NSA0NTYuNTMxIDIwNy4zMzMgNDUwLjc5NCAyMDcuMzMzSDQyMC42NzJDNDE0LjkzNiAyMDcuMzMzIDQxMC4yODUgMjAyLjY5MiA0MTAuMjg1IDE5Ni45NjdWMTY1Ljg2N0M0MTAuMjg1IDE2MC4xNDEgNDE0LjkzNiAxNTUuNSA0MjAuNjcyIDE1NS41SDQ0OS43NTZDNDU1LjQ5MiAxNTUuNSA0NjAuMTQzIDE1MC44NTkgNDYwLjE0MyAxNDUuMTMzVjExNC4wMzNDNDYwLjE0MyAxMDguMzA4IDQ2NC43OTMgMTAzLjY2NyA0NzAuNTMgMTAzLjY2N0g0OTkuNjEzQzUwNS4zNSAxMDMuNjY3IDUxMCA5OS4wMjUzIDUxMCA5My4zVjEwLjM2NjdDNTEwIDQuNjQxMzIgNTA1LjM1IDAgNDk5LjYxMyAwSDIwNi43MDFaTTE2OC4yNjkgNDQwLjU4M0MxNjIuNTMyIDQ0MC41ODMgMTU3Ljg4MiA0NDUuMjI1IDE1Ny44ODIgNDUwLjk1VjUwNy45NjdDMTU3Ljg4MiA1MTMuNjkyIDE1My4yMzEgNTE4LjMzMyAxNDcuNDk1IDUxOC4zMzNIMTE4LjQxMUMxMTIuNjc1IDUxOC4zMzMgMTA4LjAyNCA1MjIuOTc1IDEwOC4wMjQgNTI4LjdWNTU5LjhDMTA4LjAyNCA1NjUuNTI1IDExMi42NzUgNTcwLjE2NyAxMTguNDExIDU3MC4xNjdIMTU5Ljk1OVY1MjguN0MxNTkuOTU5IDUyMi45NzUgMTY0LjYxIDUxOC4zMzMgMTcwLjM0NiA1MTguMzMzSDE5OS40M0MyMDUuMTY2IDUxOC4zMzMgMjA5LjgxNyA1MTMuNjkyIDIwOS44MTcgNTA3Ljk2N1Y0NzYuODY3QzIwOS44MTcgNDcxLjE0MSAyMTQuNDY3IDQ2Ni41IDIyMC4yMDQgNDY2LjVIMjQ5LjI4N0MyNTUuMDI0IDQ2Ni41IDI1OS42NzQgNDYxLjg1OSAyNTkuNjc0IDQ1Ni4xMzNWNDI1LjAzM0MyNTkuNjc0IDQxOS4zMDggMjY0LjMyNSA0MTQuNjY3IDI3MC4wNjEgNDE0LjY2N0gyOTkuMTQ1QzMwNC44ODEgNDE0LjY2NyAzMDkuNTMyIDQxMC4wMjUgMzA5LjUzMiA0MDQuM1YzNzMuMkMzMDkuNTMyIDM2Ny40NzUgMzE0LjE4MiAzNjIuODMzIDMxOS45MTkgMzYyLjgzM0gzNDkuMDAyQzM1NC43MzkgMzYyLjgzMyAzNTkuMzg5IDM1OC4xOTIgMzU5LjM4OSAzNTIuNDY3VjMyMS4zNjdDMzU5LjM4OSAzMTUuNjQxIDM2NC4wMzkgMzExIDM2OS43NzYgMzExSDM5OC44NTlDNDA0LjU5NiAzMTEgNDA5LjI0NiAzMDYuMzU5IDQwOS4yNDYgMzAwLjYzM1YyNjkuNTMzQzQwOS4yNDYgMjYzLjgwOCA0MDQuNTk2IDI1OS4xNjcgMzk4Ljg1OSAyNTkuMTY3SDMxOC44OEMzMTMuMTQzIDI1OS4xNjcgMzA4LjQ5MyAyNTQuNTI1IDMwOC40OTMgMjQ4LjhWMjE3LjdDMzA4LjQ5MyAyMTEuOTc1IDMxMy4xNDMgMjA3LjMzMyAzMTguODggMjA3LjMzM0gzNDcuOTYzQzM1My43IDIwNy4zMzMgMzU4LjM1IDIwMi42OTIgMzU4LjM1IDE5Ni45NjdWMTY1Ljg2N0MzNTguMzUgMTYwLjE0MSAzNjMuMDAxIDE1NS41IDM2OC43MzcgMTU1LjVIMzk3LjgyMUM0MDMuNTU3IDE1NS41IDQwOC4yMDggMTUwLjg1OSA0MDguMjA4IDE0NS4xMzNWMTE0LjAzM0M0MDguMjA4IDEwOC4zMDggNDEyLjg1OCAxMDMuNjY3IDQxOC41OTUgMTAzLjY2N0g0NDcuNjc4QzQ1My40MTUgMTAzLjY2NyA0NTguMDY1IDk5LjAyNTMgNDU4LjA2NSA5My4zVjYyLjJDNDU4LjA2NSA1Ni40NzQ2IDQ1My40MTUgNTEuODMzMyA0NDcuNjc4IDUxLjgzMzNIMjA4Ljc3OEMyMDMuMDQxIDUxLjgzMzMgMTk4LjM5MSA1Ni40NzQ2IDE5OC4zOTEgNjIuMlYxNDUuMTMzQzE5OC4zOTEgMTUwLjg1OSAxOTMuNzQxIDE1NS41IDE4OC4wMDQgMTU1LjVIMTU4LjkyMUMxNTMuMTg0IDE1NS41IDE0OC41MzQgMTYwLjE0MSAxNDguNTM0IDE2NS44NjdWMjIyLjg4M0MxNDguNTM0IDIyOC42MDkgMTQzLjg4MyAyMzMuMjUgMTM4LjE0NyAyMzMuMjVIMTA5LjA2M0MxMDMuMzI3IDIzMy4yNSA5OC42NzYyIDIzNy44OTEgOTguNjc2MiAyNDMuNjE3VjMwMC42MzNDOTguNjc2MiAzMDYuMzU5IDEwMy4zMjcgMzExIDEwOS4wNjMgMzExSDE5Ny4zNTJDMjAzLjA4OSAzMTEgMjA3LjczOSAzMTUuNjQxIDIwNy43MzkgMzIxLjM2N1Y0MzAuMjE3QzIwNy43MzkgNDM1Ljk0MiAyMDMuMDg5IDQ0MC41ODMgMTk3LjM1MiA0NDAuNTgzSDE2OC4yNjlaIiBmaWxsPSIjZmZmZmZmIi8%2BPC9zdmc%2B&logoColor=white&labelColor=1E293B)](https://docs.astral.sh/ruff/linter/) |
| Release       | [![Release](https://img.shields.io/github/v/release/wattnet/wattnet-api?label=Release&color=3B5B8A&logo=github&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-api/releases) [![Publish](https://img.shields.io/github/actions/workflow/status/wattnet/wattnet-api/publish.yml?label=Publish&logo=githubactions&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-api/actions/workflows/publish.yml) [![Release Please](https://img.shields.io/github/actions/workflow/status/wattnet/wattnet-api/release-please.yml?branch=main&label=Release%20Please&logo=githubactions&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-api/actions/workflows/release-please.yml)                                                                                                                                                                                                                                                                     |
| Package       | [![PyPI](https://img.shields.io/pypi/v/wattnet-api?label=PyPI&color=9C5A32&logo=pypi&logoColor=white&labelColor=1E293B)](https://pypi.org/project/wattnet-api/) [![Python](https://img.shields.io/pypi/pyversions/wattnet-api?label=Python&color=9C5A32&logo=python&logoColor=white&labelColor=1E293B)](https://pypi.org/project/wattnet-api/) [![Downloads](https://img.shields.io/pepy/dt/wattnet-api?label=Downloads&color=9C5A32&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2ZmZiI%2BPHBhdGggZD0iTTExIDNoMnY5LjE3bDMuNTktMy41OEwxOCAxMGwtNiA2LTYtNiAxLjQxLTEuNDFMMTEgMTIuMTdWM3oiLz48cGF0aCBkPSJNNCAxOWgxNnYySDR6Ii8%2BPC9zdmc%2B&logoColor=white&labelColor=1E293B)](https://pepy.tech/projects/wattnet-api) [![Docker Hub](https://img.shields.io/docker/v/wattnet/wattnet-api?label=Docker%20Hub&sort=semver&color=9C5A32&logo=docker&logoColor=white&labelColor=1E293B)](https://hub.docker.com/r/wattnet/wattnet-api) |
| Quality       | [![Status](https://img.shields.io/badge/Status-Production%2FStable-4A8118?labelColor=1E293B)](https://pypi.org/project/wattnet-api/) [![Coverage](https://img.shields.io/codecov/c/github/wattnet/wattnet-api?label=Coverage&logo=codecov&logoColor=white&labelColor=1E293B)](https://codecov.io/gh/wattnet/wattnet-api)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    [![Ruff format](https://img.shields.io/badge/Format-Ruff-4A8118?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTEwIiBoZWlnaHQ9IjYyMiIgdmlld0JveD0iMCAwIDUxMCA2MjIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI%2BPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMDYuNzAxIDBDMjAwLjk2NCAwIDE5Ni4zMTQgNC42NDEzMSAxOTYuMzE0IDEwLjM2NjdWNDEuNDY2N0MxOTYuMzE0IDQ3LjE5MiAxOTEuNjYzIDUxLjgzMzMgMTg1LjkyNyA1MS44MzMzSDE1Ni44NDNDMTUxLjEwNyA1MS44MzMzIDE0Ni40NTYgNTYuNDc0NiAxNDYuNDU2IDYyLjJWMTQ1LjEzM0MxNDYuNDU2IDE1MC44NTkgMTQxLjgwNiAxNTUuNSAxMzYuMDY5IDE1NS41SDEwNi45ODZDMTAxLjI0OSAxNTUuNSA5Ni41OTg4IDE2MC4xNDEgOTYuNTk4OCAxNjUuODY3VjIyMi44ODNDOTYuNTk4OCAyMjguNjA5IDkxLjk0ODQgMjMzLjI1IDg2LjIxMTggMjMzLjI1SDU3LjEyODNDNTEuMzkxNyAyMzMuMjUgNDYuNzQxMyAyMzcuODkxIDQ2Ljc0MTMgMjQzLjYxN1YzMDAuNjMzQzQ2Ljc0MTMgMzA2LjM1OSA0Mi4wOTA5IDMxMSAzNi4zNTQ0IDMxMUgxMC4zODdDNC42NTA0IDMxMSAwIDMxNS42NDEgMCAzMjEuMzY3VjM1Mi40NjdDMCAzNTguMTkyIDQuNjUwNCAzNjIuODMzIDEwLjM4NyAzNjIuODMzSDE0NS40MThDMTUxLjE1NCAzNjIuODMzIDE1NS44MDQgMzY3LjQ3NSAxNTUuODA0IDM3My4yVjQzMC4yMTdDMTU1LjgwNCA0MzUuOTQyIDE1MS4xNTQgNDQwLjU4MyAxNDUuNDE4IDQ0MC41ODNIMTE2LjMzNEMxMTAuNTk3IDQ0MC41ODMgMTA1Ljk0NyA0NDUuMjI1IDEwNS45NDcgNDUwLjk1VjUwNy45NjdDMTA1Ljk0NyA1MTMuNjkyIDEwMS4yOTcgNTE4LjMzMyA5NS41NjAxIDUxOC4zMzNINjYuNDc2NkM2MC43NCA1MTguMzMzIDU2LjA4OTYgNTIyLjk3NSA1Ni4wODk2IDUyOC43VjYxMS42MzNDNTYuMDg5NiA2MTcuMzU5IDYwLjc0IDYyMiA2Ni40NzY2IDYyMkgxNDkuNTcyQzE1NS4zMDkgNjIyIDE1OS45NTkgNjE3LjM1OSAxNTkuOTU5IDYxMS42MzNWNTcwLjE2N0gyMDEuNTA3QzIwNy4yNDQgNTcwLjE2NyAyMTEuODk0IDU2NS41MjUgMjExLjg5NCA1NTkuOFY1MjguN0MyMTEuODk0IDUyMi45NzUgMjE2LjU0NCA1MTguMzMzIDIyMi4yODEgNTE4LjMzM0gyNTEuMzY1QzI1Ny4xMDEgNTE4LjMzMyAyNjEuNzUyIDUxMy42OTIgMjYxLjc1MiA1MDcuOTY3VjQ3Ni44NjdDMjYxLjc1MiA0NzEuMTQxIDI2Ni40MDIgNDY2LjUgMjcyLjEzOCA0NjYuNUgzMDEuMjIyQzMwNi45NTkgNDY2LjUgMzExLjYwOSA0NjEuODU5IDMxMS42MDkgNDU2LjEzM1Y0MjUuMDMzQzMxMS42MDkgNDE5LjMwOCAzMTYuMjU5IDQxNC42NjcgMzIxLjk5NiA0MTQuNjY3SDM1MS4wNzlDMzU2LjgxNiA0MTQuNjY3IDM2MS40NjYgNDEwLjAyNSAzNjEuNDY2IDQwNC4zVjM3My4yQzM2MS40NjYgMzY3LjQ3NSAzNjYuMTE3IDM2Mi44MzMgMzcxLjg1MyAzNjIuODMzSDQwMC45MzdDNDA2LjY3MyAzNjIuODMzIDQxMS4zMjQgMzU4LjE5MiA0MTEuMzI0IDM1Mi40NjdWMzIxLjM2N0M0MTEuMzI0IDMxNS42NDEgNDE1Ljk3NCAzMTEgNDIxLjcxMSAzMTFINDUwLjc5NEM0NTYuNTMxIDMxMSA0NjEuMTgxIDMwNi4zNTkgNDYxLjE4MSAzMDAuNjMzVjIxNy43QzQ2MS4xODEgMjExLjk3NSA0NTYuNTMxIDIwNy4zMzMgNDUwLjc5NCAyMDcuMzMzSDQyMC42NzJDNDE0LjkzNiAyMDcuMzMzIDQxMC4yODUgMjAyLjY5MiA0MTAuMjg1IDE5Ni45NjdWMTY1Ljg2N0M0MTAuMjg1IDE2MC4xNDEgNDE0LjkzNiAxNTUuNSA0MjAuNjcyIDE1NS41SDQ0OS43NTZDNDU1LjQ5MiAxNTUuNSA0NjAuMTQzIDE1MC44NTkgNDYwLjE0MyAxNDUuMTMzVjExNC4wMzNDNDYwLjE0MyAxMDguMzA4IDQ2NC43OTMgMTAzLjY2NyA0NzAuNTMgMTAzLjY2N0g0OTkuNjEzQzUwNS4zNSAxMDMuNjY3IDUxMCA5OS4wMjUzIDUxMCA5My4zVjEwLjM2NjdDNTEwIDQuNjQxMzIgNTA1LjM1IDAgNDk5LjYxMyAwSDIwNi43MDFaTTE2OC4yNjkgNDQwLjU4M0MxNjIuNTMyIDQ0MC41ODMgMTU3Ljg4MiA0NDUuMjI1IDE1Ny44ODIgNDUwLjk1VjUwNy45NjdDMTU3Ljg4MiA1MTMuNjkyIDE1My4yMzEgNTE4LjMzMyAxNDcuNDk1IDUxOC4zMzNIMTE4LjQxMUMxMTIuNjc1IDUxOC4zMzMgMTA4LjAyNCA1MjIuOTc1IDEwOC4wMjQgNTI4LjdWNTU5LjhDMTA4LjAyNCA1NjUuNTI1IDExMi42NzUgNTcwLjE2NyAxMTguNDExIDU3MC4xNjdIMTU5Ljk1OVY1MjguN0MxNTkuOTU5IDUyMi45NzUgMTY0LjYxIDUxOC4zMzMgMTcwLjM0NiA1MTguMzMzSDE5OS40M0MyMDUuMTY2IDUxOC4zMzMgMjA5LjgxNyA1MTMuNjkyIDIwOS44MTcgNTA3Ljk2N1Y0NzYuODY3QzIwOS44MTcgNDcxLjE0MSAyMTQuNDY3IDQ2Ni41IDIyMC4yMDQgNDY2LjVIMjQ5LjI4N0MyNTUuMDI0IDQ2Ni41IDI1OS42NzQgNDYxLjg1OSAyNTkuNjc0IDQ1Ni4xMzNWNDI1LjAzM0MyNTkuNjc0IDQxOS4zMDggMjY0LjMyNSA0MTQuNjY3IDI3MC4wNjEgNDE0LjY2N0gyOTkuMTQ1QzMwNC44ODEgNDE0LjY2NyAzMDkuNTMyIDQxMC4wMjUgMzA5LjUzMiA0MDQuM1YzNzMuMkMzMDkuNTMyIDM2Ny40NzUgMzE0LjE4MiAzNjIuODMzIDMxOS45MTkgMzYyLjgzM0gzNDkuMDAyQzM1NC43MzkgMzYyLjgzMyAzNTkuMzg5IDM1OC4xOTIgMzU5LjM4OSAzNTIuNDY3VjMyMS4zNjdDMzU5LjM4OSAzMTUuNjQxIDM2NC4wMzkgMzExIDM2OS43NzYgMzExSDM5OC44NTlDNDA0LjU5NiAzMTEgNDA5LjI0NiAzMDYuMzU5IDQwOS4yNDYgMzAwLjYzM1YyNjkuNTMzQzQwOS4yNDYgMjYzLjgwOCA0MDQuNTk2IDI1OS4xNjcgMzk4Ljg1OSAyNTkuMTY3SDMxOC44OEMzMTMuMTQzIDI1OS4xNjcgMzA4LjQ5MyAyNTQuNTI1IDMwOC40OTMgMjQ4LjhWMjE3LjdDMzA4LjQ5MyAyMTEuOTc1IDMxMy4xNDMgMjA3LjMzMyAzMTguODggMjA3LjMzM0gzNDcuOTYzQzM1My43IDIwNy4zMzMgMzU4LjM1IDIwMi42OTIgMzU4LjM1IDE5Ni45NjdWMTY1Ljg2N0MzNTguMzUgMTYwLjE0MSAzNjMuMDAxIDE1NS41IDM2OC43MzcgMTU1LjVIMzk3LjgyMUM0MDMuNTU3IDE1NS41IDQwOC4yMDggMTUwLjg1OSA0MDguMjA4IDE0NS4xMzNWMTE0LjAzM0M0MDguMjA4IDEwOC4zMDggNDEyLjg1OCAxMDMuNjY3IDQxOC41OTUgMTAzLjY2N0g0NDcuNjc4QzQ1My40MTUgMTAzLjY2NyA0NTguMDY1IDk5LjAyNTMgNDU4LjA2NSA5My4zVjYyLjJDNDU4LjA2NSA1Ni40NzQ2IDQ1My40MTUgNTEuODMzMyA0NDcuNjc4IDUxLjgzMzNIMjA4Ljc3OEMyMDMuMDQxIDUxLjgzMzMgMTk4LjM5MSA1Ni40NzQ2IDE5OC4zOTEgNjIuMlYxNDUuMTMzQzE5OC4zOTEgMTUwLjg1OSAxOTMuNzQxIDE1NS41IDE4OC4wMDQgMTU1LjVIMTU4LjkyMUMxNTMuMTg0IDE1NS41IDE0OC41MzQgMTYwLjE0MSAxNDguNTM0IDE2NS44NjdWMjIyLjg4M0MxNDguNTM0IDIyOC42MDkgMTQzLjg4MyAyMzMuMjUgMTM4LjE0NyAyMzMuMjVIMTA5LjA2M0MxMDMuMzI3IDIzMy4yNSA5OC42NzYyIDIzNy44OTEgOTguNjc2MiAyNDMuNjE3VjMwMC42MzNDOTguNjc2MiAzMDYuMzU5IDEwMy4zMjcgMzExIDEwOS4wNjMgMzExSDE5Ny4zNTJDMjAzLjA4OSAzMTEgMjA3LjczOSAzMTUuNjQxIDIwNy43MzkgMzIxLjM2N1Y0MzAuMjE3QzIwNy43MzkgNDM1Ljk0MiAyMDMuMDg5IDQ0MC41ODMgMTk3LjM1MiA0NDAuNTgzSDE2OC4yNjlaIiBmaWxsPSIjZmZmZmZmIi8%2BPC9zdmc%2B&logoColor=white&labelColor=1E293B)](https://docs.astral.sh/ruff/formatter/) |
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
