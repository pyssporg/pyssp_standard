from __future__ import annotations

from pathlib import Path

from pyssp_standard.common.xml_document import XmlDocument
from pyssp_standard.standard.ls_ref.codec import LSRefExperimentsCodec, LSRefManifestCodec
from pyssp_standard.standard.ls_ref.model import (
    LSRefExperimentsDocument,
    LSRefManifestDocument,
)
from pyssp_standard.standard.ls_ref.validation import LSRefExperimentsValidator, LSRefManifestValidator


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

