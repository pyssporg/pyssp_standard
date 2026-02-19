

## Layered Architecture
Adopt a layered architecture with strict boundaries:

Detailed archive-layer contract and failure semantics:
- `../archive_solution.md`

### 1) Archive Layer (`archive`)
Responsibility:
- Read/write package containers (`.ssp`, `.fmu`) and in-archive path operations.
- Provide explicit dirty tracking and deterministic persistence.
- Resolve referenced resources used by XML codecs (e.g., external `.ssv` from `.ssd`).

Key APIs:
- `ArchiveSession.open(path, mode)`
- `ArchiveSession.read_bytes(rel_path)`
- `ArchiveSession.write_bytes(rel_path, data, overwrite=False)`
- `ArchiveSession.remove(rel_path)`
- `ArchiveSession.save()` / `save_as(path)`
- `ResourceResolver.open_text(uri_or_rel_path, context_path)`
- `ResourceResolver.write_text(uri_or_rel_path, context_path, content)`

Design choices:
- Read operations never mark dirty.
- Mutating operations always mark dirty.
- Context manager keeps compatibility; explicit save is preferred internally.

### 2) Domain Model Layer (`model`)
Responsibility:
- Canonical typed objects for SSP/FMI constructs, independent of XML library types.

Examples:
- `SystemStructureDescription`, `System`, `Component`, `Connector`, `Connection`
- `ParameterSet`, `ParameterMapping`, `SignalDictionary`
- `FmiModelDescriptionV2`, `FmiModelDescriptionV3`

Design choices:
- Dataclass-based models with validation hooks.
- No direct `lxml` elements in public model fields.

### 3) Codec Layer (`codec`)
Responsibility:
- Parse/serialize XML <-> model for each format/version.

Structure:
- `codec.ssp1.ssd`, `codec.ssp2.ssd`
- `codec.fmi2.model_description`, `codec.fmi3.model_description`

Design choices:
- One codec module per format/version pair.
- Lossless round-trip for supported schema elements.
- Explicit unsupported-feature errors for uncovered branches.
- Use storage strategies for equivalent model data that can be represented in multiple ways (inline vs external).

### 3.1) ParameterSet Storage Strategy (SSD <-> SSV)
Requirement:
- In SSD, parameter values may appear inline or as external SSV references.
- The architecture must support both without duplicating core mapping/validation logic.

Approach:
- Keep one canonical domain model: `ParameterSet`.
- Add strategy interface used by SSD codec and authoring API:

```python
class ParameterSetStorage:
    def load(self, context) -> ParameterSet: ...
    def save(self, context, model: ParameterSet) -> None: ...
```

Implementations:
- `InlineParameterSetStorage`: read/write SSV XML subtree embedded in SSD.
- `ExternalParameterSetStorage`: read/write `.ssv` via `ResourceResolver` + `ArchiveSession`.

Benefits:
- Single model and semantic validator path for both representations.
- No duplicated SSV parsing/business logic.
- Enables safe conversion workflows:
  - inline -> external
  - external -> inline

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

### 5) Compatibility Facade Layer
Responsibility:
- Keep existing classes (`SSP`, `SSD`, `SSV`, `SSM`, `SSB`, `FMU`) stable.
- Route legacy operations through new archive/model/codec services.

Design choices:
- Deprecation warnings for legacy edge behavior, but no behavior breaks.
- Adapter classes map old methods/properties to new internals.


## Version Strategy
Introduce a central capability registry:
- `StandardVersion` enum: `SSP1`, `SSP2`, `FMI2`, `FMI3`.
- `CapabilityMatrix`: allowed tags/types/features by format and version.
- All codec and validation decisions use this registry instead of per-file ad hoc checks.

Benefits:
- Predictable feature gating.
- Faster implementation of new version features.
- Single source of truth for documentation and tests.

## API and UX Strategy (Authoring/Editing First)
- Keep current context-manager authoring flow.
- Add explicit high-level authoring operations:
  - `add_component(...)`
  - `add_connector(...)`
  - `connect(...)`
  - `bind_parameters(...)`
  - `add_resource(...)`
- Add deterministic persistence:
  - Keep current auto-save behavior for compatibility.
  - Introduce explicit `save()` and `save_as()` and encourage migration in docs.
