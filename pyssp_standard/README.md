# Internal Package Layout

This package is the new internal implementation target for the architecture rework.

Current state:
- public API compatibility is still provided by the facade in `pyssp_standard/__init__.py`
- legacy behavior still comes from `pyssp_standard_v1`
- new internal modules should land under this package and replace legacy behavior incrementally

Layout:
- `archive/`
  Archive/session layer.
- `orchestration/`
  Cross-file loading, resolution, and persistence logic.
- `validation/`
  Shared validation entry points.
- `ssp1/`, `ssp2/`
  Versioned SSP internals, each split into `generated/`, `model/`, `codec/`, and `validation/`.
- `fmi2/`, `fmi3/`
  Versioned FMI internals, each split into `generated/`, `model/`, `codec/`, and `validation/`.
