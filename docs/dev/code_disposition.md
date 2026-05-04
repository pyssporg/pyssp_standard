# Code Disposition

Use this page when you need to find the right code home quickly.

It is intended for both maintainers and coding agents.

## Read First

For almost any change, read in this order:

1. `AGENTS.md`
2. `docs/dev/repo_map.md`
3. `docs/dev/architecture.md`
4. `docs/dev/repo_status.md`
5. this page

## Layer Map

| Concern | Primary code home | Notes |
| --- | --- | --- |
| Archive and directory runtimes | `pyssp_standard/common/archive_runtime.py`, `pyssp_standard/common/directory_runtime.py`, `pyssp_standard/common/document_runtime.py` | Archive-aware persistence and external-document resolution live here. |
| Public facades | `pyssp_standard/ssp.py`, `pyssp_standard/ssd.py`, `pyssp_standard/ssm.py`, `pyssp_standard/ssv.py`, `pyssp_standard/fmu.py`, `pyssp_standard/md.py` | Keep these thin and user-facing. |
| Cross-standard composition | `pyssp_standard/standard/operations/model_description_to_ssd.py` | Helpers that translate between standard families belong here. |
| SSP1 codecs | `pyssp_standard/standard/ssp1/codec/` | XML parse and serialize logic for SSP1 documents. |
| SSP1 models | `pyssp_standard/standard/ssp1/model/` | Canonical in-memory document shapes. |
| SSP1 operations | `pyssp_standard/standard/ssp1/operations/` | Cross-object editing helpers and model composition logic. |
| Validation | `pyssp_standard/standard/ssp1/validation/`, `pyssp_standard/standard/fmi2/validation/` | Schema and semantic validation. |
| Shared XML helpers | `pyssp_standard/common/xml_document.py`, `pyssp_standard/standard/ssp1/codec/xml_utils.py` | Shared XML mechanics and namespace helpers. |
| Test fixtures | `pytest/` and `models/ssp/` | Reproduce architecture choices in executable form. |

## Where To Look

If you are changing:

- archive-aware `.ssp` workflows, start with `pyssp_standard/ssp.py` and `pyssp_standard/common/document_runtime.py`
- cross-standard model conversion, start with `pyssp_standard/standard/operations/model_description_to_ssd.py`
- standalone SSD document shape, start with `pyssp_standard/standard/ssp1/model/ssd_model.py` and `pyssp_standard/standard/ssp1/codec/ssd_codec.py`
- parameter bindings or mappings, start with `pyssp_standard/standard/ssp1/operations/ssd_parameter_bindings.py`
- SSP1-only system assembly, start with `pyssp_standard/standard/ssp1/operations/model_description_to_ssd.py`
- SSP1 parameter-packaging fixtures, start with `models/ssp/*/build.py`

## Agent Shortcut

For coding agents, the fastest useful path is usually:

1. `docs/dev/repo_map.md`
2. `docs/dev/code_disposition.md`
3. `docs/dev/architecture.md`
4. the relevant file under `pyssp_standard/`
5. one focused test under `pytest/`
