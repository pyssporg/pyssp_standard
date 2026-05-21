# IMP-015: SSP2 SSV Facade-Level Tests

> **Status:** Proposed  
> **Priority:** Medium  
> **Layer:** Testing

## Theme

Add facade-level end-to-end tests for the SSP2 SSV stack through the public `SSV` API, covering loading, creation, round-trip, and compliance checks for SSP2-specific features (dimensions, Float32, UInt32 types).

## Evidence

- `pytest/ssp1/facade/test_ssv.py`: 13 existing tests covering SSP1 SSV (create, round-trip, annotations, enumerations, units, compliance). **No SSP2 SSV tests exist.**
- `pytest/conftest.py` (line 67-68): An `ssv2_fixture` is defined pointing to `pytest/__fixture__/ssv2_ex.ssv`
- `pytest/__fixture__/ssv2_ex.ssv`: A valid SSP2 SSV file with `version="2.0"`, three parameters including dimensions (`<ssc:Dimension size="3"/>`) and SSP2-specific types (`<ssv:Float32>`, `<ssv:UInt32>`)
- `pyssp_standard/standard/ssp2/codec/ssv_codec.py`: Full SSP2 SSV codec implementation with dimension parsing/serialization
- `pyssp_standard/standard/ssp2/model/ssv_model.py`: Full SSP2 SSV model with `Ssp2Parameter`, `Ssp2Dimension`, `Ssp2ParameterSet`
- `pyssp_standard/standard/ssp2/validation/ssv_validation.py`: Full SSP2 SSV validator
- `pyssp_standard/standard/version_routing.py` (line 105-110): SSP2 SSV is registered in CODEC_STACK
- `pyssp_standard/ssv.py`: Currently hardcoded to SSP1 — tests depend on IMP-014 being implemented first

## Current Pain Or Risk

1. **No regression coverage for SSP2 SSV reading/writing through the public API**: The SSP2 codec, model, and validator exist but are only testable through direct imports. If someone changes the version routing or the codec interface, SSP2 SSV can break silently.
2. **Unsued fixture**: `ssv2_ex.ssv` fixture is defined but never referenced in any test.
3. **SSP2-specific features untested at facade level**: Dimensions (`<ssc:Dimension>`), `Float32`, `UInt32` types, and the SSP2 `add_parameter()` semantics are only tested implicitly (if at all) at the codec unit level.
4. **Verification gap for IMP-014**: If IMP-014 (version-aware SSV facade) is implemented, there will be no automated tests proving the new code path works end-to-end for SSP2 documents.

## Proposed Improvement

1. **Create `pytest/ssp2/facade/test_ssv.py`** with the following test scenarios:
   - **Load SSP2 fixture**: Read `ssv2_ex.ssv` through `SSV(path)`, verify `version == "2.0"`, verify parameter types (`Float32`, `UInt32`), verify dimension data on multi-dimensional parameters.
   - **Create SSP2 document from scratch**: Create a new SSV file with `version="2.0"`, add a parameter with dimensions, round-trip and verify.
   - **Round-trip preserves SSP2 parameter types**: Create parameters with `Float32` and `UInt32` types, verify serialization preserves type names and values.
   - **Compliance check with SSP2 schema**: Create an SSP2 document and call `check_compliance()`; verify it passes XSD validation against the SSP2 schema.
   - **Edit existing SSP2 document**: Load the SSP2 fixture, modify a parameter value, save, reload, verify the change.
   - **Reject SSP2-only types with SSP1 facade**: (negative test) If version is explicitly set to `"1.0"`, verify that parsing SSP2-specific XML fails gracefully.
2. **Wire the existing `ssv2_fixture`** in conftest into the new test file.
3. **Parameterized compatibility test**: Optionally, add a parameterized test that runs the same "load and verify round-trip" against both SSP1 and SSP2 fixture files to ensure the version-agnostic base path works.

## Expected Benefit

- The SSP2 SSV stack is fully covered by at least one end-to-end test at the public API level.
- The `ssv2_ex.ssv` fixture is exercised, justifying its existence.
- Future changes to version routing, codec base class, or facade initialization will be caught by regression tests for both SSP1 and SSP2 SSV.
- Provides a safety net for IMP-014 implementation — you can verify the new version-routed facade works for both versions before declaring it complete.

## Risk And Blast Radius

- **Dependency on IMP-014**: These tests cannot run until IMP-014 is implemented, because the current `SSV` facade cannot load SSP2 documents. The tests should be written alongside IMP-014 and merged together, or marked with `@pytest.mark.skip(reason="depends on IMP-014")` if merged separately.
- **Minimal blast radius**: Test files do not affect runtime behavior. Wrong tests would produce false positives/negatives but cannot break the library.
- **Fixture compatibility**: The existing `ssv2_ex.ssv` fixture uses the SSP1 namespace (`xmlns:ssv="http://ssp-standard.org/SSP1/SystemStructureParameterValues"`) despite being a version `"2.0"` document. This must be verified against how the SSP2 schema actually expects the namespace to look. If the namespace is wrong, tests will fail and the fixture may need updating.
- **SSP2 schema availability**: The test depends on the SSP2 XSD schema being present and valid under `schema/SSP2/`. If the schema is missing or the `resolve_schema_path("SSP2", "SystemStructureParameterValues.xsd")` fails, compliance tests will fail.

## Suggested Priority

Medium

## Task Contract Seed

Implement SSP2 SSV facade tests:

1. Create `pytest/ssp2/facade/test_ssv.py` with tests covering:
   - Loading the SSP2 fixture through the `SSV` facade
   - Verifying parsed SSP2-specific details (dimensions, parameter types)
   - Creating an SSP2 document from scratch with dimensions
   - Round-trip of SSP2 parameters
   - Compliance validation against SSP2 schema
2. Verify the existing `ssv2_fixture` in `pytest/conftest.py` points to a valid SSP2 fixture file.
3. Run the tests against an SSP2-aware `SSV` facade (may depend on IMP-014).
4. If IMP-014 is not yet merged, add a `pytest.mark.skip` with a clear reason.
5. Verify all existing SSP1 tests continue to pass.

## Out Of Scope

- Implementing the version-aware SSV facade (covered by IMP-014).
- Creating additional SSP2 test fixtures beyond what already exists.
- Tests for SSP2 SSV through the SSP archive layer (archive-aware workflow).
- Performance or benchmark tests for SSP2 SSV processing.
- Tests for SSP2 SSV error handling (malformed XML, missing dimensions, etc.) beyond basic sanity.

## Traceability

- Intent: Ensure SSP2 SSV works end-to-end through the public facade API.
- Product: `pytest/ssp2/facade/test_ssv.py`
- Architecture: Tests exercise the same entry point (`SSV`) that the user sees.
- Implementation: New test module, depends on IMP-014 for the facade to support SSP2.
- Verification: The tests themselves are the verification.

## Notes

- The SSP2 SSV namespace is `http://ssp-standard.org/SSP1/SystemStructureParameterValues` (same as SSP1). The namespace does not change between versions — only the schema content (new types, dimensions) changes. Verify this assumption against the actual SSP2 XSD.
- The `ssv2_ex.ssv` fixture uses `<ssv:Real value="1.0 2.0 3.0 4.0 5.0 6.0"/>` with a space-separated list, implying multi-value support. This is an SSP2 feature and should be verified through the `Ssp2Parameter.attributes["value"]` field.
- Dimensions appear as `<ssc:Dimension size="..."/>` elements within the `<ssv:Parameter>` element, before `Annotations`. Verify the serialization order matches the fixture.