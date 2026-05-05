from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from pyssp_standard.common.archive_runtime import DirectoryRuntime
from pyssp_standard.common.document_runtime import DocumentRuntime
from pyssp_standard.common.xml_document import XmlDocument
from pyssp_standard.standard.ls_ref.codec import LSRefExperimentsCodec, LSRefManifestCodec
from pyssp_standard.standard.ls_ref.model import (
    LSRefExperiment,
    LSRefExperimentsDocument,
    LSRefManifestDocument,
)
from pyssp_standard.standard.ls_ref.validation import LSRefExperimentsValidator, LSRefManifestValidator

LS_REF_EXTRA_DIR = "extra/org.fmi-standard.fmi-ls-ref"

class LSRefManifest(XmlDocument[LSRefManifestDocument]):
    """Public LS-REF manifest facade."""

    def __init__(self, path: str | Path, mode: str = "r"):
        super().__init__(path, mode)
        self._codec = LSRefManifestCodec()
        self._validator = LSRefManifestValidator()

    def _create_document(self) -> LSRefManifestDocument:
        return LSRefManifestDocument()


class LSRefExperiments(XmlDocument[LSRefExperimentsDocument]):
    """Public LS-REF experiments facade."""

    def __init__(self, path: str | Path, mode: str = "r"):
        super().__init__(path, mode)
        self._codec = LSRefExperimentsCodec()
        self._validator = LSRefExperimentsValidator()

    def _create_document(self) -> LSRefExperimentsDocument:
        return LSRefExperimentsDocument(name=self.path.stem or "experiments")

    def add_experiment(self, experiments: LSRefExperiment | Iterable[LSRefExperiment]) -> None:
        experiment_list = (
            [experiments]
            if isinstance(experiments, LSRefExperiment)
            else list(experiments)
        )
        if not experiment_list:
            raise ValueError("At least one LS-REF experiment is required")
        self.xml.experiments.extend(experiment_list)
    
    @staticmethod
    def check_document_compliance(path : str):
        with LSRefExperiments(path) as experiments:
            experiments.check_compliance()


class LSRefExperimentsRuntime(DocumentRuntime[LSRefExperiments]):
    """Archive-level LS-REF experiments facade."""

    def __init__(
        self,
        runtime: DirectoryRuntime,
        experiments_path: str = f"{LS_REF_EXTRA_DIR}/experiments.xml",
        mode: str = "r",
    ):
        super().__init__(
            runtime,
            document_path=experiments_path,
            document_type=LSRefExperiments,
            mode=mode,
        )
