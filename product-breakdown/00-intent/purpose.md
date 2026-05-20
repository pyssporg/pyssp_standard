# Purpose

> **Layer:** 00-intent
> **Question:** Why does this product exist?

## Product Purpose

`pyssp_standard` exists to provide a Python library for inspecting, creating,
and editing SSP-related artifacts (`.ssp` archives, `.ssd` system structure
descriptions, `.ssv` parameter sets, `.ssm` parameter mappings) and FMI-related
artifacts (`.fmu` archives, `modelDescription.xml`).

The library is aimed at pre-processing, inspection, and controlled edits — not
at being a full SSP authoring environment or simulation runtime. See `README.md`.

## Problem Statement

SSP (System Structure & Parameterization) and FMI (Functional Mock-up Interface)
are open standards for co-simulation and model exchange. Tooling for these
standards has been fragmented and hard to script. Users who need to:

- validate parameter sets before a simulation run
- inspect FMU archive contents programmatically
- compose an SSP from an FMU and parameter files
- automate pre-processing in CI pipelines

have lacked a focused, layered Python library that separates archive I/O from
XML parsing from domain logic.

## Goals

1. **Read and validate** SSP/FMI artifacts without proprietary tooling.
2. **Edit and create** artifacts with round-trip preservation (element order,
   annotations, extensions).
3. **Resolve cross-document references** in archive-aware workflows.
4. **Stay layered** — archive, codec, model, validation, orchestration, and
   public API each own one concern.

## Non-Goals (Current)

- Full SSP authoring environment (no GUI, no graphical system editor).
- FMU simulation or co-simulation runtime.
- SSP2 or FMI3 support (skeletons exist but are unimplemented).
- End-user CLI (Python API only).
- Performance benchmarks or large-scale processing.

## Evidence

- `README.md`: "a Python package for inspecting and editing SSP-related files"
- `02-architecture/layer-rules.md`: layered XML-document workflow
- `pyssp_standard/__init__.py`: 12 public symbols across 9 source modules
- `04-verification/acceptance-criteria.md`: behavioral requirements baseline