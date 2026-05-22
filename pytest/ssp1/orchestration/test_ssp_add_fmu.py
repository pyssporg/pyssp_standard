from __future__ import annotations

import shutil
import zipfile

import pytest

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


def test_add_fmu_accepts_directory_path(fmu_directory_fixture, tmp_path):
    ssp_path = tmp_path / "dir_fmu.ssp"
    with SSP(ssp_path, mode="w") as ssp:
        resource_name = ssp.add_fmu("plant", fmu_directory_fixture, expose_system_connectors=True)
    assert resource_name == "0001_ECS_HW.fmu"
    with SSP(ssp_path, mode="r") as ssp:
        assert "0001_ECS_HW.fmu" in ssp.resources
        with ssp.system_structure() as ssd:
            component = next(e for e in ssd.xml.system.elements if e.name == "plant")
            assert component.source == "resources/0001_ECS_HW.fmu"


def test_add_fmu_directory_missing_model_description_raises(tmp_path):
    empty_dir = tmp_path / "bad_fmu"
    empty_dir.mkdir()
    ssp_path = tmp_path / "bad.ssp"
    with SSP(ssp_path, mode="w") as ssp:
        with pytest.raises(FileNotFoundError, match="modelDescription.xml"):
            ssp.add_fmu("plant", empty_dir)


def test_add_fmu_directory_is_packed_as_nested_fmu_on_archive_commit(fmu_directory_fixture, tmp_path):
    ssp_path = tmp_path / "dir_copy_test.ssp"
    with SSP(ssp_path, mode="w") as ssp:
        resource_name = ssp.add_fmu("plant", fmu_directory_fixture)
    assert resource_name == "0001_ECS_HW.fmu"

    with zipfile.ZipFile(ssp_path, "r") as ssp_archive:
        names = set(ssp_archive.namelist())
        nested_fmu = ssp_archive.read("resources/0001_ECS_HW.fmu")

    assert "resources/0001_ECS_HW.fmu" in names
    assert "resources/0001_ECS_HW.fmu/modelDescription.xml" not in names

    nested_fmu_path = tmp_path / "0001_ECS_HW.fmu"
    nested_fmu_path.write_bytes(nested_fmu)
    with zipfile.ZipFile(nested_fmu_path, "r") as fmu_archive:
        fmu_names = set(fmu_archive.namelist())

    assert "modelDescription.xml" in fmu_names
    assert any(n.startswith("binaries/") for n in fmu_names)


def test_add_fmu_extensionless_directory_is_stored_as_compressed_fmu(fmu_directory_fixture, tmp_path):
    fmu_dir = tmp_path / "directory"
    shutil.copytree(fmu_directory_fixture, fmu_dir)
    ssp_path = tmp_path / "extensionless_directory.ssp"

    with SSP(ssp_path, mode="w") as ssp:
        resource_name = ssp.add_fmu("plant", fmu_dir)

    assert resource_name == "directory.fmu"

    with zipfile.ZipFile(ssp_path, "r") as ssp_archive:
        ssp_names = set(ssp_archive.namelist())
        nested_fmu = ssp_archive.read("resources/directory.fmu")

    assert "resources/directory.fmu" in ssp_names
    assert "resources/directory/modelDescription.xml" not in ssp_names

    nested_fmu_path = tmp_path / "directory.fmu"
    nested_fmu_path.write_bytes(nested_fmu)
    with zipfile.ZipFile(nested_fmu_path, "r") as fmu_archive:
        fmu_names = set(fmu_archive.namelist())

    assert "modelDescription.xml" in fmu_names


def test_add_fmu_directory_returns_string(fmu_directory_fixture, tmp_path):
    ssp_path = tmp_path / "ret_type.ssp"
    with SSP(ssp_path, mode="w") as ssp:
        resource_name = ssp.add_fmu("plant", fmu_directory_fixture)
    assert isinstance(resource_name, str)


def test_add_fmu_directory_custom_resource_name(fmu_directory_fixture, tmp_path):
    ssp_path = tmp_path / "custom_res.ssp"
    with SSP(ssp_path, mode="w") as ssp:
        resource_name = ssp.add_fmu("plant", fmu_directory_fixture, resource_name="custom/my_fmu_dir")
    assert resource_name == "custom/my_fmu_dir.fmu"
    with zipfile.ZipFile(ssp_path, "r") as archive:
        names = set(archive.namelist())

    assert "resources/custom/my_fmu_dir.fmu" in names
    assert "resources/custom/my_fmu_dir.fmu/modelDescription.xml" not in names
