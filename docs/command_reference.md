# Command Reference

This page is for maintainers and contributors who need the common repository commands.

There is currently no end-user CLI. Interaction is through the Python API.

## Environment

Use the repo-local virtual environment when it exists:

```bash
. venv/bin/activate
```

Install the package in editable mode with maintainer tools:

```bash
pip install -e ".[dev]"
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

Build source and wheel distributions:

```bash
python -m build
```

After packaging changes, install the built wheel in a fresh environment and verify the public imports:

```bash
python -m venv /tmp/pyssp_standard_install
/tmp/pyssp_standard_install/bin/python -m pip install dist/pyssp_standard-0.8.2-py3-none-any.whl
/tmp/pyssp_standard_install/bin/python -c "from pyssp_standard.fmu import FMU; from pyssp_standard import SSD, SSP, SSV"
```
