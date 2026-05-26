# IMP-019: Add lifecycle-safe FMU iteration over SSP components

> **Status:** Proposed
> **Priority:** Medium
> **Layer:** Operations (core) / Public API (delegation)

## Theme

Provide a lazy, lifecycle-safe way to iterate over FMU-backed components in an SSP, resolving each component's `source` attribute to an `FMU` handle without forcing the caller to manually filter `Ssd1System.elements`, resolve runtime paths, and manage FMU open/close.

## Evidence

### Current manual pattern

In `pytest/ssp1/orchestration/test_ssp.py`, lines 141–153:

```python
with SSP(embrace_ssp_fixture, mode="r") as ssp:
    with ssp.system_structure() as ssd:
        component = next(c for c in ssd.xml.system.elements
                         if c.name == "ECS_HW")
        assert component.source == "resources/0001_ECS_HW.fmu"
        # resolve + open FMU manually
        with FMU(ssp.runtime.resolve(component.source), mode="r") as fmu:
            with fmu.model_description as md:
                assert md.xml.model_name == "ECS_HW"
```

This 5-step pattern (filter elements, read source, resolve, open FMU, manage lifecycle) repeats at lines 156–175 and would need to be duplicated by every caller.

### Existing iteration primitives (`pyssp_standard/standard/ssp1/model/ssd_model.py`)

| Method | Lines | Scope | Limitation |
|--------|-------|-------|------------|
| `get_components()` | 107–109 | Flat (direct children only) | Returns model objects, not FMU handles |
| `get_subsystems()` | 111–113 | Flat (direct children only) | Returns model objects only |
| `.elements` list | 99 | Raw access | Caller must filter with `isinstance` |

**None of these resolve `component.source` to an `FMU` handle.**

### `SSP.resources` (`pyssp_standard/ssp.py`, lines 55–59)

```python
@property
def resources(self) -> list[str]:
    return [name.removeprefix("resources/")
            for name in self.runtime.list_prefix("resources/")]
```

Lists **all files** under `resources/` but provides **no correlation** to which component maps to which resource.

### Runtime resolution works for both archive modes

- `DirectoryRuntime.resolve(path)` — `self.root / Path(path)` (`pyssp_standard/common/directory_runtime.py`, lines 47–48)
- `ArchiveRuntime.resolve(path)` — delegates to `_directory_runtime.resolve(path)` (`pyssp_standard/common/archive_runtime.py`, lines 53–54)

Both produce valid filesystem paths suitable for `FMU.__init__`.

### `FMU.__init__` handles both formats

`pyssp_standard/fmu.py`, lines 12–16:

```python
class FMU:
    def __init__(self, path: str | Path, mode: str = "r"):
        self.path = Path(path)
        self.mode = mode
        self.runtime = create_runtime(self.path, mode)
```

`create_runtime()` (`pyssp_standard/common/archive_runtime.py`, lines 75–83) detects directory vs `.fmu` archive transparently.

### Existing operation-module pattern

The codebase already places standalone orchestration logic in `standard/ssp1/operations/`:

| Module | Responsibility |
|--------|---------------|
| `model_description_to_ssd.py` | FMI→SSP component creation + system structure wiring |
| `ssd_parameter_bindings.py` | External inline parameter binding |
| `ssd_parameters.py` | Parameter set extension |
| `ssd_flatten.py` | Hierarchical SSD flattening |

## Current Pain Or Risk

1. **Boilerplate duplication**: Every caller who needs to open an FMU from an SSP must repeat the same 5-step pattern. No shared utility exists.
2. **No lifecycle safety**: Manual `FMU(...)` open/close is error-prone in loops. Missing context managers can leak temp directories.
3. **No recursive traversal**: Nested `Ssd1System` elements are invisible to flat iteration. Callers must implement recursion themselves.
4. **No graceful missing-source handling**: If an FMU resource file is absent (partial SSP), the pattern crashes on `FMU.__init__` even if the caller only needed metadata.
5. **Architecture friction**: Component resolution is orchestration logic but has no home in the operations layer.

## Proposed Improvement

### Hybrid: Standalone helper function (core) + thin SSP delegation (veneer)

**Core** — New file `pyssp_standard/standard/ssp1/operations/ssd_fmu_iteration.py`:

