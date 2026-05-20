# IMP-011: Add Option to Flatten Nested SSP Archives

## Status

Proposed

## Layer

Evolution

## Theme

Archive flattening utility

## Evidence

- Stray note in `06-evolution/candidates/flatten.md`
- SSP archives may contain nested zip artifacts that require recursive extraction

## Current Pain Or Risk

SSP archives may reference or contain nested SSP/FMU structures. Users who need to inspect or transform the full flat tree must manually recurse. No utility exists in the current codebase.

## Proposed Improvement

Add a `flatten()` method or `ssp.flatten()` workflow that recursively extracts nested archives and produces a flat directory with all resources at one level.

## Expected Benefit

Users can inspect or migrate nested SSP content without manual recursion.

## Risk And Blast Radius

- Low risk if implemented as a separate utility, not touching existing codec/model/validation paths
- Affects `ssp.py` (new method) or `common/archive.py` (new helper)
- Nested archive structure must be understood before implementation

## Suggested Priority

Low

## Task Contract Seed

Add `SSP.flatten(target_path: Path)` that recursively extracts nested `.ssp`/`.fmu` entries from an open SSP archive into a flat directory tree. Each nested archive gets a subdirectory named after its original resource path.

## Out Of Scope

- Automatic re-packaging of flattened content
- Deduplication of resources across nested archives

## Traceability

- Intent: INT-001 (Inspect and edit SSP artifacts)
- Product: CAP-001 (SSP archive read/write)
- Architecture: Archive Layer
- Implementation: `ssp.py` or `common/archive.py`
- Verification: New test in `pytest/ssp1/orchestration/`

## Notes

- Determine where nested archives come from (are they always `.ssp` inside `.ssp`, or could they be `.fmu` archives?)
- Need to decide: flatten to temp dir (like archive runtime) or to a persistent target