- Add stable exceptions:
  - `SchemaValidationError`
  - `SemanticValidationError`
  - `ArchiveStateError`
  - `CompatibilityError`

## Backward Compatibility Plan (Strict)
- Maintain existing imports and class names.
- Preserve constructor signatures and default modes.
- Preserve context manager patterns and return types where practical.
- For known inconsistent legacy behaviors:
  - Keep behavior unless clearly erroneous.
  - For fixes that may alter edge behavior, add guarded compatibility mode toggles.
- Introduce `PYSSP_LEGACY_BEHAVIOR=1` environment flag if needed for specific transitions.

## Implementation Plan

### Phase 0: Stabilization (Immediate)
Scope:
- Fix correctness bugs that block trust and feature work.
- Ensure test suite green on current API.

Acceptance criteria:
- Existing tests pass.
- Add regression tests for known issues (variant handling, dirty tracking, semantic checks).

### Phase 1: Archive + Validation Foundations
Scope:
- Implement `archive` layer with deterministic dirty tracking.
- Extract schema validation utilities and structured diagnostics.
- Keep old classes backed by new archive internals.

Acceptance criteria:
- `SSP`/`FMU` legacy flows unchanged for callers.
- Read-only workflows never write archives.

### Phase 2: SSP2 Full Support (Near Term Priority)
Scope:
- Implement SSP2 codecs for SSD/SSV/SSM/SSB using capability matrix.
- Ensure support for SSP2 parameter type extensions and dimensions.
- Implement dual storage handling for SSD parameter sets (inline and external SSV) via `ParameterSetStorage` strategy.

Acceptance criteria:
- Round-trip tests for SSP2 samples pass.
- Schema and semantic validation pass for SSP2 fixtures.
- Inline/external SSV in SSD round-trip and conversion tests pass without model divergence.

### Phase 3: FMI2/FMI3 Full Support (Near Term Priority)
Scope:
- Add FMI2 model description codec and align FMI3 handling.
- Support variable/type/unit constructs consistently in model layer.

Acceptance criteria:
- FMI2/FMI3 fixtures parse and round-trip successfully.
- Unified querying for parameters/inputs/outputs across FMI versions.

### Phase 4: High-Level Authoring APIs
Scope:
- Implement composable authoring helpers built on domain models.
- Improve diagnostics and conflict detection for editing operations.

Acceptance criteria:
- Example workflows in docs can create valid SSP packages with minimal low-level XML handling.

### Phase 5: Consolidation and Deprecation Guidance
Scope:
- Add migration docs and best practices.
- Retain legacy surface; deprecate only redundant internals with long runway.

Acceptance criteria:
- Public API compatibility validated by dedicated compatibility tests.

## Testing Strategy
- Add three complementary suites:
  - Compatibility tests: legacy API behavior snapshots.
  - Round-trip tests: parse -> model -> serialize -> parse equivalence.
  - Capability tests: version-feature matrix coverage.
- Keep fixture corpora:
  - SSP1/SSP2 archives and XML files.
  - FMI2/FMI3 model descriptions.
- CI gates:
  - Schema compliance required.
  - Semantic warning budget tracked and reduced over time.

Additional representation-parity tests:
- SSD with inline SSV: parse/edit/save/round-trip.
- SSD with external SSV: parse/edit/save/round-trip.
- Conversion tests: inline -> external and external -> inline.
- Diagnostic parity tests for equivalent inline/external parameter content.

## Risks and Mitigations
- Risk: Compatibility regressions during adapter rollout.
  - Mitigation: lock behavior with compatibility tests before refactor.
- Risk: SSP2/FMI2 feature complexity causes slow delivery.
  - Mitigation: capability matrix and per-version codec boundaries.
- Risk: Partial migration creates duplicated logic.
  - Mitigation: hard rule that legacy classes must delegate to new internals once available.

## Module Layout Proposal
Suggested package organization:
- `pyssp_standard/archive/`
- `pyssp_standard/model/`
- `pyssp_standard/codec/ssp1/`
- `pyssp_standard/codec/ssp2/`
- `pyssp_standard/codec/fmi2/`
- `pyssp_standard/codec/fmi3/`
- `pyssp_standard/validation/`
- `pyssp_standard/legacy/`

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
