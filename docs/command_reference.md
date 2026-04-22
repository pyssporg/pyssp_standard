# Command Reference

This page is for maintainers and contributors who need the common repository commands.

There is currently no end-user CLI. Interaction is through the Python API.

## Environment

Use the repo-local virtual environment when it exists:

```bash
. venv/bin/activate
```

## Tests

Run the full test suite:

```bash
pytest
```

Run one focused test module:

```bash
pytest pytest/ssp1/facade/test_ssv.py
```

Run one test by name:

```bash
pytest pytest/ssp1/orchestration/test_ssp.py -k external_parameter
```

## Documentation

Build the documentation locally:

```bash
sphinx-build docs _build
```

## Packaging

Install the package from the repo:

```bash
pip install .
```
