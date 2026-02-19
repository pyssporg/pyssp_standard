# RFC1 Hybrid Architecture Mockup

This folder contains a limited-functionality prototype showing the **hybrid layered architecture** proposed in `docs/architecture-review.md`.

## What it demonstrates
- Shared `archive` layer: deterministic dirty tracking and explicit save.
- Two separated example tracks:
  - `examples/ssv_hybrid`: generated-style XML dataclasses plus handwritten mapper and public API facade.
  - `examples/ssd_handwritten`: fully handwritten model/codec/validation path without generated bindings.
- `validation` layer in each track: semantic checks separate from XML parsing.
- `public API facade` in each track: stable API surface wrapping layered internals.

## Scope limits
- Only a small subset of SSP2 SSV is modeled:
  - `ParameterSet`
  - `Parameter`
  - scalar `Real` values
- Only a small subset of SSD is modeled:
  - `SystemStructureDescription`
  - `Component` (name + source)
  - `Connection` (component-level references)
- This is a discussion mockup, not production code.

## Run demo
From repo root:

```bash
python3 RFC1_architecture-review/examples/ssv_hybrid/run_demo.py
python3 RFC1_architecture-review/examples/ssd_handwritten/run_demo.py
```

The SSV hybrid demo (`examples/ssv_hybrid/run_demo.py`):
1. Loads `examples/ssv_hybrid/data/example.ssv` through the public API facade.
2. Validates semantics.
3. Adds a parameter using domain APIs.
4. Saves back to the example file and copies to `examples/ssv_hybrid/data/example_out.ssv`.

The SSD handwritten demo (`examples/ssd_handwritten/run_demo.py`):
1. Loads `examples/ssd_handwritten/data/example.ssd` through a public API facade.
2. Uses handwritten (non-generated) codec parsing.
3. Adds a component and connection.
4. Runs semantic validation and saves back to disk.
