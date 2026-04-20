

## Layered Architecture
Adopt a layered architecture with strict boundaries:

Detailed archive-layer contract and failure semantics:
- `../archive_solution.md`

### 1) Archive Layer (`archive`)
Responsibility:
- Read/write package containers (`.ssp`, `.fmu`) and in-archive path operations.
- Provide explicit dirty tracking and deterministic persistence.
- Provide raw XML/bytes access for higher layers.

Key APIs:
- `ArchiveSession.open(path, mode)`
- `ArchiveSession.read_bytes(rel_path)`
- `ArchiveSession.write_bytes(rel_path, data, overwrite=False)`
- `ArchiveSession.remove(rel_path)`
- `ArchiveSession.save()` / `save_as(path)`

Design choices:
- Read operations never mark dirty.
- Mutating operations always mark dirty.
- Context manager keeps compatibility; explicit save is preferred internally.

### 2) Domain Model Layer (`model`)
Responsibility:
- Canonical typed objects for SSP/FMI constructs, independent of XML library types.
- Should enable reuse of earlier versions or rewrites if necessary

Examples:
- `Ssp1SystemStructureDescription`, `Ssp2SystemStructureDescription`, `Ssp1System`, `Ssp1Component`, `Ssp1Connector`, `Ssp1Connection`
- `Ssp1ParameterSet`, `Ssp1ParameterMapping`, `Ssp1SignalDictionary`
- `Fmi2ModelDescription`, `Fmi3ModelDescription`


Design choices:
- Dataclass-based models with validation hooks.
- No direct `lxml` elements in public model fields.

### 3) Codec Layer (`codec`)
Responsibility:
- Parse/serialize XML <-> model for each format/version.
- Should enable reuse of earlier versions or rewrites if necessary

Structure:
- `codec.ssp1.ssd`, `codec.ssp2.ssd`
- `codec.fmi2.model_description`, `codec.fmi3.model_description`


Design choices:
- One codec module per format/version pair.
- Lossless round-trip for supported schema elements.
- Explicit unsupported-feature errors for uncovered branches.
- Use storage strategies for equivalent model data that can be represented in multiple ways (inline vs external).
- Codecs are pure transforms: no filesystem/archive I/O.

### 3.1) Storage Strategy
Requirement:
- Some data values may appear inline or as external resource.
- The architecture must support both without duplicating core mapping/validation logic.

Implementations:
- `InlineStorage`: read/write XML subtree embedded.
- `ExternalStorage`: represent external reference metadata in SSD only.

Approach:
- Keep one canonical domain model
- Add reusable internal/external interface used by codec:

Resolution policy:
- parsing does not resolve external artifacts.
- SSP-level orchestrator resolves external references only when artifacts are within the same SSP context.

Benefits:
- Single model and semantic validator path for both representations.
- No duplicated parsing/business logic.

### 4) Validation Layer (`validation`)
Responsibility:
- XSD validation and semantic validation.

Structure:
- `validation.schema` for XML schema compliance.
- `validation.semantic` for rules (connection directionality, cardinality, references).

Design choices:
- Validation results returned as structured diagnostics.
- Optional strict mode that raises on warnings for CI pipelines.
- Semantic rules are representation-agnostic: inline/external parameter sets produce equivalent diagnostics for equivalent content.

### 5) SSP Orchestration Layer (`ssp`)
Responsibility:
- Parse related artifacts in a shared context (e.g., all files in one SSP archive).
- Resolve cross-file references (e.g., SSD `ParameterBinding@source` -> SSV file).
- Set explicit binding flags (`is_inlined`, `is_resolved`) after resolution.

Current demo mapping:
- `PublicSSD`: SSD-facing API (document creation/edit/serialize)
- `PublicSSV`: parameter-set API (add parameter + SSV load/save)
- `PublicSSP`: orchestration API (resolve external references in shared context)
- `SsdBindingCodec`: XML-only SSD transform (no file I/O)
- `Ssv2HybridCodec`: XML-only SSV transform using xsdata-generated bindings


## API and UX Strategy (Authoring/Editing First)
- Keep current context-manager authoring flow.
- Add explicit high-level authoring operations:
  - `add_component(...)`
  - `add_connector(...)`
  - `connect(...)`
  - `bind_parameters(...)`
  - `add_resource(...)`
- Add deterministic persistence:
  - Introduce explicit `save()` and `save_as()` and in docs.
- Add stable exceptions:
  - `SchemaValidationError`
  - `SemanticValidationError`
  - `ArchiveStateError`
  - `CompatibilityError`


## Module Layout Proposal
Suggested package organization:
- `pyssp_standard/archive/`
- `pyssp_standard/ssp1/model`
- `pyssp_standard/ssp1/codec`
- `pyssp_standard/ssp1/validation`
- `pyssp_standard/ssp2/...`
- `pyssp_standard/fmi2/`
- `pyssp_standard/fmi3/`


## Success Metrics
- Feature:
  - Full SSP2 and FMI2/FMI3 test fixtures supported.
- Reliability:
  - Zero known data-loss parse/serialize issues in supported features.
- Developer productivity:
  - Reduced lines touched per new schema feature (tracked by PR stats).
- Usability:
  - New authoring examples require fewer low-level XML operations.

## Immediate Next Actions
1. Create compatibility test baseline for current public API.
2. Fix known blocking correctness issues in legacy modules.
3. Implement archive layer and route `SSP`/`FMU` through it.
4. Deliver SSP2 SSV support first (highest current test pressure), then SSD/SSM/SSB.
5. Deliver FMI2 codec and unify FMI2/FMI3 query interface.
