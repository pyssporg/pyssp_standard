# IMP-016: SSP2 SSV Inline Parameter Set Support in SSD Facade

> **Status:** Proposed  
> **Priority:** Low  
> **Layer:** Domain Model / Operations

## Theme

Extend the SSD facade's `extend_system_parameterset()` to support creating SSP2 inline parameter sets, and add SSP2 model types to the SSD model to carry version-aware inline parameter data.

## Evidence

- `pyssp_standard/ssd.py` (lines 65-83): `extend_system_parameterset()` accepts a `version` parameter but always creates SSD1-level parameter bindings that reference `Ssp1Parameter`. No SSP2-aware parameter set creation logic exists.
- `pyssp_standard/standard/ssp1/model/ssd_model.py`: `Ssd1System` has `inline_parametersets: list[Ssd1InlineParameterSet]` and `extend_inline_parameterset()` creates `Ssd1InlineParameterSet` with `version="1.0"`.
- `pyssp_standard/standard/ssp1/operations/ssd_parameters.py`: `extend_component_parametersets()` works with `Ssp1Parameter` only.
- `pyssp_standard/standard/ssp2/model/`: No SSP2 SSD model exists yet — the SSP2 SSD skeleton is empty.
- `pyssp_standard/standard/ssp2/model/ssv_model.py`: `Ssp2ParameterSet` has `add_parameter()` and `extend_parameters()` methods similar to `Ssp1ParameterSet`.
- `pyssp_standard/ssv.py`: Currently hardcoded to SSP1 — the inline parameter set creation in `ssd.py` manually imports `Ssp1ParameterSet` and constructs it directly (through `ops/extend_inline_parameterset`).

## Current Pain Or Risk

1. **SSP2 SSV parameters cannot be created inline**: Even after IMP-014 makes the SSV facade version-aware, the SSD facade's `extend_system_parameterset()` creates only SSP1 inline parameter sets. An SSP2 archive cannot contain inline SSP2 parameter sets within its SSD.
2. **Mixed-version archive risk**: If an SSP archive is SSP2-level, inline parameter sets embedded in the SSD should logically be SSP2 SSV. Currently, the API forces them to be SSP1 regardless of the archive version.
3. **Ssd1InlineParameterSet version field ignored**: `Ssd1InlineParameterSet` carries a `version` field, but `extend_inline_parameterset()` always passes `version="1.0"`. The `version` parameter on the facade method is unused for SSP2 dispatch.
4. **SSP2 SSD model absent**: The SSP2 model/codec for SSD is not yet implemented, so there is no concept of an `Ssp2InlineParameterSet` or `Ssp2System` that would carry SSP2 parameter sets inline.

## Proposed Improvement

1. **Add SSP2 SSD model stub**: Create the minimal needed classes in `standard/ssp2/model/ssd_model.py` to support inline parameter sets:
   - `Ssp2InlineParameterSet(parameters: list[Ssp2Parameter])`
   - `Ssp2System(inline_parametersets: list[Ssp2InlineParameterSet])`
   - `Ssp2SystemStructureDescription(system: Ssp2System | None)`
   - These are parallel to `Ssd1InlineParameterSet`, `Ssd1System`, etc., but work with `Ssp2Parameter` instead of `Ssp1Parameter`.
2. **Update `extend_system_parameterset()` in `ssd.py`**: When `version="2.0"`, create an `Ssp2InlineParameterSet` with `Ssp2Parameter` entries instead of `Ssp1ParameterSet`/`Ssp1Parameter`.
3. **Expand parameter inference**: `infer_parameter_type_name()` and `merge_value_attribute()` in `common/utils.py` already handle Float/int/str/bool. Extend to also map `float` → `"Float32"` when the version is `"2.0"` (or always, since `Float32` in SSP2 covers what `Real` covers in SSP1 with fewer constraints).
4. **Update `extend_component_parameterset()` in `ssd_parameters.py`**: Accept an optional `version` parameter and dispatch to either `Ssp1Parameter` or `Ssp2Parameter` creation.

## Expected Benefit

