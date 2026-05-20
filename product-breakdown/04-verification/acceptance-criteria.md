# Acceptance Criteria

> **Layer:** 04-verification
> **Artifact type:** acceptance-criteria.md

## Criteria (Inferred from Requirements and Tests)

### Document Lifecycle

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-001 | Reading an existing XML document shall produce a populated in-memory model | Codec tests: parse fixture → model != None |
| AC-002 | Creating a new document in `w` mode shall produce a minimal valid skeleton | Facade tests: create → serialize → validate |
| AC-003 | Editing a document in `a` mode and exiting normally shall persist changes | Facade + orchestration tests |
| AC-004 | Editing and exiting with an exception shall not persist changes | Implicit in `XmlDocument.__exit__` logic |
| AC-005 | `check_compliance()` shall not be called automatically on read | `XmlDocument.__enter__` does not validate |

### Round-Trip Preservation

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-006 | Element order shall be preserved for supported collections (parameters, connections, mappings, variables) | Codec tests compare element order before/after |
| AC-007 | Annotations and extensions shall be preserved in read-modify-write | Codec tests parsing same fixture |
| AC-008 | Line-oriented diff tools shall remain effective on serialized output | Element order guaranteed by codec design |

### File and Archive Handling

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-009 | `.ssp` archives and directories shall produce equivalent API behavior | `SSP` facade tests with both fixture types |
| AC-010 | Archive-backed SSPs shall use a temporary directory cleaned up on context exit | Archive runtime tests |
| AC-011 | Adding and removing resources in an SSP shall work in both archive and directory modes | `pytest/ssp1/orchestration/test_ssp.py` |

### Cross-Document Resolution

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-012 | External `.ssv`/`.ssm` references shall be resolved when referenced files exist and are parseable | Orchestration tests (indirect) |
| AC-013 | External references shall be preserved even when not resolved | Orphan references survive round-trip |
| AC-014 | Changes to resolved external documents shall persist to source files on save | Orchestration tests |

### Validation

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-015 | Valid reference documents shall pass compliance checks | Facade tests: `check_compliance()` returns True |
| AC-016 | SSV validation shall reject unknown custom units | `Ssp1SsvValidator` unit validation |
| AC-017 | SSV validation shall accept built-in bracketed unit syntax `[m]` | Unit tests in validator |
| AC-018 | SSP1 documents created or edited through the API shall remain compliant | Facade tests validate output |

### FMU Access

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-019 | FMU access shall expose binaries, documentation, and modelDescription | FMU archive tests |
| AC-020 | Archive-backed and directory-backed FMU access shall be equivalent | Both fixture types tested |

## Round-Trip Preservation Detail

### Supported Now

- Read-modify-write preserves supported metadata across SSD, SSM, SSV, and FMI model description content
- Preserves annotation and extension content rather than discarding it
- Preserves input order of supported repeated child elements (parameters, connections, mappings, variables)
- Output preserves logical collection order so diff tools remain effective
- SSD preserves: connectors, connections, component attributes, default experiment data
- SSM preserves: mapping entries, transformation definitions
- SSV preserves: parameters, units, enumerations

Examples of preserved ordering:
- Input SSV with parameters `beta`, `alpha`, `gamma` → output preserves that logical parameter order
- Input SSD connections `B -> bus` before `A -> bus` → output preserves that connection order
- Input FMI `modelDescription.xml` variable/output ordering → output preserves that order

### Not Guaranteed Now

- XML lexical details not represented as ordered model data: attribute order, namespace prefix choice, indentation, line wrapping, serializer-chosen section ordering
- Example: attribute order `target="x" source="y"` may serialize as `source="y" target="x"`
- Example: namespace prefix spelling may differ
- Example: non-canonical section ordering may be normalized

### Future Compatibility Target

- Deterministic serializer-originated ordering for emitted tags and attributes
- Newly created/edited files should remain stable and reviewable across releases
- Once defined per document type, treated as explicit compatibility target with dedicated tests

## Scope Limitations (Not Currently Guaranteed)

- XML lexical details: attribute order, namespace prefix spelling, indentation
- Full byte-for-byte round trips
- Serializer-originated tag and attribute ordering (future compatibility target)

## Evidence

- `04-verification/traceability-matrix.md`: requirement-to-test mapping
- `pytest/` test files: each test exercises one or more acceptance criteria
- `common/xml_document.py`: lifecycle implementation