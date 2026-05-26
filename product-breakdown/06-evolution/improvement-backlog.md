# Improvement Backlog

> **Purpose:** Track candidates for improving `pyssp_standard` — structural,
> architectural, documentation, and testing improvements identified during
> exploratory analysis.
>
> **Workflow:** Each approved candidate triggers a new request that runs the
> full guarded workflow (planner → discovery → contract → architecture →
> lessons → packet → builder → verifier → review → gate → reporter).
>
> **Last updated:** 2026-05-26 (added IMP-019 — lifecycle-safe FMU iteration over SSP components)

---

## Overview

| Priority | Open | In Progress | Done | Total |
|----------|------|-------------|------|-------|
| High     | 2    | 0           | 5    | 7     |
| Medium   | 2    | 0           | 3    | 5     |
| Low      | 2    | 0           | 5    | 7     |
| **Total**| **6** | **0**       | **13**| **19**|

---

## Individual Candidates

| ID | Title | Priority | Layer | Status |
|----|-------|----------|-------|--------|
| IMP-001 | Consolidate DocumentRuntime subclasses | High | Orchestration | done |
| IMP-002 | Extract reference discovery from DocumentRuntime | High | Orchestration | done |
| IMP-003 | Unify EXTERNAL_REFERENCE_SPECS | High | Orchestration | done |
| IMP-004 | Route facades through version_routing | High | Public API / Versioning | done |
| IMP-005 | Implement SSP2 SSV stack | Medium | Version-Specific (SSP2) | done |
| IMP-006 | Reconcile generated-binding metadata | Medium | Versioning / Tools | done |
| IMP-007 | Add explicit test coverage for DocumentRuntime | Medium | Testing | done |
| IMP-008 | Remove empty layer_example directory | Low | Documentation | done |
| IMP-009 | Add SRMD and SSB to quick-start docs | Low | Documentation | done |
| IMP-010 | Fill FMI3 skeleton codec/model/validation | Low | Version-Specific (FMI3) | done |
| IMP-011 | Support nested `<System>` in SSD model and codec | High | Domain Model / Codec | done |
| IMP-012 | Add option to remove Model Exchange from ModelDescription | Low | Public API | done |
| IMP-013 | Flatten hierarchical SSD into single-level system structure | Low | Operations | done |
| IMP-014 | Version-aware SSV facade through version routing | High | Public API | proposed |
| IMP-015 | SSP2 SSV facade-level tests | Medium | Testing | proposed |
| IMP-016 | SSP2 SSV inline parameter set support in SSD facade | Low | Domain Model / Operations | proposed |
| IMP-017 | Automated standard version identification in XmlDocument | Medium | Public API / Versioning | proposed |
| IMP-018 | Bulk FMU import from directory via add_fmu_directory() | Low | Public API | proposed |
| IMP-019 | Lifecycle-safe FMU iteration over SSP components | Medium | Operations / Public API | proposed |

---

## Product Structure Map

### Overview

`pyssp_standard` is a Python library for inspecting, creating, and editing
SSP-related artifacts (`.ssp`, `.ssd`, `.ssv`, `.ssm`) as well as FMU archives
and FMI `modelDescription.xml`. It follows a layered XML-document workflow:
archive runtime → version routing → codec parse/serialize → validation →
orchestration → thin public facades.

### Module Tree

