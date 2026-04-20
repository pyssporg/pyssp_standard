# Implementation Plan

This file is the working implementation tracker for the architecture rework.

Hard constraint:
- architectural layering takes precedence over legacy internal structure
- user-facing API changes are allowed when they are motivated by the layered design and kept deliberate

Working rule:
- internals may change freely
- public API compatibility should be preserved when cheap, but legacy compatibility shims should not be kept if they undermine the target architecture
- the model layer should be the only in-memory model of parsed document data; facades, sessions, and orchestration objects must not introduce parallel representation-specific state

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

4. `[done]` Introduce explicit standard-version routing.
   Scope:
   - detect `(format, family, version)` once per document
   - select the correct generated binding, codec, mapper, validator, and schema stack
   - avoid scattered version conditionals in public APIs and orchestration
   - note: initial implementation focus remains `SSV` for `SSP1`; broader routing support can stay skeletal until the first layered slice is complete

5. `[in_progress]` Build the first layered implementation as an `SSP1` `SSV` vertical slice behind the existing public API.
   Scope:
   - restrict the implementation target to `SSV` for `SSP1`
   - prioritize establishing the layer boundaries end to end:
     - generated bindings
     - codec
     - mapper
     - canonical domain model
     - file/session handling
     - thin public facade
   - replace legacy XML internals with generated bindings plus mapper/codec orchestration
   - remove direct XML parsing/serialization responsibilities from `pyssp_standard/ssv.py`
   - stop depending on legacy `pyssp_standard_v1` XML/unit helpers from the new `SSV` path
   - make the model layer the only in-memory representation of parsed `SSV` data
   - move SSV units and top-level metadata into canonical SSV domain models plus mapper/codec support
   - put authoring/editing methods such as `add_parameter(...)` and `add_unit(...)` on `SsvParameterSet`
   - separate file/persistence behavior into a dedicated reader/writer/session object
   - keep `pyssp_standard/ssv.py` as a thin wrapper around the model plus the file/session object

6. `[pending]` Finish the `SSP1` `SSV` corrective refactor before expanding scope.
   Scope:
   - finish removing remaining compatibility-shaped access patterns from the `SSV` wrapper
   - add canonical SSV model coverage for:
     - parameter set metadata
     - unit definitions
     - SSP1 schema-shaped representational details hidden behind the mapper
   - isolate any required XML namespace normalization inside codec code
   - add tests that fail if:
     - authoring logic drifts out of `SsvParameterSet`
     - file/persistence logic drifts out of the session object
     - the public `SSV` wrapper regresses into owning raw XML or business logic
   - treat `SSP2` `SSV` support as follow-on work after the `SSP1` slice is architecture-compliant

7. `[in_progress]` Migrate the first SSD slice behind existing public workflows.
   Scope:
   - cover the currently demonstrated subset:
     - document
     - system
     - component
     - parameter binding inline/external
   - keep external reference resolution in orchestration

8. `[pending]` Extract a shared archive/session layer.
   Scope:
   - route `SSP` and `FMU` through the new archive/session layer
   - preserve context-manager semantics and deterministic persistence behavior

9. `[pending]` Centralize validation.
   Scope:
   - separate schema compliance from semantic validation
   - make validation callable from both new internals and compatibility facades

10. `[pending]` Expand the generated/versioned path across remaining formats after the `SSP1` `SSV` slice is solid.
   Scope:
   - `SSP2` `SSV`
   - `SSM`
   - `SSB`
   - broader `SSD` coverage
   - FMI model descriptions

11. `[pending]` Retire legacy internals incrementally.
    Scope:
    - switch each public facade from `pyssp_standard_v1` to new internals only after compatibility tests pass
    - remove dead shims and outdated duplicated notes

## Progress Notes

### 2026-04-20
- Refined the target `SSV` design:
  - the model layer is the only in-memory model of parsed data
  - authoring methods such as `add_parameter(...)` and `add_unit(...)` operate directly on `SsvParameterSet`
  - file handling lives in a separate reader/writer/session object
  - `SSV` is only a thin wrapper around the model plus the file/session object
- Updated the plan to prefer this design over compatibility-shaped wrapper state, even if that means motivated API adjustments.
- Advanced step 5 on the `SSP1` `SSV` slice:
  - expanded the canonical `SSV` model to include:
    - document metadata
    - unit definitions
  - added an explicit `SSP1` `SSV` xsdata mapper:
    - generated bindings `<->` canonical domain model
  - simplified the `SSP1` xsdata codec so it now owns parser/serializer setup and delegates schema-shape conversion to the mapper
  - rewrote `pyssp_standard/ssv.py` so file/persistence behavior and authoring behavior are no longer mixed in one implementation
  - added a focused round-trip test for metadata/unit preservation through the new SSV path
- Narrowed the near-term implementation scope:
  - the next concrete architecture milestone is a clean `SSP1` `SSV` vertical slice
  - broader `SSV` version coverage is deferred until that slice has the intended layering
- Implementation emphasis adjusted:
  - build up the layered architecture first
  - use `SSP1` `SSV` as the constrained proving ground for generated bindings, codec, mapper, domain model, and facade boundaries
- Re-opened the SSV migration step after reviewing `pyssp_standard/ssv.py` against `layered_arch.md`.
- Current divergence recorded:
  - `pyssp_standard/ssv.py` still parses and constructs XML directly with `lxml`
  - the new SSV path still depends on legacy `pyssp_standard_v1` abstractions (`ModelicaXMLFile`, `Units`, `Unit`, `BaseUnit`)
  - units are not yet represented in the canonical SSV domain model / mapper path
  - metadata/root patch-up responsibilities are still mixed into the public facade instead of being clearly assigned to lower layers
- Added an explicit corrective SSV refactor step ahead of broader format expansion so the layering pattern is fixed before it is copied into SSD/other formats.
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
- Completed step 4 version routing (SSV scope):
  - added explicit version routing module:
    - `pyssp_standard/orchestration/version_routing.py`
  - introduced:
    - `StandardVersion`
    - `ParseStackSpec`
    - SSV stack registry for SSP1/SSP2
    - XML/file version detection and stack resolution helpers
  - added tests:
    - `pytest/test_version_routing.py`
  - verified:
    - `pytest/test_version_routing.py pytest/test_public_api_compat.py -q`
    - result: `7 passed`
- Step 5 SSV migration is partially complete but not yet architecture-compliant:
  - added internal canonical SSV model:
    - `pyssp_standard/ssp1/model/ssv_model.py`
  - added version-specific xsdata codecs:
    - `pyssp_standard/ssp1/codec/ssv_xsdata_codec.py`
    - `pyssp_standard/ssp2/codec/ssv_xsdata_codec.py`
  - added new public `SSV` implementation using:
    - version detection/routing from step 4
    - generated bindings + mapper/codec orchestration
    - compatibility-preserving API shape (`identifier`, `parameters`, `units`, `add_parameter`, `add_unit`)
    - file path: `pyssp_standard/ssv.py`
  - switched facade export so `pyssp_standard.ssv` now uses the new implementation:
    - `pyssp_standard/__init__.py`
  - verified:
    - `pytest/test_ssv.py pytest/test_public_api_compat.py -q`
    - full compatibility suite (`pytest/test_public_api_compat.py ... pytest/test_utils.py -q`)
    - result: `37 passed`
  - remaining gap:
    - facade still owns raw XML/unit handling that should move into model/codec/mapper layers before this step can be marked done
