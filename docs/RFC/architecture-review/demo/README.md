# RFC1 Hybrid Architecture Mockup

This folder contains a limited-functionality prototype showing the **hybrid layered architecture** proposed in `docs/RFC/architecture-review/__overview__.md`.

## What it demonstrates
- Shared `archive` layer: deterministic dirty tracking and explicit save.
- One unified example track: `examples/ssd_binding_modes`.
- Hybrid codec for `ParameterSet`: generated-style bindings + handwritten domain mapping.
- Handwritten SSD codec using storage strategy pattern for parameter bindings:
  - inline SSV payload
  - external SSV file reference
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

The merged demo (`examples/ssd_binding_modes/run_demo.py`):
1. Loads `data/inline_example.ssd` and parses inline SSV binding.
2. Loads `data/external_example.ssd` and resolves external SSV binding.
3. Adds a parameter through one public API for both modes.
4. Runs shared semantic validation and saves all updated files.
