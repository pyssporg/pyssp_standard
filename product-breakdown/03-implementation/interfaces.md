# Interfaces

> **Layer:** 03-implementation
> **Artifact type:** interfaces.md

## Public API Surface

All public exports from `pyssp_standard/__init__.py`:

```python
__all__ = [
    "FMU", "LSRefExperiments", "LSRefExperimentsRuntime",
    "LSRefManifest", "ModelDescription", "SRMD", "SSB", "SSD",
    "SSM", "SSP", "SSV", "get_repo_root", "LS_REF_EXTRA_DIR",
]
```

## Facade Interface Pattern

All document facades follow a common pattern via `XmlDocument[T]` base class:

```python
class XmlDocument(Generic[DocumentT]):
    def __init__(self, path, mode="r"):     # path + mode
    def __enter__(self) -> "XmlDocument":    # context manager
    def __exit__(self, exc_type, exc, tb):   # auto-save on success
    @property
    def xml(self) -> DocumentT:              # access canonical model
    def check_compliance(self) -> bool:      # explicit validation
    def load_document(self) -> DocumentT:    # parse from file
    def save_document(self):                 # serialize to file
    def from_xml(self, text):               # parse from string
```

## Mode Semantics

| Mode | Read | Edit | Create | Auto-save on exit |
|------|------|------|--------|-------------------|
| `r` | Yes | No | No | No |
| `a` | Yes | Yes | No | Yes (if no exception) |
| `w` | No | Yes | Yes | Yes (if no exception) |

## External Reference Interface

`DocumentRuntime` provides archive-aware external reference resolution:

```python
class DocumentRuntime(Generic[FacadeT]):
    def __init__(self, runtime, *, document_path, document_type,
                 external_reference_specs=(), mode="r"):
    def __enter__(self) -> FacadeT:    # resolves external refs
    def __exit__(self, ...):           # persists external refs, detaches
```

External references are declared as `ExternalReferenceSpec` tuples:

```python
# In ssd.py:
EXTERNAL_REFERENCE_SPECS = (
    ExternalReferenceSpec(owner_type=Ssd1ParameterBinding,
                          source_attr="source",
                          document_attr="parameter_set",
                          facade_type=SSV),
    ExternalReferenceSpec(owner_type=Ssd1ParameterMappingReference,
                          source_attr="source",
                          document_attr="mapping",
                          facade_type=SSM),
)
```

## Archive Runtime Interface

```python
def create_runtime(path, mode) -> DirectoryRuntime | ArchiveRuntime

class ArchiveRuntime(DirectoryRuntime):  # zip-backed
class DirectoryRuntime:                  # filesystem-backed
    def __enter__/__exit__(self)
    def resolve(self, path) -> Path
    def list_prefix(self, prefix) -> list[str]
    def add_file(self, source, target_name) -> str
    def remove_file(self, target_name)
```

## Codec Interface

Each codec provides two methods (pattern from all active codecs):

```python
class Ssp1SsvCodec:
    def parse(self, xml_text: str) -> Ssp1ParameterSet
    def serialize(self, model: Ssp1ParameterSet) -> str
```

## Validation Interface

Each validator provides one method:

```python
class Ssp1SsvValidator:
    def validate(self, model, xml_text: str | None = None) -> None
```

## Key Implementation Decisions

| Decision | Location | Rationale |
|----------|----------|-----------|
| Direct `xml.etree.ElementTree` | All codec modules | Standard library, no external dependency |
| Dataclass models | `model/` modules per standard | Simple, testable, immutable-like |
| `XmlDocument[T]` generics | `common/xml_document.py` | Reusable lifecycle for all facades |
| `check_compliance()` explicit | `XmlDocument.__exit__` calls it | Never auto-validate without user knowledge |
| `DocumentRuntime` for cross-file | `common/document_runtime.py` | Keeps codecs simple, orchestration separate |
| Facades hardcode codecs | Each facade `__init__` | Quick to start, but bypasses routing |

## Evidence

- `pyssp_standard/__init__.py`: exports
- Each facade module: constructor, `_create_document()`, `xml` property
- `common/xml_document.py`: base class
- `common/document_runtime.py`: generic orchestration
- `common/archive_runtime.py`: `create_runtime()` dispatch

## Quick Lookup: Concern to Code Home

| Concern | Primary Code Home |
|---------|-------------------|
| Archive and directory runtimes | `common/archive_runtime.py`, `common/directory_runtime.py`, `common/document_runtime.py` |
| Public facades | `ssp.py`, `ssd.py`, `ssm.py`, `ssv.py`, `fmu.py`, `md.py` |
| Cross-standard composition | `standard/operations/model_description_to_ssd.py` |
| SSP1 codecs | `standard/ssp1/codec/` |
| SSP1 models | `standard/ssp1/model/` |
| SSP1 operations | `standard/ssp1/operations/` |
| Validation | `standard/ssp1/validation/`, `standard/fmi2/validation/` |
| Shared XML helpers | `common/xml_document.py`, `standard/ssp1/codec/xml_utils.py` |
| Test fixtures | `pytest/` and `models/ssp/` |

### Where to Start for Specific Changes

| Change | Start At |
|--------|----------|
| Archive-aware `.ssp` workflows | `ssp.py`, `common/document_runtime.py` |
| Cross-standard model conversion | `standard/operations/model_description_to_ssd.py` |
| Standalone SSD document shape | `standard/ssp1/model/ssd_model.py`, `standard/ssp1/codec/ssd_codec.py` |
| Parameter bindings or mappings | `standard/ssp1/operations/ssd_parameter_bindings.py` |
| SSP1-only system assembly | `standard/ssp1/operations/model_description_to_ssd.py` |