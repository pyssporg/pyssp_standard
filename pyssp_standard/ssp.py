from __future__ import annotations

from pathlib import Path

from pyssp_standard.ssd import SSD
from pyssp_standard.ssm import SSM
from pyssp_standard.ssv import SSV
from pyssp_standard.common.zip_archive import DirectoryRuntime, open_archive


class _SspSystemStructureFacade:
    """Archive-level SSD facade with dependency resolution.

    Standalone `SSD` and `SSV` remain plain file facades. Cross-file reference
    loading and persistence belongs here at the SSP archive boundary.
    """

    def __init__(self, runtime: DirectoryRuntime, ssd_name: str = "SystemStructure.ssd", mode: str = "r"):
        self._runtime = runtime
        self._ssd_path = runtime.resolve(ssd_name)
        self._mode = mode
        self._ssd = SSD(self._ssd_path, mode=mode)

    def __enter__(self) -> SSD:
        self._ssd.__enter__()
        self._load_external_references()
        return self._ssd

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None and self._mode in {"w", "a"}:
            self._persist_external_references()
        return self._ssd.__exit__(exc_type, exc, tb)

    @property
    def path(self) -> Path:
        return self._ssd_path

    def _load_external_references(self) -> None:
        for binding in self._ssd.parameter_bindings:
            if not binding.is_inlined and binding.external_path:
                external_path = self._runtime.resolve(binding.external_path)
                if external_path.exists():
                    try:
                        with SSV(external_path, mode="r") as ssv:
                            binding.parameter_set = ssv.document
                        binding.is_resolved = True
                    except Exception:
                        binding.parameter_set = None
                        binding.is_resolved = False
                else:
                    binding.parameter_set = None
                    binding.is_resolved = False

            if binding.parameter_mapping_path:
                mapping_path = self._runtime.resolve(binding.parameter_mapping_path)
                if mapping_path.exists():
                    try:
                        with SSM(mapping_path, mode="r") as ssm:
                            binding.parameter_mapping = ssm.document
                        binding.is_mapping_resolved = True
                    except Exception:
                        binding.parameter_mapping = None
                        binding.is_mapping_resolved = False
                else:
                    binding.parameter_mapping = None
                    binding.is_mapping_resolved = False

    def _persist_external_references(self) -> None:
        for binding in self._ssd.parameter_bindings:
            if not binding.is_inlined and binding.external_path and binding.parameter_set is not None:
                external_path = self._runtime.resolve(binding.external_path)
                with SSV(external_path, mode="w") as ssv:
                    ssv._document = binding.parameter_set

            if binding.parameter_mapping_path and binding.parameter_mapping is not None:
                mapping_path = self._runtime.resolve(binding.parameter_mapping_path)
                with SSM(mapping_path, mode="w") as ssm:
                    ssm._document = binding.parameter_mapping


class SSP:
    def __init__(self, path: str | Path, mode: str = "a"):
        self.path = Path(path)
        self.mode = mode
        self._archive = open_archive(self.path, mode)
        self._runtime: DirectoryRuntime | None = None

    def __enter__(self) -> "SSP":
        self._runtime = self._archive.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            return self._archive.__exit__(exc_type, exc, tb)
        finally:
            self._runtime = None

    @property
    def runtime(self) -> DirectoryRuntime:
        if self._runtime is None:
            raise RuntimeError("SSP is not open")
        return self._runtime

    @property
    def resources(self) -> list[str]:
        return [name.removeprefix("resources/") for name in self.runtime.list_prefix("resources/")]

    def add_resource(self, source: str | Path) -> str:
        source_path = Path(source)
        return self.runtime.add_file(source_path, target_name=f"resources/{source_path.name}").removeprefix("resources/")

    def remove_resource(self, resource_name: str) -> None:
        self.runtime.remove_file(f"resources/{resource_name}")

    @property
    def system_structure(self) -> _SspSystemStructureFacade:
        return _SspSystemStructureFacade(self.runtime, ssd_name="SystemStructure.ssd", mode="a" if self.mode == "w" else self.mode)
