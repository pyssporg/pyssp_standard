from pathlib import Path
from xml.etree import ElementTree as ET

from .parameter_storage import ExternalParameterSetStorage, InlineParameterSetStorage
from .ssd_model import SsdDocument, SsdParameterBinding


NS_SSD = "http://ssp-standard.org/SSP1/SystemStructureDescription"


class SsdBindingCodec:
    """Handwritten SSD codec with storage strategy for inline/external parameter sets."""

    def __init__(self):
        self._inline = InlineParameterSetStorage()
        self._external = ExternalParameterSetStorage()

    def parse(self, xml_text: str, *, context_path: Path) -> SsdDocument:
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
                    model = self._external.load(context_path=context_path, encoded_value=rel_path)
                    doc.parameter_bindings.append(
                        SsdParameterBinding(
                            target=target,
                            mode="external",
                            parameter_set=model,
                            external_path=rel_path,
                        )
                    )
                    continue

                # Standard-like inline form: <ssd:ParameterBinding><ssd:ParameterSet .../></...>
                inline_param_set = next((c for c in binding if localname(c.tag) == "ParameterSet"), None)
                if inline_param_set is not None:
                    xml = ET.tostring(inline_param_set, encoding="unicode")
                    model = self._inline.load(context_path=context_path, encoded_value=xml)
                    doc.parameter_bindings.append(
                        SsdParameterBinding(target=target, mode="inline", parameter_set=model)
                    )

        return doc

    def serialize(self, doc: SsdDocument, *, context_path: Path) -> str:
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

            if binding.mode == "inline" and binding.parameter_set is not None:
                xml = self._inline.save(context_path=context_path, model=binding.parameter_set)
                elem.append(ET.fromstring(xml))
            elif binding.mode == "external" and binding.parameter_set is not None and binding.external_path:
                rel_path = self._external.save(
                    context_path=context_path,
                    model=binding.parameter_set,
                    encoded_value=binding.external_path,
                )
                elem.set("source", rel_path)

        return ET.tostring(root, encoding="unicode")
