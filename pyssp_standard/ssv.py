from __future__ import annotations

import tempfile
from pathlib import Path

import xmlschema

from pyssp_standard.orchestration.version_routing import StandardVersion, get_standard_version_from_file
from pyssp_standard.ssp1.codec.ssv_xsdata_codec import Ssp1SsvXsdataCodec
from pyssp_standard.ssp1.model.ssv_model import SsvParameterSet
from pyssp_standard.ssp2.codec.ssv_xsdata_codec import Ssp2SsvXsdataCodec
from pyssp_standard.standard import ModelicaStandard


class SsvFileSession:
    def __init__(self, filepath: Path, mode: str):
        self.file_path = filepath
        self.mode = mode

    def load(self) -> SsvParameterSet:
        standard = get_standard_version_from_file(self.file_path)
        xml_text = self.file_path.read_text(encoding="utf-8")
        return self._codec_for_standard(standard).parse(xml_text)

    def save(self, model: SsvParameterSet) -> None:
        self.file_path.write_text(self.serialize(model), encoding="utf-8")

    def serialize(self, model: SsvParameterSet) -> str:
        standard = StandardVersion(
            family="SSP",
            format="SSV",
            version=model.version,
        )
        return self._codec_for_standard(standard).serialize(model)

    def validate(
        self,
        model: SsvParameterSet | None,
        *,
        identifier: str,
        schemas: dict,
        namespaces: dict,
    ) -> None:
        schema = xmlschema.XMLSchema10(schemas[identifier])
        if self.mode == "r":
            xmlschema.validate(self.file_path, schema, namespaces=namespaces)
            return

        with tempfile.TemporaryDirectory(suffix="_pyssp") as temp_dir:
            temp_file_path = Path(temp_dir) / "tmp.ssv"
            temp_file_path.write_text(self.serialize(model), encoding="utf-8")
            xmlschema.validate(temp_file_path, schema, namespaces=namespaces)

    @staticmethod
    def _codec_for_standard(standard: StandardVersion):
        if standard.version == "1.0":
            return Ssp1SsvXsdataCodec()
        if standard.version == "2.0":
            return Ssp2SsvXsdataCodec()
        raise ValueError(f"Unsupported SSV standard version '{standard.version}'")


class SSV(ModelicaStandard):
    def __init__(self, filepath, mode="r", name="unnamed"):
        self._mode = mode
        self._session = SsvFileSession(
            filepath if isinstance(filepath, Path) else Path(filepath),
            mode,
        )
        self.model = SsvParameterSet(name=name, version="1.0")
        self.root = None

        if mode in {"r", "a"}:
            self.__read__()

    @property
    def file_path(self):
        return self._session.file_path

    @property
    def metadata(self):
        return self.model.metadata

    @property
    def base_element(self):
        return self.model.metadata

    @property
    def top_level_metadata(self):
        return self.model.metadata

    @property
    def BaseElement(self):
        return self.model.metadata

    @property
    def TopLevelMetaData(self):
        return self.model.metadata

    @property
    def version(self):
        return self.model.version

    @version.setter
    def version(self, value):
        self.model.version = value

    @property
    def identifier(self):
        return "ssv2" if self.model.version == "2.0" else "ssv"

    @property
    def parameters(self):
        return self.model.parameters

    @property
    def units(self):
        return self.model.units

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._mode in {"w", "a"}:
            self.__save__()

    def __read__(self):
        self.model = self._session.load()

    def __save__(self):
        self._session.save(self.model)

    def __check_compliance__(self):
        self._session.validate(
            None if self._mode == "r" else self.model,
            identifier=self.identifier,
            schemas=self.schemas,
            namespaces=self.namespaces,
        )

    def add_parameter(
        self,
        parname: str,
        ptype: str = "Real",
        *,
        value: float = None,
        name: str = None,
        mimetype=None,
        unit: str = None,
    ):
        return self.model.add_parameter(
            parname,
            ptype,
            value=value,
            name=name,
            mimetype=mimetype,
            unit=unit,
        )

    def add_unit(self, name: str, base_unit: dict = None):
        return self.model.add_unit(name, base_unit)
