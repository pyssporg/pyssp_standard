# Constraints

> **Layer:** 00-intent
> **Artifact type:** constraints.md

## Technology Constraints

| ID | Constraint | Source | Impact |
|----|-----------|--------|--------|
| CON-001 | Python 3.x standard library only for XML parsing (`xml.etree.ElementTree`) | `docs/dev/repo_status.md`, all codec modules | No lxml or external XML dependency |
| CON-002 | Standard library `zipfile` for archive handling | `common/archive.py` | No archive library dependency |
| CON-003 | Dataclasses as canonical model representation | `standard/ssp1/model/*`, `standard/fmi2/model/*` | No ORM or heavy persistence framework |
| CON-004 | No external runtime dependencies (pure Python) | `README.md`, `pyproject.toml` (implicit) | Library is pip-installable without heavy dependency chain |

## Standard Constraints

| ID | Constraint | Source | Impact |
|----|-----------|--------|--------|
| CON-005 | Must support SSP1 and FMI2 as active standards | `docs/dev/repo_status.md`, `product-breakdown/index.md` | Active codec/model/validation layers |
| CON-006 | SSP2 and FMI3 skeletons exist but are not implemented | `standard/ssp2/` (empty), `standard/fmi3/` (empty), `06-evolution/improvement-backlog.md` (G1, G2) | Cannot parse SSP2/FMI3 documents |
| CON-007 | Version routing must detect document root to select standard stack | `standard/version_routing.py` | Routing exists but is not the universal entry point |
| CON-008 | Round-trip preservation: element order, annotations, extensions | `docs/dev/requirements.md` | Codecs must preserve logical collection ordering |

## Design Constraints

| ID | Constraint | Source | Impact |
|----|-----------|--------|--------|
| CON-009 | Archive code must not parse XML semantics | `docs/dev/architecture.md` | Layer separation enforced by architecture rules |
| CON-010 | Codecs must not own archive I/O | `docs/dev/architecture.md` | Codecs are pure parse/serialize |
| CON-011 | Validation must remain separate from parsing and persistence | `docs/dev/guidelines.md` | Validation is explicit, not automatic |
| CON-012 | Public facades must stay thin | `docs/dev/architecture.md` | Editing helpers delegate to canonical model |

## Derived Constraints

| ID | Constraint | Source | Impact |
|----|-----------|--------|--------|
| CON-013 | Compliance check is explicit (`check_compliance()`) not automatic | `common/xml_document.py`, `docs/dev/requirements.md` | User must explicitly call .check_compliance() |
| CON-014 | External references preserved even when not resolved | `docs/dev/requirements.md` | `document_runtime.py` keeps source attributes |
| CON-015 | Changes through resolved external references persist back on success | `docs/dev/requirements.md` | `document_runtime.py` saves external docs on mode 'w'/'a' |

## Evidence

- All codec modules: `from xml.etree import ElementTree as ET`
- `common/archive.py`: `import zipfile`
- `docs/dev/architecture.md`: 7-layer architecture with explicit rules
- `docs/dev/requirements.md`: 15+ behavioral requirements
- `docs/dev/guidelines.md`: separation of concerns