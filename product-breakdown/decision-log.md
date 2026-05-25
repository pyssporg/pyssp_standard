# Decision Log

> **Purpose:** Global index of design decisions across all product-breakdown layers.
> Each entry links to the full decision record in the owning layer.
>
> **Maintenance:** When a decision file is added, renamed, superseded, or deprecated,
> update this index in the same change.

## Decisions

*No formal decision records have been written yet. All architecture and design choices
are currently implicit in the codebase. The following table catalogs known decisions
that should be formalized as separate decision files.*

| ID | Title | Layer | Status | Location | Related Artifacts |
|----|-------|-------|--------|----------|-------------------|
| PD-001 | Public facades hardcode codec/validator (implicit) | Product | Explicit | `03-implementation/interfaces.md` | `pyssp_standard/ssv.py`, `ssd.py`, `ssm.py`, `md.py`, `srmd.py`, `ssb.py` |
| AD-001 | Layered XML-document workflow architecture (implicit) | Architecture | Explicit | `02-architecture/component-view.md` | `02-architecture/layer-rules.md`, `02-architecture/component-view.md` |
| AD-002 | Version routing exists but facades bypass it (implicit) | Architecture | Active | `02-architecture/quality-attributes.md` | `standard/version_routing.py`, `06-evolution/improvement-backlog.md` (G4, G10) |
| AD-003 | Direct ElementTree codecs instead of generated bindings (implicit) | Implementation | Explicit | `03-implementation/interfaces.md` | `standard/ssp1/codec/`, `standard/fmi2/codec/` |
| AD-004 | Dataclass domain models as canonical in-memory representation (implicit) | Implementation | Explicit | `03-implementation/code-structure.md` | `standard/ssp1/model/`, `standard/fmi2/model/` |
| TD-001 | xml.etree.ElementTree for XML parsing (implicit) | Technology | Explicit | `03-implementation/interfaces.md` | All codec modules |
| VD-001 | Compliance check is explicit, not automatic (implicit) | Verification | Explicit | `04-verification/acceptance-criteria.md` | `common/xml_document.py` |
| PD-002 | Drop round-trip stability from IMP-012; defer codec fix to backlog | Product | Accepted | `06-evolution/decisions/DEC-IMP012-R1-001.md` | `pytest/fmi2/codec/test_model_description_xml_codec.py`, `06-evolution/improvement-backlog.md` |
| **IMD-001** | **set_generation_date_and_time placement and scope** | **Implementation** | **Active** | **`03-implementation/decisions/IMD-001-set-generation-date-time.md`** | **`pyssp_standard/common/datetime_utils.py`, `pyssp_standard/ssd.py`, `ssv.py`, `ssb.py`, `ssm.py`, `srmd.py`, `md.py`, `ssp.py`, `fmu.py`** |

## Open Decisions

The following topics need explicit decisions with formal records:

- Which parts of the public API are stable vs. experimental
- How missing XML files in `r` or `a` mode should be handled (error vs. implicit creation)
- Whether compliance validation should be required before persistence in all workflows
- How far annotation and extension preservation must go for unsupported content
- Which malformed external references should fail loudly vs. degrade to `None`
- Whether to expose a CLI (currently Python API only)
- How to handle partial SSP2/FMI3 support at the facade level (error vs. feature-gated vs. auto-detect)

## Related

- **Naming conventions:** `.opencode/templates/product-breakdown/naming.md`
- **Decision placement guidance:** `.opencode/templates/product-breakdown/decision-placement.md`