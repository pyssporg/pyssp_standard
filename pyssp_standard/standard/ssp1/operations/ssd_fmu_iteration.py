"""Lazy iteration over FMU-backed components in an SSP1 system structure.

Provides the ``FmuEntry`` dataclass and the ``iter_fmu_entries`` generator
for lifecycle-safe discovery of FMU resources referenced by SSD components.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1Component,
    Ssd1System,
)
from pyssp_standard.common.directory_runtime import DirectoryRuntime


@dataclass
class FmuEntry:
    """A discovered FMU-backed component with a resolved filesystem path.

    Attributes:
        component: The Ssd1Component instance from the system structure.
        source: The resolved absolute filesystem path to the FMU resource.
        resource_path: The raw ``source`` string as it appears on the component.
    """

    component: Ssd1Component
    source: Path
    resource_path: str

    def open_fmu(self, mode: str = "r") -> FMU:
        """Open the FMU at *source* and return an :class:`~pyssp_standard.fmu.FMU` instance.

        The caller is responsible for the context-manager lifecycle::

            with entry.open_fmu() as fmu:
                ...

        Args:
            mode: File access mode for the FMU (default ``"r"``).

        Returns:
            An :class:`~pyssp_standard.fmu.FMU` instance wrapping *source*.
        """
        from pyssp_standard.fmu import FMU

        return FMU(self.source, mode=mode)


def iter_fmu_entries(
    system: Ssd1System,
    runtime: DirectoryRuntime,
    *,
    recursive: bool = False,
    skip_missing: bool = True,
) -> Iterator[FmuEntry]:
    """Yield an ``FmuEntry`` for every component whose ``source`` references an FMU.

    Walks ``system.elements`` and yields ``FmuEntry`` for each direct
    ``Ssd1Component`` child.  ``Ssd1System`` children are skipped unless
    *recursive* is ``True``, in which case they are traversed depth-first
    (components of nested subsystems are yielded *after* the direct
    components of the current level).

    Args:
        system: The root ``Ssd1System`` to walk.
        runtime: The ``DirectoryRuntime`` used to resolve component source
            paths via ``runtime.resolve()``.
        recursive: If ``True``, recurse into ``Ssd1System`` children.
        skip_missing: When ``True`` (default), components whose resolved
            source path does not exist on disk are silently skipped.  When
            ``False``, the entry is yielded even for missing files, allowing
            callers to inspect or handle the missing resource themselves.

    Yields:
        ``FmuEntry`` instances for each FMU-backed component.
    """
    for element in system.elements:
        if isinstance(element, Ssd1System):
            if recursive:
                yield from iter_fmu_entries(
                    element, runtime, recursive=True, skip_missing=skip_missing
                )
            continue

        if not isinstance(element, Ssd1Component):
            continue

        resolved = runtime.resolve(element.source)
        if skip_missing and not resolved.exists():
            continue

        yield FmuEntry(
            component=element,
            source=resolved,
            resource_path=element.source,
        )