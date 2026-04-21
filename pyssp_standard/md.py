from __future__ import annotations

from pathlib import Path

from pyssp_standard.standard.fmi2.codec import Fmi2ModelDescriptionXmlCodec
from pyssp_standard.standard.fmi2.model import Fmi2ModelDescriptionDocument
from pyssp_standard.standard.fmi2.validation import Fmi2ModelDescriptionValidator
from pyssp_standard.common.xml_document import XmlDocumentFacade


class ModelDescription(XmlDocumentFacade[Fmi2ModelDescriptionDocument]):
    def __init__(self, path: str | Path | None = None, mode: str = "r", *, xml_text: str | None = None):
        if path is None and xml_text is None:
            raise ValueError("Either path or xml_text must be provided")
        self._xml_text = xml_text
        super().__init__(path or "<xml_text>", mode)
        self._codec = Fmi2ModelDescriptionXmlCodec()
        self._validator = Fmi2ModelDescriptionValidator()

    @property
    def root(self):
        return self.document.root

    @property
    def variables(self):
        return self.document.variables

    @property
    def inputs(self):
        return self.document.inputs

    @property
    def outputs(self):
        return self.document.outputs

    @property
    def parameters(self):
        return self.document.parameters

    @property
    def type_definitions(self):
        return self.document.type_definitions

    @property
    def model_structure(self):
        return self.document.model_structure

    def get(self, causality: str | None = None, variability: str | None = None):
        return self.document.get(causality=causality, variability=variability)

    def _create_document(self) -> Fmi2ModelDescriptionDocument:
        return Fmi2ModelDescriptionDocument(
            root=None,
            fmi_version="2.0",
            model_name=self.path.stem or "model",
            guid="",
            interface_type="CoSimulation",
        )
