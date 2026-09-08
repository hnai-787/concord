from conftest import FRAMEWORKS_DIR

from grcmap import loader


def _load(name):
    _, requirements = loader.load_framework(FRAMEWORKS_DIR / name)
    return requirements


def test_iso27001_has_93_controls_across_4_themes():
    reqs = _load("iso27001-2022.yaml")
    assert len(reqs) == 93
    themes = {r.parent for r in reqs}
    assert themes == {"organizational", "people", "physical", "technological"}

    by_theme = {}
    for r in reqs:
        by_theme.setdefault(r.parent, 0)
        by_theme[r.parent] += 1
    assert by_theme["organizational"] == 37
    assert by_theme["people"] == 8
    assert by_theme["physical"] == 14
    assert by_theme["technological"] == 34


def test_iso27001_control_ids_are_well_formed_and_unique():
    reqs = _load("iso27001-2022.yaml")
    ids = [r.id for r in reqs]
    assert len(ids) == len(set(ids))
    assert all(r.id.startswith("A.5") or r.id.startswith("A.6") or r.id.startswith("A.7") or r.id.startswith("A.8") for r in reqs)


def test_pci_dss_has_12_top_level_requirements():
    reqs = _load("pci-dss-4.0.1.yaml")
    assert len(reqs) == 12
    assert {r.id for r in reqs} == {str(i) for i in range(1, 13)}


def test_pci_dss_catalog_version_is_4_0_1():
    metadata, _ = loader.load_framework(FRAMEWORKS_DIR / "pci-dss-4.0.1.yaml")
    assert metadata["version"] == "4.0.1"


def test_nist_csf_has_6_functions_22_categories_and_real_subcategory_count():
    from grcmap.gaps import is_withdrawn

    reqs = _load("nist-csf-2.0.yaml")
    functions = [r for r in reqs if r.level == "function"]
    categories = [r for r in reqs if r.level == "category"]
    subcategories = [r for r in reqs if r.level == "subcategory"]

    assert len(functions) == 6
    assert {r.id for r in functions} == {"GV", "ID", "PR", "DE", "RS", "RC"}
    assert len(categories) == 22

    # This project's catalog was built by parsing NIST's own official CPRT
    # export directly (see PROJECT_NOTES.md). The raw dataset has 132
    # subcategory ID rows -- but 26 of those are `[Withdrawn: ...]`
    # placeholder stubs NIST kept to document the CSF 1.1 -> 2.0
    # renumbering, not real active requirements. 132 - 26 = 106 active
    # subcategories, which is the commonly-cited figure -- both numbers
    # are correct, they're just counting different things.
    assert len(subcategories) == 132
    withdrawn = [r for r in subcategories if is_withdrawn(r)]
    assert len(withdrawn) == 26
    active = [r for r in subcategories if not is_withdrawn(r)]
    assert len(active) == 106


def test_nist_csf_govern_function_exists_and_is_new_relative_to_1_1():
    reqs = _load("nist-csf-2.0.yaml")
    govern = next(r for r in reqs if r.id == "GV")
    assert govern.level == "function"
    govern_categories = [r for r in reqs if r.parent == "GV"]
    assert len(govern_categories) == 6


def test_sbp_etgrm_has_6_domains():
    reqs = _load("sbp-etgrm-2017.yaml")
    assert len(reqs) == 6
    titles = {r.title for r in reqs}
    assert "Business Continuity and Disaster Recovery" in titles


def test_every_framework_requirement_id_is_unique_within_its_framework():
    for name in ("iso27001-2022.yaml", "pci-dss-4.0.1.yaml", "nist-csf-2.0.yaml", "sbp-etgrm-2017.yaml"):
        reqs = _load(name)
        ids = [r.id for r in reqs]
        assert len(ids) == len(set(ids)), f"duplicate requirement ids in {name}"
