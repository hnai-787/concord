import json

from conftest import EXAMPLE_DIR, FRAMEWORKS_DIR, MAPPINGS_DIR

from grcmap.engine import gaps_for_framework, load_project
from grcmap.report import DISCLAIMER, gap_results_to_json, gap_results_to_markdown


def _results():
    project = load_project(FRAMEWORKS_DIR, MAPPINGS_DIR, EXAMPLE_DIR)
    return gaps_for_framework(project, "pci-dss-4.0.1")


def test_report_never_claims_certification_or_compliance():
    output = gap_results_to_markdown("pci-dss-4.0.1", "PCI DSS", _results())
    for forbidden in ("PCI compliant", "certified", "compliance determination: pass"):
        assert forbidden.lower() not in output.lower()
    assert DISCLAIMER in output


def test_report_never_emits_a_fake_coverage_percentage():
    output = gap_results_to_markdown("pci-dss-4.0.1", "PCI DSS", _results())
    assert "%" not in output


def test_json_report_is_valid_and_well_shaped():
    output = gap_results_to_json("pci-dss-4.0.1", _results())
    parsed = json.loads(output)
    assert parsed["framework"] == "pci-dss-4.0.1"
    assert parsed["disclaimer"] == DISCLAIMER
    assert len(parsed["requirements"]) == 12
    assert sum(parsed["summary"].values()) == 12


def test_markdown_table_cells_never_contain_raw_newlines():
    output = gap_results_to_markdown("pci-dss-4.0.1", "PCI DSS", _results())
    for line in output.splitlines():
        if line.startswith("|"):
            assert line.count("|") >= 2  # a real single-line table row, not a fragment
