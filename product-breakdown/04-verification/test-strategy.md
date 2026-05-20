# Test Strategy

> **Layer:** 04-verification
> **Artifact type:** test-strategy.md

## Test Pyramid

```text
              ╱╲
             ╱  ╲  Few: Integration / archive-aware / orchestration tests
            ╱    ╲  (pytest/ssp1/orchestration/, pytest/fmi2/archive/)
           ╱______╲
          ╱        ╲
         ╱          ╲  Some: Facade / public API tests
        ╱            ╲  (pytest/ssp1/facade/, pytest/fmi2/facade/)
       ╱              ╲
      ╱________________╲
     ╱                  ╲
    ╱                    ╲  Many: Codec / XML round-trip tests
   ╱                      ╲  (pytest/ssp1/codec/, pytest/fmi2/codec/, pytest/ls_ref/codec/)
  ╱________________________╲
```

## Test Distribution by Layer

| Test Category | Location | Count (approx) | Covers |
|---------------|----------|----------------|--------|
| SSP1 codec (round-trip) | `pytest/ssp1/codec/` | 5 test files | SSV, SSM, SSD, SSB, SRMD XML parse/serialize |
| SSP1 facade | `pytest/ssp1/facade/` | 5 test files | SSV, SSM, SSD, SSB, SRMD public API |
| SSP1 orchestration | `pytest/ssp1/orchestration/` | 3 test files | Archive-aware SSP, add_fmu, archive tools |
| FMI2 codec | `pytest/fmi2/codec/` | 1 test file | ModelDescription XML round-trip |
| FMI2 facade | `pytest/fmi2/facade/` | 1 test file | ModelDescription public API |
| FMI2 archive | `pytest/fmi2/archive/` | 1 test file | FMU archive workflows |
| LS-REF codec | `pytest/ls_ref/codec/` | 1 test file | Manifest + experiments XML |
| LS-REF facade | `pytest/ls_ref/facade/` | 1 test file | LS-REF public API |
| Tools | `pytest/tools/` | 3 test files | Schema targets, validation, version routing |

## Test Patterns

1. **Codec tests**: Parse fixture XML → inspect model → serialize → verify round-trip
2. **Facade tests**: Use context managers → edit model → verify compliance → verify save
3. **Archive tests**: Create SSP/FMU from fixture dirs → verify resource listing → verify persistence
4. **Orchestration tests**: Open SSP → resolve external refs → edit → save → verify

## Test Fixtures

- Shared fixtures in `pytest/conftest.py`: embrace_ssd_fixture, embrace_ssm_fixture,
  embrace_ssp_dir_fixture, embrace_ssp_fixture, embrace_ssp_archive_fixture,
  mixed_ssd_fixture, external_ssv_fixture, ssv2_fixture,
  model_description_fixture, fmu_directory_fixture, fmu_archive_fixture
- Fixture source data: `pytest/__fixture__/embrace/`

## Known Test Gaps

| Gap | Description | Backlog Reference |
|-----|-------------|-------------------|
| No dedicated DocumentRuntime tests | `_iter_external_reference_targets` untestable | `06-evolution/improvement-backlog.md` (G7, G18) |
| No cross-standard integration tests | FMI→SSP composition not integration-tested | G6 |
| No SSP2/FMI3 tests | Skeletons have no tests | G17 |
| No benchmark/performance tests | Performance regression risk | G19 |
| LS-REF arcana tests missing | See `pytest/ls_ref/facade/` for coverage gaps | Implicit |

## Evidence

- `pytest/conftest.py`: fixture definitions
- Directory listings of all `pytest/` subdirectories
- `06-evolution/improvement-backlog.md`: gap summary (G6, G7, G17, G18, G19)