# Getting Started

This page is for users who want the fastest path to reading or editing SSP-related files with `pyssp_standard`.

## Install

Install the package from the repository root:

```bash
pip install .
```

## Choose The Right Entry Point

Use these facades depending on the file you are working with:

- `SSP` for `.ssp` archives or unpacked SSP directories
- `SSD` for a standalone `SystemStructure.ssd`
- `SSV` for `.ssv` parameter sets
- `SSM` for `.ssm` parameter mappings
- `FMU` for `.fmu` archives or unpacked FMU directories

## First Success

Validate an existing parameter set:

```python
from pyssp_standard import SSV

with SSV("parameters.ssv") as ssv:
    assert ssv.check_compliance() is True
```

Open an SSP and inspect its system structure:

```python
from pyssp_standard import SSP

with SSP("system.ssp", mode="r") as ssp:
    with ssp.system_structure() as ssd:
        print(ssd.xml.name)
        print(len(ssd.xml.connections()))
```

## External References

There is one important workflow distinction:

- `SSD(path)` works on the SSD file only
- `SSP(path).system_structure()` is the archive-aware entry point and resolves external `.ssv` and `.ssm` references while the context is open

Use the SSP entry point when a task spans `SystemStructure.ssd` and referenced parameter files in one session.

## Next Pages

- Go to [Python API workflows](user/python_api.md) for focused examples
- Go to [Command reference](command_reference.md) for common test and docs commands