```
pyssp_standard/
├── __init__.py                    # Public API surface exports
├── ssp.py                         # SSP archive entry point (context-managed)
├── ssd.py                         # SSD facade
├── ssv.py                         # SSV (ParameterSet) facade
├── ssm.py                         # SSM (ParameterMapping) facade
├── fmu.py                         # FMU archive entry point + package_as_ssp()
├── md.py                          # ModelDescription facade
├── ls_ref.py                      # LSRefManifest + LSRefExperiments
├── srmd.py                        # SRMD facade
├── ssb.py                         # SSB facade
├── todo.md                        # Known technical debt notes
│
├── common/                        # Shared implementation layer
│   ├── archive.py                 #   Zip unpack/repack
│   ├── archive_runtime.py         #   Context-managed archive runtime
│   ├── directory_runtime.py       #   Directory-based file runtime
│   ├── document_runtime.py        #   Cross-document reference resolution
│   ├── reference_specs.py         #   External reference specifications (SSV, SSM)
│   ├── reference_discovery.py     #   Standalone external reference discovery
│   ├── xml_document.py            #   Base XmlDocument[T] facade
│   └── xml_schema_validation.py   #   XSD-backed XML validator
│
├── standard/                      # Standard-specific stacks
│   ├── version_routing.py         #   Document-root detection + registry
│   ├── unit_conversion.py         #   Minimal base-unit definitions
│   ├── common/
│   │   └── utils.py               #   Shared helpers
│   ├── operations/
│   │   └── model_description_to_ssd.py  # FMI→SSP composition
│   ├── ssp1/                      # [ACTIVE] Full SSP1 impl.
│   │   ├── codec/
│   │   ├── model/
│   │   ├── operations/
│   │   └── validation/
│   ├── ssp2/                      # [SKELETON]
│   │   ├── codec/       (empty)
│   │   ├── model/       (empty)
│   │   └── validation/  (empty)
│   ├── fmi2/                      # [ACTIVE] Full FMI2 impl.
│   │   ├── codec/
│   │   ├── model/
│   │   └── validation/
│   ├── fmi3/                      # [SKELETON]
│   │   ├── codec/       (empty)
│   │   ├── model/       (empty)
│   │   └── validation/  (empty)
│   └── ls_ref/                    # [ACTIVE] LS-REF impl.
│       ├── codec/
│       ├── model/
│       └── validation/
│
├── tools/
│   └── schema_targets.py          # Schema target registration
│
└── schema/                        # Vendored XSD schema files
    ├── SSP1/
    ├── SSP2/
    ├── FMI2/
    ├── FMI3/
    ├── SSP-LS-Traceability/
    └── _shared/
```

### Layer Responsibilities

| Layer | Responsibility | Primary Location |
|-------|---------------|-----------------|
| **Public API** | Thin user-facing facades | `ssp.py`, `ssd.py`, `ssv.py`, `ssm.py`, `fmu.py`, `md.py`, `ls_ref.py`, `srmd.py`, `ssb.py` |
| **Orchestration** | Cross-file resolution, archive-aware sessions | `common/document_runtime.py`, `common/reference_discovery.py` |
| **Archive** | Zip unpack/repack, directory abstraction | `common/archive.py`, `common/archive_runtime.py`, `common/directory_runtime.py` |
| **Codec** | XML parse/serialize per document type | `standard/<family>/codec/` |
| **Domain Model** | In-memory dataclass shapes | `standard/<family>/model/` |
| **Validation** | XSD schema + semantic rules | `standard/<family>/validation/` |
| **Schema/Binding** | XSD files + registrations | `schema/`, `tools/schema_targets.py` |
| **Cross-Standard Ops** | FMI↔SSP composition | `standard/operations/` |

### Public API Surface

Exported from `__init__.py`:

| Symbol | Source Module |
|--------|---------------|
| `SSP` | `ssp.py` |
| `SSD` | `ssd.py` |
| `SSM` | `ssm.py` |
| `SSV` | `ssv.py` |
| `FMU` | `fmu.py` |
| `ModelDescription` | `md.py` |
| `SRMD` | `srmd.py` |
| `SSB` | `ssb.py` |
| `LSRefManifest` | `ls_ref.py` |
| `LSRefExperiments` | `ls_ref.py` |
| `LS_REF_EXTRA_DIR` (constant) | `ls_ref.py` |
| `get_repo_root()` (function) | `__init__.py` |

### Test Structure

