# Scope

> **Layer:** 01-product
> **Question:** What should it do?

## In Scope

| Artifact | Standards | Status |
|----------|-----------|--------|
| SSP (System Structure Package) — `.ssp` | SSP1 | Active |
| SSD (System Structure Description) — `.ssd` | SSP1 | Active |
| SSV (Parameter Set) — `.ssv` | SSP1 | Active |
| SSM (Parameter Mapping) — `.ssm` | SSP1 | Active |
| SSB (Signal Dictionary) — `.ssb` | SSP1 | Active |
| SRMD (Simulation Resource MetaData) — `.srmd` | SSP1 | Active |
| FMU (Functional Mock-up Unit) — `.fmu` | FMI2 | Active |
| ModelDescription — `modelDescription.xml` | FMI2 | Active |
| LS-REF Manifest — `manifest.xml` | LS-REF (FMI3 layered std) | Active |
| LS-REF Experiments — `experiments.xml` | LS-REF (FMI3 layered std) | Active |

## Out of Scope (Current)

- SSP2 document processing (skeleton exists)
- FMI3 document processing (skeleton exists)
- End-user CLI tool
- GUI or graphical editors
- FMU simulation or co-simulation runtime
- Performance benchmarking
- Cross-standard validation (e.g., FMI→SSP consistency)

## Boundary Decision

The library focuses on scriptable, layered artifact manipulation. It does not
aim to be a full SSP authoring environment. Archive I/O, XML parse/serialize,
in-memory models, validation, orchestration, and public API are separated into
distinct layers to support reuse and testability.

## Evidence

- `product-breakdown/index.md`: document types table with status
- `pyssp_standard/__init__.py`: 12 exported symbols
- `docs/dev/repo_status.md`: layer status per standard family
- `docs/dev/requirements.md`: scope paragraph