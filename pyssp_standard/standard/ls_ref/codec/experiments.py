from __future__ import annotations

from xml.etree import ElementTree as ET

from pyssp_standard.standard.ls_ref.constants import (
    EXPERIMENTS_ROOT_TAG,
    EXPERIMENT_TAG,
    PARAMETERS_TAG,
    REFERENCES_TAG,
    SIGNAL_TAG,
    STIMULI_TAG,
)
from pyssp_standard.standard.ls_ref.model.experiments import (
    LSRefExperiment,
    LSRefExperimentResource,
    LSRefExperimentsDocument,
)


class LSRefExperimentsCodec:
    def parse(self, xml_text: str) -> LSRefExperimentsDocument:
        root = ET.fromstring(xml_text)
        document = LSRefExperimentsDocument(
            name=root.attrib["name"],
            description=root.attrib.get("description"),
        )
        document.experiments = [
            self._parse_experiment(element)
            for element in root.findall(EXPERIMENT_TAG)
        ]
        return document

    def serialize(self, document: LSRefExperimentsDocument) -> str:
        root = ET.Element(EXPERIMENTS_ROOT_TAG)
        root.set("name", document.name)
        if document.description is not None:
            root.set("description", document.description)

        for experiment in document.experiments:
            root.append(self._serialize_experiment(experiment))

        ET.indent(root, space="  ")
        return ET.tostring(root, encoding="unicode", xml_declaration=True)

    def _parse_experiment(self, element: ET.Element) -> LSRefExperiment:
        experiment = LSRefExperiment(
            name=element.attrib["name"],
            description=element.attrib.get("description"),
            target=element.attrib.get("target"),
            start_time=self._parse_float(element.attrib.get("startTime")),
            stop_time=self._parse_float(element.attrib.get("stopTime")),
            tolerance=self._parse_float(element.attrib.get("tolerance")),
            step_size=self._parse_float(element.attrib.get("stepSize")),
        )
        experiment.parameters = [
            self._parse_resource(resource)
            for resource in element.findall(PARAMETERS_TAG)
        ]
        experiment.stimuli = [
            self._parse_resource(resource)
            for resource in element.findall(STIMULI_TAG)
        ]
        experiment.references = [
            self._parse_resource(resource)
            for resource in element.findall(REFERENCES_TAG)
        ]
        return experiment

    def _serialize_experiment(self, experiment: LSRefExperiment) -> ET.Element:
        element = ET.Element(EXPERIMENT_TAG)
        element.set("name", experiment.name)
        if experiment.description is not None:
            element.set("description", experiment.description)
        if experiment.target is not None:
            element.set("target", experiment.target)
        self._set_optional_float(element, "startTime", experiment.start_time)
        self._set_optional_float(element, "stopTime", experiment.stop_time)
        self._set_optional_float(element, "tolerance", experiment.tolerance)
        self._set_optional_float(element, "stepSize", experiment.step_size)

        for resource in experiment.parameters:
            element.append(self._serialize_resource(PARAMETERS_TAG, resource))
        for resource in experiment.stimuli:
            element.append(self._serialize_resource(STIMULI_TAG, resource))
        for resource in experiment.references:
            element.append(self._serialize_resource(REFERENCES_TAG, resource))
        return element

    def _parse_resource(self, element: ET.Element) -> LSRefExperimentResource:
        return LSRefExperimentResource(
            source=element.attrib["source"],
            type=element.attrib.get("type"),
            mapping=element.attrib.get("mapping"),
            match_by=element.attrib.get("matchBy"),
            signals=[
                signal.attrib["name"]
                for signal in element.findall(SIGNAL_TAG)
            ],
        )

    def _serialize_resource(self, tag: str, resource: LSRefExperimentResource) -> ET.Element:
        element = ET.Element(tag)
        if resource.type is not None:
            element.set("type", resource.type)
        element.set("source", resource.source)
        if resource.mapping is not None:
            element.set("mapping", resource.mapping)
        if resource.match_by is not None:
            element.set("matchBy", resource.match_by)
        for signal in resource.signals:
            signal_element = ET.SubElement(element, SIGNAL_TAG)
            signal_element.set("name", signal)
        return element

    def _parse_float(self, value: str | None) -> float | None:
        if value is None:
            return None
        return float(value)

    def _set_optional_float(self, element: ET.Element, attr_name: str, value: float | None) -> None:
        if value is not None:
            element.set(attr_name, str(value))
