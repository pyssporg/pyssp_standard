# Runbook

> **Layer:** 05-operation
> **Question:** How is it run, monitored, and supported?

> **Note:** `pyssp_standard` is a Python library, not a deployed service.
> This layer is intentionally sparse.

## Installation

```bash
pip install .
```

Developers: use `pip install -e .` for editable install.

## Execution Model

- `pyssp_standard` has no CLI, no daemon, no server process.
- All usage is through Python import and context-managed facades.
- Typical usage: CI script, preprocessing pipeline, or interactive notebook.

## Testing

```bash
# From repo root with venv activated:
pytest

# Run specific test categories:
pytest pytest/ssp1/         # SSP1 tests only
pytest pytest/fmi2/         # FMI2 tests only
pytest pytest/ls_ref/       # LS-REF tests only
pytest pytest/tools/        # Tooling tests only

# With markers (configured in conftest.py):
pytest -m codec             # All codec tests
pytest -m facade            # All facade tests
pytest -m archive           # All archive tests
pytest -m demo              # Demo/test examples
pytest -m tooling           # Tooling tests
```

## Documentation

- User docs: `docs/getting_started.md`, `docs/user/python_api.md`
- Dev docs: `02-architecture/layer-rules.md`, `02-architecture/workflow.md`
- Build docs locally: see `docs/integrations/read_the_docs.md`

## Debugging

- All facades expose `.xml` property for direct model inspection
- Codecs can be called independently: `codec.parse(text)` / `codec.serialize(model)`
- Validation raises on failure; no silent corruption

## Known Operational Notes

- Archive-backed workflows use temporary directories cleaned up on context exit
- External reference resolution degrades silently to `None` when files don't exist
- Compliance check is explicit; errors raised as exceptions
- Thread safety: not tested; library assumes single-threaded usage

## Evidence

- `README.md`: install + quick start
- `docs/getting_started.md`: user workflows
- `pytest/conftest.py`: `pytest_collection_modifyitems` for marker configuration