```python
@dataclass
class FmuEntry:
    """Lightweight handle for one FMU-backed component."""
    component: Ssd1Component        # The SSD component dataclass
    source: Path                     # Resolved filesystem path
    resource_path: str               # Original .source value (e.g. "resources/foo.fmu")

    def open_fmu(self, mode: str = "r") -> FMU:
        """Open this entry's FMU. Caller must use as context manager."""
        return FMU(self.source, mode=mode)

def iter_fmu_entries(
    system: Ssd1System,
    runtime: DirectoryRuntime,
    *,
    recursive: bool = False,
    skip_missing: bool = True,
) -> Iterator[FmuEntry]:
    """Yield FmuEntry for each Ssd1Component in *system*.

    When *recursive* is True, traverse into nested Ssd1System children.
    When *skip_missing* is True, entries whose source file does not exist
    at resolution time are skipped instead of raising.
    """
    ...
```

**Veneer** — New method on `SSP` class in `pyssp_standard/ssp.py`:

```python
def iter_fmu_entries(
    self, *, recursive: bool = False, skip_missing: bool = True
) -> Iterator[FmuEntry]:
    """Yield FmuEntry for every FMU-backed component in the SSP.

    Calls the standalone helper, opening the SSD document automatically.
    Returns metadata-only entries; open the FMU via entry.open_fmu().
    """
    from pyssp_standard.standard.ssp1.operations.ssd_fmu_iteration import (
        iter_fmu_entries as _iter,
    )
    with self.system_structure() as ssd:
        if ssd.xml.system is None:
            return
        yield from _iter(
            ssd.xml.system, self.runtime,
            recursive=recursive, skip_missing=skip_missing,
        )
```

### Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| `skip_missing` default | `True` | Callers exploring metadata shouldn't crash on incomplete SSPs. |
| `open_fmu()` return type | `FMU` (context-managed class) | Caller must `with entry.open_fmu() as fmu:`. Returning a context manager would add import overhead. Document that FMU must be used as context manager. |
| Recursion default | `False` (flat) | Most common case; deep iteration must be explicitly opted into. |
| Entry source type | `Path` (resolved) | Caller receives a usable file path immediately without needing to call `runtime.resolve()`. |

## Expected Benefit

- **Eliminates boilerplate**: Replaces 5-step pattern with `ssp.iter_fmu_entries()`.
- **Architecture-aligned**: Core logic in operations layer (testable without archive), thin delegation on SSP.
- **Lifecycle-safe**: Lazy — FMUs are only opened when `open_fmu()` is called, not during iteration.
- **Graceful missing sources**: `skip_missing=True` allows metadata-only exploration.
- **Recursive opt-in**: `recursive=True` handles nested `Ssd1System` transparently.
- **No breaking changes**: Existing `SSP.add_fmu()`, `SSP.resources`, `Ssd1System` API all untouched.

## Risk And Blast Radius

| Risk | Severity | Mitigation |
|------|----------|------------|
| `open_fmu()` creates FMU outside context manager | Medium | Document clearly; consider returning `contextlib.contextmanager` in future |
| Archive resolution of `.fmu` .zip in temp dir | Low | Already works — `ArchiveRuntime.resolve()` returns temp-extracted path; `FMU.__init__` opens `.zip` via `create_runtime()` |
| Perf: opening same FMU multiple times | Low | Each `open_fmu()` creates a new `FMU` instance; callers should cache if needed |
| Missing resource in archive context | Low | `skip_missing=True` checks `path.exists()` before yielding; archive temp dir will have the extracted file if it exists in the archive |
| SSP2 compatibility | Low | `Ssd1System` and `Ssd1Component` are SSP1-specific; scope to SSP1 only |
| Recursion depth | Low | Nested SSP is uncommon; recursion follows existing `get_all_parameter_bindings()` pattern (line 138 of `ssd_model.py`) |

## Suggested Priority

**Medium** — Not a correctness fix, but eliminates duplicated boilerplate patterns that are already present in tests and would multiply as new callers appear. The architecture alignment (operations layer) makes it higher value than a simple convenience method.

## Task Contract Seed

### Phase 1 — Core standalone function

1. Create `pyssp_standard/standard/ssp1/operations/ssd_fmu_iteration.py`:
   - `FmuEntry` dataclass with `.component` (Ssd1Component), `.source` (Path), `.resource_path` (str), `.open_fmu(mode)` returning `FMU`.
   - `iter_fmu_entries(system, runtime, recursive=False, skip_missing=True)`:
     - Iterate `system.get_components()`, resolve each `.source` via `runtime.resolve()`.
     - Check file existence when `skip_missing=True`; skip non-existent.
     - Yield `FmuEntry` for each component.
     - When `recursive=True`, recurse into `system.get_subsystems()`.
   - Pure function; no context-manager dependency.

