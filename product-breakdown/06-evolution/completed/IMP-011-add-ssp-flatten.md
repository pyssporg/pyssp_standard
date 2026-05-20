# IMP-011: Support Nested `<System>` Elements in SSD Model and Codec

## Status

Proposed

## Priority

High

## Layer

Domain Model / Codec

## Theme

SSD nested system data model and parsing

## Problem

The SSP standard allows nested `<ssd:System>` elements within an SSD — a `<System>` can contain `<Elements>` that include both `<Component>` elements and further `<System>` elements. However, the current `pyssp_standard` implementation silently drops nested systems:

1. **Data model** — `Ssd1System.elements` is typed as `list[Ssd1Component]`, cannot hold child `Ssd1System` instances.
2. **Codec** — `_parse_system` only looks for `<ssd:Component>` children inside `<ssd:Elements>`, ignoring nested `<ssd:System>`.
3. **Parameter bindings** — `get_parameter_bindings()` only returns the system's own bindings, with a TODO noting nested systems and component sets are missing.
4. **Existing TODO** at `ssd_model.py:127` confirms this is known technical debt.

## Evidence

- **Example fixture**: `pytest/__fixture__/dcmotor/SystemStructure.ssd` shows a hierarchy:
  ```
  System "DC-Motor"
    ├── System "SuT"               ← nested system (NOT parsed)
    │   ├── Component "edrive_mass"
    │   └── Component "emachine_model"
    └── Component "stimuli_model"
  ```
- Codec line (`ssd_codec.py:86-91`): only parses `<ssd:Component>` under `<ssd:Elements>`.
- Model line (`ssd_model.py:99`): `elements: list[Ssd1Component]`.
- TODO line (`ssd_model.py:127`): `# TODO: + nested systems + component specific sets`.
- The `dcmotor` fixture (SSP2 namespace) cannot be parsed at all — nested content is silently lost.

## Current Pain / Risk

- **Data loss**: any SSD with nested systems loses child system content on parse.
- **Unusable fixture**: the `dcmotor` fixture contains valid SSP structure but cannot be used in tests.
- **Blocked downstream**: the flatten operation (IMP-013) depends on the model and codec supporting nested systems first.

## Proposed Improvement

### 1. Data Model (`ssd_model.py`)

- Change `Ssd1System.elements` type from `list[Ssd1Component]` to `list[Ssd1Component | Ssd1System]`.
- Add type-safe helpers:
  ```python
  def get_components(self) -> list[Ssd1Component]: ...
  def get_subsystems(self) -> list[Ssd1System]: ...
  def get_all_parameter_bindings(self) -> list[Ssd1ParameterBinding]: ...
  ```

### 2. Codec (`ssd_codec.py`)

- Extend `_parse_system` Elements parsing to handle both `<ssd:Component>` and `<ssd:System>` children:
  ```python
  for child in elements_element:
      if local_name(child.tag) == "Component":
          yield _parse_component(child)
      elif local_name(child.tag) == "System":
          yield _parse_system(child)
  ```
- Extend `_serialize_system` to serialize both element types:
  ```python
  for element in system.elements:
      if isinstance(element, Ssd1Component):
          elements_element.append(_serialize_component(element))
      elif isinstance(element, Ssd1System):
          elements_element.append(_serialize_system(element))
  ```

### 3. Constraint

Only **inlined** child `<System>` elements — no support for `<System source="other.ssp">` cross-file references.

## Expected Benefit

- Hierarchical SSDs (including the `dcmotor` fixture) are parsed, serialized, and round-tripped faithfully.
- The TODO at `ssd_model.py:127` is resolved.
- Unblocks IMP-013 (flatten operation).
- Existing flat-only SSDs continue to work unchanged.

## Risk and Blast Radius

| Risk | Severity | Mitigation |
|------|----------|------------|
| Breaking change if callers iterate `elements` expecting only `Ssd1Component` | High | Use `get_components()` as safe accessor; audit all callers |
| Codec serialization order mismatch for mixed elements | Low | Round-trip test with the `dcmotor` fixture |
| `get_parameter_bindings()` callers miss nested bindings | Low | New method `get_all_parameter_bindings()` is additive; old method unchanged |

## Suggested Priority

**High** — blocks IMP-013 and the `dcmotor` fixture adoption. This is pure data model work with clear testable boundaries.

## Task Contract Seed

```python
# Ssd1System changes (additive, not breaking)
class Ssd1System:
    elements: list[Ssd1Component | Ssd1System]  # was: list[Ssd1Component]

    def get_components(self) -> list[Ssd1Component]: ...
    def get_subsystems(self) -> list[Ssd1System]: ...

    def get_all_parameter_bindings(self) -> list[Ssd1ParameterBinding]:
        """Return own bindings + recursively all child-system bindings."""
```

## Verification

- Existing tests in `pytest/ssp1/codec/test_ssd_xml_codec.py` and `pytest/ssp1/facade/test_ssd.py` pass unchanged.
- New test: parse `dcmotor/SystemStructure.ssd` (converted to SSP1 namespace or via SSP2 codec), verify that `system.get_subsystems()` returns 1 system named "SuT" with 2 components.
- Round-trip test: serialized output re-parsed preserves the nested structure.
- Audit all callers of `system.elements` and `system.connectors` for type safety.

## Out of Scope

- Cross-file System references (`<System source="other.ssp">`).
- Flatten operation (moved to IMP-013).
- SSP2 codec implementation — fixture may need SSP1 conversion for testing.
- Parameter binding recursion in `get_parameter_bindings()` — new method `get_all_parameter_bindings()` is additive.

## Implementation Files

- `pyssp_standard/standard/ssp1/model/ssd_model.py` — Union type, helpers
- `pyssp_standard/standard/ssp1/codec/ssd_codec.py` — nested parse/serialize
- `pytest/ssp1/codec/test_ssd_xml_codec.py` — new nested-system test cases

## Traceability

- **Intent**: INT-001 (Inspect and edit SSP artifacts)
- **Product**: CAP-003 (SSD parsing/serialization)
- **Architecture**: Domain Model Layer, Codec Layer
- **Dependencies**: None (standalone)
- **Blocked by**: Nothing

## Notes

- The `dcmotor` fixture uses SSP version "2.0" on the root element. For iteration 1, convert it to SSP1 namespace or create a minimal SSP1 nested-system fixture `pytest/__fixture__/nested_system.ssd`.
- Audit all direct accesses to `.elements` in the codebase — the `embrace` and `mixed_example` fixtures are flat and unaffected.
- The `get_parameter_bindings()` TODO message should be replaced with a docstring pointing to `get_all_parameter_bindings()` for recursive access.