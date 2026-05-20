# IMP-002: Extract Reference Discovery from DocumentRuntime

**Status:** candidate  
**Priority:** high  
**Layer:** Orchestration

## Problem

`DocumentRuntime._iter_external_reference_targets` and related reference
discovery logic cannot be tested in isolation — they are instance methods
interleaved with archive/document lifecycle management.

Source: `common/document_runtime.py` line 99:
`# ---- TODO: break out the reference discovery to test separately ....`

## Proposed Solution

1. Extract reference discovery into a standalone function (e.g.,
   `discover_external_references(document, reference_specs)`) that takes
   an XML document and reference spec patterns and returns discovered
   targets.
2. Keep `DocumentRuntime` calling the extracted function.
3. Write dedicated unit tests for the extracted function.

## Verification

- New unit tests cover edge cases: no references, nested references,
  malformed paths, multiple reference types.
- `DocumentRuntime` behavior is unchanged — all existing orchestration tests pass.
- No changes to public API.