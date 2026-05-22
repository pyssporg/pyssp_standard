# IMP-018: Allow `SSP.add_fmu()` to accept both `.fmu` file and a directory

> **Status:** Proposed
> **Priority:** Low
> **Layer:** Public API

## Theme

Extend `SSP.add_fmu()` so that when given a *directory* path (instead of a single
`.fmu` file), it bulk-imports all `.fmu` files found in that directory into the
SSP system structure, with sensible defaults for component naming and connector
exposure.

## Evidence

- **Current signature** (`pyssp_standard/ssp.py`, lines 137–178):
  ```python
  def add_fmu(
      self,
      component_name: str,
      fmu_path: str | Path,
      *,
      resource_name: str | None = None,
      implementation: str | None = "ModelExchange",
      component_type: str | None = "application/x-fmu-sharedlibrary",
      expose_system_connectors: bool = False,
      connector_prefix: str | None = None,
  ) -> str:
  ```
  The second parameter is named `fmu_path` and is typed `str | Path`, implying
  a single file. The implementation uses `Path(fmu_path)` directly and passes it
  to `self.add_resource()` and `FMU(fmu_path)` — both of which currently fail or
  behave unexpectedly if `fmu_path` points to a directory with multiple `.fmu`
  files.

- **Current caller pattern** (`pyssp_standard/fmu.py`, lines 55–61):
  ```python
  ssp.add_fmu(
      component_name=component_name,
      fmu_path=self.path,
      resource_name=resource_name,
      ...
  )
  ```
  Every call site passes exactly one FMU file.

- **Existing directory-glob pattern** (`pyssp_standard/common/archive.py`,
  line 75):
  ```python
  for fmu_archive in sorted(output_dir.rglob("*.fmu")):
  ```
  The codebase already uses `rglob("*.fmu")` for directory traversal — the
  concept is not new.

- **Existing tests** (`pytest/ssp1/orchestration/test_ssp_add_fmu.py`, 4 tests):
  All pass a single `.fmu` archive path. No test covers a directory input.

- **Component naming**: Currently `component_name` is a required positional
  parameter. For a bulk-import from a directory, the component name would need
  to be derived from each FMU filename (e.g., `"ECS_HW"` from
  `"0001_ECS_HW.fmu"` by taking the stem), or the user must provide a callable /
  mapping.

- **`add_resource()` behavior** (`ssp.py`, lines 59–63): Calls
  `self.runtime.add_file(source_path, target_name=...)`. A directory source
  would not produce a single file to add — this path would need to loop.

## Current Pain Or Risk

1. **No bulk import workflow**: Users who need to compose an SSP from multiple
   FMU files must call `add_fmu()` in a loop, writing a boilerplate `for` loop
   with `Path(dir).glob("*.fmu")` and manually picking component names.
2. **Inconsistent interface**: `add_resource()` accepts both files and
   directories (the archive runtime's `add_file` does not — but the public layer
   could), so `add_fmu` being file-only is a usability gap.
3. **Discovery friction**: New users familiar with the SSP workflow may expect
   the library to accept a directory and "just work" by importing everything.
4. **Wasted codebase knowledge**: The `archive.py` module already has the
   `rglob("*.fmu")` pattern; the API does not expose it to users.

## Proposed Improvement

Introduce an overload or dispatch in `SSP.add_fmu()` that detects whether
`fmu_path` is a file or a directory:

### Option A — Single return type extension (recommended)

1. **Detect directory vs file** at the top of `add_fmu()`:
   ```python
   fmu_path = Path(fmu_path)
   if fmu_path.is_dir():
       return self._add_fmu_directory(component_name, fmu_path, ...)
   # existing single-file path
   ```

2. **Internal `_add_fmu_directory()` method** that:
   - Lists all `.fmu` files in the directory (non-recursive, sorted).
   - Loops over each file, calling the single-file `add_fmu` logic.
   - Derives `component_name_i` for each file from `file_path.stem` (the
     filename without extension).
   - Accepts an optional `component_names: list[str] | None` parameter to
     override auto-naming.
   - Returns a `list[str]` of added resource names instead of a single `str`.

3. **Return type change**: The return would differ between the two paths — a
   single `str` for file, a `list[str]` for directory. This asymmetry is the
   main design tension.

### Option B — Separate method

Add a dedicated `add_fmu_directory()` method that accepts a directory path and
returns a `list[str]`. The existing `add_fmu()` remains unchanged. This avoids
the return-type asymmetry but adds another public method.

### Option C — Keyword dispatch with explicit parameter

Add a `bulk: bool = False` parameter. When `bulk=True`, `component_name` is
ignored (or re-purposed as a prefix), and `fmu_path` is treated as a directory.
Cleaner but less discoverable.

## Recommended Choice

**Option B** (separate method) is preferred because:

