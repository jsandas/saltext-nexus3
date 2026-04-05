# Copier Template Migration Plan

## Phase 1 — Bootstrap copier (generates the canonical scaffold)

1. Install copier: `pip install copier`
2. Run against the existing repo root:
   ```bash
   copier copy --trust https://github.com/salt-extensions/salt-extension-copier .
   ```
3. Answer the template questions. Recommended answers for this project:

   | Question | Value |
   |---|---|
   | `project_name` | `nexus3` |
   | `author` | `saltext-nexus3 contributors` |
   | `integration_name` | `Sonatype Nexus Repository 3` |
   | `summary` | `Salt extension modules and states to manage Nexus Repository 3` |
   | `source_url` | `https://github.com/jsandas/saltext-nexus3` |
   | `loaders` | `modules`, `states`, `utils` |
   | `salt_version` | `3006` |
   | `python_requires` | `3.10` |
   | `license` | `MIT` |
   | `no_saltext_namespace` | `false` |
   | `test_containers` | `false` (Nexus runs separately via Docker) |
   | `deploy_docs` | `never` or `release` |

4. Resolve merge conflicts — copier will conflict on `pyproject.toml`, `noxfile.py`,
   `docs/conf.py`, `.pre-commit-config.yaml`, and `README.md`. Keep the generated
   versions as the base and re-apply any project-specific content.
5. Commit `.copier-answers.yml` and all generated files as the baseline.

---

## Phase 2 — `pyproject.toml`

- **Keep**: all `[project]` metadata, `[project.entry-points]`, `[tool.ruff]`, `[tool.pytest.ini_options]`
- **Replace**: `[project.optional-dependencies]` with the template version which adds
  `pytest-salt-factories`, `coverage`, `furo`, `sphinx-copybutton`, `sphinxcontrib-spelling`
- **Add**:
  ```toml
  [tool.towncrier]
  name = "saltext-nexus3"
  package = "saltext.nexus3"
  filename = "CHANGELOG.md"
  directory = "changelog/"
  template = "changelog/.template.jinja"

  [tool.coverage.run]
  branch = true
  source = ["saltext.nexus3"]
  ```

---

## Phase 3 — `noxfile.py` (full replacement)

The current noxfile is minimal. Replace it with the template's version which adds:

- `SKIP_REQUIREMENTS_INSTALL=1` env var support for fast re-runs
- `EXTRA_REQUIREMENTS_INSTALL` env var support
- `docs-dev` live-reloading session
- `coverage` session
- `pre-commit` lint session
- Proper `pytest-salt-factories`-compatible test matrix across Salt versions

Remove the `make docs` / `docs-check` targets from `Makefile` (or replace them with `nox -e docs`).

---

## Phase 4 — Documentation

**Remove:**
- `bin/generate_docs_from_docstrings.py`
- All of `docs/modules/*.md` — redundant once autodoc works directly from docstrings
- All of `docs/states/*.md` — same reason
- `Makefile` targets `docs:` and `docs-check:`

**Update `docs/conf.py`:**
- Change theme from `alabaster` to `furo`
- Add extensions: `sphinx-copybutton`, `sphinxcontrib.spelling`
- Add `intersphinx_mapping` for Salt docs
- Remove the `exclude_patterns` entries for `modules` and `states`

**`docs/ref/modules.rst` and `docs/ref/states.rst`:** Already use `.. automodule::` correctly — no changes needed.

**Fix docstrings** in all source files under `src/saltext/nexus3/`:
- `CLI Example::` must be followed by a blank line then the `.. code-block::` directive
  (already correct in most files; the `verify()` function in `nexus3_email.py` is
  missing the `CLI Example::` header)
- `.. note::` directives are already present and valid RST

**`changelog/.template.jinja`:** Copier generates this — no manual work needed.

---

## Phase 5 — Unit tests (low effort, mostly compatible)

The unit tests in `tests/unit/` use `monkeypatch` to inject dunders directly — this
pattern is explicitly supported and recommended by the template. **No rewrites needed.**

