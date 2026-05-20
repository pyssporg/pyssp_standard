# Code Structure

> **Layer:** 03-implementation
> **Artifact type:** code-structure.md

## Package Layout

```
pyssp_standard/
├── __init__.py              # Public API exports + get_repo_root()
├── ssp.py                   # SSP archive facade (context-managed)
├── ssd.py                   # SSD facade + SsdRuntime + EXTERNAL_REFERENCE_SPECS
├── ssv.py                   # SSV ParameterSet facade
├── ssm.py                   # SSM ParameterMapping facade
├── fmu.py                   # FMU archive facade + package_as_ssp()
├── md.py                    # ModelDescription facade
├── ls_ref.py                # LSRefManifest + LSRefExperiments + Runtime
├── srmd.py                  # SRMD facade
├── ssb.py                   # SSB facade
├── todo.md                  # Known technical debt notes (2 items)
│
├── common/                  # Shared implementation
│   ├── archive.py           #   ZipFile unpack/repack
│   ├── archive_runtime.py   #   Context-managed archive runtime + create_runtime()
│   ├── directory_runtime.py #   Directory-based file runtime
│   ├── document_runtime.py  #   Cross-document reference resolution
│   ├── xml_document.py      #   Base XmlDocument[T] facade (shared lifecycle)
│   └── xml_schema_validation.py  # XSD-backed validation
│
├── standard/                # Standard-specific logic
│   ├── version_routing.py   #   Document-root detection + ParseStackSpec registry
│   ├── unit_conversion.py   #   Base-unit definitions (minimal)
│   ├── common/              #   Shared standard helpers
│   │   └── utils.py
│   ├── operations/          #   Cross-standard composition
│   │   └── model_description_to_ssd.py
│   ├── ssp1/                #   [ACTIVE] Full SSP1
│   │   ├── codec/           #     6 codec modules
│   │   ├── model/           #     7 model modules
│   │   ├── operations/      #     3 operation modules
│   │   └── validation/      #     6 validation modules
│   ├── ssp2/                #   [SKELETON] Empty
│   │   ├── codec/ (empty)
│   │   ├── model/ (empty)
│   │   └── validation/ (empty)
│   ├── fmi2/                #   [ACTIVE] Full FMI2
│   │   ├── codec/           #     1 codec module
│   │   ├── model/           #     1 model module
│   │   └── validation/      #     1 validation module
│   ├── fmi3/                #   [SKELETON] Empty
│   │   ├── codec/ (empty)
│   │   ├── model/ (empty)
│   │   └── validation/ (empty)
│   └── ls_ref/              #   [ACTIVE] LS-REF
│       ├── codec/           #     2 codec modules
│       ├── model/           #     2 model modules
│       └── validation/      #     2 validation modules
│
├── tools/
│   └── schema_targets.py    #   Schema target registration (10 targets)
│
└── schema/                  # Vendored XSD files
    ├── SSP1/
    ├── SSP2/
    ├── FMI2/
    ├── FMI3/
    ├── SSP-LS-Traceability/
    └── _shared/
```

## Key Architectural Patterns

1. **XmlDocument base class** (`common/xml_document.py`): All document facades inherit
   from `XmlDocument[T]`, which provides context-managed lifecycle, load/save,
   compliance checking, and `_create_document()` creation.

2. **Direct codec instantiation**: Facades instantiate their codec and validator
   directly in `__init__()`:
   ```python
   class SSV(XmlDocument[Ssp1ParameterSet]):
       def __init__(self, path, mode="r"):
           self._codec = Ssp1SsvCodec()
           self._validator = Ssp1SsvValidator()
   ```
   This pattern is consistent across `SSD`, `SSM`, `MD`, `SRMD`, `SSB`, `LSRefManifest`,
   `LSRefExperiments`.

3. **DocumentRuntime subclasses**: `SsdRuntime` and `LSRefExperimentsRuntime` are
   near-identical wrappers over `DocumentRuntime`. Both are flagged as candidates
   for inlining (`todo.md`).

4. **Version routing archive**: `version_routing.py` registers `ParseStackSpec`s for
   10 standard/format/version combinations, but facades do not use it for dispatch.

## Code Counts (Active Implementation)

| Layer | Files | Estimated LOC |
|-------|-------|---------------|
| Top-level facades | 9 | ~450 |
| Common | 6 | ~450 |
| Standard/SSP1 | 22 | ~3,500 |
| Standard/FMI2 | 3 | ~500 |
| Standard/LS-REF | 6 | ~300 |
| Standard/other | 3 | ~200 |
| Tools | 1 | ~85 |
| **Total** | **~50** | **~5,500** |

## Evidence

- All modules listed above exist at the paths shown
- All facade `__init__` methods show direct codec/validator instantiation
- `todo.md`: "All Specialized runtime should be inlined"
- `common/document_runtime.py` line 99: TODO to extract reference discovery