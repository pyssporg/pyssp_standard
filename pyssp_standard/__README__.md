# Internal Library Layout

This document is the developer-oriented summary of how `pyssp_standard` is structured internally.
It is based on the architecture review in:

- `docs/RFC/architecture-review/__overview__.md`
- `docs/RFC/architecture-review/layered_arch.md`
- `docs/RFC/architecture-review/implementation-plan.md`

The intent is to explain how the library is built up, which layer owns what, and where new code should go.

Important distinction:

- this file documents both the target architecture and the current implementation state
- when they differ, the current code takes precedence for maintenance decisions
- the architecture review describes the direction of travel, not a claim that every layer is already fully migrated

## Purpose

The internal package is being moved toward a layered architecture with this authority chain:

- `XSD -> generated bindings -> codec/mapper -> domain model -> orchestration/public API`

That split exists to keep separate concerns separate:

- schema-shaped XML classes should stay generated
- handwritten code should work on compact domain models
- archive/session behavior should stay outside XML codecs
- public facades should stay thin

## Core Rule

Each layer should own one kind of responsibility only.

Recommended flow through the library:

- archive/session opens the package or file context
- version routing selects the correct stack
- codec parses XML
- mapper converts between generated XML bindings and compact domain models
- validation checks schema and semantics
- orchestration resolves related artifacts and persistence flow
- public API exposes a stable editing workflow

Current reality:

- some parts already follow this split closely
- some public facades still point directly at version-specific implementations
- SSD in particular is only partially migrated to the target split

## Layers

### 1. Archive Layer

Responsibility:

- open and save package containers such as `.ssp` and `.fmu`
- provide deterministic persistence behavior
- expose extracted file paths and archive-relative resolution

Current modules:

- `pyssp_standard/common/zip_archive.py`

Current reality:

- there is no dedicated `archive/` package yet
- archive/session responsibilities currently live under `common/`

Rules:

- archive code may handle directories, temp extraction, repacking, and file placement
- archive code must not parse schema-specific XML meaning
- archive code must not decide semantic validity

### 2. Generated Binding Layer

Responsibility:

- hold schema-shaped classes generated from XSD
- reflect the XML structure directly

Current modules:

- `pyssp_standard/standard/ssp1/generated/`
- `pyssp_standard/standard/ssp2/generated/`
- versioned generated modules for FMI and future standards are only partially present today

Rules:

- generated code is derived, not handwritten source of truth
- generated code is internal only
- do not add business logic to generated classes

### 3. Codec Layer

Responsibility:

- parse and serialize XML text
- isolate XML parser/serializer mechanics from business logic

Current modules:

- `pyssp_standard/standard/ssp1/codec/ssv_xsdata_codec.py`
- `pyssp_standard/standard/ssp1/codec/ssv_xsdata_mapper.py`
- `pyssp_standard/standard/ssp1/codec/ssd_xml_codec.py`
- `pyssp_standard/standard/ssp1/codec/ssm_xml_codec.py`
- equivalent versioned codec packages under `standard/ssp2`, `standard/fmi2`, `standard/fmi3`

Current reality:

- `SSV` is the clearest example of the intended generated-binding path
- `SSD` and `SSM` still use more handwritten XML codecs
- the mapper split is not yet consistent across all formats

Expected split:

- codec classes own parser/serializer setup and root document handling
- mapper classes convert generated bindings `<->` compact domain models
- codecs must not own archive I/O
- codecs must not own cross-file resolution

### 4. Domain Model Layer

Responsibility:

- define compact typed objects used by the rest of the system
- provide the stable in-memory shape used by validation, orchestration, and facades

Current modules:

- `pyssp_standard/standard/ssp1/model/`
- `pyssp_standard/standard/fmi2/model/`
- placeholder packages also exist for other standard families and versions

Rules:

- no raw XML element objects in model fields
- no generated binding objects in model fields
- models should reflect workflow concepts, not schema awkwardness

This is the canonical in-memory representation of document data.

Current reality:

- this is the intended rule and is mostly true for the newer SSP1 model paths
- some older compatibility-oriented behavior still lives in top-level facades

### 5. Validation Layer

Responsibility:

- schema compliance checks
- semantic validation checks

Current modules:

- `pyssp_standard/standard/ssp1/validation/`
- sibling validation packages for other standard families and versions

Current reality:

- SSP1 validation is the most concrete implementation
- several sibling validation packages currently exist mainly as scaffolding

Rules:

- schema validation checks binding/XML compliance
- semantic validation checks meaning: references, consistency, directions, cardinality
- validation should stay representation-agnostic where possible

### 6. Orchestration Layer

Responsibility:

- coordinate multiple related artifacts in one session
- resolve cross-file references
- persist external artifacts in the correct order
- expose shared workflow behavior above version-specific codecs

Current modules:

- `pyssp_standard/ssp.py`
- `pyssp_standard/common/extenal_references.py`
- `pyssp_standard/standard/version_routing.py`

Rules:

- orchestration owns archive-relative resolution
- orchestration owns temporary hydrated state for external references
- orchestration must not re-implement XML parsing details already owned by codecs

Current reality:

- `ssp.py` plus `common/extenal_references.py` are the active orchestration path for archive-aware SSD sessions
- `standard/version_routing.py` exists, but it is not yet the universal entry point for all public document facades

### 7. Public API Layer

Responsibility:

- preserve the user-facing workflow
- keep file/session usage simple
- hide version routing and schema-binding details

Current modules:

