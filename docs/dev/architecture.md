# Architecture

This page explains the intended internal structure of `pyssp_standard`.
It is for maintainers deciding where new code should go.

Use this page for architectural boundaries and layer ownership.
Use `dev/repo_status.md` for what is currently implemented.

## Purpose

The library is organized around a layered XML-document workflow:

- XML schema and format definitions
- version-specific codec and validation stacks
- compact in-memory document models
- orchestration for archive-aware workflows
- thin public facades

The goal is to keep each layer responsible for one kind of concern.

## Core Flow

Recommended flow through the library:

1. archive or file runtime opens the working context
2. version routing selects the correct standard stack
3. codec parses or serializes XML text
4. validation checks schema and semantic rules
5. orchestration resolves related artifacts and persistence order
6. public API exposes the editing workflow

## Layers

### Archive Layer

Responsibility:

- open and save package containers such as `.ssp` and `.fmu`
- provide deterministic persistence behavior
- expose extracted paths and archive-relative resolution

Rules:

- archive code may handle directories, extraction, repacking, and file placement
- archive code must not parse schema-specific XML semantics
- archive code must not decide document meaning

### Schema and Binding Layer

Responsibility:

- hold standard schemas and any generated or derived schema-shaped artifacts
- reflect format structure directly when such artifacts are used

Rules:

- schema-derived artifacts are internal
- schema-derived artifacts must not contain business logic
- handwritten behavior belongs in codec, model, validation, or orchestration layers

### Codec Layer

Responsibility:

- parse and serialize XML text
- isolate XML parser and serializer mechanics from workflow logic

Rules:

- codecs own document-shape translation
- codecs must not own archive I/O
- codecs must not own cross-file resolution

### Domain Model Layer

Responsibility:

- define compact typed objects used by the rest of the system
- provide the canonical in-memory representation used by validation and editing

Rules:

- models should reflect workflow concepts, not schema awkwardness
- generated binding objects should not leak into model state
- archive/session state should not leak into model state

### Validation Layer

Responsibility:

- schema compliance checks
- semantic validation checks

Rules:

- schema validation checks XML or document-shape compliance
- semantic validation checks meaning, consistency, references, and constraints
- validation should stay representation-agnostic where possible

### Orchestration Layer

Responsibility:

- coordinate multiple related artifacts in one session
- resolve cross-file references
- persist external artifacts in the correct order

Rules:

- orchestration owns archive-relative resolution
- orchestration owns multi-document persistence flow
- orchestration must not re-implement XML parsing details already owned by codecs

### Public API Layer

Responsibility:

- preserve the user-facing workflow
- keep file and session usage simple
- hide version-specific implementation choices
- expose a small set of entry points for SSP, SSD, SSM, SSV, FMU, and model description workflows

Rules:

- public facades should stay thin
- editing helpers should delegate to the canonical model
- persistence should delegate to document and orchestration layers

## Versioning Strategy

Version handling should be explicit and centralized.

Design rule:

- detect `(format, family, version)` once
- route to the correct codec, validator, and schema stack early
- avoid scattered version checks in higher-level workflows

What should vary by version:

- XSD files
- schema-target registrations
- root codecs
- schema validators
- version-specific semantic handling

What should stay version-independent where possible:

- archive and file runtime behavior
- orchestration flow
- public editing workflow
- shared helper utilities

## External Reference Handling

Some SSP content may be inline in the SSD or externally referenced, for example:

- parameter bindings pointing to `.ssv`
- parameter mappings pointing to `.ssm`

Design rule:

- keep one canonical model shape regardless of inline or external storage
- let codecs handle representation differences
- let standalone document facades remain file-local
- let orchestration resolve external files during archive-aware sessions

This keeps file-local parse and serialize logic simple and keeps cross-file behavior out of codecs.

## How the Pieces Fit Together

For a typical archive-aware `SSP` system-structure session:

1. `SSP` opens an archive or directory runtime
2. `ssp.system_structure()` creates an archive-aware SSD session
3. the SSD facade loads `SystemStructure.ssd` through its codec stack
4. orchestration resolves referenced `.ssv` and `.ssm` files
5. callers edit the hydrated in-memory model
6. external artifacts are saved first
7. the SSD is saved in reference form
8. the archive runtime persists the final package state

For a standalone `SSV` or `SSM`:

1. the facade opens a single file
2. the codec parses it into the canonical model
3. edits happen on that model
4. validation and save operate on that single-file context

## Where New Code Should Go

Use this rule of thumb:

- archive mechanics: shared archive/runtime helpers
- version selection: `standard/version_routing.py`
- standard-specific models: `standard/<family>/<version or shared>/model/`
- standard-specific parse and serialize logic: `standard/<family>/<version or shared>/codec/`
- standard-specific validation: `standard/<family>/<version or shared>/validation/`
- user-facing wrapper behavior: top-level facade modules such as `ssv.py` and `ssp.py`

Before adding code, ask:

- is this XML-shape logic, model logic, orchestration logic, or public facade logic?
- does it belong to one standard version, or is it shared?
- can it be pushed down into codec, model, or validation instead of growing the public facade?

## Practical Guidance

When changing the library:

- prefer extending the canonical model rather than adding parallel facade state
- prefer orchestration for cross-file behavior
- prefer small registries for selecting version-specific stacks
- do not put archive logic in codecs
- do not put XML business logic in archive helpers
- do not mix user-facing facade concerns with schema-specific parsing details
