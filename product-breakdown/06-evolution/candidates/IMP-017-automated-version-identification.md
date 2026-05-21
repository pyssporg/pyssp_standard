# IMP-017: Automated Standard Version Identification When Opening Existing Artifacts

## Status

Proposed

## Layer

Public API / Versioning

## Theme

Version-aware XmlDocument base class with lazy codec resolution

## Evidence

- `version_routing.py` has `get_standard_version(xml_text)` and `get_standard_version_from_file(path)` — both work correctly for all registered formats
- `CODEC_STACK` has multiple entries for SSV (1.0, 2.0) and ModelDescription (2.0, 3.0) with distinct codec/validator types
- `get_codec_and_validator(standard)` exists at line 180 of `version_routing.py` but is never called by any facade
- Every facade (`ssv.py`, `md.py`, `ssd.py`, `ssm.py`, `ssb.py`, `srmd.py`, `ls_ref.py`) hardcodes a single codec/validator pair in `__init__()`
- `XmlDocument.__enter__()` (line 20-25 of `xml_document.py`) calls `load_document()` with no version detection
- `XmlDocument.from_xml()` (line 51-52) parses with the hardcoded codec regardless of XML content
- `XmlDocument.__exit__()` for append mode does not re-detect version before saving
- Opening an existing SSP2 SSV file with `SSV(path)` silently uses the SSP1 codec

## Current Pain Or Risk

1. **Silent data corruption**: Opening an existing multi-version artifact with the wrong codec may silently lose data or parse incorrectly. SSP2 SSV files with dimensions/Float32/UInt32 get parsed as SSP1 SSV, losing dimension metadata.
2. **Inconsistent model types**: `SSV.__enter__()` returns `XmlDocument[Ssp1ParameterSet]` even when the file is SSP2. The user accesses `ssv.xml` expecting `Ssp1ParameterSet` but the actual XML structure is SSP2.
3. **Manual version switching required**: Users who know the version must instantiate codec/validator directly, bypassing the facade entirely.
4. **Append mode corruption**: `SSV(path, "a")` re-parses with the hardcoded codec, potentially mutating content.
5. **Brittle future-proofing**: Adding a new version (e.g., SSB 2.0) requires updating every facade's `__init__` and all callers.

## Proposed Improvement

Implement **lazy, auto-detecting codec/validator resolution** in the `XmlDocument` base class so that facades automatically detect the correct codec and validator from the file content on read, while still allowing explicit overrides.

### Design (Approach C — Full Integration)

**A. `XmlDocument` base class changes:**

1. Add class-level attributes:
```python
_default_codec_type: type | None = None
_default_validator_type: type | None = None
```

2. Modify `__init__()` to accept optional `codec_type` and `validator_type` parameters:
```python
def __init__(self, path, mode="r", *, codec_type=None, validator_type=None):
    self.path = Path(path)
    self.mode = mode
    self._document = None
    self._codec_type = codec_type or self._default_codec_type
    self._validator_type = validator_type or self._default_validator_type
    self._codec = None
    self._validator = None
```

3. Add a `_resolve_codec()` method that lazy-resolves from file content or explicit types:
```python
def _resolve_codec(self, xml_text=None):
    if self._codec is not None and self._validator is not None:
        return  # already resolved
    if self._codec_type and self._validator_type:
        self._codec = self._codec_type()
        self._validator = self._validator_type()
    elif xml_text:
        from pyssp_standard.standard.version_routing import get_parse_stack_from_xml
        spec = get_parse_stack_from_xml(xml_text)
        self._codec = spec.codec_type()
        self._validator = spec.validator_type()
```

4. Add a `@classmethod from_standard` alternative constructor:
```python
@classmethod
def from_standard(cls, path, mode="r"):
    from pyssp_standard.standard.version_routing import get_parse_stack_from_file
    spec = get_parse_stack_from_file(Path(path))
    return cls(path, mode, codec_type=spec.codec_type, validator_type=spec.validator_type)
```

5. Modify `__enter__` to auto-detect in read mode:
```python
def __enter__(self):
    if self.mode == "w":
        self._document = self._create_document()
    else:
        self._resolve_codec()
        self._document = self.load_document()
    return self
```

6. Modify `load_document()` to detect version from the file if codec not yet resolved:
```python
def load_document(self):
    if not self.path.exists():
        return self._create_document()
    text = self.path.read_text(encoding="utf-8")
    self._resolve_codec(text)
    return self._codec.parse(text)
```

7. Modify `from_xml()` to detect version from XML string:
```python
def from_xml(self, text):
    self._resolve_codec(text)
    self._document = self._codec.parse(text)
```

8. Modify `check_compliance()` to resolve codec first if needed:
```python
def check_compliance(self):
    self._resolve_codec()
    xml_text = self._codec.serialize(self.xml)
    self._validator.validate(self.xml, xml_text)
    return True
```

