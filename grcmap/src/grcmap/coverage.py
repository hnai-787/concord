"""The gap-analysis algorithm.

Two independent axes, combined explicitly (never conflated):

1. **Conceptual coverage** -- does the SET of mapped internal controls,
   by relationship alone, fully or partially cover a requirement?
   - `equal`/`equivalent`/`superset` on any single mapping -> full
     (that one control's relationship to the requirement is already
     complete; if several independent mappings each individually claim
     full coverage, only ONE of them needs to actually be implemented).
   - `subset`/`intersects` only -> partial, UNLESS an explicit,
     reviewed `CoverageAssertion` states that a specific SET of these
     controls TOGETHER fully covers the requirement (never inferred
     automatically by summing fractions -- see models.py / README.md).
   - no mapping at all -> GAP, full stop; conceptual coverage doesn't apply.

2. **Implementation reality** -- of the controls that actually
   contribute to that conceptual coverage, what is their real,
   evidence-backed implementation state. How multiple contributing
   controls' states are combined depends on WHY they're contributing:

   - Independently-sufficient controls (several unrelated mappings each
     individually claiming full or each individually claiming partial
     coverage) are combined with the BEST state found: any one of them
     being implemented is enough to realize that mapping's own claim.
     Taking the worst here would be wrong -- e.g. one fully-implemented
     `superset` control does not stop being COVERED just because a
     completely unrelated `not_implemented` control also happens to
     `intersect` the same requirement (a real bug caught by this
     project's own gap report: PCI Requirement 3 was showing GAP despite
     a real, implemented, superset-equivalent control, dragged down by
     an unrelated not-yet-implemented one -- see PROJECT_NOTES.md).
   - Controls named in an explicit `CoverageAssertion` (a reviewer's
     claim that this SPECIFIC set jointly and necessarily covers the
     requirement) are combined with the WORST state: the assertion's
     validity depends on every named member actually being done, so if
     any one of them isn't, the joint claim doesn't hold in practice.

`combine_conceptual_and_implementation` is the single function that
merges conceptual coverage with an already-aggregated implementation
state -- test it directly rather than only end-to-end.
"""

from __future__ import annotations

from .models import (
    CoverageAssertion,
    GapStatus,
    ImplementationState,
    Mapping,
    Relationship,
)

_FULL_COVERAGE_RELATIONSHIPS = {Relationship.EQUAL, Relationship.EQUIVALENT, Relationship.SUPERSET}
_PARTIAL_COVERAGE_RELATIONSHIPS = {Relationship.SUBSET, Relationship.INTERSECTS}

# Best-to-worst.
_STATE_RANK = {
    ImplementationState.IMPLEMENTED: 0,
    ImplementationState.ALTERNATIVE: 1,
    ImplementationState.PARTIAL: 2,
    ImplementationState.PLANNED: 3,
    ImplementationState.NOT_IMPLEMENTED: 4,
    ImplementationState.NOT_APPLICABLE: 4,
}


def conceptual_coverage(
    mappings_for_target: list[Mapping],
    assertions_for_target: list[CoverageAssertion],
) -> tuple[str, tuple[str, ...], str]:
    """Returns ("full" | "partial" | "none", contributing_control_ids, aggregation)
    where aggregation is "best" or "worst" -- see module docstring for why
    it differs between independently-sufficient mappings and a reviewed
    collective assertion.

    Both argument lists are expected to already be filtered to one
    (framework, requirement) target by the caller (gaps.py does this),
    but this function re-checks every assertion's own `target_framework`/
    `target_control` against the mappings' target before trusting it --
    found via a real bug where a caller-supplied assertion for a
    DIFFERENT requirement was silently applied because nothing here
    actually verified it belonged to this one.
    """
    full_mappings = [m for m in mappings_for_target if m.relationship in _FULL_COVERAGE_RELATIONSHIPS]
    if full_mappings:
        return "full", tuple(m.source_control for m in full_mappings), "best"

    partial_mappings = [m for m in mappings_for_target if m.relationship in _PARTIAL_COVERAGE_RELATIONSHIPS]
    if partial_mappings:
        contributing = tuple(m.source_control for m in partial_mappings)
        target_framework = partial_mappings[0].target_framework
        target_control = partial_mappings[0].target_control
        for assertion in assertions_for_target:
            if (
                assertion.result == "full"
                and assertion.target_framework == target_framework
                and assertion.target_control == target_control
                and set(assertion.source_controls) >= set(contributing)
            ):
                return "full", assertion.source_controls, "worst"
        return "partial", contributing, "best"

    return "none", (), "best"


def combine_conceptual_and_implementation(conceptual: str, aggregated_state: ImplementationState | None) -> GapStatus:
    if conceptual == "none" or aggregated_state is None:
        return GapStatus.GAP

    if aggregated_state == ImplementationState.NOT_IMPLEMENTED:
        return GapStatus.GAP
    if aggregated_state == ImplementationState.PLANNED:
        return GapStatus.PLANNED

    if conceptual == "full":
        if aggregated_state == ImplementationState.IMPLEMENTED:
            return GapStatus.COVERED
        return GapStatus.PARTIAL  # partial or alternative implementation of a fully-covering mapping

    return GapStatus.PARTIAL  # conceptual == "partial": can never be more than PARTIAL


def aggregate_implementation_state(
    control_ids: tuple[str, ...],
    implementation_by_control: dict[str, ImplementationState],
    aggregation: str,
) -> ImplementationState | None:
    states = [implementation_by_control[cid] for cid in control_ids if cid in implementation_by_control]
    if not states:
        return None
    pick = min if aggregation == "best" else max
    return pick(states, key=lambda s: _STATE_RANK[s])
