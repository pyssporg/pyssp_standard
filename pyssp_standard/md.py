from __future__ import annotations

from pathlib import Path

from pyssp_standard.standard.fmi2.codec import Fmi2ModelDescriptionXmlCodec
from pyssp_standard.standard.fmi2.model import Fmi2ModelDescriptionDocument
from pyssp_standard.standard.fmi2.validation import Fmi2ModelDescriptionValidator
from pyssp_standard.common.xml_document import XmlDocument


class ModelDescription(XmlDocument[Fmi2ModelDescriptionDocument]):
    def __init__(self, path: str | Path | None = None, mode: str = "r"):

        super().__init__(path, mode)
        self._codec = Fmi2ModelDescriptionXmlCodec()
        self._validator = Fmi2ModelDescriptionValidator()

    def _create_document(self) -> Fmi2ModelDescriptionDocument:
        return Fmi2ModelDescriptionDocument(
            root=None,
            fmi_version="2.0",
            model_name=self.path.stem or "model",
            guid="",
            interface_type="CoSimulation",
        )
