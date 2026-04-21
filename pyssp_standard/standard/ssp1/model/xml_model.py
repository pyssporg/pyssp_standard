from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class XmlElementNode:
    local_name: str
    namespace_uri: str | None = None
    attributes: dict[str, str] = field(default_factory=dict)
    children: list["XmlElementNode"] = field(default_factory=list)
    text: str | None = None

    @property
    def qualified_name(self) -> str:
        if self.namespace_uri:
            return f"{{{self.namespace_uri}}}{self.local_name}"
        return self.local_name


@dataclass
class XmlDocumentNode:
    root: XmlElementNode
    namespaces: dict[str, str] = field(default_factory=dict)


@dataclass
class Ssp1SsdDocument(XmlDocumentNode):
    @property
    def name(self) -> str | None:
        return self.root.attributes.get("name")

    @name.setter
    def name(self, value: str | None) -> None:
        self._set_root_attribute("name", value)

    @property
    def version(self) -> str | None:
        return self.root.attributes.get("version")

    @version.setter
    def version(self, value: str | None) -> None:
        self._set_root_attribute("version", value)

    def _set_root_attribute(self, key: str, value: str | None) -> None:
        if value is None:
            self.root.attributes.pop(key, None)
            return
        self.root.attributes[key] = value


@dataclass
class Ssp1SsmDocument(XmlDocumentNode):
    @property
    def version(self) -> str | None:
        return self.root.attributes.get("version")

    @version.setter
    def version(self, value: str | None) -> None:
        if value is None:
            self.root.attributes.pop("version", None)
            return
        self.root.attributes["version"] = value