**B. Facade changes (per-facade, opt-in):**

Each facade that supports multiple versions adds `_default_codec_type` and `_default_validator_type` class attributes:

```python
class SSV(XmlDocument[Ssp1ParameterSet]):
    _default_codec_type = Ssp1SsvCodec
    _default_validator_type = Ssp1SsvValidator

    def __init__(self, path, mode="r", *, codec_type=None, validator_type=None):
        super().__init__(path, mode, codec_type=codec_type, validator_type=validator_type)

    def _create_document(self):
        return Ssp1ParameterSet(name=self.path.stem or "parameters", version="1.0")
```

Facades with a single version (SSB, SSD, SSM, SRMD) leave `_default_codec_type` as `None` and continue to set `_codec`/`_validator` directly in `__init__()` — no change needed.

**C. Public API additions:**

- `SSV.from_standard(path)` → auto-detects version from file
- `SSV(path, mode="r", codec_type=Ssp2SsvCodec, validator_type=Ssp2SsvValidator)` → explicit override
- `SSV(path, mode="w")` → creates default SSP1 document
- `SSV(path, mode="a")` → detects version from existing file before appending

## Expected Benefit

1. **Correct-by-construction**: Opening an existing artifact always uses the right codec/validator, regardless of version.
2. **Backward compatible**: All existing code continues to work unchanged. `SSV(path)` still returns SSP1 by default for new documents. Only read behavior changes when the file content indicates a different version.
3. **Explicit escape hatch**: Users can still override version with `codec_type=`/`validator_type=` or `from_standard()`.
4. **Graceful append**: `SSV(path, "a")` detects the version from the existing file, not the facade default.
5. **Future-proof**: Adding a new SSV 3.0 or SSB 2.0 requires no facade changes — just register in `CODEC_STACK` and `get_standard_version()`.

## Risk And Blast Radius

| Risk | Severity | Mitigation |
|------|----------|------------|
| Base class change affects ALL facades | Medium | Add `_default_codec_type`/`_default_validator_type` as `None` — existing facades that don't set them fall back to their current `__init__` behavior |
| `check_compliance()` signature change | Low | Adding lazy resolution is backward-compatible; existing validators still work |
| Performance regression from auto-detection | Low | Only happens once per `__enter__`; the file is already being read |

## Suggested Priority

Medium

## Task Contract Seed

### Phase 1 — XmlDocument base class
1. Add `_default_codec_type` and `_default_validator_type` class attributes (default `None`)
2. Add `_resolve_codec(xml_text=None)` method with lazy resolution
3. Modify `__init__` to accept `codec_type=`/`validator_type=` kwargs
4. Add `from_standard` classmethod
5. Modify `__enter__`, `load_document`, `from_xml`, `check_compliance` to call `_resolve_codec`

### Phase 2 — Multi-version facades (SSV, ModelDescription)
6. Set `_default_codec_type`/`_default_validator_type` on `SSV`
7. Override `__init__` to pass through `codec_type`/`validator_type`
8. Set same on `ModelDescription` (FMI2 default, FMI3 auto-detected)
9. Add tests:

### Phase 3 — Tests
10. Auto-detect SSP1 SSV → `Ssp1SsvCodec`
11. Auto-detect SSP2 SSV → `Ssp2SsvCodec`
12. Auto-detect FMI2 MD → `Fmi2ModelDescriptionXmlCodec`
13. Auto-detect FMI3 MD → `Fmi3ModelDescriptionXmlCodec`
14. Explicit override with `codec_type=` works
15. `from_standard()` creates correct instance
16. Append mode detects version from existing file

## Out Of Scope

- Creating a unified `SsvParameterSet` model that works for both SSP1 and SSP2 (addresses symptom differently)
- Adding version auto-detection to archive facades (`SSP`, `FMU`) — they work on archives, not individual XML files
- Changing the `_create_document()` version default — new documents still default to SSP1/FMI2

## Traceability

- Intent: INT-001 (Inspect and edit SSP artifacts)
- Product: CAP-006 (Model description editing), CAP-003 (SSD/SSV parsing/serialization)
- Architecture: Public API Layer, Codec Layer (version_routing)
- Implementation: `common/xml_document.py`, `ssv.py`, `md.py`
- Verification: `pytest/common/`, `pytest/ssp1/facade/`, `pytest/fmi2/facade/`, `pytest/fmi3/` (if exists)

## Notes

- The `XmlDocument` base class is the single lever that controls all 7 XML facades. Getting the base class right is critical.
- The `_resolve_codec` method uses lazy initialization to avoid breaking the current pattern where facades set `_codec` in `__init__()`.
- The `from_xml()` path (used in tests) now auto-detects from the XML string, so tests that pass raw XML don't need explicit version hints.
- For SSP archive context, `DocumentRuntime` already handles version routing separately via `_iter_external_reference_targets`. The proposed change in `XmlDocument` is independent of that.