- A user creating an SSP2 SSV file can also create an SSP2 archive with inline parameter sets through the SSD facade.
- The `version` parameter on `extend_system_parameterset()` becomes meaningful for SSP2.
- The gap between SSP1 full support and SSP2 skeleton narrows in the inline-parameter domain.
- Mixed-version archive creation becomes possible (SSD1 structure with SSP2 parameter sets inline).

## Risk And Blast Radius

- **SSP2 SSD model is partial**: Adding only the SSP2 SSD model for inline parameter sets creates a partial model with no codec support. The SSD codec (`ssp1/codec/ssd_codec.py`) would not serialize SSP2 models. The inline parameter sets live inside an SSP2 SSD that would need its own codec — which doesn't exist yet.
- **No round-trip without SSP2 SSD codec**: Without an SSP2 SSD codec, the created SSP2 inline parameter sets cannot be serialized to/from XML. Testing would be limited to in-memory model manipulation.
- **`Ssp2Parameter` vs `Ssp1Parameter` type mismatch**: `extend_parameters()` in the SSD facade currently returns `list[Ssp1Parameter]`. Version-aware dispatch would need to return a union type or the caller must know the version.
- **Low blast radius**: Changes are additive (new model classes, version dispatch in operations). Existing SSP1 behavior is preserved by the default `version="1.0"`.
- **Dependencies**: Depends on IMP-014 if the SSV facade is expected to handle SSP2 inline parameter sets. Depends on SSP2 SSD codec for actual serialization round-trips.

## Suggested Priority

Low

## Task Contract Seed

Add minimal SSP2 inline parameter set support to the SSD facade:

1. Create `pyssp_standard/standard/ssp2/model/ssd_model.py` with:
   - `Ssp2InlineParameterSet` (wrapping `list[Ssp2Parameter]`)
   - `Ssp2System` with `inline_parametersets: list[Ssp2InlineParameterSet]`
   - `Ssp2SystemStructureDescription` with `system: Ssp2System | None`
2. Update `SSD.extend_system_parameterset()` in `ssd.py` to accept and handle `version="2.0"`:
   - Create `Ssp2Parameter` entries using SSP2 type mapping
   - Wrap them in `Ssp2InlineParameterSet` on an `Ssp2System`
3. Verify in-memory model construction works via a unit test (no XML round-trip without SSP2 SSD codec).
4. Ensure all existing SSP1 SSD tests continue to pass unchanged.
5. Document that SSP2 inline parameter sets are in-memory only until the SSP2 SSD codec is implemented.

## Out Of Scope

- Full SSP2 SSD codec implementation (codec, validator, schema registration).
- SSP2 SSV facade changes (covered by IMP-014).
- Support for SSP2 inline parameter sets in the SSP archive layer (SSP archive context manager).
- Cross-version conversion between SSP1 and SSP2 parameter types.
- Changes to `extend_component_parameterset()` for SSP2 components.

## Traceability

- Intent: Enable SSP2 inline parameter set creation through the SSD facade.
- Product: `pyssp_standard/ssd.py`, `pyssp_standard/standard/ssp2/model/ssd_model.py`, `pyssp_standard/standard/ssp1/operations/ssd_parameters.py`
- Architecture: SSP2 model classes parallel SSP1 model classes; dispatch by version parameter.
- Implementation: New model file, facade changes in `ssd.py`, operations changes in `ssd_parameters.py`.
- Verification: In-memory model construction tests in `pytest/ssp2/facade/test_ssd.py`.

## Notes

- This candidate is intentionally narrow: it only enables *in-memory* creation of SSP2 inline parameter sets through the SSD facade. Full SSP2 SSD serialization requires a separate SSP2 SSD codec (which is a larger effort).
- The `Ssd1InlineParameterSet` already stores a `version` field. SSP2 model classes should reuse the same pattern.
- Consider whether `Ssp2Parameter` could be used directly inside `Ssd1InlineParameterSet` with `version="2.0"` instead of creating a separate `Ssp2InlineParameterSet` class. This would reduce model proliferation but couples SSP1 model to SSP2 types.