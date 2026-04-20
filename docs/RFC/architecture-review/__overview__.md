# Architecture RFC: PySSP Standard SDK Evolution

## Status
- Proposed

## Date
- February 19, 2026

## Decision Summary
The project should move to a layered architecture with `xsdata` as the primary XML binding solution.

Recommended authority chain:
- `XSD -> xsdata generated bindings -> mapper/codec layer -> domain/public API`

This keeps one schema truth while separating:
- generated XML bindings
- compact domain models
- archive/orchestration logic
- semantic validation
- public compatibility adapters

## Why Change
The current codebase mixes archive I/O, XML parsing, mutable state, version handling, and semantic validation in the same classes. That makes SSP2/FMI2/FMI3 work slower and riskier than it needs to be.

Main problems:
- too much handwritten XML logic in multiple places
- inconsistent parsing and save behavior across formats
- weak separation between schema structure and business logic
- difficult extension path for new standard versions

## Primary Recommendation
Use `xsdata` as the primary internal XML representation.

That means:
- XSD files are the schema source of truth
- generated bindings are internal only
- handwritten mappers adapt generated bindings to compact domain models
- handwritten codecs orchestrate parse/serialize around generated root types
- archive access, cross-file resolution, validation, and authoring APIs stay outside generated code

Standard versioning should be treated as a first-class architectural concern:
- detect version once at load time
- route to the correct generated binding and codec stack early
- keep version-specific schema handling below the public API layer
- keep shared workflow behavior above the version-specific binding layer

## Document Split
- `layered_arch.md`
  Responsibility split and layer boundaries.
- `xsd_alternative.md`
  Why `xsdata` is the preferred XML strategy and what tradeoffs remain.
- `demo/README.md`
  Demo scope and regeneration commands.

## Demo Alignment
The demo shows the intended shape in a small slice:
- `xsdata`-generated SSV bindings plus a wrapper generation script
- handwritten SSV mapping on top of generated bindings
- SSD `xsdata` codec/mapper skeleton showing the recommended SSD split
- SSP-level external reference resolution outside codecs
