"""Core data model.

Four concepts kept strictly separate throughout this codebase (the
central architectural rule from the research this was built from):

    mapping relationship != implementation status != risk priority != compliance determination

A `Relationship` describes a conceptual relationship between an internal
control and an external framework requirement (does it fully cover it,
partially, not at all) -- a property of the MAPPING, decided once by a
reviewer. An `ImplementationState` describes whether the organization
has actually done the control -- a property of the ORGANIZATION, that
changes over time independently of the mapping. `GapStatus` is computed
by combining both (see coverage.py). None of these ever produce a
"certified compliant" claim -- see report.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Relationship(str, Enum):
    EQUAL = "equal"
    EQUIVALENT = "equivalent"
    SUBSET = "subset"
    SUPERSET = "superset"
    INTERSECTS = "intersects"
    NO_RELATIONSHIP = "no_relationship"


class Rationale(str, Enum):
    SYNTACTIC = "syntactic"
    SEMANTIC = "semantic"
    FUNCTIONAL = "functional"


class ImplementationState(str, Enum):
    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    PLANNED = "planned"
    ALTERNATIVE = "alternative"
    NOT_IMPLEMENTED = "not_implemented"
    NOT_APPLICABLE = "not_applicable"


class GapStatus(str, Enum):
    COVERED = "COVERED"
    PARTIAL = "PARTIAL"
    PLANNED = "PLANNED"
    GAP = "GAP"
    NOT_APPLICABLE = "NOT_APPLICABLE"


_INVERSE = {
    Relationship.EQUAL: Relationship.EQUAL,
    Relationship.EQUIVALENT: Relationship.EQUIVALENT,
    Relationship.SUBSET: Relationship.SUPERSET,
    Relationship.SUPERSET: Relationship.SUBSET,
    Relationship.INTERSECTS: Relationship.INTERSECTS,
    Relationship.NO_RELATIONSHIP: Relationship.NO_RELATIONSHIP,
}


def invert_relationship(relationship: Relationship) -> Relationship:
    """The relationship as seen from the other direction (NIST IR 8477
    set-theory semantics): if A is a superset of B, then B is a subset
    of A. Used only for consistency testing here -- this project stores
    one directed edge per mapping and does not persist reciprocal edges.
    """
    return _INVERSE[relationship]


@dataclass(frozen=True)
class FrameworkRequirement:
    framework_id: str
    id: str
    level: str
    parent: str | None
    title: str
    description: str | None = None


@dataclass(frozen=True)
class InternalControl:
    id: str
    title: str
    owner: str | None = None


@dataclass(frozen=True)
class Implementation:
    control_id: str
    state: ImplementationState
    evidence: tuple[str, ...] = field(default_factory=tuple)
    notes: str | None = None
    justification: str | None = None  # required when state == NOT_APPLICABLE


@dataclass(frozen=True)
class Mapping:
    id: str
    source_control: str
    target_framework: str
    target_control: str
    relationship: Relationship
    rationale: Rationale
    evidence: tuple[str, ...] = field(default_factory=tuple)
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class CoverageAssertion:
    target_framework: str
    target_control: str
    source_controls: tuple[str, ...]
    result: str  # "full" | "partial"
    rationale: str
    evidence: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class GapResult:
    framework_id: str
    requirement_id: str
    requirement_title: str
    status: GapStatus
    contributing_controls: tuple[str, ...] = field(default_factory=tuple)
    justification: str | None = None
