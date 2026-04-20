# Layered Architecture

## Core Rule
Each layer should own one kind of responsibility only.

Recommended flow:
- `archive -> generated bindings -> mapper/codec -> domain model -> public API/orchestration`

## 1) Archive Layer (`archive`)
Responsibility:
- read/write package containers such as `.ssp` and `.fmu`
- provide deterministic save behavior and dirty tracking
- expose raw XML/bytes to higher layers

Must not own:
- XML business logic
- cross-file semantic decisions
- schema-specific model mapping

## 2) Generated Binding Layer (`generated`)
Responsibility:
- hold `xsdata`-generated classes for SSP/FMI XSDs
- represent the schema-shaped XML structure directly

Rules:
- generated files are derived artifacts
- generated files are regenerated from wrapper scripts
- generated files are not public API
- do not hand-edit generated files

## 3) Codec Layer (`codec`)
Responsibility:
- parse and serialize XML using generated root types
- keep XML transform orchestration separate from business logic

Recommended split:
- `*_xsdata_codec`
  - owns parser/serializer setup
  - chooses generated root type
  - handles namespace normalization when needed
  - contains no archive I/O and no semantic logic
- `*_mapper`
  - converts generated bindings `<->` compact domain model
  - handles inline vs external representation branching
  - hides awkward schema-shaped objects from the rest of the codebase

SSD recommendation:
- prefer one `SsdXsdataCodec`
- prefer one `SsdXsdataMapper`
- split into smaller helper mappers only if that mapper becomes hard to test
- avoid a large monolithic handwritten SSD XML codec

## Standard Versioning
Standard versioning should be explicit and centralized.

Rules:
- detect standard family and version once per document
- select the generated binding, codec, mapper, validator, and schema stack before parsing deeply
- avoid scattered `if version == ...` checks across public APIs and orchestration code
- keep version-specific schema differences in generated bindings and version-specific codec/mapper stacks
- keep shared workflow behavior version-independent where possible

Recommended routing shape:
- inspect namespace, root element, and version attribute
- resolve a `StandardVersion`
- select the version-specific stack
- parse and map with that stack

Recommended split:
- version-specific:
  - XSD files
  - generated bindings
  - schema validators
  - root codecs
  - mappers for schema differences
- version-independent where possible:
  - archive/session handling
  - public editing workflows
  - shared semantic validation rules
  - orchestration and persistence flow

Preferred implementation pattern:
- use a small registry/factory for `(format, family, version) -> stack`
- prefer separate versioned codec families over one codec with many internal branches
- use canonical domain models for shared concepts, and version-specific extensions only when semantics diverge materially

Compatibility note:
- schema version support, public API compatibility, and semantic behavior compatibility should be documented separately

## 4) Domain Model Layer (`model`)
Responsibility:
- hold compact typed objects for SSP/FMI concepts
- provide the stable shape used by validation, orchestration, and public APIs

Rules:
- no XML library elements in domain fields
- no generated binding objects in domain fields
- keep models closer to workflow needs than schema layout

## 5) Validation Layer (`validation`)
Responsibility:
- schema compliance checks
- semantic validation rules

Rules:
- schema validation checks XML/binding compliance
- semantic validation checks meaning: references, directions, cardinality, consistency
- validation stays representation-agnostic where possible

## 6) Orchestration Layer (`ssp`, 'ssd')
Responsibility:
- load related artifacts in shared context
- resolve cross-file references
- persist external artifacts
- expose compatibility behavior expected by higher-level APIs

Must own:
- archive-relative resolution
- binding state such as resolved/unresolved external references

Must not own:
- low-level XML parsing details

## 7) Public API Layer
Responsibility:
- preserve the existing user-facing workflow
- provide authoring/editing helpers
- hide version and schema-binding complexity

Examples:
- `add_component(...)`
- `connect(...)`
- `bind_parameters(...)`
- `save()` / `save_as()`

## Storage Strategy
Some data can appear inline or externally referenced.

Rule:
- keep one canonical domain model
- let the mapper/codec distinguish inline vs external XML representation
- let orchestration resolve external artifacts

Do not:
- resolve external files during plain parse
- duplicate validation logic for inline and external cases

## Suggested Package Shape
- `pyssp_standard/archive/`
- `pyssp_standard/ssp1/generated/`
- `pyssp_standard/ssp1/model/`
- `pyssp_standard/ssp1/codec/`
- `pyssp_standard/ssp1/validation/`
- `pyssp_standard/ssp2/...`
- `pyssp_standard/fmi2/...`
- `pyssp_standard/fmi3/...`