The only change: replace the current hand-rolled `tests/conftest.py` (which only patches
`sys.path`) with the template-generated version that provides `minion_opts` and
`master_opts` fixtures from `pytest-salt-factories`.

---

## Phase 6 — Functional tests (medium effort)

**Replace `tests/functional/conftest.py`** — the current version manually builds Salt opts
and calls `salt.loader.*` directly. Replace with the template's conftest that provides
the `loaders` fixture from `pytest-salt-factories`.

**Rewrite `tests/functional/test_loader_calls.py` and `test_loader_smoke.py`:**

Current pattern:
```python
def test_loader_state_call(loaded_modules, loaded_states):
    ret = loaded_states["nexus3_security.anonymous_access"]("name", enabled=True)
```

Template pattern:
```python
def test_loader_state_call(loaders):
    ret = loaders.states.nexus3_security.anonymous_access("name", enabled=True)
```

The logic of each test stays the same; only the fixture names and access patterns change.

---

## Phase 7 — Integration tests (high effort)

This is the most significant change. The current tests use `salt.client.LocalClient()`
which requires a running Salt master in the same process (the Docker-based setup). The
template uses `pytest-salt-factories` daemon fixtures (`master`, `minion`, `salt_call_cli`).

**New approach:**
- `tests/conftest.py` defines a `master_config` fixture to inject Nexus3 connection
  settings (hostname, credentials) from environment variables
- `tests/integration/conftest.py` starts `master` and `minion` daemons via `pytest-salt-factories`
- Each test uses `salt_call_cli` instead of `LocalClient`

Current:
```python
ret = client.cmd('test.minion', 'nexus3_email.configure', ['enabled=True', ...])
assert ret['test.minion']['email']['host'] == 'notlocalhost'
```

New:
```python
def test_configure_email(salt_call_cli):
    res = salt_call_cli.run("nexus3_email.configure", enabled=True, host="notlocalhost", ...)
    assert res.returncode == 0
    assert res.data["email"]["host"] == "notlocalhost"
```

The Nexus3 service itself still runs in Docker — the difference is the Salt daemons are
managed by `pytest-salt-factories` rather than a separate Docker container. The
`docker-compose.yml` for Nexus only (not the Salt containers) can be retained.

> **Note:** This phase can be deferred. The existing Docker-based integration tests can
> continue to work in parallel until the migration is complete.

---

## Phase 8 — GitHub Actions workflows

The copier template generates all six workflow files. No manual work — just commit what
copier generates and configure the required GitHub repository settings:

- Add `PYPI_API_TOKEN` secret (if publishing to PyPI)
- Enable GitHub Pages (if deploying docs)
- Trusted Publisher setup on PyPI (if using `deploy-package-action.yml`)

---

## Phase 9 — Pre-commit

Replace the current minimal `.pre-commit-config.yaml` (ruff only) with the
template's version which adds:

- `towncrier` news fragment presence check
- `check-merge-conflict`, `end-of-file-fixer`, `trailing-whitespace`
- `pyupgrade`
- Optionally `pylint` (controlled by `relax_pylint` template answer)

---

## Phase 10 — CHANGELOG.md

Once `towncrier` is configured (Phase 2), build the changelog from the existing fragments:

```bash
towncrier build --version 0.4.0
```

This produces `CHANGELOG.md` and removes the processed fragments from `changelog/`.

---

## Summary — effort by phase

| Phase | Description | Effort | Risk |
|---|---|---|---|
| 1 | Bootstrap copier | Low | Medium (merge conflicts) |
| 2 | `pyproject.toml` | Low | Low |
| 3 | `noxfile.py` | Low | Low |
| 4 | Documentation | Low | Low |
| 5 | Unit tests | Negligible | Low |
| 6 | Functional tests | Medium | Low |
| 7 | Integration tests | High | High (architectural change) |
| 8 | GitHub Actions workflows | Negligible | Low |
| 9 | Pre-commit | Low | Low |
| 10 | CHANGELOG.md | Low | Low |
