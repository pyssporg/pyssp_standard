# IMP-006: Reconcile Generated-Binding Metadata

**Status:** candidate  
**Priority:** medium  
**Layer:** Versioning / Tools

## Problem

`version_routing.py` and `tools/schema_targets.py` reference metadata fields
that point to non-existent `generated/` packages — `generated_module`,
`generated_output_path`, `root_type`, `codec_id`, `mapper_id`. These fields
suggest generated data-binding code was planned but never created (or was
removed).

This is dead metadata — it could cause `ImportError` at runtime if code
tries to use the generated paths.

## Proposed Solution

Remove the dead metadata fields from the data
structures. Keep only the fields that are actually used (standard name,
version, document types).


## Verification

- `version_routing.py` no longer references `generated_module`,
  `generated_output_path`, `root_type`, `codec_id`, `mapper_id`.
- All tests in `pytest/tools/` pass.
- No imports fail due to missing `generated` packages.