# Constraints

> **Layer:** 00-intent
> **Artifact type:** constraints.md

## Technology Constraints

| ID | Constraint | Source | Impact |
|----|-----------|--------|--------|
| CON-001 | Python 3.x standard library only for XML parsing (`xml.etree.ElementTree`) | `02-architecture/quality-attributes.md`, all codec modules | No lxml or external XML dependency |
| CON-005 | Must support SSP1 and FMI2 as active standards | `02-architecture/quality-attributes.md`, `product-breakdown/index.md` | Active codec/model/validation layers |
| CON-008 | Round-trip preservation: element order, annotations, extensions | `04-verification/acceptance-criteria.md` | Codecs must preserve logical collection ordering |
| CON-013 | Compliance check is explicit (`check_compliance()`) not automatic | `common/xml_document.py`, `04-verification/acceptance-criteria.md` | User must explicitly call .check_compliance() |
| CON-014 | External references preserved even when not resolved | `common/xml_document.py` | `document_runtime.py` keeps source attributes |
| CON-015 | Changes through resolved external references persist back on success | `04-verification/acceptance-criteria.md` | `document_runtime.py` saves external docs on mode 'w'/'a' |

## Evidence

- All codec modules: `from xml.etree import ElementTree as ET`
- `common/archive.py`: `import zipfile`
- `02-architecture/layer-rules.md`: per-layer rules and responsibilities
- `04-verification/acceptance-criteria.md`: behavioral requirements
- `03-implementation/code-structure.md`: code organization patterns