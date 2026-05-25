# IMD-001: set_generation_date_and_time placement and scope

- **Status:** Active
- **Date:** 2026-05-25
- **Context:** Adding a feature to set `generationDateAndTime` across all XML facades. The attribute exists in SSP1 document metadata (`Ssp1DocumentMetadata.generation_date_and_time`), FMI2 model description (`Fmi2ModelDescriptionDocument.generation_date_and_time`), and FMI3 model description (`Fmi3ModelDescriptionDocument.generation_date_and_time`). The implementation needs to cover 7 XML facades (SSD, SSV, SSB, SSM, SRMD, ModelDescription) and 2 archive facades (SSP, FMU) while excluding LS-REF facades (LSRefManifest, LSRefExperiments) that do not carry the attribute.
- **Decision:** Each facade implements `set_generation_date_and_time(dt=None)` directly — no base-class method. A shared utility `format_generation_datetime()` in `pyssp_standard/common/datetime_utils.py` handles datetime formatting (ISO 8601 with `T`/`Z`, default `2000-01-01T00:00:00Z`). XML facades assign to the model attribute directly (`self.xml.metadata.generation_date_and_time` for SSP1 documents, `self.xml.generation_date_and_time` for ModelDescription). Archive facades delegate via inner context (`SSP.system_structure()` → SSD, `FMU.model_description` → ModelDescription). String inputs pass through without validation.
- **Consequences:**
  - Consistent public API across all relevant facades.
  - No changes to the domain model layer (only facade methods).
  - Archive delegation automatically acquires/releases document context.
  - LS-REF facades are explicitly excluded — no method added.
  - Users must create/filter raw strings outside the library; no format validation inside.
  - Test burden covers 9 facades × 6 scenarios each ≈ 54 test cases.