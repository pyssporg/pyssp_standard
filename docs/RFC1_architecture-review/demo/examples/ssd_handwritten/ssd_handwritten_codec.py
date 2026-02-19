from xml.etree import ElementTree as ET

from .ssd_model import SsdConnection, SsdDocument


NS_SSD = "http://ssp-standard.org/SSP1/SystemStructureDescription"


class SsdHandwrittenCodec:
    """Handwritten codec path for SSD (no generated intermediate types)."""

    def parse(self, xml_text: str) -> SsdDocument:
        root = ET.fromstring(xml_text)
        model = SsdDocument(
            name=root.attrib.get("name", "unnamed"),
            version=root.attrib.get("version", "1.0"),
        )

        system = root.find(f"{{{NS_SSD}}}System")
        if system is None:
            return model

        elements = system.find(f"{{{NS_SSD}}}Elements")
        if elements is not None:
            for comp in elements.findall(f"{{{NS_SSD}}}Component"):
                model.add_component(
                    name=comp.attrib.get("name", "unnamed"),
                    source=comp.attrib.get("source", ""),
                )

        connections = system.find(f"{{{NS_SSD}}}Connections")
        if connections is not None:
            for con in connections.findall(f"{{{NS_SSD}}}Connection"):
                model.connections.append(
                    SsdConnection(
                        start_element=con.attrib.get("startElement", ""),
                        start_connector=con.attrib.get("startConnector", ""),
                        end_element=con.attrib.get("endElement", ""),
                        end_connector=con.attrib.get("endConnector", ""),
                    )
                )

        return model

    def serialize(self, model: SsdDocument) -> str:
        root = ET.Element(
            f"{{{NS_SSD}}}SystemStructureDescription",
            attrib={"name": model.name, "version": model.version},
        )
        root.set("xmlns:ssd", NS_SSD)

        system = ET.SubElement(root, f"{{{NS_SSD}}}System", attrib={"name": "system"})

        elements = ET.SubElement(system, f"{{{NS_SSD}}}Elements")
        for comp in model.components:
            ET.SubElement(
                elements,
                f"{{{NS_SSD}}}Component",
                attrib={"name": comp.name, "source": comp.source},
            )

        if model.connections:
            connections = ET.SubElement(system, f"{{{NS_SSD}}}Connections")
            for con in model.connections:
                ET.SubElement(
                    connections,
                    f"{{{NS_SSD}}}Connection",
                    attrib={
                        "startElement": con.start_element,
                        "startConnector": con.start_connector,
                        "endElement": con.end_element,
                        "endConnector": con.end_connector,
                    },
                )

        return ET.tostring(root, encoding="unicode")
