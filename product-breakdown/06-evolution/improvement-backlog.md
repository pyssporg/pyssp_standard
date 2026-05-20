# Improvement Backlog

> **Purpose:** Track candidates for improving `pyssp_standard` — structural,
> architectural, documentation, and testing improvements identified during
> exploratory analysis.
>
> **Workflow:** Each approved candidate triggers a new request that runs the
> full guarded workflow (planner → discovery → contract → architecture →
> lessons → packet → builder → verifier → review → gate → reporter).
>
> **Last updated:** 2026-05-20 (split IMP-011 into IMP-011 + IMP-013)

---

## Overview

| Priority | Open | In Progress | Done | Total |
|----------|------|-------------|------|-------|
| High     | 5    | 0           | 0    | 5     |
| Medium   | 3    | 0           | 0    | 3     |
| Low      | 5    | 0           | 0    | 5     |
| **Total**| **13**| **0**       | **0**| **13**|

---

## Individual Candidates

| ID | Title | Priority | Layer | Status |
|----|-------|----------|-------|--------|
| IMP-001 | Consolidate DocumentRuntime subclasses | High | Orchestration | candidate |
| IMP-002 | Extract reference discovery from DocumentRuntime | High | Orchestration | candidate |
| IMP-003 | Unify EXTERNAL_REFERENCE_SPECS | High | Orchestration | candidate |
| IMP-004 | Route facades through version_routing | High | Public API / Versioning | candidate |
| IMP-005 | Implement SSP2 SSV stack | Medium | Version-Specific (SSP2) | candidate |
| IMP-006 | Reconcile generated-binding metadata | Medium | Versioning / Tools | candidate |
| IMP-007 | Add explicit test coverage for DocumentRuntime | Medium | Testing | candidate |
| IMP-008 | Remove empty layer_example directory | Low | Documentation | candidate |
| IMP-009 | Add SRMD and SSB to quick-start docs | Low | Documentation | candidate |
| IMP-010 | Fill FMI3 skeleton codec/model/validation | Low | Version-Specific (FMI3) | candidate |
| IMP-011 | Support nested `<System>` in SSD model and codec | High | Domain Model / Codec | candidate |
| IMP-012 | Add option to remove Model Exchange from ModelDescription | Low | Public API | candidate |
| IMP-013 | Flatten hierarchical SSD into single-level system structure | Low | Operations | candidate |

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
├── ssd.py                         # SSD facade + SsdRuntime
├── ssv.py                         # SSV (ParameterSet) facade
├── ssm.py                         # SSM (ParameterMapping) facade
├── fmu.py                         # FMU archive entry point + package_as_ssp()
├── md.py                          # ModelDescription facade
├── ls_ref.py                      # LSRefManifest + LSRefExperiments + Runtime
├── srmd.py                        # SRMD facade
├── ssb.py                         # SSB facade
├── todo.md                        # Known technical debt notes
│
├── common/                        # Shared implementation layer
│   ├── archive.py                 #   Zip unpack/repack
│   ├── archive_runtime.py         #   Context-managed archive runtime
│   ├── directory_runtime.py       #   Directory-based file runtime
│   ├── document_runtime.py        #   Cross-document reference resolution
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
| **Orchestration** | Cross-file resolution, archive-aware sessions | `common/document_runtime.py`, `ssp.py` (SsdRuntime) |
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
| `LSRefExperimentsRuntime` | `ls_ref.py` |
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
| G7 | DocumentRuntime reference discovery untestable | Code quality | Cannot unit-test reference discovery |
| G8 | Specialized runtimes should be inlined | Code quality | Duplicated boilerplate |
| G9 | EXTERNAL_REFERENCE_SPECS duplicated | Code quality | Import dependency issue |
| G10 | Loose coupling between facade and codec/validator | Architecture | Bypasses routing abstraction |
| G11 | SSP2 SSV registered but not implemented | Missing impl | Dead registration |
| G12 | ls_ref.py and ssd.py define near-identical runtimes | Code quality | Duplication |
| G13 | No SSP2/FMI3 user docs | Doc gap | Unclear version support |
| G14 | Empty layer_example directory | Doc gap | Dead directory |
| G15 | SRMD/SSB not in quick-start | Doc gap | Hidden capability |
| G16 | No CLI docs | Doc gap | No discoverable CLI path |
| G17 | No SSP2/FMI3 tests | Test gap | No coverage |
| G18 | No dedicated document_runtime tests | Test gap | TODO noted in source |
| G19 | No benchmarks | Test gap | Performance regression risk |

---

## Architectural Tensions (Key Insights)

1. **Version routing bypassed** — Facades import codec/validator classes
   directly instead of querying `version_routing.py`. The routing layer
   exists but is not the universal dispatch mechanism.

2. **DocumentRuntime subclass sprawl** — `SsdRuntime` and
   `LSRefExperimentsRuntime` are thin subclasses with near-identical logic.
   `todo.md` flags these as unnecessary.

3. **Reference specs duplicated** — `EXTERNAL_REFERENCE_SPECS` is local to
   `ssd.py` but needed by `common/document_runtime.py`.

4. **SSP2/FMI3 skeletons** — Directory structure exists for SSP2 and FMI3
   but has no implementation. The version routing already references SSP2 SSV.

---

*This backlog was initialized by the Improvement Workflow (iteration 1) on
2026-05-20. No files were modified during the analysis; all proposed changes
require explicit approval.*