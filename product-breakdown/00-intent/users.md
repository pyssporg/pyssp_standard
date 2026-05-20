# Users

> **Layer:** 00-intent
> **Artifact type:** users.md

## Primary Users

| User | Description | Key Workflow |
|------|-------------|--------------|
| **SSP integrator** | Engineer composing FMU components into an SSP system structure | `SSP.system_structure()`, `SSP.add_fmu()` |
| **Parameter author** | Engineer creating or editing `.ssv` parameter sets and `.ssm` mappings | `SSV`, `SSM` facades |
| **CI pipeline** | Automated validation of SSP artifacts in build/test pipelines | `check_compliance()` on any facade |
| **FMU consumer** | Engineer inspecting FMU archive contents (binaries, model description) | `FMU` facade, `ModelDescription` |
| **Tool integrator** | Developer building higher-level tools on top of SSP/FMI | All public facades, `pyssp_standard/__init__.py` |

## User Workflows (from docs)

1. **Quick validation** — Open a `.ssv`, call `check_compliance()`, confirm valid.
2. **Archive inspection** — Open a `.ssp` or `.fmu`, list resources/binaries.
3. **Parameter editing** — Open an `SSV` in write mode, add/change parameters, save.
4. **System structure editing** — Open SSD via SSP, add components and connections.
5. **Cross-document editing** — Open SSP, resolve `SystemStructure.ssd` with external `.ssv`/`.ssm`.
6. **FMU-to-SSP packaging** — Call `FMU.package_as_ssp()` to create an SSP from an FMU.

## Evidence

- `docs/getting_started.md`: first-success workflows
- `docs/user/python_api.md`: 7 example workflows
- `pyssp_standard/ssp.py`: `add_fmu()`, `add_resource()`, `system_structure()`
- `pyssp_standard/ssv.py`: read/create/edit SSV
- `pyssp_standard/fmu.py`: `package_as_ssp()`, `model_description`, `binaries`