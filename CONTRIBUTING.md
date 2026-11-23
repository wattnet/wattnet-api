# Contributing to wattnet-api

Thank you for your interest in contributing. This document covers how to set up your environment, the code standards we follow, and the process for submitting changes.

## Prerequisites

- Python ≥ 3.11
- [Poetry](https://python-poetry.org/) ≥ 2.0
- Docker and Docker Compose (for integration tests)
- Git

## Getting Started

1. Fork the repository and clone your fork:

   ```bash
   git clone https://github.com/<your-username>/wattnet-api.git
   cd wattnet-api
   ```

2. Install all dependency groups:

   ```bash
   poetry install --with dev,test,lint,types,security
   ```

3. Install the pre-commit hooks:

   ```bash
   pre-commit install --hook-type pre-commit --hook-type commit-msg
   ```

## Running the Tests

**Unit tests** (no external services needed):

```bash
poetry run pytest tests/unit/
```

**Integration tests** (storage layer is mocked, no external services needed):

```bash
poetry run pytest tests/integration/
```

Or via tox:

```bash
tox -e integration
```

**Full tox matrix** (unit tests on py3.11–3.14, lint, type-check, format, security, dependency audit, build):

```bash
tox
```

## The API contract

`tests/contract/openapi-v1.json` is the OpenAPI document of `/v1` that clients rely on, and `tests/integration/test_openapi_contract.py` fails when a pull request removes or changes anything in it: a path, a parameter, a response property, an enum value or a type. Adding is allowed, and so is marking something as deprecated. If a change must alter the contract on purpose, regenerate the file in the same pull request, so that the diff shows what changes for the clients:

```bash
UPDATE_OPENAPI_CONTRACT=1 poetry run pytest tests/integration/test_openapi_contract.py
```

## The MCP tools

Every data endpoint of `/v1` is also a tool of the MCP interface (`wattnet/api/mcp/tools/`, one line per endpoint: its name, its handler and its group of the access policy). A new endpoint without a tool fails `test_every_data_route_has_a_tool`.

## Code Style

We enforce a consistent style automatically. Before opening a PR, run:

```bash
# Format and lint
ruff format .
ruff check wattnet

# Type-check
mypy -p wattnet.api

# Security scan
bandit -r wattnet/
```

All of these also run via pre-commit on every commit and are verified in CI.

Key rules:
- Line length: 88 characters (Ruff default).
- Import order: standard library → third-party → first-party, enforced by Ruff's isort rules.
- Docstrings: required on all public modules, classes, and functions, enforced by Ruff's pydocstyle rules with the pep257 convention.
- Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`).

## Submitting a Pull Request

1. Create a branch from `main` with a descriptive name:

   ```bash
   git checkout -b feat/my-new-feature
   ```

2. Make your changes, ensuring all tests pass and the linter is clean.

3. Push your branch and open a PR against `main`. Fill in the PR template.

4. A maintainer will review your PR. Please address any requested changes promptly.

## Reporting Issues

Please use the GitHub issue templates for bug reports and feature requests. For security vulnerabilities, see [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
