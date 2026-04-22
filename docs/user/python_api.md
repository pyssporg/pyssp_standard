# Python API Workflows

This page is for users who want practical Python entry points without reading the full codebase.

## SSV

Use `SSV` for standalone parameter sets.

```python
from pyssp_standard import SSV

with SSV("parameters.ssv", "w") as ssv:
    ssv.xml.metadata.author = "tester"
    ssv.xml.add_parameter(parname="Weight", ptype="Real", value=20.4, unit="kg")
    ssv.xml.add_unit("kg", {"kg": 1})
```

## SSM

Use `SSM` for parameter mappings.

```python
from pyssp_standard.ssm import SSM, Ssp1Transformation

with SSM("mapping.ssm", "w") as ssm:
    ssm.xml.add_mapping("source", "target")
    ssm.xml.add_mapping(
        "scaled_source",
        "scaled_target",
        transformation=Ssp1Transformation("LinearTransformation", {"factor": 2, "offset": 0}),
    )
```

## SSD

Use `SSD` for standalone system structure files.

```python
from pyssp_standard.ssd import Component, Connection, Connector, DefaultExperiment, SSD, System

with SSD("SystemStructure.ssd", mode="w") as ssd:
    ssd.xml.name = "Demo"
    ssd.xml.version = "1.0"
    ssd.xml.default_experiment = DefaultExperiment(start_time=0.0, stop_time=1.0)

    component = Component()
    component.name = "component"
    component.component_type = "application/x-fmu-sharedlibrary"
    component.source = "resources/example.fmu"
    component.implementation = "CoSimulation"
    component.connectors.append(Connector(None, "x", "output", "Real"))

    ssd.xml.system = System(None, "system")
    ssd.xml.system.elements.append(component)
    ssd.xml.system.connectors.append(Connector(None, "x", "output", "Real"))
    ssd.xml.add_connection(Connection(start_element="component", start_connector="x", end_connector="x"))
```

## SSP

Use `SSP` when the workflow is archive-aware or directory-aware.

```python
from pyssp_standard import SSP

with SSP("system.ssp", mode="a") as ssp:
    print(ssp.resources)

    with ssp.system_structure() as ssd:
        print(ssd.xml.name)
```

When you open `SystemStructure.ssd` through `SSP`, external parameter bindings and mappings can be resolved and written back in the same session.

## FMU

Use `FMU` for `.fmu` archives or unpacked FMU directories.

```python
from pyssp_standard import FMU

with FMU("component.fmu", mode="r") as fmu:
    print(fmu.binaries)

    with fmu.model_description as md:
        print(md.xml.model_name)
        print(len(md.xml.inputs))
```

## Validation

Standalone document facades support compliance checks:

```python
with SSV("parameters.ssv") as ssv:
    assert ssv.check_compliance() is True
```

The same pattern applies to `SSM`, `SSD`, and model description workflows where supported by the facade.