```
pytest/
├── conftest.py                    # Shared fixtures
├── ssp1/
│   ├── codec/                     # XML round-trip tests
│   ├── facade/                    # Public API tests
│   └── orchestration/             # Archive-aware workflow tests
├── common/                       # Common layer tests (reference discovery, etc.)
├── fmi2/
│   ├── archive/                   # FMU workflow tests
│   ├── codec/                     # ModelDescription codec tests
│   └── facade/                    # ModelDescription facade tests
├── ls_ref/
│   ├── codec/                     # LS-REF codec tests
│   └── facade/                    # LS-REF facade tests
├── tools/                         # Schema target, validation, routing tests
└── legacy_unsupported/            # Out-of-maintenance tests
```

### Documentation Structure

```
docs/
├── index.md                    # Documentation router
├── getting_started.md          # Installation + first workflow
├── command_reference.md        # Dev commands (no CLI exists)
├── user/
│   └── python_api.md           # Python API examples
├── dev/
│   ├── repo_map.md             # Codebase orientation
│   ├── code_disposition.md     # Layer-to-file map
│   ├── architecture.md         # Internal layer boundaries
│   ├── repo_status.md          # Implementation reality
│   ├── guidelines.md           # Code/doc conventions
│   └── requirements.md         # Behavioral requirements
└── integrations/
    └── read_the_docs.md        # RTD publishing setup
```

---

## Gap Summary

| # | Gap | Category | Impact |
|---|-----|----------|--------|
| G1 | SSP2 codec/model/validation are empty | Missing impl | Cannot parse SSP2 documents |
| G2 | FMI3 codec/model/validation are empty | Missing impl | Cannot parse FMI3 documents |
| G3 | Generated binding paths referenced but absent | Dead metadata | Risk of ImportError |
| G4 | Facades hardcode codecs instead of version routing | Architecture | Adding version requires facade change |
| G5 | No end-user CLI | Missing feature | Python API only |
| G6 | No cross-standard integration tests | Test gap | Risk of regression |
| G7 | DocumentRuntime reference discovery untestable | Code quality | (resolved - IMP-002) |
| G8 | Specialized runtimes should be inlined | Code quality | (resolved - IMP-001) |
| G9 | EXTERNAL_REFERENCE_SPECS duplicated | Code quality | (resolved - IMP-003) |
| G10 | Loose coupling between facade and codec/validator | Architecture | Bypasses routing abstraction |
| G11 | SSP2 SSV registered but not implemented | Missing impl | Dead registration |
| G12 | ls_ref.py and ssd.py define near-identical runtimes | Code quality | (resolved - G12 merged into IMP-001) |
| G13 | No SSP2/FMI3 user docs | Doc gap | Unclear version support |
| G14 | Empty layer_example directory | Doc gap | (directory already removed) |
| G15 | SRMD/SSB not in quick-start | Doc gap | Hidden capability |
| G16 | No CLI docs | Doc gap | No discoverable CLI path |
| G17 | No SSP2/FMI3 tests | Test gap | No coverage |
| G18 | No dedicated document_runtime tests | Test gap | (resolved - IMP-007) |
| G19 | No benchmarks | Test gap | Performance regression risk |

---

## Architectural Tensions (Key Insights)

1. **Version routing bypassed** — Facades import codec/validator classes
   directly instead of querying `version_routing.py`. The routing layer
   exists but is not the universal dispatch mechanism.

2. **DocumentRuntime subclass sprawl** — Resolved (IMP-001): `SsdRuntime` and
   `LSRefExperimentsRuntime` have been removed. Both are now direct uses of
   `DocumentRuntime[...]`.

3. **Reference specs duplicated** — Resolved (IMP-003): `EXTERNAL_REFERENCE_SPECS`
   moved to `common/reference_specs.py`.

4. **SSP2/FMI3 skeletons** — Directory structure exists for SSP2 and FMI3
   but has no implementation. The version routing already references SSP2 SSV.

---

*This backlog was initialized by the Improvement Workflow (iteration 1) on
2026-05-20. No files were modified during the analysis; all proposed changes
require explicit approval.*