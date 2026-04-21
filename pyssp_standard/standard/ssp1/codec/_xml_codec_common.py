from __future__ import annotations

from io import StringIO
from typing import Callable, TypeVar
from xml.etree import ElementTree as ET

from pyssp_standard.standard.ssp1.model.xml_model import XmlDocumentNode, XmlElementNode


DocumentT = TypeVar("DocumentT", bound=XmlDocumentNode)


def parse_xml_document(
    xml_text: str,
    *,
    expected_namespace: str,
    expected_local_name: str,
    document_factory: Callable[[XmlElementNode, dict[str, str]], DocumentT],
) -> DocumentT:
    namespaces = _collect_namespaces(xml_text)
    root = ET.fromstring(xml_text)
    namespace_uri, local_name = _split_tag(root.tag)
    if namespace_uri != expected_namespace or local_name != expected_local_name:
        raise ValueError(
            f"Unexpected root element '{local_name}' in namespace '{namespace_uri}', "
            f"expected '{expected_local_name}' in namespace '{expected_namespace}'"
        )
    return document_factory(_element_to_node(root), namespaces)


def serialize_xml_document(document: XmlDocumentNode) -> str:
    for prefix, uri in document.namespaces.items():
        if prefix in {"xml", "xmlns"}:
            continue
        ET.register_namespace(prefix, uri)

    root = _node_to_element(document.root)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    return ET.tostring(root, encoding="unicode")


def _collect_namespaces(xml_text: str) -> dict[str, str]:
    namespaces: dict[str, str] = {}
    for _, pair in ET.iterparse(StringIO(xml_text), events=("start-ns",)):
        prefix, uri = pair
        namespaces.setdefault(prefix, uri)
    return namespaces


def _element_to_node(element: ET.Element) -> XmlElementNode:
    namespace_uri, local_name = _split_tag(element.tag)
    return XmlElementNode(
        local_name=local_name,
        namespace_uri=namespace_uri,
        attributes=dict(element.attrib),
        children=[_element_to_node(child) for child in list(element)],
        text=element.text if element.text and element.text.strip() else None,
    )


def _node_to_element(node: XmlElementNode) -> ET.Element:
    element = ET.Element(node.qualified_name, attrib=dict(node.attributes))
    if node.text is not None:
        element.text = node.text
    for child in node.children:
        element.append(_node_to_element(child))
    return element


def _split_tag(tag: str) -> tuple[str | None, str]:
    if tag.startswith("{"):
        namespace_uri, local_name = tag[1:].split("}", 1)
        return namespace_uri, local_name
    return None, tag
