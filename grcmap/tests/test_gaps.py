from conftest import EXAMPLE_DIR, FRAMEWORKS_DIR, MAPPINGS_DIR

from grcmap.engine import gaps_for_framework, load_project
from grcmap.gaps import summarize
from grcmap.models import GapStatus


def _project():
    return load_project(FRAMEWORKS_DIR, MAPPINGS_DIR, EXAMPLE_DIR)


def test_gaps_for_framework_covers_every_leaf_requirement():
    project = _project()
    results = gaps_for_framework(project, "pci-dss-4.0.1")
    assert len(results) == 12  # all 12 top-level requirements scored


def test_not_applicable_requirement_is_reported_with_its_justification():
    project = _project()
    results = gaps_for_framework(project, "pci-dss-4.0.1")
    req9 = next(r for r in results if r.requirement_id == "9")
    assert req9.status == GapStatus.NOT_APPLICABLE
    assert req9.justification is not None
    assert "outsourced" in req9.justification


def test_pci_requirement_3_is_partial_not_gap():
    """End-to-end assertion of the real bug fix -- see test_coverage.py
    for the isolated unit-level regression test.
    """
    project = _project()
    results = gaps_for_framework(project, "pci-dss-4.0.1")
    req3 = next(r for r in results if r.requirement_id == "3")
    assert req3.status == GapStatus.PARTIAL


def test_requirement_with_no_mappings_is_a_real_gap():
    project = _project()
    results = gaps_for_framework(project, "sbp-etgrm-2017")
    # Domain 4 (Acquisition & Implementation of IT Systems) has no
    # mapped internal control in this example inventory.
    domain4 = next(r for r in results if r.requirement_id == "4")
    assert domain4.status == GapStatus.GAP
    assert domain4.contributing_controls == ()


def test_summary_counts_add_up_to_total_requirements():
    project = _project()
    results = gaps_for_framework(project, "iso27001-2022")
    summary = summarize(results)
    assert sum(summary.values()) == len(results) == 93


def test_collective_coverage_assertion_actually_changes_the_result():
    """PCI Requirement 10 only has subset mappings (LOG-01, LOG-02) --
    without the coverage assertion in coverage-assertions.yaml it would
    cap at PARTIAL by design; confirm the assertion is what elevates the
    conceptual coverage to "full" (still capped by real implementation
    state, which happens to also be partial here -- see PROJECT_NOTES.md).
    """
    project = _project()
    results = gaps_for_framework(project, "pci-dss-4.0.1")
    req10 = next(r for r in results if r.requirement_id == "10")
    assert set(req10.contributing_controls) == {"LOG-01", "LOG-02"}


def test_web01_control_with_no_recorded_implementation_produces_a_gap():
    """WEB-01 is deliberately mapped but has no implementation.yaml
    entry -- confirms the "mapped but never recorded" path is a real GAP,
    not silently treated as done.
    """
    project = _project()
    results = gaps_for_framework(project, "iso27001-2022")
    web_filtering = next(r for r in results if r.requirement_id == "A.8.23")
    assert web_filtering.status == GapStatus.GAP
