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

## Scope Limitations (Not Currently Guaranteed)

- XML lexical details: attribute order, namespace prefix spelling, indentation
- Full byte-for-byte round trips
- Serializer-originated tag and attribute ordering (future compatibility target)

## Evidence

- `docs/dev/requirements.md`: 20+ behavioral requirements
- `pytest/` test files: each test exercises one or more acceptance criteria
- `common/xml_document.py`: lifecycle implementation