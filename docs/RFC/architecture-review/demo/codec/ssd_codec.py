from xml.etree import ElementTree as ET

from ..model.ssd_model import SsdDocument, SsdParameterBinding
from .ssv_hybrid_codec import Ssv2HybridCodec


NS_SSD = "http://ssp-standard.org/SSP1/SystemStructureDescription"


class SsdBindingCodec:
    """Handwritten SSD codec: XML <-> domain only, no file/resource I/O."""

    def __init__(self):
        self._ssv_codec = Ssv2HybridCodec()

    def parse(self, xml_text: str) -> SsdDocument:
        root = ET.fromstring(xml_text)
        doc = SsdDocument(name=root.attrib.get("name", "unnamed"), version=root.attrib.get("version", "1.0"))

        def localname(tag: str) -> str:
            return tag.split("}", 1)[-1]

        system = root.find(f"{{{NS_SSD}}}System")
        if system is None:
            return doc

        elements = system.find(f"{{{NS_SSD}}}Elements")
        if elements is not None:
            for component in elements.findall(f"{{{NS_SSD}}}Component"):
                doc.add_component(component.attrib.get("name", "unnamed"), component.attrib.get("source", ""))

        bindings = system.find(f"{{{NS_SSD}}}ParameterBindings")
        if bindings is not None:
            for binding in bindings.findall(f"{{{NS_SSD}}}ParameterBinding"):
                target = binding.attrib.get("target") or (doc.components[0].name if doc.components else "")

                # Standard-like external form: <ssd:ParameterBinding source="..."/>
                if "source" in binding.attrib:
                    rel_path = binding.attrib.get("source", "")
                    doc.parameter_bindings.append(
                        SsdParameterBinding(
                            target=target,
                            is_inlined=False,
                            parameter_set=None,
                            external_path=rel_path,
                            is_resolved=False,
                        )
                    )
                    continue

                # Standard-like inline form: <ssd:ParameterBinding><ssd:ParameterSet .../></...>
                inline_param_set = next((c for c in binding if localname(c.tag) == "ParameterSet"), None)
                if inline_param_set is not None:
                    xml = ET.tostring(inline_param_set, encoding="unicode")
                    model = self._ssv_codec.parse(xml)
                    doc.parameter_bindings.append(
                        SsdParameterBinding(
                            target=target,
                            is_inlined=True,
                            parameter_set=model,
                            is_resolved=True,
                        )
                    )

        return doc

    def serialize(self, doc: SsdDocument) -> str:
        root = ET.Element(
                f"{{{NS_SSD}}}SystemStructureDescription",
                attrib={"name": doc.name, "version": doc.version},
        )
        root.set("xmlns:ssd", NS_SSD)

        system = ET.SubElement(root, f"{{{NS_SSD}}}System", attrib={"name": "system"})

        elements = ET.SubElement(system, f"{{{NS_SSD}}}Elements")
        for component in doc.components:
            ET.SubElement(
                elements,
                f"{{{NS_SSD}}}Component",
                attrib={"name": component.name, "source": component.source},
            )

        bindings = ET.SubElement(system, f"{{{NS_SSD}}}ParameterBindings")
        for binding in doc.parameter_bindings:
            attrib = {"target": binding.target} if binding.target else {}
            elem = ET.SubElement(bindings, f"{{{NS_SSD}}}ParameterBinding", attrib=attrib)

            if binding.is_inlined and binding.parameter_set is not None:
                xml = self._ssv_codec.serialize(
                    binding.parameter_set,
                    namespace_uri="http://ssp-standard.org/SSP1/SystemStructureDescription",
                )
                elem.append(ET.fromstring(xml))
            elif not binding.is_inlined and binding.external_path:
                rel_path = binding.external_path
                elem.set("source", rel_path)

        return ET.tostring(root, encoding="unicode")
