# Archive Design Spec

## Status
- Proposed
- Might be a case of premature optimization....

## Date
- February 19, 2026

## Archive Strategies

  1. Full unpack to temp dir (current style)

  - Pros: simplest mental model, easy random file edits, works with existing code.
  - Cons: slow for large archives, high disk usage, risky extractall path handling, hard to do atomic saves.
  - Fit: good baseline, but should be hardened (safe extraction + atomic write + better dirty tracking).

  2. In-memory indexed ZIP access (no full extract)

  - Pros: faster open, lower disk churn, good for read-heavy workflows.
  - Cons: complex for many writes/renames; ZIP format still requires rebuild on save.
  - Fit: good for inspection/query APIs, less ideal for authoring unless wrapped well.

  3. Hybrid overlay FS (recommended)

  - Approach: read from ZIP index lazily, write changes to temp overlay, rebuild archive once on save.
  - Pros: best balance for SDK editing: fast reads, controlled writes, explicit dirty set, predictable saves.
  - Cons: moderate implementation complexity.
  - Fit: strongest option for your “robust authoring/editing SDK” goal.


## Scope
This spec defines a concrete archive subsystem for `.ssp` and `.fmu` handling that supports:
- strict backward compatibility through facade adapters,
- robust authoring/editing workflows,
- deterministic persistence semantics,
- safe and atomic write behavior.

## Goals
- Avoid full eager extraction for read-heavy usage.
- Support ergonomic multi-file edits before a single save.
- Guarantee read operations do not mark state dirty.
- Guarantee writes are atomic at archive-file level.
- Provide clear, typed failures for callers.

## Non-Goals
- Cross-process file locking guarantees.
- Streaming write support for extremely large binaries (can be added later).

## Core Model

### Open Modes
- `r`: read-only, no writes allowed.
- `a`: read-write, create if missing.
- `w`: truncate/create new archive.

### Internal Storage Model
Hybrid overlay with three sources of truth during a session:
1. `base_index`: manifest of members from source archive.
2. `overlay_add_or_replace`: map of `rel_path -> staged content`.
3. `overlay_delete`: set of removed relative paths.

Resolution rule for reads:
1. If path in `overlay_delete`: missing.
2. If path in `overlay_add_or_replace`: return staged content.
3. Else read from source archive member.

No full extraction is required for default path.

## Public Interface

```python
class ArchiveSession:
    @classmethod
    def open(
        cls,
        source_path: Path | str,
        *,
        mode: str = "a",
        archive_kind: ArchiveKind | None = None,
        target_path: Path | str | None = None,
    ) -> "ArchiveSession": ...

    # context manager
    def __enter__(self) -> "ArchiveSession": ...
    def __exit__(self, exc_type, exc, tb) -> None: ...

    # metadata
    @property
    def mode(self) -> str: ...
    @property
    def source_path(self) -> Path: ...
    @property
    def target_path(self) -> Path: ...
    @property
    def dirty(self) -> bool: ...

    # listing and probing
    def list_files(self, prefix: str | None = None) -> list[str]: ...
    def exists(self, rel_path: str) -> bool: ...

    # reads
    def read_bytes(self, rel_path: str) -> bytes: ...
    def read_text(self, rel_path: str, encoding: str = "utf-8") -> str: ...

    # writes
    def write_bytes(self, rel_path: str, data: bytes, *, overwrite: bool = True) -> None: ...
    def write_text(self, rel_path: str, data: str, *, encoding: str = "utf-8", overwrite: bool = True) -> None: ...
    def remove(self, rel_path: str, *, missing_ok: bool = False) -> None: ...

    # transaction control
    def save(self) -> None: ...
    def save_as(self, target_path: Path | str) -> None: ...
    def discard(self) -> None: ...
```

## Path Rules and Safety
- All member paths are normalized POSIX relative paths.
- Reject absolute paths and `..` traversal at API boundary.
- On load, reject unsafe ZIP members that would escape archive root semantics.
- Canonicalize duplicate separators and leading `./`.

## Dirty Tracking Semantics
Dirty is `True` if and only if there is at least one staged mutation:
- write add/replace,
- remove existing member.

Dirty is not set by:
- reads,
- list/probe operations,
- no-op writes where resulting bytes are byte-identical (optional optimization).

After successful `save` / `save_as`:
- overlays clear,
- dirty becomes `False`,
- base index refreshes from written archive.

## Persistence Semantics

### save()
- Writes to `target_path` if set; otherwise `source_path`.
- Implementation must use atomic replace:
  1. build archive into sibling temp file,
  2. fsync temp file,
  3. atomic replace target.

### save_as(path)
- Same as `save` but to explicit path.
- Session remains open; `target_path` updates to new path.

### discard()
- Drops overlay mutations.
- Restores clean view from base index.

## Build Algorithm (Repack)
When saving:
1. Enumerate final member set = `(base_index - overlay_delete) U overlay_add_or_replace.keys()`.
2. Stream unchanged members from source archive.
3. Write staged members from overlay.
4. Preserve deterministic ordering (lexicographic) for reproducible builds.
5. Preserve compression method defaults (configurable later).

## Error Model

Failure guarantees:
- If `save` fails before replace, original target archive remains unchanged.
- On replace failure, temp output is retained for diagnostics and should surfaced in exception context.

## Concurrency and Threading
- Session object is not thread-safe by default.
- Parallel read sessions on same file are allowed.
- Concurrent write sessions to same target path are undefined; later improvement can add advisory lock.

## Test Plan
Required tests:
1. Read path normalization and traversal rejection.
2. `mode="r"` mutation failures.
3. Dirty tracking correctness for read vs write/remove/discard.
4. Save atomicity behavior (original archive preserved on induced failure).
5. Save-as behavior and path switching.
6. Overlay precedence resolution rules.
7. Deterministic archive member ordering.
8. Compatibility adapter parity (`SSP`/`FMU` smoke flows).
