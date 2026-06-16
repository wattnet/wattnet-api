# Contributing to wattnet-api

Thank you for your interest in contributing. This document covers how to set up your environment, the code standards we follow, and the process for submitting changes.

## Prerequisites

- Python ≥ 3.10
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
   poetry install --with dev,test,lint,format,types,security
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

**Integration tests** (storage layer is mocked — no external services needed):

```bash
poetry run pytest tests/integration/
```

Or via tox:

```bash
tox -e integration
```

**Full tox matrix** (unit tests on py3.10–3.14, lint, type-check, format, security, dependency audit, build):

```bash
tox
```

## Code Style

We enforce a consistent style automatically. Before opening a PR, run:

```bash
# Format code
black wattnet/
isort wattnet/

# Lint
flake8 wattnet/

# Type-check
mypy -p wattnet.api

# Security scan
bandit -r wattnet/
```

All of these also run via pre-commit on every commit and are verified in CI.

Key rules:
- Line length: 88 characters (Black default).
- Import order: standard library → third-party → first-party (`isort` with Black profile).
- Docstrings: required on all public modules, classes, and functions (`pydocstyle`).
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
