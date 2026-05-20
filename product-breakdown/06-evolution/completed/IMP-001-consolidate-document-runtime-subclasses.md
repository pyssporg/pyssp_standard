# IMP-001: Consolidate DocumentRuntime Subclasses

**Status:** candidate  
**Priority:** high  
**Layer:** Orchestration

## Problem

`SsdRuntime` (in `ssd.py`) and `LSRefExperimentsRuntime` (in `ls_ref.py`) both subclass
`DocumentRuntime` (in `common/document_runtime.py`) with nearly identical
context-manager patterns. These thin wrappers add maintenance surface without
providing distinct behavior.

Source references:
- `ssd.py` line 105: `# ----TODO: All Specialized runtime should be inlined....`
- `todo.md`: "these should not be needed"

## Proposed Solution

1. Add a generic `DocumentRuntime` usage pattern that accepts document type
   configuration at construction time instead of via subclassing.
2. Remove `SsdRuntime` and `LSRefExperimentsRuntime` subclasses.
3. Update callers in `ssd.py` and `ls_ref.py` to use the generic runtime directly.

## Verification

- All existing tests in `pytest/ssp1/orchestration/` and `pytest/ls_ref/facade/` pass.
- No public API changes — existing `SSD` and `LSRefExperiments` class signatures
  remain stable.
- `SsdRuntime` and `LSRefExperimentsRuntime` are no longer importable symbols
  (check: remove from any `__init__.py` exports).