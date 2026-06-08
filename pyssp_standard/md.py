"""ModelDescription facade — version-aware through version routing."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pyssp_standard.common.xml_document import XmlDocument
from pyssp_standard.standard.fmi2.model import Fmi2ModelDescriptionDocument
from pyssp_standard.standard.fmi3.model import (
    Fmi3ModelDescriptionDocument,
    Fmi3ScalarVariable,
)
from pyssp_standard.standard.version_routing import (
    StandardVersion,
    get_codec_and_validator,
    get_standard_version_from_file,
)

_ME_ONLY_CAPABILITY_FIELDS: frozenset[str] = frozenset(
    {"completedIntegratorStepNotNeeded", "needsExecutionTool"}
)


class ModelDescription(XmlDocument[Fmi2ModelDescriptionDocument | Fmi3ModelDescriptionDocument]):
    """ModelDescription facade — version-aware through version routing."""

    def __init__(self, path: str | Path | None = None, mode: str = "r", version: str | None = None) -> None:
        super().__init__(path, mode)
        self._version = version or "2.0"

        self._codec, self._validator = self.get_codec_and_validator("FMI", "MD")

    def _create_document(self) -> Fmi2ModelDescriptionDocument | Fmi3ModelDescriptionDocument:
        if self._version == "3.0":
            return Fmi3ModelDescriptionDocument(
                root=None,
                fmi_version="3.0",
                model_name=self.path.stem or "model",
                instantiation_token=self.path.stem or "generated",
                variables=[
                    Fmi3ScalarVariable(
                        name="auto_generated",
                        value_reference=0,
                        type_name="Float64",
                    ),
                ],
            )
        return Fmi2ModelDescriptionDocument(
            root=None,
            fmi_version="2.0",
            model_name=self.path.stem or "model",
            guid="",
            interface_type="CoSimulation",
        )

    def set_generation_date_and_time(self, dt: datetime | str | None = None) -> None:
        """Set the generation date and time on the XML document.

        Args:
            dt: A datetime, ISO 8601 string, or None.
                None defaults to "2000-01-01T00:00:00Z".
        """
        from pyssp_standard.common.datetime_utils import format_generation_datetime

        self.xml.generation_date_and_time = format_generation_datetime(dt)

    def strip_model_exchange(self) -> None:
        """Convert a ModelExchange document to CoSimulation in-place. FMI2 only."""
        if self._version != "2.0":
            return
        if self.xml.interface_type == "CoSimulation":
            return
        if self.xml.interface_type is None:
            return
        self.xml.interface_type = "CoSimulation"
        if self.xml.capabilities is not None:
            self.xml.capabilities.completed_integrator_step_not_needed = False
            self.xml.capabilities.needs_execution_tool = False
            self.xml.capabilities.extra_attributes.pop("completedIntegratorStepNotNeeded", None)
            self.xml.capabilities.extra_attributes.pop("needsExecutionTool", None)
        self.xml.model_structure.derivatives.clear()
        self.xml.number_of_event_indicators = None
        self.check_compliance()