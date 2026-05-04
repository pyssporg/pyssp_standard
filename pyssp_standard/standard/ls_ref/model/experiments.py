from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LSRefExperimentResource:
    source: str
    type: str | None = None


@dataclass
class LSRefExperiment:
    name: str
    description: str | None = None
    start_time: float | None = None
    stop_time: float | None = None
    tolerance: float | None = None
    step_size: float | None = None
    parameters: LSRefExperimentResource | None = None
    stimuli: LSRefExperimentResource | None = None
    references: LSRefExperimentResource | None = None

    def add_parameters(self, source: str, *, type: str | None = None) -> LSRefExperimentResource:
        resource = LSRefExperimentResource(source=source, type=type)
        self.parameters = resource
        return resource

    def add_stimuli(self, source: str, *, type: str | None = None) -> LSRefExperimentResource:
        resource = LSRefExperimentResource(source=source, type=type)
        self.stimuli = resource
        return resource

    def add_references(self, source: str, *, type: str | None = None) -> LSRefExperimentResource:
        resource = LSRefExperimentResource(source=source, type=type)
        self.references = resource
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
        start_time: float | None = None,
        stop_time: float | None = None,
        tolerance: float | None = None,
        step_size: float | None = None,
    ) -> LSRefExperiment:
        experiment = LSRefExperiment(
            name=name,
            description=description,
            start_time=start_time,
            stop_time=stop_time,
            tolerance=tolerance,
            step_size=step_size,
        )
        self.experiments.append(experiment)
        return experiment
