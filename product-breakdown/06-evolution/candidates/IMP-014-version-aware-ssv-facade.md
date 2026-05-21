# IMP-014: Version-Aware SSV Facade Through Version Routing

> **Status:** Proposed  
> **Priority:** High  
> **Layer:** Public API

## Theme

Wire the SSV facade through the existing `version_routing.py` module so that it can handle both SSP1 and SSP2 documents, detect version automatically on read, and create documents at a specified version.

## Evidence

- `pyssp_standard/ssv.py` (lines 5-7, 16-17): Hardcodes `Ssp1SsvCodec` and `Ssp1SsvValidator` at import level and instantiation
- `pyssp_standard/ssv.py` (line 19-20): `_create_document()` always returns `Ssp1ParameterSet` with `version="1.0"`
- `pyssp_standard/standard/version_routing.py` (lines 69-74, 105-110): `CODEC_STACK` already registers both `SSP/SSV/1.0` → `(Ssp1SsvCodec, Ssp1SsvValidator)` and `SSP/SSV/2.0` → `(Ssp2SsvCodec, Ssp2SsvValidator)`
- `pyssp_standard/standard/version_routing.py` (lines 136-137): `get_standard_version()` already detects SSV version from `<ssv:ParameterSet version="...">`
- `pyssp_standard/standard/version_routing.py` (line 180-183): `get_codec_and_validator()` exists but is never called by any facade
- `pyssp_standard/standard/ssp2/codec/ssv_codec.py`, `pyssp_standard/standard/ssp2/model/ssv_model.py`, `pyssp_standard/standard/ssp2/validation/ssv_validation.py`: The full SSP2 SSV stack exists and is registered in `CODEC_STACK`
- `pyssp_standard/common/xml_document.py` (lines 13-18, 44-49): Base class stores `_codec` and `_validator` per instance, uses them for `load_document()` and `check_compliance()`

## Current Pain Or Risk

1. **SSV facade is version-locked to SSP1**: Cannot read, create, or validate SSP2 SSV documents through the public `SSV` class. Users must import `Ssp2SsvCodec`/`Ssp2SsvValidator`/`Ssp2ParameterSet` directly, bypassing the entire facade layer.
2. **Version routing infrastructure is wasted**: `version_routing.py` has full SSV version support (CODEC_STACK, get_standard_version, get_codec_and_validator) but no consumer connects to it.
3. **Silent corruption risk**: If a user passes `SSV(path)` with an SSP2 file, the SSP1 codec will attempt to parse it, potentially losing dimension data (`<ssc:Dimension>`), SSP2-specific types (`Float32`, `UInt32`), and producing wrong model shape.
4. **Maintenance burden**: Adding SSP3 SSV (or any future version) requires modifying `ssv.py` in addition to the version routing, rather than being a data-driven registration.

## Proposed Improvement

1. **Add `version` parameter to `SSV.__init__`**: Accept `version: str | None = None`. When `None` and `mode != "w"`, detect version automatically from XML. When provided, use it for both read and write paths.
2. **Replace hardcoded imports with routing dispatch**: Call `get_codec_and_validator(StandardVersion("SSP", "SSV", version))` to obtain the correct codec/validator type pair for the target version.
3. **Version-detect on read**: Override `load_document()` or use the existing `get_standard_version_from_file()` to detect the version from XML before dispatching to the right codec.
4. **Version-aware `_create_document()`**: When `mode == "w"` and no version is specified, default to `"1.0"` for backward compatibility. When `version` is specified, create the matching ParameterSet type (`Ssp1ParameterSet` or `Ssp2ParameterSet`).
5. **Use `Union` type for the TypeVar**: Change `SSV` to be `XmlDocument[Ssp1ParameterSet | Ssp2ParameterSet]` so it can hold either document type.

## Expected Benefit

- Users can read SSP2 SSV files through the standard `SSV(path)` API without any special flags — version is detected from XML automatically.
- Users can create SSP2 SSV documents via `SSV(path, "w", version="2.0")`.
- The version routing layer becomes the single source of truth for codec/validator dispatch.
- Adding SSP3 SSV support requires only adding a `CODEC_STACK` entry (zero facade changes).
- Eliminates the silent data-loss risk when reading SSP2 files as SSP1.

