# pyssp_standard

`pyssp_standard` is a Python package for inspecting and editing SSP-related files.

The current public entry points are:
- `SSP` for archive and directory workflows
- `SSD` for standalone system structure documents
- `SSM` for parameter mappings
- `SSV` for parameter sets
- `SRMD` for simulation resource meta data (compute resources, tool versions, licenses)
- `SSB` for signal dictionaries
- `FMU` and `ModelDescription` for FMI model archives and `modelDescription.xml`

The package is aimed at pre-processing, inspection, and controlled edits of SSP artifacts.

## Install

```bash
pip install .
```

## Quick Start

Read and validate a standalone parameter set:

```python
from pyssp_standard import SSV

with SSV("parameters.ssv") as ssv:
    assert ssv.check_compliance() is True
    print(ssv.xml.parameters[0].name)
```

Open an SSP archive and work on `SystemStructure.ssd` in archive context:

```python
from pyssp_standard import SSP

with SSP("system.ssp", mode="r") as ssp:
    with ssp.system_structure() as ssd:
        print(ssd.xml.name)
```

## Documentation

- [Docs index](docs/index.md)
- [Getting started](docs/getting_started.md)
- [Python API workflows](docs/user/python_api.md)
- [Command reference](docs/command_reference.md)
- [Product breakdown](product-breakdown/index.md) — architecture, capabilities, traceability
- [Code structure](product-breakdown/03-implementation/code-structure.md)
- [Quick code lookup](product-breakdown/03-implementation/interfaces.md)

## Notes

- Use `SSD(path)` for file-local SSD work.
- Use `SSP(path).system_structure()` when edits need archive-aware resolution of external `.ssv` and `.ssm` references.
- For SSD structure edits, prefer `ssd.xml.system` as the canonical model entry point.
- Legacy and unsupported material is kept outside the main docs flow and should not be treated as the primary API surface.
