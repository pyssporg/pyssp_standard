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

- Read-modify-write workflows shall preserve supported metadata across SSD, SSM, SSV, and FMI model description content.
- Read-modify-write workflows shall preserve supported annotation and extension content rather than discarding it.
- Read-modify-write workflows shall preserve input ordering for supported repeated elements whenever no intentional reordering was requested.
- Output serialization shall reflect the original logical order of inputs so line-oriented and textual diff tools remain effective during review.
- SSD round trips shall preserve supported structural content such as connectors, connections, component attributes, and default experiment data.
- SSM round trips shall preserve mapping entries and transformation definitions.
- SSV round trips shall preserve parameters, units, and enumerations.

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
