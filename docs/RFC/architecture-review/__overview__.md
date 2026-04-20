# Architecture RFC: PySSP Standard SDK Evolution

## Status
- Proposed

## Date
- February 19, 2026

## Authors
- Codex architecture review (based on repository analysis and maintainers' priorities)

## Decision Drivers

- Near-term feature priority is full SSP1/SSP2 plus FMI2/FMI3 support.
- The project should be a robust authoring/editing SDK, not only an inspection utility.
- Current codebase has correctness and consistency gaps that slow feature delivery.

## Problem Statement
The current architecture mixes archive I/O, XML parsing, mutable in-memory state, schema/version decisions, and semantic validation in the same classes. This creates:
- High degree of custom xml solutions in multiple abstraction layers
- High coupling between file formats and standard versions.
- Inconsistent behavior across modules for read/write and parsing fidelity.
- Challenging extension path for SSP2 and FMI2/FMI3.
- Elevated risk of regressions when adding features due to shared mutable patterns.

## Goals
- Preserve existing public API behavior while introducing a stronger internal architecture.
- Deliver full SSP1/2 and FMI2/FMI3 support.
- Improve authoring/editing ergonomics with deterministic save semantics.
- Improve maintainability through clearer layering and testable boundaries.

## Constraints and Assumptions
- Context-manager workflows (`with SSP(...) as ssp`) remain supported.
- Existing serialized outputs should remain schema-compliant and functionally equivalent.
- Migration should be incremental with compatibility adapters.

## Current State Summary
Observed architectural characteristics:
- `ZIPFile` and XML objects are tightly coupled to runtime mutation and write-on-exit behavior.
- Version handling is fragmented across classes (`identifier` and ad hoc checks).
- Parsing and serialization fidelity varies by format (SSV/SSB/SSM/SSD/SRMD/FMUs).
- Semantic validation is present but not centralized.
- Test coverage exists but currently allows regressions in priority areas.

## Supporting Specs
- `layered_arch.md`
- `xsd_alternative.md`
- `../archive_solution.md`
- `demo/README.md`

## Demo Alignment
Current RFC demo implementation (in `docs/RFC/architecture-review/demo/`) demonstrates:
- One mixed SSD example (`__data__/mixed_example.ssd`) containing one inlined parameter set and one external parameter set reference.
- XML-only codecs (`codec/ssd_codec.py`, `codec/ssv_hybrid_codec.py`)
- SSP-level reference resolution and persistence (`public_api.py`, `PublicSSP`)
- Public API modularization with `PublicSSD` for SSD document operations and `PublicSSV` for parameter-set edits and SSV persistence.
- `is_inlined` + `is_resolved` binding state in the SSD model
