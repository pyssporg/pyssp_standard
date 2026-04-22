# Requirements Baseline

This page is for maintainers who need a first explicit list of application requirements for `pyssp_standard`.

It captures:
- application-level behavioral requirements
- requirements inferred from implementation and tests

This is a starting baseline, not a frozen specification. Items marked as implicit should be confirmed or revised as the project evolves.

Design choices, API layout, and workflow examples belong in the architecture and user documentation. This page focuses on requirements that constrain behavior.

## Scope

The current application is a Python library for inspecting and editing SSP-related artifacts, including:
- SSP archives and unpacked SSP directories
- SSD, SSM, and SSV XML documents
- FMU archives and unpacked FMU directories
- FMI `modelDescription.xml`

## Requirements

These are inferred from the current implementation, tests, and user-facing documentation and should be treated as the first draft of application requirements.

### Document Lifecycle

- The application shall support reading, creating, and editing SSP-related XML artifacts and archive content.
- Successful edit sessions shall persist changes; failed sessions shall not partially commit changes.
- Creating a new supported document shall produce a minimal valid document skeleton.
- Compliance checking shall be an explicit operation, not an automatic side effect of save.

### File and Archive Handling

- The application shall support both archive-backed and directory-backed workflows for `.ssp` and `.fmu` content.
- Archive-backed workflows shall use a temporary extracted working directory and clean it up after the context exits.
- Directory-backed workflows shall operate directly on the persistent directory tree.
- New SSP containers shall be able to create and persist a `SystemStructure.ssd` entry.
- The application shall support adding, listing, and removing SSP resources.

### Cross-Document Behavior

- The application shall preserve external SSD references even when they are not resolved.
- In archive-aware SSP workflows, the application shall resolve supported external `.ssv` and `.ssm` references when the referenced files exist and can be parsed.
- Changes made through resolved external references shall persist back to the referenced source files on successful exit.

### Round-Trip Preservation

Current support and future intent need to stay separate here. The library already preserves some round-trip properties, while others are only targets for future stabilization.

#### Supported Now

- Read-modify-write workflows shall preserve supported metadata across SSD, SSM, SSV, and FMI model description content.
- Read-modify-write workflows shall preserve supported annotation and extension content rather than discarding it.
- Read-modify-write workflows shall preserve the input order of supported repeated child elements whenever no intentional reordering was requested.
- Output serialization shall preserve those logical collection orders so line-oriented and textual diff tools remain effective during review.
- SSD round trips shall preserve supported structural content such as connectors, connections, component attributes, and default experiment data.
- SSM round trips shall preserve mapping entries and transformation definitions.
- SSV round trips shall preserve parameters, units, and enumerations.

Examples of supported ordering today:
- if an input `SSV` lists parameters in the order `beta`, `alpha`, `gamma`, the round-tripped document should preserve that logical parameter order
- if an input `SSD` lists connections in the order `B -> bus` before `A -> bus`, the round-tripped document should preserve that connection order
- if an input FMI `modelDescription.xml` lists variables or outputs in a specific order, the round-tripped document should preserve that order

#### Not Guaranteed Now

- XML lexical details that are not represented as ordered model data are not required to round-trip byte-for-byte.
- This currently includes attribute order, namespace prefix choice, indentation, line wrapping, and serializer-chosen canonical section ordering.

Examples of what is not currently guaranteed:
- an input element with attributes written as `target="x" source="y"` may be serialized back as `source="y" target="x"`
- an input document using one namespace prefix spelling may be serialized with a different prefix spelling
- an input document that places sections in a non-canonical order may be serialized in the serializer's preferred section order
  example: an input `modelDescription.xml` that lists `ModelVariables` before `UnitDefinitions` may be serialized back with `UnitDefinitions` before `ModelVariables`

#### Future Compatibility Target

- The library should converge on deterministic serializer-originated ordering for emitted tags and attributes so newly created or normalized files remain stable and reviewable as the library evolves.
- Once serializer-originated ordering is defined per supported document type, it should be treated as an explicit compatibility target and covered by dedicated tests.

Examples of future serializer-level guarantees:
- newly created `SSM` files should emit mapping entry attributes in one documented order
- newly created `SSV` files should emit top-level sections in one documented order
- normalized `SSD` output should use one documented tag and attribute ordering strategy across releases

### Validation Expectations

- SSP and FMI reference documents that are treated as valid by the project test suite shall pass compliance checks.
- SSV validation shall reject references to unknown custom units.
- SSV validation shall accept built-in bracketed unit syntax such as `[m]`.
- The application shall allow creation and editing workflows that remain compliant after supported modifications.

### FMU Access

- The application shall expose FMU binaries, documentation entries, and `modelDescription.xml` content from both archive-backed and directory-backed FMUs.
- Archive-backed and directory-backed FMU access shall present equivalent model description content to callers.

## Gaps To Confirm

The current code suggests open questions that should become explicit decisions later:

- Whether missing XML files in `r` or `a` mode should be treated as an error or as implicit document creation.
- Which malformed external references should fail loudly versus degrade to unresolved `None`.
- Whether compliance validation should be required before persistence in some workflows.
- Which parts of the public facade API are intended to remain stable versus experimental.
- How far annotation and extension preservation must go for unsupported or unknown SSP/FMI content.
