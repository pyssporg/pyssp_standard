# IMP-012: Add Option to Remove Model Exchange from ModelDescription

## Status

Proposed

## Layer

Evolution

## Theme

ModelDescription editing utility

## Evidence

- Stray note in `06-evolution/candidates/remove_me.md`
- Some co-simulation engines reject FMUs that support both Model Exchange and Co-Simulation even when only Co-Simulation is needed

## Current Pain Or Risk

Users who have an FMU supporting both `me` and `cs` may need to strip the `me` capability to make the FMU compatible with import engines that require exclusive Co-Simulation. Currently no utility exists.

## Proposed Improvement

Add a method or option on `ModelDescription` to remove the Model Exchange capability, leaving only Co-Simulation. This would modify the `modelDescription.xml` to remove the `fmiModelDescription.attributes.canBeInstantiatedOnlyOncePerProcess` and related ME-specific attributes/sections.

## Expected Benefit

Users can adapt FMU metadata for import into engines that require Co-Simulation-only FMUs, without re-exporting from the source tool.

## Risk And Blast Radius

- Medium: modifying model description semantics could produce non-compliant FMUs
- Affects `md.py` facade and potentially `standard/fmi2/codec/`
- Must ensure the FMU remains structurally valid after removal

## Suggested Priority

Low

## Task Contract Seed

Add `ModelDescription.strip_model_exchange()` that removes ME-specific attributes and capabilities from the parsed model, then re-serializes. Validate the resulting document still passes compliance.

## Out Of Scope

- Reverse operation (adding Model Exchange to a Co-Simulation-only FMU)
- Batch processing of multiple FMUs

## Traceability

- Intent: INT-001 (Inspect and edit SSP artifacts)
- Product: CAP-006 (Model description editing)
- Architecture: Codec Layer, Public API Layer
- Implementation: `md.py`, `standard/fmi2/model/model_description.py`
- Verification: New test in `pytest/fmi2/facade/`

## Notes

- Must research FMI2 specification for exactly which attributes/sections are ME-only vs shared
- Consider whether this should be a `ModelDescription` method or a standalone utility function
- Verify with the known target engine behavior before release