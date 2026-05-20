# IMP-013: Flatten Hierarchical SSD Into Single-Level System Structure

## Status

Proposed

## Priority

Low

## Layer

Operations

## Theme

SSD flatten transformation for simulation engine compatibility

## Problem

Many simulation engines do not support multi-level SSP hierarchies — they expect a flat SSD where all `<Component>` elements are direct children of the top-level `<System>` with connections remapped accordingly. No utility currently exists to perform this transformation.

The underlying data model and codec support for nested systems is being added separately (IMP-011). Once that is done, a flatten operation is needed to produce simulator-compatible output.

## Evidence

- Most simulation engines cannot execute multi-level SSP hierarchies.
- The `dcmotor` fixture (`pytest/__fixture__/dcmotor/SystemStructure.ssd`) shows a real-world hierarchy that needs flattening:
  ```
  System "DC-Motor"
    ├── System "SuT"
    │   ├── Component "edrive_mass"
    │   ├── Component "emachine_model"
    │   └── <Connections> (internal)
    ├── Component "stimuli_model"
    └── <Connections> (reference SuT's connectors)
  ```
- No existing code in `pyssp_standard/standard/ssp1/operations/` addresses this.

## Current Pain / Risk

- Users with hierarchical SSDs cannot produce flat SSDs for simulation engines.
- Manual flattening requires rewriting connection references — error-prone and unscalable.
- The `dcmotor` fixture cannot be used as a test input for engine compatibility.

## Proposed Improvement

Add a `flatten_ssd(system: Ssd1System) -> Ssd1System` function that transforms a hierarchical SSD system tree into a single-level system:

1. **Promote child-system components** into the parent's `<Elements>`, prefixing component names to avoid collisions (e.g., `SuT.edrive_mass`).
2. **Remap connections** — internal child-system connections get updated component names; parent-level connections that reference child-system connectors are resolved to actual component connectors.
3. **Merge parameter bindings** from child systems with prefix adjustments.
4. **Preserve top-level structure** — root system name, connectors, default experiment, units, annotations remain intact.

### Constraints (First Iteration)

- Only **inlined** child `<System>` elements — no cross-file `.ssp` references.
- Within a single SSD document, not cross-archive.
- Dot-prefix collision resolution (`Parent.Child`).
- **Depends on IMP-011** for the underlying model and codec support.

## Expected Benefit

- Hierarchical SSDs become transformable into the flat format engines expect.
- The `dcmotor` fixture gains practical utility as a test input.
- Users get a programmatic path from multi-level to single-level.

## Risk and Blast Radius

| Risk | Severity | Mitigation |
|------|----------|------------|
| Connection remapping breaks signal routing | High | Exhaustive tests with known-correct flat reference fixture |
| Name collision on promoted components | Medium | Dot-prefix + uniqueness validation |
| Parameter binding prefix semantics change | Medium | Preserve original prefixes; document remapping |
| Flat output fails XSD validation | Medium | Run `check_compliance()` on flattened output |
| Cross-file System references encountered | Low | Raise `ValueError` with clear message |

## Suggested Priority

**Low** — standalone transformation; users with flat-only SSDs are unaffected. Blocked on IMP-011.

## Task Contract Seed

```python
def flatten_ssd(system: Ssd1System) -> Ssd1System:
    """Flatten a hierarchical SSD system tree into a single-level system.

    Promotes all nested system components to the top level, remaps
    connections, merges parameter bindings, and preserves the root
    structure. Raises ValueError if any nested System has an external
    'source' attribute (cross-file references not supported yet).
    """
```

## Implementation

### New file: `standard/ssp1/operations/ssd_flatten.py`

Core algorithm:
1. Recursively walk the system tree collecting components with mangled names.
2. Build name map: `old_name → new_name` for all promoted components.
3. Walk all connections at every level, rewrite `startElement`/`endElement` via the name map.
4. Resolve parent-level connections targeting child-system connectors — trace through the child system's connections to find the actual component connector.
5. Merge child-system parameter bindings with prefix adjustments.
6. Drop graphical geometry (ConnectionGeometry, ElementGeometry, SystemGeometry).

### Test file: `pytest/ssp1/operations/test_ssd_flatten.py`

Tests should cover:
- Basic one-level nesting
- Two-level nesting
- Multiple child systems
- Parameter bindings at system and component levels
- Connection remapping accuracy (internal + cross-level)
- Name collision edge cases
- Round-trip: flattened output re-parsed through codec
- Rejection of external-source Systems (`ValueError`)
- Flat output passes XSD validation

## Verification

- All existing SSD tests pass.
- New flatten tests pass with the `dcmotor` fixture (or an SSP1-converted equivalent).
- Flattened output matches a hand-written flat reference.
- `check_compliance()` passes on flattened output.

## Out of Scope (First Iteration)

- Cross-file System references (`<System source="other.ssp">`).
- Graphical geometry remapping (dropped on flatten).
- Reverse operation (flat → hierarchical).
- Batch processing multiple SSD files.
- SSP archive flattening (whole `.ssp` context).
- Public `SSD` facade method — standalone function only.

## Dependencies

- **IMP-011**: Required — nested system data model and codec support must be merged first.
- Test fixture: the `dcmotor` SSD may need SSP1 namespace conversion, or a minimal SSP1 nested fixture created.

## Implementation Files

- `pyssp_standard/standard/ssp1/operations/ssd_flatten.py` — new file
- `pytest/ssp1/operations/test_ssd_flatten.py` — new file
- `pytest/__fixture__/dcmotor/` — adopted fixture (may need SSP1 variant)

## Traceability

- **Intent**: INT-001 (Inspect and edit SSP artifacts)
- **Product**: CAP-003 (SSD parsing/serialization)
- **Architecture**: Operations Layer
- **Depends on**: IMP-011
- **Blocked by**: IMP-011

## Notes

- Connection remapping is the hardest part: when parent `Connections` reference a child system's `Connector`, the actual signal path passes through internal connections. The algorithm must trace these paths.
- Geometry data loss is acceptable — most simulation engines ignore it.
- The dot-prefix strategy (`SuT.edrive_mass`) may create names beyond FMU length limits. A configurable separator can be added later.
- The `dcmotor` fixture is SSP2-namespaced; for iteration 1 either the SSP2 codec must be functional or a SSP1-converted fixture must be created.