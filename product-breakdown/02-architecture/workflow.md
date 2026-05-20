# Workflow

> **Layer:** 02-architecture
> **Artifact type:** workflow.md

## Core Flow

Recommended flow through the library:

1. **Archive or file runtime** opens the working context
2. **Version routing** selects the correct standard stack
3. **Codec** parses or serializes XML text
4. **Validation** checks schema and semantic rules
5. **Orchestration** resolves related artifacts and persistence order
6. **Public API** exposes the editing workflow

## Archive-Aware SSP Session

For a typical archive-aware `SSP` system-structure session:

1. `SSP` opens an archive or directory runtime
2. `ssp.system_structure()` creates an archive-aware SSD session
3. The SSD facade loads `SystemStructure.ssd` through its codec stack
4. Orchestration resolves referenced `.ssv` and `.ssm` files
5. Callers edit the hydrated in-memory model
6. External artifacts are saved first
7. The SSD is saved in reference form
8. The archive runtime persists the final package state

## Standalone Document Session

For a standalone `SSV` or `SSM`:

1. The facade opens a single file
2. The codec parses it into the canonical model
3. Edits happen on that model
4. Validation and save operate on that single-file context

## Where New Code Should Go

| Concern | Primary code home |
|---------|-------------------|
| Archive mechanics | `common/archive/` helpers |
| Version selection | `standard/version_routing.py` |
| Standard-specific models | `standard/<family>/<version>/model/` |
| Standard-specific parse/serialize | `standard/<family>/<version>/codec/` |
| Standard-specific validation | `standard/<family>/<version>/validation/` |
| Cross-standard composition | `standard/operations/` |
| User-facing wrapper behavior | Top-level facade modules (`ssv.py`, `ssp.py`, etc.) |

## Code Placement Checklist

Before adding code, check:

- Is this XML-shape logic, model logic, orchestration logic, or public facade logic?
- Does it belong to one standard version, or is it shared?
- Can it be pushed down into codec, model, or validation instead of growing the public facade?