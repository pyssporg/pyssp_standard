from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LSRefExperimentResource:
    source: str
    type: str | None = None
    mapping: str | None = None
    match_by: str | None = None
    signals: list[str] = field(default_factory=list)


@dataclass
class LSRefExperiment:
    name: str
    description: str | None = None
    target: str | None = None
    start_time: float | None = None
    stop_time: float | None = None
    tolerance: float | None = None
    step_size: float | None = None
    parameters: list[LSRefExperimentResource] = field(default_factory=list)
    stimuli: list[LSRefExperimentResource] = field(default_factory=list)
    references: list[LSRefExperimentResource] = field(default_factory=list)

    def add_parameters(
        self,
        source: str,
        *,
        type: str | None = None,
        mapping: str | None = None,
    ) -> LSRefExperimentResource:
        resource = LSRefExperimentResource(source=source, type=type, mapping=mapping)
        self.parameters.append(resource)
        return resource

    def add_stimuli(
        self,
        source: str,
        *,
        type: str | None = None,
        mapping: str | None = None,
        match_by: str | None = None,
    ) -> LSRefExperimentResource:
        resource = LSRefExperimentResource(
            source=source,
            type=type,
            mapping=mapping,
            match_by=match_by,
        )
        self.stimuli.append(resource)
        return resource

    def add_references(
        self,
        source: str,
        *,
        type: str | None = None,
        mapping: str | None = None,
        match_by: str | None = None,
        signals: list[str] | None = None,
    ) -> LSRefExperimentResource:
        resource = LSRefExperimentResource(
            source=source,
            type=type,
            mapping=mapping,
            match_by=match_by,
            signals=list(signals or []),
        )
        self.references.append(resource)
        return resource


@dataclass
class LSRefExperimentsDocument:
    name: str
    description: str | None = None
    experiments: list[LSRefExperiment] = field(default_factory=list)

    def add_experiment(
        self,
        name: str,
        *,
        description: str | None = None,
        target: str | None = None,
        start_time: float | None = None,
        stop_time: float | None = None,
        tolerance: float | None = None,
        step_size: float | None = None,
    ) -> LSRefExperiment:
        experiment = LSRefExperiment(
            name=name,
            description=description,
            target=target,
            start_time=start_time,
            stop_time=stop_time,
            tolerance=tolerance,
            step_size=step_size,
        )
        self.experiments.append(experiment)
        return experiment
