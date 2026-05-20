# IMP-003: Unify EXTERNAL_REFERENCE_SPECS

**Status:** candidate  
**Priority:** high  
**Layer:** Orchestration

## Problem

`EXTERNAL_REFERENCE_SPECS` is defined as a file-local constant in `ssd.py`
but is needed by both SSP and LS-REF document resolution in
`common/document_runtime.py`. This forces an import dependency from the
shared orchestration layer into a specific document facade.

Source: `todo.md` — "EXTERNAL_REFERENCE_SPECS could be global and reused in
ssp and in ls-ref"

## Proposed Solution

1. Move `EXTERNAL_REFERENCE_SPECS` to `common/` (e.g.,
   `common/reference_specs.py`).
2. Update all importers (`ssd.py`, `document_runtime.py`, `ls_ref.py`) to
   import from the shared location.
3. Remove the file-local duplicate in `ssd.py`.

## Verification

- All existing tests pass.
- `from pyssp_standard.common.reference_specs import EXTERNAL_REFERENCE_SPECS`
   works and returns the same structure.
- No duplicates of the specs constant remain.