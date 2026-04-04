# Installation

This project is distributed as a Salt extension package.

## Supported installation path

Use the package path for all deployments and development workflows.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e '.[dev,tests,docs]'
```

Package-based installation enables:

- Loader discovery from the extension package.
- Reproducible dependency management.
- CI parity with local development.
