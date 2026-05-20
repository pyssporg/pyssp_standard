# Domain Model

> **Layer:** 01-product
> **Artifact type:** domain-model.md

## Core Domain Concepts

| Concept | Description | Model File |
|---------|-------------|------------|
| **SSP Archive** | Zip-based container for SSP system structure, resources, and extra files | `ssp.py` (facade) |
| **SSD (System Structure Description)** | Describes system topology: components, connectors, connections, parameter bindings | `standard/ssp1/model/ssd_model.py` |
| **SSV (Parameter Set)** | Named parameter set with typed parameters, units, and enumerations | `standard/ssp1/model/ssv_model.py` |
| **SSM (Parameter Mapping)** | Mapping from source to target with optional transformations | `standard/ssp1/model/ssm_model.py` |
| **SSB (Signal Dictionary)** | Dictionary of signal definitions for system interfaces | `standard/ssp1/model/ssb_model.py` |
| **SRMD (Simulation Resource MetaData)** | Classification and metadata for simulation resources | `standard/ssp1/model/srmd_model.py` |
| **FMU Archive** | Zip-based FMU container with binaries, documentation, and model description | `fmu.py` (facade) |
| **ModelDescription** | FMI model description: variables, unit definitions, type definitions | `standard/fmi2/model/model_description.py` |
| **LS-REF Manifest** | FMI layered standard reference manifest | `standard/ls_ref/model/manifest.py` |
| **LS-REF Experiments** | FMI layered standard reference experiments | `standard/ls_ref/model/experiments.py` |
| **External Reference** | An SSD parameter binding or mapping pointing to an external `.ssv`/`.ssm` file | `common/document_runtime.py` (ExternalReferenceSpec) |

## Key Relationships

```text
SSP Archive
├── SystemStructure.ssd (SSD)
│   ├── System
│   │   ├── Elements (Components)
│   │   ├── Connectors
│   │   ├── Connections
│   │   └── ParameterBindings → external SSV/SSM
│   └── DefaultExperiment
├── resources/
│   ├── *.fmu (FMU)
│   │   └── modelDescription.xml
│   ├── *.ssv (ParameterSet)
│   └── *.ssm (ParameterMapping)
└── extra/
    └── org.fmi-standard.fmi-ls-ref/
        ├── manifest.xml
        └── experiments.xml
```

## Model Principles

- All active models are plain Python `dataclass` objects (see `standard/ssp1/model/*`).
- Domain models reflect workflow concepts, not schema awkwardness (`02-architecture/layer-rules.md`).
- Model objects are version-specific but share a common pattern: `__init__.py` re-exports.

## Evidence

- `standard/ssp1/model/ssd_model.py`, `ssv_model.py`, `ssm_model.py`, `ssb_model.py`, `srmd_model.py`
- `standard/fmi2/model/model_description.py`
- `standard/ls_ref/model/experiments.py`, `manifest.py`
- `02-architecture/layer-rules.md`: "Domain models should reflect workflow concepts"