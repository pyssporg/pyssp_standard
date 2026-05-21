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
- `SRMD` for `.srmd` simulation resource meta data
- `SSB` for `.ssb` signal dictionaries
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
        assert ssd.xml.system is not None
        print(len(ssd.xml.system.get_connections()))
```

## External References

There is one important workflow distinction:

- `SSD(path)` works on the SSD file only
- `SSP(path).system_structure()` is the archive-aware entry point and resolves external `.ssv` and `.ssm` references while the context is open

Use the SSP entry point when a task spans `SystemStructure.ssd` and referenced parameter files in one session.

### Simulation Resource Meta Data (SRMD)

SRMD describes resource requirements for simulation (compute resources, tool versions, license information):

```python
from pyssp_standard import SRMD
with SRMD("path/to/resources.srmd") as srmd:
    print(srmd.xml)
```

### Signal Dictionary (SSB)

SSB defines signal dictionaries used for signal-based communication between components:

```python
from pyssp_standard import SSB
with SSB("path/to/dictionary.ssb") as ssb:
    print(ssb.xml)
```

## Next Pages

- Go to [Python API workflows](user/python_api.md) for focused examples
- Go to [Command reference](command_reference.md) for common test and docs commands
