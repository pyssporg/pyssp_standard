from __future__ import annotations

from pathlib import Path

from pyssp_standard.standard.ssp1.codec.ssd_xml_codec import Ssp1SsdXmlCodec
from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1Component,
    Ssd1Connection,
    Ssd1Connector,
    Ssd1DefaultExperiment,
    Ssd1SystemStructureDescription,
    Ssd1System,
)
from pyssp_standard.standard.ssp1.validation import Ssp1SsdValidator
from pyssp_standard.common.xml_document import XmlDocumentFacade


Connection = Ssd1Connection
System = Ssd1System
DefaultExperiment = Ssd1DefaultExperiment
Component = Ssd1Component
Connector = Ssd1Connector


class SSD(XmlDocumentFacade[Ssd1SystemStructureDescription]):
    """Public SSD facade following the same layered pattern as SSV."""

    def __init__(self, path: str | Path, mode: str = "r"):
        super().__init__(path, mode)
        self._codec = Ssp1SsdXmlCodec()
        self._validator = Ssp1SsdValidator()

    def _create_document(self) -> Ssd1SystemStructureDescription:
        return Ssd1SystemStructureDescription(name=self.path.stem or "system", version="1.0", system=Ssd1System(name="system"))

    @property
    def name(self) -> str:
        return self.document.name

    @name.setter
    def name(self, value: str) -> None:
        self.document.name = value

    @property
    def version(self) -> str:
        return self.document.version

    @version.setter
    def version(self, value: str) -> None:
        self.document.version = value

    @property
    def system(self) -> Ssd1System | None:
        return self.document.system

    @system.setter
    def system(self, value: Ssd1System | None) -> None:
        self.document.system = value

    @property
    def default_experiment(self) -> Ssd1DefaultExperiment | None:
        return self.document.default_experiment

    @default_experiment.setter
    def default_experiment(self, value: Ssd1DefaultExperiment | None) -> None:
        self.document.default_experiment = value

    def add_connection(self, connection: Ssd1Connection) -> Ssd1Connection:
        return self.document.add_connection(connection)

    def remove_connection(self, connection: Ssd1Connection) -> None:
        self.document.remove_connection(connection)

    def list_connectors(self, parent: str | None = None):
        return self.document.list_connectors(parent=parent)

    def connections(self):
        return self.document.connections()
