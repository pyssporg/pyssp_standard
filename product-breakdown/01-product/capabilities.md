# Capabilities

> **Layer:** 01-product
> **Artifact type:** capabilities.md

## Active Capabilities

| ID | Capability | Description | Primary Module(s) |
|----|-----------|-------------|-------------------|
| CAP-001 | SSP archive read/write | Open `.ssp` archives and directories in r/a/w modes, list/add/remove resources | `ssp.py`, `common/archive.py`, `common/archive_runtime.py` |
| CAP-002 | Parameter set (SSV) | Read, create, edit, validate `.ssv` parameter sets with round-trip preservation | `ssv.py`, `standard/ssp1/codec/ssv_codec.py`, `standard/ssp1/model/ssv_model.py` |
| CAP-003 | Parameter mapping (SSM) | Read, create, edit, validate `.ssm` parameter mappings | `ssm.py`, `standard/ssp1/codec/ssm_codec.py`, `standard/ssp1/model/ssm_model.py` |
| CAP-004 | System structure (SSD) | Read, create, edit, validate `SystemStructure.ssd` including components, connectors, connections | `ssd.py`, `standard/ssp1/codec/ssd_codec.py`, `standard/ssp1/model/ssd_model.py` |
| CAP-005 | FMU archive access | Open `.fmu` archives, list binaries/documentation, access modelDescription.xml | `fmu.py`, `md.py` |
| CAP-006 | Model description (FMI2) | Read/create/edit/validate FMI2 `modelDescription.xml` | `md.py`, `standard/fmi2/codec/`, `standard/fmi2/model/` |
| CAP-007 | Compliance validation | Explicit schema + semantic validation per document type | All `standard/*/validation/` modules, `common/xml_schema_validation.py` |
| CAP-008 | Cross-document reference resolution | In archive-aware SSP sessions, resolve external `.ssv`/`.ssm` references, persist back on save | `common/document_runtime.py`, `ssd.py` (EXTERNAL_REFERENCE_SPECS) |
| CAP-009 | FMU-to-SSP packaging | Convert an FMU archive into an SSP package with system structure | `fmu.py` (`package_as_ssp()`), `ssp.py` (`add_fmu()`) |
| CAP-010 | Signal dictionary (SSB) | Read, create, edit, validate `.ssb` signal dictionaries | `ssb.py`, `standard/ssp1/codec/ssb_codec.py` |
| CAP-011 | Simulation resource metadata (SRMD) | Read, create, edit, validate `.srmd` resource metadata | `srmd.py`, `standard/ssp1/codec/srmd_codec.py` |
| CAP-012 | LS-REF manifest/experiments | Read/create/edit/validate LS-REF manifest and experiments documents | `ls_ref.py`, `standard/ls_ref/codec/` |
| CAP-013 | Archive-aware parameter binding | Add external parameter sets + mappings to SSP system structures | `ssp.py` (`add_external_parameterset()`) |

## Future Capabilities (registered but not implemented)

| ID | Capability | Standard | Status in backlog |
|----|-----------|----------|-------------------|
| CAP-014 | SSP2 parameter set | SSP2 | Skeleton exists, empty codec/model/validation (`06-evolution/improvement-backlog.md` G1) |
| CAP-015 | FMI3 model description | FMI3 | Skeleton exists, empty codec/model/validation (G2) |

## Evidence

- `pyssp_standard/__init__.py`: full public API surface
- All facade modules under `pyssp_standard/`: thin wrappers over shared behavior
- `02-architecture/quality-attributes.md`: active vs. skeleton status