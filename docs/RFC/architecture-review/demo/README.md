# RFC1 Hybrid Architecture Mockup

This folder contains a limited-functionality prototype showing the **hybrid layered architecture** proposed in `docs/RFC/architecture-review/__overview__.md`.

## What it demonstrates
- Shared `archive` layer: deterministic dirty tracking and explicit save.
- One unified example in this `demo/` package.
- `xsdata`-backed codec for `ParameterSet`: generated bindings + handwritten domain mapping.
- Handwritten SSD codec using storage strategy pattern for parameter bindings:
  - inline SSV payload
  - external SSV file reference
- SSD codec is XML-only (no file I/O).
- SSP-level orchestrator resolves external references after parsing related files.
- `validation` layer: semantic checks separate from XML parsing.
- `public API facade`: stable API surface wrapping layered internals.

## Scope limits
- Only a small subset of SSP2 SSV is modeled:
  - `ParameterSet`
  - `Parameter`
  - scalar `Real` values
- Only a small subset of SSD is modeled:
  - `SystemStructureDescription`
  - `Component` (name + source)
  - `ParameterBinding` with two modes: `inline`, `external`
- This is a discussion mockup, not production code.

## Run demo
From repo root:

```bash
./venv/bin/python docs/RFC/architecture-review/demo/run_demo.py
```

## Generate bindings
The merged example uses real `xsdata`-generated bindings from:
- `generated/SystemStructureParameterValues.xsd`

Use the repo venv:

```bash
./venv/bin/python docs/RFC/architecture-review/demo/generated/generate_ssv_bindings.py
```

Notes:
- Ensure `SystemStructureCommon.xsd` is present next to `SystemStructureParameterValues.xsd`.
- The wrapper script prefixes the repo venv `bin` directory on `PATH` so `xsdata` can invoke `ruff` during generation.
- Run the demo with the same venv Python if system Python does not have `xsdata` installed.

The merged demo (`run_demo.py`):
1. Loads `__data__/mixed_example.ssd`.
2. Parses one inline SSV binding and one external SSV reference in the same SSD.
3. Resolves the external SSV only at SSP orchestration level.
4. Adds a parameter through one public API for both modes.
5. Runs shared semantic validation and saves updated files.

## xsdata wrapper proof of concept
The demo now uses `xsdata` directly as the schema authority and keeps only a small handwritten
mapping layer for the public-facing domain model.

Regenerate the checked-in generated module with:

```bash
./venv/bin/python docs/RFC/architecture-review/demo/generated/generate_ssv_bindings.py
```

The goal is a smaller authority chain for one narrow slice:
`XSD -> xsdata generated bindings -> demo codec/domain mapping`
