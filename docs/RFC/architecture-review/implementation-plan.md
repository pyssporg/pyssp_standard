# Implementation Plan

This file is the working implementation tracker for the architecture rework.

Hard constraint:
- public API compatibility in `pyssp_standard` must be preserved

Working rule:
- internals may change freely as long as compatibility is preserved or explicitly adapted behind the public facade

Status legend:
- `[in_progress]`
- `[pending]`
- `[done]`

## Active Plan

1. `[done]` Establish the compatibility baseline.
   Scope:
   - freeze the public surface exported by `pyssp_standard`
   - map that surface to the current tests
   - add any missing compatibility tests around:
     - context-manager behavior
     - save semantics
     - version detection
     - core authoring flows

2. `[done]` Create the new internal package layout under `pyssp_standard/`.
   Scope:
   - add internal structure for:
     - archive
     - generated
     - codec
     - model
     - validation
     - orchestration
   - keep `pyssp_standard_v1` untouched as the legacy fallback during migration

3. `[done]` Standardize schema generation tooling.
   Scope:
   - add wrapper scripts for `xsdata` generation
   - keep generated outputs checked in
   - separate generated modules by standard family and version
   - ensure regeneration is deterministic

4. `[in_progress]` Introduce explicit standard-version routing.
   Scope:
   - detect `(format, family, version)` once per document
   - select the correct generated binding, codec, mapper, validator, and schema stack
   - avoid scattered version conditionals in public APIs and orchestration

5. `[pending]` Migrate `SSV` behind the existing public API.
   Scope:
   - keep `SSV` signatures and behavior stable
   - replace legacy XML internals with generated bindings plus mapper/codec orchestration

6. `[pending]` Migrate the first SSD slice behind existing public workflows.
   Scope:
   - cover the currently demonstrated subset:
     - document
     - system
     - component
     - parameter binding inline/external
   - keep external reference resolution in orchestration

7. `[pending]` Extract a shared archive/session layer.
   Scope:
   - route `SSP` and `FMU` through the new archive/session layer
   - preserve context-manager semantics and deterministic persistence behavior

8. `[pending]` Centralize validation.
   Scope:
   - separate schema compliance from semantic validation
   - make validation callable from both new internals and compatibility facades

9. `[pending]` Expand the generated/versioned path across remaining formats.
   Scope:
   - `SSM`
   - `SSB`
   - broader `SSD`/`SSV` coverage
   - FMI model descriptions

10. `[pending]` Retire legacy internals incrementally.
    Scope:
    - switch each public facade from `pyssp_standard_v1` to new internals only after compatibility tests pass
    - remove dead shims and outdated duplicated notes

## Progress Notes

### 2026-04-20
- Stored the implementation plan on disk.
- Architecture RFC updated to recommend the layered `xsdata` approach as the primary direction.
- Demo includes:
  - `xsdata` SSV generation wrapper
  - `xsdata`-backed SSV codec path
  - SSD `xsdata` codec/mapper skeleton
- Began step 1 compatibility work:
  - created a real `pyssp_standard` compatibility facade package
  - aliased legacy public submodules from `pyssp_standard_v1`
  - fixed local pytest collection to use the repo package instead of an installed site-package copy
  - redirected legacy schema paths to the checked-in standards in `3rdParty`
  - added fallback handling for missing SRMD schemas using the installed package resources
  - added an initial public API compatibility test
  - verified the current public compatibility suite:
    - `pytest/test_public_api_compat.py`
    - `pytest/test_common.py`
    - `pytest/test_fmu.py`
    - `pytest/test_srmd.py`
    - `pytest/test_ssb.py`
    - `pytest/test_ssd.py`
    - `pytest/test_ssm.py`
    - `pytest/test_ssp.py`
    - `pytest/test_ssv.py`
    - `pytest/test_units.py`
    - `pytest/test_utils.py`
  - result: `37 passed`
- Began step 2 internal layout work:
  - created the new internal package scaffold under `pyssp_standard/`
  - added placeholder packages for:
    - `archive`
    - `orchestration`
    - `validation`
    - `ssp1`, `ssp2`
    - `fmi2`, `fmi3`
  - documented the internal target layout in `pyssp_standard/README.md`
- Completed step 3 generation tooling (prioritized SSV targets):
  - added reusable generation utility:
    - `pyssp_standard/tools/xsdata_generation.py`
  - added CLI wrapper:
    - `scripts/generate_xsdata_bindings.py`
  - registered versioned targets:
    - `ssp1_ssv` -> `pyssp_standard/ssp1/generated/ssv_generated_types.py`
    - `ssp2_ssv` -> `pyssp_standard/ssp2/generated/ssv_generated_types.py`
  - generated and checked in both target modules
  - added tooling smoke test:
    - `pytest/test_xsdata_generation_tooling.py`
  - verified:
    - `pytest/test_xsdata_generation_tooling.py pytest/test_public_api_compat.py -q`
    - result: `4 passed`
