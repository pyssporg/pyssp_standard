# Repo Status

This page summarizes the current implementation state of `pyssp_standard`.
It is for maintainers who need to know what is true in the codebase today.

Use `dev/architecture.md` for intended layer boundaries.

## Current Direction

The active implementation currently favors:

- plain dataclass document models
- direct `xml.etree.ElementTree` codecs
- small shared XML helper utilities when they reduce duplication
- thin top-level facades over shared document runtime behavior

## Layer Status

### Archive Layer

Current status:

- archive and directory runtime behavior lives under `pyssp_standard/common/`
- there is not a separate dedicated `archive/` package

### Schema and Binding Layer

Current status:

- schemas are still tracked and registered
- schema target registration is centralized in `pyssp_standard/tools/schema_targets.py`
- generated binding output paths are still registered for tooling and routing metadata
- active SSP1 and FMI2 runtime parsing no longer depends on generated binding modules

### Codec Layer

Current status:

- `SSP1` `SSD`, `SSV`, and `SSM` use direct `ElementTree` codecs
- `FMI2` model description uses a direct `ElementTree` codec
- shared SSP XML fragments are factored into `standard/ssp1/codec/xml_utils.py`

### Domain Model Layer

Current status:

- `standard/ssp1/model/` and `standard/fmi2/model/` provide the active in-memory document shapes
- newer paths mostly operate on compact dataclass models

### Validation Layer

Current status:

- SSP1 validation is the most complete and concrete validation path
- FMI2 model description schema validation is active
- sibling validation packages for other standards exist with varying depth

### Orchestration Layer

Current status:

- archive-aware SSP behavior is implemented through `ssp.py` and shared runtime helpers
- external SSD references to `.ssv` and `.ssm` are resolved in archive-aware sessions
- version routing exists, but it is not the universal entry point for every public facade

### Public API Layer

Current status:

- `SSV`, `SSD`, and `SSM` are relatively thin wrappers over shared XML document behavior
- public facades still instantiate specific codec and validator implementations directly

## Version Routing Status

Current status:

- `standard/version_routing.py` contains registered stacks for:
  - SSP1 `SSV`, `SSD`, `SSM`
  - SSP2 `SSV`
  - FMI2 model description
- version detection currently recognizes those document roots
- routing metadata still includes schema and binding-output information for tooling-oriented use

## External Reference Status

Current status:

- standalone `SSD`, `SSV`, and `SSM` remain file-local
- archive-aware `SSP.system_structure()` sessions hydrate external `.ssv` and `.ssm` documents into memory
- referenced external documents are saved first, then detached before the parent SSD is persisted

## Current Package Map

Current active structure:

- `common/`
  shared runtime, archive, and document-session helpers
- `standard/version_routing.py`
  version-selection registry and document-root detection
- `standard/<family>/codec/`
  version-specific or family-specific XML codecs
- `standard/<family>/model/`
  in-memory document models
- `standard/<family>/validation/`
  validators
- top-level modules such as `ssd.py`, `ssv.py`, `ssm.py`, `ssp.py`, `md.py`
  public entry points

## Active Maintenance Preferences

Current preference:

- if you are touching archive-aware external reference behavior, the active home is the shared document runtime plus SSP-specific wiring
- if you are touching plain XML-backed file behavior, the active base is the shared XML document workflow plus the format codec
- if you need schema-target metadata, use `tools/schema_targets.py`

## Notes

This page should describe current reality only.

If code and architecture guidance disagree:

- maintenance decisions should follow the codebase as it exists today
- architectural changes should first update `dev/architecture.md`, then the implementation
