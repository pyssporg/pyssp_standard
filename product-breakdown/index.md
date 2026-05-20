# Product Breakdown: pyssp_standard

> **Purpose:** This directory organizes the product knowledge of `pyssp_standard`
> — what it is, what it does, how it is structured, and how it should evolve.
>
> It serves as a shared reference for development planning, feature prioritization,
> and architectural decision-making.

---

## Structure

```text
product-breakdown/
├── index.md                    ← You are here
├── decision-log.md             # Global decision index
├── traceability-map.md         # Cross-layer traceability
├── 00-intent/                  # Purpose, users, constraints, assumptions
│   ├── purpose.md
│   ├── users.md
│   └── constraints.md
├── 01-product/                 # Scope, capabilities, domain model
│   ├── scope.md
│   ├── capabilities.md
│   └── domain-model.md
├── 02-architecture/            # Quality attributes, context, components
│   ├── quality-attributes.md
│   ├── context-view.md
│   └── component-view.md
├── 03-implementation/          # Code structure, interfaces, configuration
│   ├── code-structure.md
│   └── interfaces.md
├── 04-verification/            # Test strategy, acceptance criteria, traceability
│   ├── test-strategy.md
│   ├── acceptance-criteria.md
│   └── traceability-matrix.md
├── 05-operation/               # Runbook, support model
│   ├── runbook.md
│   └── support-model.md
└── 06-evolution/               # Improvement backlog and candidates
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
        ├── IMP-010-fill-fmi3-skeleton.md
        ├── IMP-011-add-ssp-flatten.md
        └── IMP-012-strip-model-exchange.md
```

---

## Quick Reference: Document Types

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

\* = skeleton (not yet implemented)

---

## Layer Architecture

```text
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

---

## Traceability Chain

```text
00-intent (purpose, users, constraints)
  -> 01-product (scope, capabilities, domain model)
    -> 02-architecture (quality, context, components)
      -> 03-implementation (code structure, interfaces)
        -> 04-verification (tests, acceptance, traceability)
          -> 05-operation (runbook, support)
            -> 06-evolution (backlog, improvement candidates)
```

Each layer documents decisions that affect the layer below.
See `traceability-map.md` for concrete paths from intent to code.

---

## Key References

- **Improvement backlog:** `06-evolution/improvement-backlog.md`
- **Layer rules:** `02-architecture/layer-rules.md`
- **Current status:** `02-architecture/quality-attributes.md` (Layer Status)
- **Code map:** `03-implementation/code-structure.md`
- **Decision index:** `decision-log.md`
- **Traceability map:** `traceability-map.md`

---

*This product breakdown uses the standard layer structure:
00-intent → 01-product → 02-architecture → 03-implementation →
04-verification → 05-operation → 06-evolution.*

*Last updated: 2026-05-20*