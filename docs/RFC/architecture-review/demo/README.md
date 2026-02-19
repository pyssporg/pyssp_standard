# RFC1 Hybrid Architecture Mockup

This folder contains a limited-functionality prototype showing the **hybrid layered architecture** proposed in `docs/RFC/architecture-review/__overview__.md`.

## What it demonstrates
- Shared `archive` layer: deterministic dirty tracking and explicit save.
- One unified example track: `examples/ssd_binding_modes`.
- Hybrid codec for `ParameterSet`: generated-style bindings + handwritten domain mapping.
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
python3 docs/RFC/architecture-review/demo/examples/ssd_binding_modes/run_demo.py
```

## Generate bindings
The merged example uses real `xsdata`-generated bindings from:
- `examples/ssd_binding_modes/generated/SystemStructureParameterValues.xsd`

Use the project venv where `xsdata` is installed:

```bash
../pycps_sysml/venv/bin/python -m xsdata generate \
  docs/RFC/architecture-review/demo/examples/ssd_binding_modes/generated/SystemStructureParameterValues.xsd \
  -p docs.RFC.architecture_review.demo.examples.ssd_binding_modes.generated.bindings \
  -ss single-package \
  --relative-imports
```

Then copy the generated module into the demo import location:

```bash
cp -f docs/rfc/architecture_review/demo/examples/ssd_binding_modes/generated/bindings.py \
  docs/RFC/architecture-review/demo/examples/ssd_binding_modes/generated/ssv2_generated_types.py
```

Notes:
- Ensure `SystemStructureCommon.xsd` is present next to `SystemStructureParameterValues.xsd`.
- If `xsdata` fails because `ruff` is missing in `PATH`, add a temporary no-op `ruff` shim or install `ruff`.
- Run the demo with the same venv Python if system Python does not have `xsdata` installed.

The merged demo (`examples/ssd_binding_modes/run_demo.py`):
1. Loads `data/mixed_example.ssd`.
2. Parses one inline SSV binding and one external SSV reference in the same SSD.
3. Resolves the external SSV only at SSP orchestration level.
4. Adds a parameter through one public API for both modes.
5. Runs shared semantic validation and saves updated files.
