## Alternative Architecture: xsdata-Centric
`xsdata` is a schema-driven XML binding tool that can generate Python dataclasses and serializers/deserializers from XSD files.

### What an xsdata-centric architecture would look like
- Generate model classes from SSP/FMI XSDs.
- Use generated parsers/serializers as primary XML codec path.
- Wrap generated objects with authoring services and compatibility adapters.

### Fit with this project's priorities
- Strict backward compatibility:
  - Achievable, but requires a deliberate compatibility facade to preserve legacy API contracts and edge behaviors.
- Near-term SSP2 + FMI2/FMI3 support:
  - Strong fit for broad schema coverage and faster coverage expansion.
- Robust authoring/editing SDK:
  - Requires additional handwritten service layer; generated classes alone are not sufficient UX.

## Comparison: Layered Handwritten vs xsdata-Centric

### 1) Delivery speed for SSP2/FMI2/FMI3
- Layered handwritten codecs:
  - Slower initial implementation.
  - Higher precision control from day one.
- xsdata-centric:
  - Faster initial schema coverage.
  - Requires tuning for complex/optional schema branches.

### 2) Backward compatibility risk
- Layered handwritten codecs:
  - Lowest risk for preserving legacy behavior exactly.
- xsdata-centric:
  - Moderate risk unless all public behavior is mediated by compatibility adapters.

### 3) Long-term maintenance cost
- Layered handwritten codecs:
  - Higher ongoing maintenance burden as standards evolve.
- xsdata-centric:
  - Lower maintenance for schema drift; regenerate and adjust adapters.

### 4) Authoring/editing usability
- Layered handwritten model:
  - Can be designed around user workflows directly.
- xsdata-centric:
  - Generated models are typically schema-shaped and verbose.
  - Needs a higher-level authoring API layer either way.

### 5) Validation model
- Both approaches still need:
  - XSD validation.
  - Separate semantic validation (connections, references, consistency, archive safety).
- xsdata does not eliminate semantic validator implementation.

### 6) Failure modes
- Layered handwritten codecs:
  - Manual parser/serializer bugs.
- xsdata-centric:
  - Generator configuration drift, awkward generated type ergonomics, and namespace/schema edge-case handling.

## Decision Matrix
Scoring: 1 (weak) to 5 (strong), weighted to current project priorities.

| Criterion | Weight | Handwritten Layered | xsdata-Centric | Hybrid (Recommended) |
|---|---:|---:|---:|---:|
| Strict backward compatibility | 5 | 5 | 3 | 5 |
| SSP2/FMI2/FMI3 near-term delivery | 5 | 3 | 5 | 5 |
| Authoring/editing SDK ergonomics | 4 | 5 | 3 | 5 |
| Maintainability under schema evolution | 4 | 3 | 5 | 5 |
| Testability and isolation | 3 | 5 | 4 | 5 |
| **Weighted outcome** |  | **79** | **74** | **95** |

## Recommended Direction: Hybrid
Use the layered architecture as the system design, and adopt `xsdata` selectively inside the codec layer.

### Hybrid rules
- Keep public classes stable (`SSP`, `SSD`, `SSV`, `SSM`, `SSB`, `FMU`).
- Generated types are internal implementation details.
- Compatibility adapters own old behavior contracts.
- Authoring APIs are handwritten workflow-oriented services.
- Semantic validation remains handwritten and version-aware.

## Hybrid Adoption Plan

### Phase A: Feasibility Spike (1-2 weeks)
Scope:
- Generate SSP2 SSV bindings from XSD with `xsdata`.
- Parse/serialize existing `pytest/doc/ssv2_ex.ssv`.
- Compare output and compliance against current tests.

Exit criteria:
- Successful round-trip and schema validation for SSP2 SSV fixtures.
- Documented generator config and namespace handling approach.

### Phase B: First Production Integration
Scope:
- Integrate generated SSP2 SSV codec behind compatibility facade.
- Preserve existing `SSV` class behavior and signatures.
- Add regression tests for old API expectations plus SSP2 features.

Exit criteria:
- No compatibility regressions on legacy SSV tests.
- SSP2 SSV tests pass with new codec path.

### Phase C: Expand to SSD/SSM/SSB and FMI2/FMI3
Scope:
- Add generated bindings for SSP2 SSD/SSM/SSB.
- Add FMI2/3 generated bindings for model description.
- Reuse shared mapper patterns (generated <-> domain model).

Exit criteria:
- Feature-complete parse/serialize support for prioritized formats.
- Unified querying APIs over FMI2/FMI3 exposed through legacy facade.

### Phase D: Consolidate Tooling and CI
Scope:
- Pin `xsdata` version and generation configs in repo.
- Add CI check for reproducible generation diffs.
- Lock compatibility snapshots and round-trip corpora.

Exit criteria:
- Deterministic code generation.
- Stable compatibility and capability test suites.