- It keeps the existing API stable and backward-compatible.
- No return-type polymorphism — callers always know what they get.
- The bulk-import logic can be independently tested and documented.
- The existing `add_fmu()` signature stays clean.

## Expected Benefit

- Users can populate an SSP with all FMU files from a directory in a single
  call: `ssp.add_fmu_directory("path/to/fmus/")`.
- Component names are automatically derived from `.fmu` filenames, eliminating
  boilerplate.
- The existing `add_fmu()` API is untouched, so no regression risk.
- Patterns already present in `archive.py` (`rglob("*.fmu")`) are surfaced as
  first-class API.

## Risk And Blast Radius

| Risk | Severity | Mitigation |
|------|----------|------------|
| Return type inconsistency (Option A) | Medium | Chosen Option B avoids this entirely |
| Directory with zero `.fmu` files | Low | Raise `FileNotFoundError` with a descriptive message |
| Deeply nested subdirectories | Low | Use `glob("*.fmu")` (non-recursive) by default; add `recursive: bool = False` option |
| Naming collision when auto-deriving from stem | Low | Raise `ValueError` if two files have the same stem within the same directory |
| `add_resource()` not suitable for directories | Low | The bulk method would loop over files internally, calling the single-file add path |
| `package_as_ssp()` in `fmu.py` only handles one FMU | Low | Out of scope — that method wraps a single FMU; users can call `add_fmu_directory()` directly on an `SSP` instance |

## Suggested Priority

**Low** — This is a convenience improvement, not a correctness or data-loss
prevention fix. Users can already bulk-import with a `for` loop. The API gap
does not block any required workflow.

## Task Contract Seed

### Phase 1 — `add_fmu_directory()` method on `SSP`

1. Add method to `SSP` class:
   ```python
   def add_fmu_directory(
       self,
       directory: str | Path,
       *,
       recursive: bool = False,
       implementation: str | None = "ModelExchange",
       component_type: str | None = "application/x-fmu-sharedlibrary",
       expose_system_connectors: bool = False,
       connector_prefix: str | None = None,
   ) -> list[str]:
   ```
2. Implementation:
   - Resolve `directory` to `Path(directory)`, verify it exists and is a directory.
   - Gather `.fmu` files: use `rglob("*.fmu")` if `recursive=True`, else `glob("*.fmu")`.
   - Sort files alphabetically for deterministic order.
   - Raise `FileNotFoundError` if no `.fmu` files found.
   - For each `.fmu` file, derive `component_name = file_path.stem`.
   - Call the existing single-file logic for each FMU.
   - Accumulate resource names into a `list[str]` and return it.

3. Detect and warn/error on duplicate stems (e.g., `ECS.fmu` and `ECS.fmu` in
   different subdirectories when `recursive=True`).

### Phase 2 — Tests

4. Add tests to `pytest/ssp1/orchestration/test_ssp_add_fmu.py`:
   - `test_add_fmu_directory_imports_all_fmu_files`: place 2+ FMU files in
     `tmp_path` subdirectory, call `add_fmu_directory()`, verify all appear
     in `ssp.resources` and `ssd.xml.system.elements`.
   - `test_add_fmu_directory_empty_directory_raises`: empty directory → error.
   - `test_add_fmu_directory_non_recursive_ignores_subdirs`: nested FMU files
     are not imported unless `recursive=True`.
   - `test_add_fmu_directory_recursive_flag`: `recursive=True` imports all
     levels.
   - `test_add_fmu_directory_component_name_derived_from_stem`: component name
     matches the `.fmu` file stem.

## Out Of Scope

- Modifying the return type of the existing `add_fmu()` method (Option A).
- Adding `component_names: list[str]` parameter to `add_fmu_directory()` — that
  would require the user to know the file list in advance.
- Adding a `directory` overload to `fmu.FMU.__init__()` — the `FMU` class is
  designed for a single FMU archive.
- Changing `add_resource()` to handle directories — thats a separate API topic.
- Adding subdirectory structure mirroring (e.g., preserving relative paths as
  resource names).

## Traceability

- **Intent**: Convenience workflow for composing an SSP from multiple FMU files.
- **Product**: `SSP.add_fmu_directory()` (new method) in `pyssp_standard/ssp.py`.
- **Architecture**: Public API layer, Archive layer (reuses `add_resource()`
  internals).
- **Implementation**: `pyssp_standard/ssp.py` (new method), no changes to
  `common/archive.py` or `fmu.py`.
- **Verification**: `pytest/ssp1/orchestration/test_ssp_add_fmu.py` (extended).

## Notes

- The existing `archive.py:rglob("*.fmu")` pattern can serve as implementation
  reference for the directory walk.
- The `component_name` derivation from `file_path.stem` follows the same pattern
  that `fmu.package_as_ssp()` uses (`component_name or self.path.stem`).
- Candidate was inspired by a user suggestion: "allow ssp.add_fmu to accept both
  file.fmu and a directory".