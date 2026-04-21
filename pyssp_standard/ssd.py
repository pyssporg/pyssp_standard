from __future__ import annotations

from pathlib import Path

from pyssp_standard.standard.ssp1.codec.ssd_xml_codec import Ssp1SsdXmlCodec
from pyssp_standard.standard.ssp1.model.ssd_model import (
    SsdComponent,
    SsdConnection,
    SsdConnector,
    SsdDefaultExperiment,
    SsdSystemStructureDescription,
    SsdSystem,
)
from pyssp_standard.standard.ssp1.validation import Ssp1SsdValidator
from pyssp_standard.xml_document import XmlDocumentFacade


Connection = SsdConnection
System = SsdSystem
DefaultExperiment = SsdDefaultExperiment
Component = SsdComponent
Connector = SsdConnector


class SSD(XmlDocumentFacade[SsdSystemStructureDescription]):
    """Public SSD facade following the same layered pattern as SSV."""

    def __init__(self, path: str | Path, mode: str = "r"):
        super().__init__(path, mode)
        self._codec = Ssp1SsdXmlCodec()
        self._validator = Ssp1SsdValidator()

    def _create_document(self) -> SsdSystemStructureDescription:
        return SsdSystemStructureDescription(name=self.path.stem or "system", version="1.0", system=SsdSystem(name="system"))

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
    def system(self) -> SsdSystem | None:
        return self.document.system

    @system.setter
    def system(self, value: SsdSystem | None) -> None:
        self.document.system = value

    @property
    def default_experiment(self) -> SsdDefaultExperiment | None:
        return self.document.default_experiment

    @default_experiment.setter
    def default_experiment(self, value: SsdDefaultExperiment | None) -> None:
        self.document.default_experiment = value

    def add_connection(self, connection: SsdConnection) -> SsdConnection:
        return self.document.add_connection(connection)

    def remove_connection(self, connection: SsdConnection) -> None:
        self.document.remove_connection(connection)

    def list_connectors(self, parent: str | None = None):
        return self.document.list_connectors(parent=parent)

    def connections(self):
        return self.document.connections()
