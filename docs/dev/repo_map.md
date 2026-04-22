# Repo Map

This page is the fastest way to orient in `pyssp_standard`.
Use it before opening implementation files.

## Read First

For most coding tasks, read in this order:
- `AGENTS.md`
- `docs/dev/repo_map.md`
- `pyssp_standard/__init__.py`
- one relevant module under `pyssp_standard/`
- one relevant test under `pytest/`

## Main Code

`pyssp_standard/` is the main package.

Top-level public facades:
- `pyssp_standard/ssp.py` for archive-level SSP workflows
- `pyssp_standard/ssd.py` for SSD access
- `pyssp_standard/ssm.py` for SSM access
- `pyssp_standard/ssv.py` for SSV access
- `pyssp_standard/fmu.py` for FMU access
- `pyssp_standard/md.py` for model description access

Shared implementation:
- `pyssp_standard/common/` for runtime, archive, document, and XML helpers
- `pyssp_standard/standard/` for standard-specific helpers and version routing
- `pyssp_standard/tools/` for developer tooling such as code generation support

## Tests

`pytest/` is the main test tree.

Useful starting points:
- `pytest/ssp1/facade/test_ssd.py`, `pytest/ssp1/facade/test_ssm.py`, `pytest/ssp1/facade/test_ssv.py`
- `pytest/ssp1/orchestration/test_ssp.py`
- `pytest/fmi2/archive/test_fmu.py`
- `pytest/tools/` for tooling-related tests
- `pytest/conftest.py` for shared fixtures

Open fixture files only when a selected test references them.

## Usually Ignore

Do not read these by default:
- `3rdParty/` vendored standards and reference material
- `venv/` local environment
- `.git/`, `.pytest_cache/`, `__pycache__/`
- `pytest/legacy_unsupported/` old behavior kept outside the main path
- binary and archive fixtures such as `*.fmu`, `*.ssp`, `*.zip`

## When To Open Deeper Docs

Open these only if the task needs them:
- `README.md` for package overview and user-facing positioning
- `docs/dev/architecture.md` for intended internal layer boundaries
- `docs/dev/repo_status.md` for current implementation reality
- `docs/dev/guidelines.md` for project-wide code and documentation conventions
