from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..model.ssd_model import SsdComponent, SsdDocument, SsdParameterBinding


NS_SSD = "http://ssp-standard.org/SSP1/SystemStructureDescription"

if TYPE_CHECKING:
    from ..generated.ssd_generated_types import SystemStructureDescription


class SsdXsdataMapper:
    """Map xsdata-generated SSD bindings to the compact demo domain model.

    This keeps generated classes internal and preserves a small authoring-facing
    model. The implementation here intentionally covers only the same subset as
    the handwritten demo codec:
    - document name/version
    - top-level system
    - component name/source
    - parameter bindings in inline/external form
    """

    def __init__(self, ssv_codec):
        self._ssv_codec = ssv_codec

    def to_domain(self, generated: "SystemStructureDescription") -> SsdDocument:
        doc = SsdDocument(
            name=generated.name,
            version=generated.version,
        )

        system = generated.system
        if system is None:
            return doc

        elements = getattr(system, "elements", None)
        if elements is not None:
            for component in getattr(elements, "component", []):
                doc.components.append(
                    SsdComponent(
                        name=component.name or "unnamed",
                        source=component.source or "",
                    )
                )

        for binding in self._iter_parameter_bindings(system):
            doc.parameter_bindings.append(self._binding_to_domain(binding, doc))

        return doc

    def from_domain(self, doc: SsdDocument) -> Any:
        generated = self._generated_types()

        elements = generated.Tsystem.Elements(
            component=[
                generated.Tcomponent(name=component.name, source=component.source)
                for component in doc.components
            ]
        )

        bindings = generated.TparameterBindings(
            parameter_binding=[
                self._binding_from_domain(binding, generated)
                for binding in doc.parameter_bindings
            ]
        )

        system = generated.Tsystem(
            name="system",
            elements=elements,
            parameter_bindings=bindings,
        )

        return generated.SystemStructureDescription(
            name=doc.name,
            version=doc.version,
            system=system,
        )

    def _iter_parameter_bindings(self, system: Any) -> list[Any]:
        bindings = getattr(system, "parameter_bindings", None)
        if bindings is None:
            return []
        return list(getattr(bindings, "parameter_binding", []))

    def _binding_to_domain(self, binding: Any, doc: SsdDocument) -> SsdParameterBinding:
        target = getattr(binding, "prefix", "") or (doc.components[0].name if doc.components else "")

        if getattr(binding, "source", None):
            return SsdParameterBinding(
                target=target,
                is_inlined=False,
                parameter_set=None,
                external_path=binding.source,
                is_resolved=False,
            )

        inline_values = getattr(binding, "parameter_values", None)
        if inline_values is not None and getattr(inline_values, "any_element", None):
            xml = self._first_inline_xml(inline_values.any_element[0])
            model = self._ssv_codec.parse(xml)
            return SsdParameterBinding(
                target=target,
                is_inlined=True,
                parameter_set=model,
                is_resolved=True,
            )

        return SsdParameterBinding(target=target, is_inlined=True, parameter_set=None)

    def _binding_from_domain(self, binding: SsdParameterBinding, generated: Any) -> Any:
        attrs: dict[str, Any] = {}
        if binding.target:
            # The SSP1 SSD schema has no dedicated target attribute on ParameterBinding.
            # For the demo skeleton we map the component name into prefix to show where
            # workflow policy would sit when adapting generated classes to a compact API.
            attrs["prefix"] = f"{binding.target}."

        if binding.is_inlined and binding.parameter_set is not None:
            xml = self._ssv_codec.serialize(
                binding.parameter_set,
                namespace_uri=NS_SSD,
            )
            return generated.TparameterBindings.ParameterBinding(
                parameter_values=generated.TparameterBindings.ParameterBinding.ParameterValues(
                    any_element=[self._parse_inline_xml(xml)]
                ),
                **attrs,
            )

        if not binding.is_inlined and binding.external_path:
            return generated.TparameterBindings.ParameterBinding(
                source=binding.external_path,
                **attrs,
            )

        return generated.TparameterBindings.ParameterBinding(**attrs)

    @staticmethod
    def _first_inline_xml(value: Any) -> str:
        if hasattr(value, "tag"):
            from xml.etree import ElementTree as ET

            return ET.tostring(value, encoding="unicode")
        return str(value)

    @staticmethod
    def _parse_inline_xml(xml_text: str) -> Any:
        from xml.etree import ElementTree as ET

        return ET.fromstring(xml_text)

    @staticmethod
    def _generated_types() -> Any:
        from ..generated import ssd_generated_types

        return ssd_generated_types
