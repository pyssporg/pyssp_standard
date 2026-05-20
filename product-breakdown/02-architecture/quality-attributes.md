# Quality Attributes

> **Layer:** 02-architecture
> **Artifact type:** quality-attributes.md

## Architecture Quality Goals

| Attribute | Target | Evidence |
|-----------|--------|----------|
| **Layered separation** | Each layer owns one concern (archive, codec, model, validation, orchestration, public API) | `02-architecture/layer-rules.md` — per-layer rules |
| **Testability** | Codecs, models, validators, facades each testable in isolation | `pytest/` test tree mirrors the layer structure |
| **Round-trip preservation** | Read-modify-write preserves element order, annotations, extensions | `04-verification/acceptance-criteria.md` — round-trip criteria |
| **Library simplicity** | Minimal external dependencies, standard library for XML and archives | All codec modules use `xml.etree.ElementTree`, archive uses `zipfile` |
| **Archive/directory transparency** | Same workflow for `.ssp` archives and unpacked directories | `common/archive_runtime.py`, `common/directory_runtime.py` share interface |

## Current Implementation Direction

The active implementation favors:
- Plain dataclass document models
- Direct `xml.etree.ElementTree` codecs
- Small shared XML helper utilities when they reduce duplication
- Thin top-level facades over shared document runtime behavior
- Cross-standard composition helpers under `standard/operations/`
- SSP1 composition helpers under `standard/ssp1/operations/`

## Layer Status (Current Reality)

| Layer | Status | Notes |
|-------|--------|-------|
| **Archive** | Active | Lives under `common/`, no dedicated `archive/` package |
| **Schema/Binding** | Active (partial) | Schemas tracked and registered; generated binding output paths registered but runtime no longer depends on them |
| **Codec** | Active (SSP1, FMI2, LS-REF) | Direct ElementTree codecs. SSP2 and FMI3 are skeleton (empty). |
| **Domain Model** | Active (SSP1, FMI2, LS-REF) | Dataclass models. SSP2 and FMI3 none. |
| **Validation** | Active (SSP1, FMI2, LS-REF) | SSP1 validation most complete. SSP2 and FMI3 none. |
| **Orchestration** | Active (partial) | Archive-aware behavior implemented; version routing exists but is not universal dispatch |
| **Public API** | Active (partial) | Facades are thin wrappers but hardcode codec/validator classes directly |

## Version Routing Status

- Registered stacks: SSP1 (SSV, SSD, SSM), SSP2 (SSV), FMI2 (model description)
- Detects document roots for those registered types
- Not the universal entry point for every public facade

## Current Tensions

| Tension | Description | Backlog Reference |
|---------|-------------|-------------------|
| **Version routing bypass** | Facades hardcode codec/validator classes instead of using `version_routing.py` | `06-evolution/improvement-backlog.md` (G4, G10) |
| **Sprawling runtimes** | `SsdRuntime` and `LSRefExperimentsRuntime` duplicate near-identical logic | `06-evolution/improvement-backlog.md` (G8, G12); `IMP-001` |
| **Untestable reference discovery** | `_iter_external_reference_targets` is coupled to `DocumentRuntime` | `common/document_runtime.py` line 99 TODO; `IMP-002` |
| **Duplicated specs** | `EXTERNAL_REFERENCE_SPECS` local to `ssd.py` but needed by `document_runtime.py` | `06-evolution/improvement-backlog.md` (G9); `IMP-003` |
| **Bypass routing** | Facades route manually per facade instead of universally | `IMP-004` |
| **Skeleton stacks** | SSP2 and FMI3 have empty codec/model/validation | `IMP-005`, `IMP-010` |