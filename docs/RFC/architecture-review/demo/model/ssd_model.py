from dataclasses import dataclass, field

from .ssv_model import ParameterSet


@dataclass
class SsdComponent:
    name: str
    source: str


@dataclass
class SsdParameterBinding:
    target: str
    is_inlined: bool
    parameter_set: ParameterSet | None = None
    external_path: str | None = None
    is_resolved: bool = False


@dataclass
class SsdDocument:
    name: str
    version: str
    components: list[SsdComponent] = field(default_factory=list)
    parameter_bindings: list[SsdParameterBinding] = field(default_factory=list)

    def add_component(self, name: str, source: str):
        self.components.append(SsdComponent(name=name, source=source))

    def add_parameter_set(
        self,
        *,
        target: str,
        inlined: bool,
        external_path: str | None = None,
        set_name: str | None = None,
        set_version: str = "2.0",
    ) -> SsdParameterBinding:
        """Create or return a parameter binding in inline/external form."""
        existing = next(
            (b for b in self.parameter_bindings if b.target == target and b.is_inlined == inlined),
            None,
        )
        if existing is not None:
            return existing

        if not inlined and not external_path:
            raise ValueError("external_path is required when inlined=False")

        parameter_set = ParameterSet(
            name=set_name or f"{target}_params",
            version=set_version,
        )
        binding = SsdParameterBinding(
            target=target,
            is_inlined=inlined,
            parameter_set=parameter_set,
            external_path=external_path,
            is_resolved=True if inlined else False,
        )
        self.parameter_bindings.append(binding)
        return binding