## Risk And Blast Radius

- **Breaking change**: `SSV.__init__` signature changes (adding `version=` keyword parameter). Must be backward-compatible if `version` is omitted (default `None` → auto-detect on read, `"1.0"` on create).
- **Type narrowing**: Changing `SSV` from `XmlDocument[Ssp1ParameterSet]` to `XmlDocument[Ssp1ParameterSet | Ssp2ParameterSet]` may require callers to narrow the type before accessing version-specific fields (e.g., `.dimensions`). Existing tests access `.parameters`, `.units`, `.enumerations`, `.metadata` which are present on both model types — those should work without changes.
- **SSP1 SSV fixture loading**: Existing tests assume SSP1. The version-detection path must correctly identify existing SSP1 fixtures as version `"1.0"`. The `get_standard_version()` function already does this (reads `<ssv:ParameterSet version="1.0">`).
- **`_create_document()` return type**: Must return either `Ssp1ParameterSet` or `Ssp2ParameterSet`. The base class calls `_create_document()` in `__enter__()` before the codec/validator are used for `check_compliance()`. The codec/validator pair must match the created model type.
- **Scope**: Only SSV. Other facades (SSD, SSM, SSB, SRMD) have the same problem but are out of scope for this candidate.

## Suggested Priority

High

## Task Contract Seed

Implement version-aware SSV facade:

1. Update `SSV.__init__` to accept `version: str | None = None`.
2. When `mode != "w"` and version is `None`, detect version from file using `get_standard_version_from_file()` before loading.
3. Use `get_codec_and_validator(StandardVersion("SSP", "SSV", version))` to set `self._codec` and `self._validator`.
4. Update `_create_document()` to return `Ssp1ParameterSet` when version is `"1.0"` and `Ssp2ParameterSet` when version is `"2.0"`.
5. Update `SSV` type annotation to `XmlDocument[Ssp1ParameterSet | Ssp2ParameterSet]`.
6. Remove the hardcoded imports of `Ssp1SsvCodec`, `Ssp1ParameterSet`, `Ssp1SsvValidator` from `ssv.py`.
7. Ensure existing SSP1 SSV tests pass without modification.
8. Add at least one test that reads the SSP2 fixture file through the `SSV` facade.
9. Add at least one test that creates an SSP2 document via `SSV(path, "w", version="2.0")` and verifies round-trip.

## Out Of Scope

- Wiring other facades (SSD, SSM, SSB, SRMD, MD) through version routing — this candidate is SSV-specific.
- Adding `version` parameter to the base `XmlDocument` class.
- Creating a unified SSV model type (adapter/unification layer).
- Performance benchmarking of the version routing path.
- Changes to `XmlDocument` base class beyond what is needed for optional version dispatch.

## Traceability

- Intent: SSV facade must handle multiple SSP versions through the existing routing infrastructure.
- Product: `SSV` class in `pyssp_standard/ssv.py`
- Architecture: Uses `get_codec_and_validator()` from `pyssp_standard/standard/version_routing.py` as the single dispatch mechanism
- Implementation: `ssv.py`, `xml_document.py` (minimal), `version_routing.py` (no changes expected)
- Verification: `pytest/ssp1/facade/test_ssv.py` (existing), `pytest/ssp2/facade/test_ssv.py` (new)

## Notes

- `Ssp1ParameterSet` and `Ssp2ParameterSet` share `name`, `version`, `metadata`, `parameters`, `enumerations`, `units` fields but differ in parameter types (`Ssp1Parameter` has no `dimensions`, `Ssp2Parameter` does). A union type will require callers to handle the difference.
- The existing SSP2 SSV fixture (`pytest/__fixture__/ssv2_ex.ssv`) uses version `"2.0"` and can be used as the test input for version-aware loading.
- `get_standard_version_from_file()` reads the entire file and parses XML to detect version. For very large SSV files this may be costly, but SSV files are typically small. This is acceptable for the initial implementation.