- `pyssp_standard/__init__.py`
- `pyssp_standard/ssd.py`
- `pyssp_standard/ssv.py`
- `pyssp_standard/ssm.py`
- `pyssp_standard/ssp.py`
- `pyssp_standard/fmu.py`
- `pyssp_standard/md.py`

Rules:

- public facades should stay thin
- editing helpers should delegate to the canonical model
- persistence should delegate to file/session/orchestration layers

Current reality:

- `SSV`, `SSD`, and `SSM` are already relatively thin wrappers over `XmlDocumentFacade`
- they are still directly bound to specific codec and validator implementations rather than fully routed through a central stack registry

## Versioning Strategy

Version handling is meant to be explicit and centralized.

Design rule:

- detect `(format, family, version)` once
- route to the correct generated binding, codec, mapper, and validator stack early
- keep scattered version checks out of higher-level workflows

Current module:

- `pyssp_standard/standard/version_routing.py`

Current reality:

- this module currently covers a narrow slice
- it contains registered parse stacks for `SSV`
- `get_standard_version(...)` currently recognizes `ParameterSet` documents and leaves the rest as TODO
- the top-level public facades are not yet broadly wired through this registry

What should vary by version:

- XSD files
- generated bindings
- root codecs
- schema validators
- mappers for version-specific schema differences

What should stay version-independent where possible:

- archive/session handling
- orchestration flow
- public editing workflow
- shared semantic validation rules

## External Reference Handling

Some SSP content may be inline in the SSD or externally referenced, for example:

- parameter bindings pointing to `.ssv`
- parameter mappings pointing to `.ssm`

Design rule:

- keep one canonical model shape regardless of inline or external storage
- let codec/mapper handle the representation difference
- let orchestration resolve external files during an archive session

Current implementation:

- standalone facades such as `SSD`, `SSV`, and `SSM` are file-local
- `SSP.system_structure` opens an archive-aware document session
- `ArchiveDocumentFacade` walks the loaded document tree for declared external reference slots
- referenced files are loaded once and cached by path and facade type
- parsed external documents are attached temporarily into the in-memory tree
- on close, external documents are saved first
- the temporary attachments are then removed so the parent document is saved with references, not inlined copies

This keeps plain parse/serialize logic simple and keeps cross-file behavior out of codecs.

Current scope:

- this behavior is currently implemented for `SSP.system_structure`
- the registered external reference slots are SSD parameter bindings to `.ssv` and SSD parameter mappings to `.ssm`

## How the Pieces Fit Together

For a typical `SSP` system-structure session, the flow is:

1. `SSP` opens an archive or directory runtime.
2. `ssp.system_structure` creates an archive-aware SSD session.
3. The SSD facade loads `SystemStructure.ssd` using its codec stack.
4. Orchestration walks the SSD domain model and resolves external references such as `.ssv` and `.ssm`.
5. Callers edit the hydrated in-memory model.
6. On close, orchestration saves external artifacts first.
7. The SSD is then saved in reference form.
8. The archive runtime persists the final package state.

For a standalone `SSV` or `SSM`, the flow is simpler:

1. the facade opens a single file
2. the codec parses it into the canonical model
3. edits happen on that model
4. validation and save operate on that single-file context only

Current reality:

- `SSD`, `SSV`, and `SSM` all inherit from `common/xml_document.py:XmlDocumentFacade`
- standalone facades therefore currently share the same basic context-manager/load/save behavior

## Current Package Map

The current repository does not yet fully match the target names used in the RFC, but the intent is:

- `common/`
  shared infrastructure such as archive/session helpers and generic external-reference orchestration
- `standard/version_routing.py`
  shared version-selection entry point
- `standard/<family>/<layer>/`
  versioned implementation stacks
- top-level public modules such as `ssd.py`, `ssv.py`, `ssm.py`, `ssp.py`
  public entrypoints and compatibility facades

Notable current state:

- some modules still use older naming or placement
- some codecs are still more handwritten than the target architecture prefers
- the implementation plan treats `SSP1` `SSV` as the reference vertical slice for the target architecture
- SSD support is in progress and not yet fully migrated to the preferred `xsdata + mapper` split

## Where New Code Should Go

Use this rule of thumb:

- archive mechanics: `common/zip_archive.py` or a dedicated shared archive helper
- generic archive document session behavior: `common/extenal_references.py`
- version selection: `standard/version_routing.py`
- standard-specific domain concepts: `standard/<family>/model/`
- standard-specific parse/serialize logic: `standard/<family>/codec/`
- standard-specific validation: `standard/<family>/validation/`
- user-facing wrapper behavior: top-level facade modules such as `ssv.py` and `ssp.py`

Before adding code, ask:

- is this XML-shape logic, model logic, orchestration logic, or public facade logic?
- does it belong to one standard version, or is it shared?
- can it be pushed down into codec/mapper/model instead of growing the public facade?

Current preference:

- if you are touching archive-aware external reference behavior today, the active home is `common/extenal_references.py` plus the SSP-specific wiring in `ssp.py`
- if you are touching plain XML-backed file behavior today, the active base class is `common/xml_document.py`

## Practical Guidance

When changing the library:

- prefer extending the canonical model rather than adding parallel facade state
- prefer orchestration for cross-file behavior
- prefer version-specific stacks over condition-heavy shared codecs
- prefer small registries/factories for selecting stacks
- do not put archive logic in codecs
- do not put XML business logic in archive helpers
- do not hand-edit generated bindings

If a feature touches multiple layers, the desired direction is usually:

- add model support
- extend mapper/codec support
- add validation as needed
- wire it into orchestration if cross-file behavior is required
- expose it through the public facade last
