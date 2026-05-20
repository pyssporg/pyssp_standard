# Traceability Map

> **Purpose:** Broad cross-layer traceability for `pyssp_standard`.
> Connects intent → product capability → use case → requirement → architecture → implementation → verification.

## Traceability Chain

```text
Intent
  -> Product capability
    -> Use case
      -> Requirement
        -> Decision
          -> Architecture artifact
            -> Implementation artifact
              -> Test or verification artifact
```

## Known Traceability Paths

*This map captures the current implicit traceability. Formal IDs are assigned where
patterns are clear; gaps are marked explicitly.*

### SSP Document Lifecycle

```text
INT-001 Inspect and edit SSP artifacts
  -> CAP-001 SSP archive read/write
    -> UC-001 Open SSP archive, inspect resources
-> REQ-001 Read SSP archives in r/a/w modes
      -> REQ-002 Read-modify-write preserves parameter order
      -> REQ-003 External .ssv/.ssm resolved when files exist
        -> AD-002 DocumentRuntime owns cross-file resolution
          -> impl: pyssp_standard/common/document_runtime.py
            -> TEST: pytest/ssp1/orchestration/test_ssp.py (indirect)
```

### FMU Access

```text
INT-001 Inspect and edit SSP artifacts
  -> CAP-004 FMU archive read + package as SSP
    -> UC-004 Open .fmu, inspect binaries and model description
      -> REQ-004 FMU exposes binaries, documentation, modelDescription.xml
        -> AD-001 Archive layer abstraction
          -> impl: pyssp_standard/fmu.py
            -> TEST: pytest/fmi2/archive/test_fmu.py
```

### Validation

```text
INT-003 Ensure SSP artifacts are valid
  -> CAP-005 Compliance checking per document type
    -> UC-005 Validate SSV, SSM, SSD, modelDescription.xml
      -> REQ-005 Compliance check is explicit, not automatic
        -> VD-001 Explicit check_compliance() method
          -> impl: common/xml_document.py -> check_compliance()
            -> TEST: pytest/ssp1/facade/test_ssv.py, etc.
```

## Traceability Gaps

| Gap | Description | Layer Source |
|-----|-------------|--------------|
| TG-1 | No explicit requirement-to-test mapping | 04-verification |
| TG-2 | LS-REF experiments/manifest no traceable requirements | 00-intent / 01-product |
| TG-3 | SRMD and SSB capabilities have no documented use cases | 01-product |
| TG-4 | SSP2 and FMI3 skeletons traced but not implemented | 06-evolution (G1, G2) |
| TG-5 | No performance or scalability requirements documented | 00-intent (constraints) |

## Related

- **Full traceability matrix:** `04-verification/traceability-matrix.md` (proposed)
- **Improvement backlog gaps:** `06-evolution/improvement-backlog.md` (G1–G19)