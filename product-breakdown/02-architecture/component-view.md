# Component View

> **Layer:** 02-architecture
> **Artifact type:** component-view.md

## Layer Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                     Public API Facades                           │
│  SSP │ SSD │ SSV │ SSM │ FMU │ MD │ SRMD │ SSB │ LSRef*        │
│  pyssp_standard/ssp.py, ssd.py, ssv.py, ssm.py, fmu.py, ...    │
└──────────────────────────┬──────────────────────────────────────┘
                           │ depends on
┌──────────────────────────▼──────────────────────────────────────┐
│                      Orchestration                               │
│  DocumentRuntime │ ArchiveRuntimes │ DirectoryRuntimes           │
│  pyssp_standard/common/document_runtime.py                      │
│  pyssp_standard/common/archive_runtime.py                       │
│  pyssp_standard/common/directory_runtime.py                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ dispatches
┌──────────────────────────▼──────────────────────────────────────┐
│                    Standard-Specific Stacks                      │
│  SSP1 │ SSP2* │ FMI2 │ FMI3* │ LS-REF                            │
│  ┌─────────┐ ┌─────────┐ ┌──────────────┐                      │
│  │ codec   │ │ model   │ │ validation   │                      │
│  └─────────┘ └─────────┘ └──────────────┘                      │
│  pyssp_standard/standard/<family>/codec/model/validation/       │
└──────────────────────────┬──────────────────────────────────────┘
                           │ backed by
┌──────────────────────────▼──────────────────────────────────────┐
│                   Schema / Tooling                               │
│  XSD files │ schema_targets │ version_routing                   │
│  pyssp_standard/schema/                                         │
│  pyssp_standard/tools/schema_targets.py                         │
│  pyssp_standard/standard/version_routing.py                    │
└─────────────────────────────────────────────────────────────────┘

* = skeleton (codec/model/validation directories exist but are empty)
```

## Component Descriptions

| Component | Location | Responsibility |
|-----------|----------|----------------|
| **Public API Facades** | `pyssp_standard/*.py` (top-level) | Thin user-facing entry points, delegate to codec/model/validation |
| **Orchestration** | `common/document_runtime.py` | Cross-file reference resolution, archive-aware sessions |
| **Archive Layer** | `common/archive.py`, `archive_runtime.py`, `directory_runtime.py` | Zip unpack/repack, directory abstraction, context management |
| **Codec** | `standard/<family>/codec/` | XML parse/serialize per document type, standalone XML logic |
| **Domain Model** | `standard/<family>/model/` | In-memory dataclass document shapes |
| **Validation** | `standard/<family>/validation/` | Schema + semantic validation per document type |
| **Version Routing** | `standard/version_routing.py` | Document-root detection, standard stack registry |
| **Cross-Standard Ops** | `standard/operations/` | FMI→SSP composition and helpers |
| **Schema Targets** | `tools/schema_targets.py` | XSD path registry for tooling |
| **Shared XML** | `common/xml_document.py`, `standard/ssp1/codec/xml_utils.py` | Base XmlDocument facade, shared XML helpers |

## Dependencies Between Components

| Dependent | Depends On | Nature |
|-----------|-----------|--------|
| Public Facades | Orchestration, Codec, Model, Validation | Direct instantiation (bypasses routing) |
| Orchestration (DocumentRuntime) | Archive Layer, Codec, Model | Archive-aware resolution |
| Codec | Model | Parse → model, Serialize ← model |
| Validation | Model, Schema | Schema + semantic checks |
| Cross-Standard Ops | Multiple Models | Composition (e.g., FMI→SSP) |
| Version Routing | Tools/Schema Targets | Registry lookup |

## Standard Stack Implementations

| Standard | Codec | Model | Validation | Operations |
|----------|-------|-------|------------|------------|
| SSP1 | Active | Active | Active | Active |
| SSP2 | Skeleton | Skeleton | Skeleton | None |
| FMI2 | Active | Active | Active | None |
| FMI3 | Skeleton | Skeleton | Skeleton | None |
| LS-REF | Active | Active | Active | None |

## Evidence

- `docs/dev/architecture.md`: layer definitions with responsibilities and rules
- `docs/dev/repo_status.md`: current implementation state per layer
- Directory structure of `standard/` families
- `product-breakdown/06-evolution/improvement-backlog.md`: module tree