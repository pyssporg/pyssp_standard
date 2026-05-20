# Quality Attributes

> **Layer:** 02-architecture
> **Artifact type:** quality-attributes.md

## Architecture Quality Goals

| Attribute | Target | Evidence |
|-----------|--------|----------|
| **Layered separation** | Each layer owns one concern (archive, codec, model, validation, orchestration, public API) | `docs/dev/architecture.md` — 7-layer architecture with explicit rules |
| **Testability** | Codecs, models, validators, facades each testable in isolation | `pytest/` test tree mirrors the layer structure |
| **Round-trip preservation** | Read-modify-write preserves element order, annotations, extensions | `docs/dev/requirements.md` — explicit round-trip requirements |
| **Library simplicity** | Minimal external dependencies, standard library for XML and archives | All codec modules use `xml.etree.ElementTree`, archive uses `zipfile` |
| **Archive/directory transparency** | Same workflow for `.ssp` archives and unpacked directories | `common/archive_runtime.py`, `common/directory_runtime.py` share interface |

## Current Tensions

| Tension | Description | Backlog Reference |
|---------|-------------|-------------------|
| **Version routing bypass** | Facades hardcode codec/validator classes instead of using `version_routing.py` | `06-evolution/improvement-backlog.md` (G4, G10) |
| **Sprawling runtimes** | `SsdRuntime` and `LSRefExperimentsRuntime` duplicate near-identical logic | `06-evolution/improvement-backlog.md` (G8, G12); `IMP-001` |
| **Untestable reference discovery** | `_iter_external_reference_targets` is coupled to `DocumentRuntime` | `common/document_runtime.py` line 99 TODO; `IMP-002` |
| **Duplicated specs** | `EXTERNAL_REFERENCE_SPECS` local to `ssd.py` but needed by `document_runtime.py` | `06-evolution/improvement-backlog.md` (G9); `IMP-003` |
| **Bypass routing** | Facades route manually per facade instead of universally | `IMP-004` |
| **Skeleton stacks** | SSP2 and FMI3 have empty codec/model/validation | `IMP-005`, `IMP-010` |

## Evidence

- `docs/dev/architecture.md`: complete layer rules
- `docs/dev/repo_status.md`: current state vs. intended architecture
- `06-evolution/improvement-backlog.md`: architectural tensions section
- All facade modules: direct import of specific codec/validator classes