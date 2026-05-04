from __future__ import annotations

from xml.etree import ElementTree as ET

from pyssp_standard.standard.ls_ref.constants import (
    DEFAULT_LS_REF_DESCRIPTION,
    DEFAULT_LS_REF_NAME,
    DEFAULT_LS_REF_VERSION,
    FMI_LS_MANIFEST_NAMESPACE,
    FMI_LS_MANIFEST_PREFIX,
    MANIFEST_ROOT_TAG,
    RELATED_TAG,
)
from pyssp_standard.standard.ls_ref.model.manifest import LSRefManifestDocument, LSRefRelated


def _attr(name: str) -> str:
    return f"{{{FMI_LS_MANIFEST_NAMESPACE}}}{name}"


class LSRefManifestCodec:
    def parse(self, xml_text: str) -> LSRefManifestDocument:
        root = ET.fromstring(xml_text)
        document = LSRefManifestDocument(
            version=root.attrib.get(_attr("fmi-ls-version"), DEFAULT_LS_REF_VERSION),
            name=root.attrib.get(_attr("fmi-ls-name"), DEFAULT_LS_REF_NAME),
            description=root.attrib.get(_attr("fmi-ls-description"), DEFAULT_LS_REF_DESCRIPTION),
        )
        document.related = [
            self._parse_related(element)
            for element in root.findall(RELATED_TAG)
        ]
        return document

    def serialize(self, document: LSRefManifestDocument) -> str:
        ET.register_namespace(FMI_LS_MANIFEST_PREFIX, FMI_LS_MANIFEST_NAMESPACE)

        root = ET.Element(MANIFEST_ROOT_TAG)
        root.set(_attr("fmi-ls-name"), document.name)
        root.set(_attr("fmi-ls-version"), document.version)
        root.set(_attr("fmi-ls-description"), document.description)

        for related in document.related:
            root.append(self._serialize_related(related))

        ET.indent(root, space="  ")
        return ET.tostring(root, encoding="unicode", xml_declaration=True)

    def _parse_related(self, element: ET.Element) -> LSRefRelated:
        return LSRefRelated(
            source=element.attrib["source"],
            role=element.attrib["role"],
            type=element.attrib.get("type"),
            description=element.attrib.get("description"),
        )

    def _serialize_related(self, related: LSRefRelated) -> ET.Element:
        element = ET.Element(RELATED_TAG)
        if related.type is not None:
            element.set("type", related.type)
        element.set("source", related.source)
        element.set("role", related.role)
        if related.description is not None:
            element.set("description", related.description)
        return element
