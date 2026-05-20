# Layer Rules

> **Layer:** 02-architecture
> **Artifact type:** layer-rules.md

Each layer owns one concern. The rules below define what each layer may and may not do.

## Archive Layer

**Responsibility:** Open and save package containers (`.ssp`, `.fmu`), provide deterministic persistence, expose extracted paths and archive-relative resolution.

Rules:
- May handle directories, extraction, repacking, and file placement
- Must not parse schema-specific XML semantics
- Must not decide document meaning

## Schema and Binding Layer

**Responsibility:** Hold standard schemas and any generated/derived schema-shaped artifacts.

Rules:
- Schema-derived artifacts are internal
- Must not contain business logic
- Handwritten behavior belongs in codec, model, validation, or orchestration

## Codec Layer

**Responsibility:** Parse and serialize XML text. Isolate XML mechanics from workflow logic.

Rules:
- Codecs own document-shape translation
- Must not own archive I/O
- Must not own cross-file resolution

## Domain Model Layer

**Responsibility:** Define compact typed objects used by the rest of the system. Provide the canonical in-memory representation.

Rules:
- Models should reflect workflow concepts, not schema awkwardness
- Generated binding objects must not leak into model state
- Archive/session state must not leak into model state

## Validation Layer

**Responsibility:** Schema compliance checks and semantic validation.

Rules:
- Schema validation checks XML / document-shape compliance
- Semantic validation checks meaning, consistency, references, constraints
- Validation should stay representation-agnostic where possible

## Orchestration Layer

**Responsibility:** Coordinate multiple related artifacts in one session. Resolve cross-file references. Persist external artifacts in correct order.

Rules:
- Orchestration owns archive-relative resolution
- Orchestration owns multi-document persistence flow
- Must not re-implement XML parsing details already owned by codecs

## Public API Layer

**Responsibility:** Preserve the user-facing workflow. Keep file and session usage simple. Hide version-specific choices. Expose a small set of entry points.

Rules:
- Public facades should stay thin
- Editing helpers should delegate to the canonical model
- Persistence should delegate to document and orchestration layers

## Cross-Cutting Design Rules

### Versioning
- Detect `(format, family, version)` once, route to the correct stack early
- Avoid scattered version checks in higher-level workflows
- Vary by version: XSD files, schema-target registrations, root codecs, validators, semantic handling
- Stay version-independent: archive/file runtime, orchestration flow, public editing workflow, shared utilities

### External References
- Keep one canonical model shape regardless of inline or external storage
- Codecs handle representation differences
- Standalone document facades remain file-local
- Orchestration resolves external files during archive-aware sessions

### Placement Guidance
- Archive mechanics → `common/archive/` helpers
- Version selection → `standard/version_routing.py`
- Standard-specific models → `standard/<family>/<version>/model/`
- Standard-specific codecs → `standard/<family>/<version>/codec/`
- Standard-specific validation → `standard/<family>/<version>/validation/`
- User-facing facades → top-level modules (`ssv.py`, `ssp.py`, etc.)

Before adding code, ask:
- Is this XML-shape logic, model logic, orchestration logic, or public facade logic?
- Does it belong to one standard version, or is it shared?
- Can it be pushed down into codec, model, or validation instead of growing the public facade?

## Practical Guidance

| Do | Don't |
|----|-------|
| Prefer extending the canonical model over adding parallel facade state | Put archive logic in codecs |
| Prefer orchestration for cross-file behavior | Put XML business logic in archive helpers |
| Prefer small registries for selecting version-specific stacks | Mix user-facing facade concerns with schema-specific parsing details |