from __future__ import annotations

from pathlib import Path

from pyssp_standard.standard.fmi2.codec import Fmi2ModelDescriptionXmlCodec
from pyssp_standard.standard.fmi2.model import Fmi2ModelDescriptionDocument
from pyssp_standard.standard.fmi2.validation import Fmi2ModelDescriptionValidator
from pyssp_standard.common.xml_document import XmlDocument

_ME_ONLY_INTERFACE_ATTRIBUTES: frozenset[str] = frozenset({"completedIntegratorStepNotNeeded", "needsExecutionTool"})


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

    def strip_model_exchange(self) -> None:
        """Convert a ModelExchange document to CoSimulation in-place.

        Mutates:
            - interface_type → "CoSimulation"
            - Removes ME-only attributes from interface_attributes
            - Clears model_structure.derivatives
            - Sets number_of_event_indicators → None

        No-op when interface_type is already "CoSimulation" or None.
        Raises RuntimeError if document is not loaded.
        """
        if self.xml.interface_type == "CoSimulation":
            return

        if self.xml.interface_type is None:
            return

        self.xml.interface_type = "CoSimulation"

        for key in _ME_ONLY_INTERFACE_ATTRIBUTES:
            self.xml.interface_attributes.pop(key, None)

        self.xml.model_structure.derivatives.clear()
        self.xml.number_of_event_indicators = None
        self.check_compliance()
