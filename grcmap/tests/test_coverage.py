from grcmap.coverage import (
    aggregate_implementation_state,
    combine_conceptual_and_implementation,
    conceptual_coverage,
)
from grcmap.models import (
    CoverageAssertion,
    ImplementationState,
    Mapping,
    Rationale,
    Relationship,
)


def _mapping(source, framework, control, relationship):
    return Mapping(
        id=f"map-{source}-{control}", source_control=source, target_framework=framework,
        target_control=control, relationship=relationship, rationale=Rationale.FUNCTIONAL,
    )


# --- combine_conceptual_and_implementation: the exact matrix from the research brief ---

def test_full_and_implemented_is_covered():
    assert combine_conceptual_and_implementation("full", ImplementationState.IMPLEMENTED) == "COVERED"


def test_full_and_partial_is_partial():
    assert combine_conceptual_and_implementation("full", ImplementationState.PARTIAL) == "PARTIAL"


def test_partial_and_implemented_is_partial():
    assert combine_conceptual_and_implementation("partial", ImplementationState.IMPLEMENTED) == "PARTIAL"


def test_no_mapped_implementation_is_gap():
    assert combine_conceptual_and_implementation("full", None) == "GAP"
    assert combine_conceptual_and_implementation("none", None) == "GAP"


def test_not_implemented_is_always_gap_regardless_of_conceptual_coverage():
    assert combine_conceptual_and_implementation("full", ImplementationState.NOT_IMPLEMENTED) == "GAP"
    assert combine_conceptual_and_implementation("partial", ImplementationState.NOT_IMPLEMENTED) == "GAP"


def test_planned_is_planned_regardless_of_conceptual_coverage():
    assert combine_conceptual_and_implementation("full", ImplementationState.PLANNED) == "PLANNED"
    assert combine_conceptual_and_implementation("partial", ImplementationState.PLANNED) == "PLANNED"


# --- conceptual_coverage ---

def test_single_superset_mapping_is_full_coverage():
    mappings = [_mapping("A", "iso27001-2022", "A.5.1", Relationship.SUPERSET)]
    conceptual, contributing, aggregation = conceptual_coverage(mappings, [])
    assert conceptual == "full"
    assert contributing == ("A",)
    assert aggregation == "best"


def test_subset_only_mapping_is_partial_coverage_without_an_assertion():
    mappings = [_mapping("A", "iso27001-2022", "A.5.1", Relationship.SUBSET)]
    conceptual, _contributing, _aggregation = conceptual_coverage(mappings, [])
    assert conceptual == "partial"


def test_intersects_mappings_elevated_to_full_by_a_matching_assertion():
    mappings = [
        _mapping("A", "pci-dss-4.0.1", "10", Relationship.SUBSET),
        _mapping("B", "pci-dss-4.0.1", "10", Relationship.SUBSET),
    ]
    assertions = [
        CoverageAssertion(target_framework="pci-dss-4.0.1", target_control="10", source_controls=("A", "B"), result="full", rationale="test")
    ]
    conceptual, contributing, aggregation = conceptual_coverage(mappings, assertions)
    assert conceptual == "full"
    assert set(contributing) == {"A", "B"}
    assert aggregation == "worst"


def test_assertion_for_a_different_requirement_does_not_apply():
    mappings = [_mapping("A", "pci-dss-4.0.1", "10", Relationship.SUBSET)]
    assertions = [
        CoverageAssertion(target_framework="pci-dss-4.0.1", target_control="11", source_controls=("A",), result="full", rationale="test")
    ]
    conceptual, _, _ = conceptual_coverage(mappings, assertions)
    assert conceptual == "partial"


def test_no_mapping_at_all_is_none():
    conceptual, contributing, _ = conceptual_coverage([], [])
    assert conceptual == "none"
    assert contributing == ()


# --- aggregate_implementation_state ---

def test_best_aggregation_picks_the_most_implemented_state():
    states = {"A": ImplementationState.NOT_IMPLEMENTED, "B": ImplementationState.IMPLEMENTED}
    result = aggregate_implementation_state(("A", "B"), states, "best")
    assert result == ImplementationState.IMPLEMENTED


def test_worst_aggregation_picks_the_least_implemented_state():
    states = {"A": ImplementationState.NOT_IMPLEMENTED, "B": ImplementationState.IMPLEMENTED}
    result = aggregate_implementation_state(("A", "B"), states, "worst")
    assert result == ImplementationState.NOT_IMPLEMENTED


def test_independent_partial_mappings_do_not_drag_down_an_unrelated_implemented_full_mapping():
    """Regression test for a real bug found while building this project:
    PCI Requirement 3 showed GAP because an unrelated not_implemented
    `intersects` control was being combined via worst-case with an
    entirely independent, actually-implemented `superset`-equivalent
    control. Independent full-coverage mappings must be judged on their
    own -- any ONE of them being implemented is sufficient.
    """
    full_mapping = [_mapping("GOOD", "iso27001-2022", "A.8.24", Relationship.SUPERSET)]
    conceptual, contributing, aggregation = conceptual_coverage(full_mapping, [])
    states = {"GOOD": ImplementationState.IMPLEMENTED, "UNRELATED_BAD": ImplementationState.NOT_IMPLEMENTED}
    aggregated = aggregate_implementation_state(contributing, states, aggregation)
    assert combine_conceptual_and_implementation(conceptual, aggregated) == "COVERED"