2. Add import to `pyssp_standard/standard/ssp1/operations/__init__.py`.

### Phase 2 — SSP delegation method

3. Add `iter_fmu_entries(self, recursive=False, skip_missing=True)` to `SSP` class in `pyssp_standard/ssp.py`:
   - Opens SSD via `self.system_structure()`.
   - Delegates to standalone helper.
   - Yields `FmuEntry` instances.

4. Export `FmuEntry` from `pyssp_standard/__init__.py`? (Decide: yes for discoverability, but it's a dataclass, not a facade — may be better to document it in the method docstring and keep it importable from the operations module.)

### Phase 3 — Tests

5. Create `pytest/ssp1/orchestration/test_ssp_fmu_iteration.py`:

   | Test | Purpose |
   |------|---------|
   | `test_iter_fmu_entries_flat` | Single component yielded with correct entry fields |
   | `test_iter_fmu_entries_multiple_components` | All components in a system yielded |
   | `test_iter_fmu_entries_skip_missing` | Missing FMU source silently skipped |
   | `test_iter_fmu_entries_skip_missing_false` | Missing source included but `open_fmu()` raises |
   | `test_iter_fmu_entries_recursive` | Nested system components yielded with `recursive=True` |
   | `test_iter_fmu_entries_non_recursive_skips_nested` | Nested components *not* yielded when `recursive=False` |
   | `test_iter_fmu_entries_open_fmu_returns_fmu_handle` | `open_fmu()` returns an `FMU` instance with valid model description |
   | `test_iter_fmu_entries_empty_system` | No components → empty iterator |
   | `test_iter_fmu_entries_from_standalone_helper` | Direct call to `iter_fmu_entries(system, runtime)` without SSP |
   | `test_iter_fmu_entries_from_ssp_delegation` | `ssp.iter_fmu_entries()` yields same results as standalone |

6. Use existing fixtures (`embrace_ssp_fixture`, `embrace_ssp_archive_fixture`, `fmu_archive_fixture`).

### Phase 4 — Decision record

7. Create `product-breakdown/06-evolution/decisions/DEC-IMP019-R1-001.md` documenting the hybrid-API choice (standalone helper + thin SSP delegation) and the rationale for rejecting Options A (eager property) and B alone.

## Out Of Scope

- **SSP2 support** — `Ssd1System`/`Ssd1Component` are SSP1-specific. SSP2 would need its own model or an abstract base.
- **Filtering by FMU metadata** — e.g., "only components implementing ModelExchange". Caller can filter the yielded entries.
- **Bulk FMU open** — Opening every FMU in a single `with` block. Keep per-entry lifecycle.
- **Modifying existing `SSP.add_fmu()` or `SSP.resources`** — Additive only.
- **`FMU` lifecycle guarantee enforcement** — `open_fmu()` returns a `FMU`, not a `contextmanager`. Document that callers must use `with`. A future improvement could wrap it in `@contextmanager`.

## Traceability

- **Intent**: Eliminate boilerplate for iterating FMU components in an SSP, with architecture-aligned placement.
- **Product**: `FmuEntry` dataclass + `iter_fmu_entries()` function in `standard/ssp1/operations/ssd_fmu_iteration.py`, thin `SSP.iter_fmu_entries()` method.
- **Architecture**: Operations layer (core logic), Public API layer (thin delegation).
- **Implementation**: New file (`ssd_fmu_iteration.py`), amended file (`ssp.py`).
- **Verification**: New test file (`test_ssp_fmu_iteration.py`).

## Notes

- The `get_all_parameter_bindings()` method on `Ssd1System` (line 138 of `ssd_model.py`) demonstrates the exact recursion pattern to use: `for element in self.elements: if isinstance(element, Ssd1System): recurse; elif isinstance(element, Ssd1Component): process`.
- The `model_description_to_ssd.py` module in `standard/operations/` (cross-standard) and `standard/ssp1/operations/` (SSP1-specific) provides the placement precedent.
- `Architecture Guardrail Finding` from the evaluation: "Orchestration layer owns archive-relative resolution" (layer-rules.md line 58). The standalone helper is orchestration logic; the SSP delegation is a thin public API method. This aligns cleanly.
