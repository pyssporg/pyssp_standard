# Product Breakdown: pyssp_standard

> **Purpose:** This directory organizes the product knowledge of `pyssp_standard`
> — what it is, what it does, how it is structured, and how it should evolve.
>
> It serves as a shared reference for development planning, feature prioritization,
> and architectural decision-making.

---

## Structure

```
product-breakdown/
├── index.md                  ← You are here
├── 01-overview/              # Product vision, positioning, stakeholders
├── 02-features/              # Feature descriptions, usage scenarios
├── 03-architecture/          # Module/component structure, layer map
├── 04-roadmap/               # Release plans, milestones
├── 05-backlog/               # Active and deferred work items
└── 06-evolution/             # Improvement candidates and structural proposals
    ├── improvement-backlog.md
    └── candidates/
        ├── IMP-001-consolidate-document-runtime-subclasses.md
        ├── IMP-002-extract-reference-discovery.md
        ├── IMP-003-unify-external-reference-specs.md
        ├── IMP-004-route-facades-through-version-routing.md
        ├── IMP-005-implement-ssp2-ssv-stack.md
        ├── IMP-006-reconcile-generated-binding-metadata.md
        ├── IMP-007-document-runtime-test-coverage.md
        ├── IMP-008-remove-empty-layer-example-directory.md
        ├── IMP-009-add-srmd-ssb-to-quickstart.md
        └── IMP-010-fill-fmi3-skeleton.md
```

---

## Quick Reference: Product Structure

### Layer Architecture

```
┌─────────────────────────────────────────────┐
│              Public API Facades             │
│  SSP │ SSD │ SSV │ SSM │ FMU │ MD │ SRMD   │
│  SSB │ LSRefManifest │ LSRefExperiments     │
└────────────────┬────────────────────────────┘
                 │ depends on
┌────────────────▼────────────────────────────┐
│           Orchestration Layer               │
│  DocumentRuntime │ Archive-runtimes         │
└────────────────┬────────────────────────────┘
                 │ dispatches to
┌────────────────▼────────────────────────────┐
│           Standard-Specific Stacks          │
│  SSP1 │ SSP2* │ FMI2 │ FMI3* │ LS-REF     │
│  ┌─────────┐ ┌─────────┐ ┌──────────────┐ │
│  │ codec   │ │ model   │ │ validation   │ │
│  └─────────┘ └─────────┘ └──────────────┘ │
└────────────────┬────────────────────────────┘
                 │ backed by
┌────────────────▼────────────────────────────┐
│           Schema / Tooling                  │
│  XSD files │ schema_targets │ version_route │
└─────────────────────────────────────────────┘
```

\* = skeleton (not yet implemented)

### Document Types

| Type | Extension | Standards | Status |
|------|-----------|-----------|--------|
| SSP (System Structure Package) | `.ssp` | SSP1 | Active |
| SSD (System Structure Description) | `.ssd` | SSP1 | Active |
| SSV (Parameter Set) | `.ssv` | SSP1, SSP2* | Active (SSP1 only) |
| SSM (Parameter Mapping) | `.ssm` | SSP1 | Active |
| SSB (Signal Dictionary) | `.ssb` | SSP1 | Active |
| SRMD (Simulation Resource MetaData) | `.srmd` | SSP1 | Active |
| FMU (Functional Mock-up Unit) | `.fmu` | FMI2, FMI3* | Active (FMI2 only) |
| Model Description | `modelDescription.xml` | FMI2, FMI3* | Active (FMI2 only) |
| LS-REF Manifest | `manifest.xml` | LS-REF | Active |
| LS-REF Experiments | `experiments.xml` | LS-REF | Active |

---

## Key References

- **Product structure details:** `06-evolution/improvement-backlog.md`
- **Architecture decisions:** `docs/dev/architecture.md`
- **Current status:** `docs/dev/repo_status.md`
- **Code map:** `docs/dev/repo_map.md`
- **Improvement candidates:** `06-evolution/candidates/`

---

*This product breakdown was initialized from the Improvement Workflow analysis (2026-05-20).
The structure is intentionally partial — each subdirectory (`01-overview`, `02-features`, etc.)
will be populated as product-definition work is done.*