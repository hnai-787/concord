"""Build the full gap-analysis report for one framework.

Only LEAF requirements are scored (a requirement with no children --
e.g. NIST subcategories, ISO controls, PCI/SBP top-level requirements in
this v1 catalog which has no sub-requirements yet). Parent rows
(functions, categories, themes) exist for navigation/context but scoring
them directly would double-count their children's results.

WITHDRAWN requirements are also excluded from scoring. NIST's own
official CSF 2.0 dataset keeps 26 old CSF 1.1 subcategory IDs as
`[Withdrawn: Incorporated into ...]` placeholder stubs, to document where
that content moved during the 1.1->2.0 renumbering, rather than reusing
or deleting the ID outright. 132 raw subcategory rows exist in the
downloaded catalog; 132 - 26 withdrawn = 106 currently active ones (see
PROJECT_NOTES.md) -- scoring a withdrawn stub as a real GAP would be
counting a requirement that no longer exists.
"""

from __future__ import annotations

from .coverage import (
    aggregate_implementation_state,
    combine_conceptual_and_implementation,
    conceptual_coverage,
)
from .models import (
    CoverageAssertion,
    FrameworkRequirement,
    GapResult,
    GapStatus,
    Implementation,
    Mapping,
)


def is_withdrawn(requirement: FrameworkRequirement) -> bool:
    return requirement.title.strip().startswith("[Withdrawn")


def leaf_requirements(requirements: list[FrameworkRequirement]) -> list[FrameworkRequirement]:
    parent_ids = {r.parent for r in requirements if r.parent}
    return [r for r in requirements if r.id not in parent_ids and not is_withdrawn(r)]


def analyze_framework(
    framework_id: str,
    requirements: list[FrameworkRequirement],
    mappings: list[Mapping],
    implementations: list[Implementation],
    coverage_assertions: list[CoverageAssertion],
    not_applicable: list[dict],
) -> list[GapResult]:
    implementation_by_control = {impl.control_id: impl.state for impl in implementations}

    not_applicable_by_requirement = {
        (na["framework"], str(na["control"])): na["justification"]
        for na in not_applicable
        if na["framework"] == framework_id
    }

    results: list[GapResult] = []
    for requirement in leaf_requirements(requirements):
        key = (framework_id, requirement.id)
        if key in not_applicable_by_requirement:
            results.append(
                GapResult(
                    framework_id=framework_id,
                    requirement_id=requirement.id,
                    requirement_title=requirement.title,
                    status=GapStatus.NOT_APPLICABLE,
                    justification=not_applicable_by_requirement[key],
                )
            )
            continue

        mappings_for_target = [
            m for m in mappings if m.target_framework == framework_id and m.target_control == requirement.id
        ]
        assertions_for_target = [
            a for a in coverage_assertions if a.target_framework == framework_id and a.target_control == requirement.id
        ]

        conceptual, contributing, aggregation = conceptual_coverage(mappings_for_target, assertions_for_target)
        aggregated_state = aggregate_implementation_state(contributing, implementation_by_control, aggregation)
        status = combine_conceptual_and_implementation(conceptual, aggregated_state)

        results.append(
            GapResult(
                framework_id=framework_id,
                requirement_id=requirement.id,
                requirement_title=requirement.title,
                status=status,
                contributing_controls=contributing,
            )
        )

    return results


def summarize(results: list[GapResult]) -> dict[str, int]:
    counts = dict.fromkeys(GapStatus, 0)
    for r in results:
        counts[r.status] += 1
    return {status.value: count for status, count in counts.items()}
