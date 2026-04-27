from __future__ import annotations

from pyssp_standard.ssp import SSP


def test_add_fmu_creates_component_and_top_level_connectors(fmu_archive_fixture, tmp_path):
    ssp_path = tmp_path / "single_component.ssp"

    with SSP(ssp_path, mode="w") as ssp:
        resource_name = ssp.add_fmu("plant", fmu_archive_fixture, expose_system_connectors=True)

    assert resource_name == "0001_ECS_HW.fmu"

    with SSP(ssp_path, mode="r") as ssp:
        assert "0001_ECS_HW.fmu" in ssp.resources
        with ssp.system_structure() as ssd:
            assert ssd.xml.system is not None
            component = next(element for element in ssd.xml.system.elements if element.name == "plant")
            assert component.source == "resources/0001_ECS_HW.fmu"
            assert len(component.connectors) > 0
            assert any(connector.kind == "input" for connector in component.connectors)
            assert any(connector.kind == "output" for connector in component.connectors)
            assert any(connection.start_element == "plant" for connection in ssd.xml.system.connections)
            assert any(connection.end_element == "plant" for connection in ssd.xml.system.connections)


def test_add_fmu_without_system_connector_exposure_only_adds_component(fmu_archive_fixture, tmp_path):
    ssp_path = tmp_path / "single_component_internal_only.ssp"

    with SSP(ssp_path, mode="w") as ssp:
        ssp.add_fmu("plant", fmu_archive_fixture)

    with SSP(ssp_path, mode="r") as ssp:
        with ssp.system_structure() as ssd:
            assert ssd.xml.system is not None
            assert len(ssd.xml.system.elements) == 1
            assert ssd.xml.system.connectors == []
            assert ssd.xml.system.connections == []
            component = ssd.xml.system.elements[0]
            assert component.name == "plant"
            assert len(component.connectors) > 0


def test_add_fmu_supports_custom_resource_name_and_prefixed_system_connectors(fmu_archive_fixture, tmp_path):
    ssp_path = tmp_path / "single_component_prefixed.ssp"

    with SSP(ssp_path, mode="w") as ssp:
        resource_name = ssp.add_fmu(
            "plant",
            fmu_archive_fixture,
            resource_name="custom/plant.fmu",
            expose_system_connectors=True,
            connector_prefix="plant_",
        )

    assert resource_name == "custom/plant.fmu"

    with SSP(ssp_path, mode="r") as ssp:
        assert "custom/plant.fmu" in ssp.resources
        with ssp.system_structure() as ssd:
            assert ssd.xml.system is not None
            component = next(element for element in ssd.xml.system.elements if element.name == "plant")
            assert component.source == "resources/custom/plant.fmu"
            assert all(connector.name.startswith("plant_") for connector in ssd.xml.system.connectors)
            assert all(
                connection.start_connector.startswith("plant_") or connection.end_connector.startswith("plant_")
                for connection in ssd.xml.system.connections
            )


def test_add_fmu_preserves_component_connector_type_metadata(fmu_archive_fixture, tmp_path):
    ssp_path = tmp_path / "single_component_metadata.ssp"

    with SSP(ssp_path, mode="w") as ssp:
        ssp.add_fmu("plant", fmu_archive_fixture, expose_system_connectors=True)

    with SSP(ssp_path, mode="r") as ssp:
        with ssp.system_structure() as ssd:
            component = next(element for element in ssd.xml.system.elements if element.name == "plant")

            integer_parameter = next(
                connector for connector in component.connectors if connector.name == "AirToL_HEX.looptypRed"
            )
            real_parameter = next(
                connector for connector in component.connectors if connector.name == "AirToL_HEX.Kst"
            )
            mirrored_integer_parameter = next(
                connector for connector in ssd.xml.system.connectors if connector.name == "AirToL_HEX.looptypRed"
            )
            mirrored_real_parameter = next(
                connector for connector in ssd.xml.system.connectors if connector.name == "AirToL_HEX.Kst"
            )

            assert integer_parameter.kind == "parameter"
            assert integer_parameter.type_name == "Integer"
            assert integer_parameter.type_attributes == {}
            assert "start" not in integer_parameter.type_attributes
            assert real_parameter.kind == "parameter"
            assert real_parameter.type_name == "Real"
            assert real_parameter.type_attributes == {}
            assert "start" not in real_parameter.type_attributes
            assert mirrored_integer_parameter.type_attributes == integer_parameter.type_attributes
            assert mirrored_real_parameter.type_attributes == real_parameter.type_attributes
