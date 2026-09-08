"""Load a full project (frameworks + one organization's inventory) and
provide the query operations the CLI exposes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import loader
from .gaps import analyze_framework
from .models import (
    CoverageAssertion,
    FrameworkRequirement,
    Implementation,
    InternalControl,
    Mapping,
)
from .validator import validate_all


@dataclass
class Project:
    organization: dict
    controls: list[InternalControl]
    implementations: list[Implementation]
    mappings: list[Mapping]
    coverage_assertions: list[CoverageAssertion]
    not_applicable: list[dict]
    frameworks: dict[str, tuple[dict, list[FrameworkRequirement]]]


def load_project(
    frameworks_dir: str | Path,
    mappings_dir: str | Path,
    example_dir: str | Path,
) -> Project:
    example_dir = Path(example_dir)
    frameworks = loader.load_frameworks_dir(frameworks_dir)
    organization, controls = loader.load_organization_controls(example_dir / "controls.yaml")
    implementations = loader.load_implementations(example_dir / "implementation.yaml")
    mappings = loader.load_mappings_dir(mappings_dir)
    coverage_assertions = loader.load_coverage_assertions(example_dir / "coverage-assertions.yaml")
    not_applicable = loader.load_not_applicable(example_dir / "not-applicable.yaml")

    return Project(
        organization=organization,
        controls=controls,
        implementations=implementations,
        mappings=mappings,
        coverage_assertions=coverage_assertions,
        not_applicable=not_applicable,
        frameworks=frameworks,
    )


def validate_project(project: Project) -> None:
    validate_all(
        project.controls,
        project.implementations,
        project.mappings,
        project.frameworks,
        project.coverage_assertions,
    )


def gaps_for_framework(project: Project, framework_id: str):
    _, requirements = project.frameworks[framework_id]
    return analyze_framework(
        framework_id,
        requirements,
        project.mappings,
        project.implementations,
        project.coverage_assertions,
        project.not_applicable,
    )


def coverage_for_control(project: Project, control_id: str) -> list[Mapping]:
    return [m for m in project.mappings if m.source_control == control_id]
