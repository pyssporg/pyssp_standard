from __future__ import annotations

from pathlib import Path

from pyssp_standard.ssd import SSD
from pyssp_standard.ssm import SSM
from pyssp_standard.ssv import SSV
from pyssp_standard.common.zip_archive import ZipArchiveFacade


class _SspSystemStructureFacade:
    """Archive-level SSD facade with dependency resolution.

    Standalone `SSD` and `SSV` remain plain file facades. Cross-file reference
    loading and persistence belongs here at the SSP archive boundary.
    """

    def __init__(self, ssd_path: str | Path, mode: str = "r"):
        self._ssd_path = Path(ssd_path)
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
                external_path = self._ssd_path.parent / binding.external_path
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
                mapping_path = self._ssd_path.parent / binding.parameter_mapping_path
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
                external_path = self._ssd_path.parent / binding.external_path
                with SSV(external_path, mode="w") as ssv:
                    ssv._document = binding.parameter_set

            if binding.parameter_mapping_path and binding.parameter_mapping is not None:
                mapping_path = self._ssd_path.parent / binding.parameter_mapping_path
                with SSM(mapping_path, mode="w") as ssm:
                    ssm._document = binding.parameter_mapping


class SSP:
    def __init__(self, path: str | Path, mode: str = "a"):
        self.path = Path(path)
        self.mode = mode
        self._archive = ZipArchiveFacade(self.path, mode)

    def __enter__(self) -> "SSP":
        self._archive.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._archive.__exit__(exc_type, exc, tb)
        return False

    @property
    def resources(self) -> list[str]:
        return [name.removeprefix("resources/") for name in self._archive.list_prefix("resources/")]

    def add_resource(self, source: str | Path) -> str:
        source_path = Path(source)
        return self._archive.add_file(source_path, target_name=f"resources/{source_path.name}").removeprefix("resources/")

    def remove_resource(self, resource_name: str) -> None:
        self._archive.remove_file(f"resources/{resource_name}")

    @property
    def system_structure(self) -> _SspSystemStructureFacade:
        workdir = self._archive._require_workdir()
        ssd_path = workdir / "SystemStructure.ssd"
        # opening the ssp in w should not create a new SSD, change to a
        return _SspSystemStructureFacade(ssd_path, mode="a" if self.mode == "w" else self.mode)
