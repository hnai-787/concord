import copy

import pytest
from conftest import EXAMPLE_DIR, FRAMEWORKS_DIR, MAPPINGS_DIR

from grcmap import loader
from grcmap.models import (
    CoverageAssertion,
    Implementation,
    ImplementationState,
    Mapping,
    Rationale,
    Relationship,
    invert_relationship,
)
from grcmap.validator import ValidationError, validate_all


@pytest.mark.parametrize(
    "relationship,expected_inverse",
    [
        (Relationship.SUBSET, Relationship.SUPERSET),
        (Relationship.SUPERSET, Relationship.SUBSET),
        (Relationship.EQUAL, Relationship.EQUAL),
        (Relationship.EQUIVALENT, Relationship.EQUIVALENT),
        (Relationship.INTERSECTS, Relationship.INTERSECTS),
        (Relationship.NO_RELATIONSHIP, Relationship.NO_RELATIONSHIP),
    ],
)
def test_relationship_inverse(relationship, expected_inverse):
    assert invert_relationship(relationship) == expected_inverse


def test_relationship_inverse_is_involutive():
    for rel in Relationship:
        assert invert_relationship(invert_relationship(rel)) == rel


def _load_everything():
    frameworks = loader.load_frameworks_dir(FRAMEWORKS_DIR)
    _, controls = loader.load_organization_controls(EXAMPLE_DIR / "controls.yaml")
    implementations = loader.load_implementations(EXAMPLE_DIR / "implementation.yaml")
    mappings = loader.load_mappings_dir(MAPPINGS_DIR)
    assertions = loader.load_coverage_assertions(EXAMPLE_DIR / "coverage-assertions.yaml")
    return frameworks, controls, implementations, mappings, assertions


def test_real_example_project_validates_cleanly():
    frameworks, controls, implementations, mappings, assertions = _load_everything()
    validate_all(controls, implementations, mappings, frameworks, assertions)  # must not raise


def test_validator_rejects_mapping_to_unknown_control():
    frameworks, controls, implementations, mappings, assertions = _load_everything()
    broken = [*mappings, Mapping(
        id="map-bad-001", source_control="NOPE-99", target_framework="iso27001-2022",
        target_control="A.5.1", relationship=Relationship.EQUAL, rationale=Rationale.SEMANTIC,
    )]
    with pytest.raises(ValidationError):
        validate_all(controls, implementations, broken, frameworks, assertions)


def test_validator_rejects_mapping_to_unknown_requirement():
    frameworks, controls, implementations, mappings, assertions = _load_everything()
    broken = [*mappings, Mapping(
        id="map-bad-002", source_control=controls[0].id, target_framework="iso27001-2022",
        target_control="A.99.99", relationship=Relationship.EQUAL, rationale=Rationale.SEMANTIC,
    )]
    with pytest.raises(ValidationError):
        validate_all(controls, implementations, broken, frameworks, assertions)


def test_validator_rejects_not_applicable_implementation_without_justification():
    frameworks, controls, implementations, mappings, assertions = _load_everything()
    broken = [*implementations, Implementation(
        control_id=controls[0].id, state=ImplementationState.NOT_APPLICABLE, justification=None,
    )]
    with pytest.raises(ValidationError):
        validate_all(controls, broken, mappings, frameworks, assertions)


def test_validator_rejects_duplicate_mapping_ids():
    frameworks, controls, implementations, mappings, assertions = _load_everything()
    dup = copy.deepcopy(mappings[0])
    broken = [*mappings, dup]
    with pytest.raises(ValidationError):
        validate_all(controls, implementations, broken, frameworks, assertions)


def test_validator_rejects_coverage_assertion_with_unknown_source():
    frameworks, controls, implementations, mappings, assertions = _load_everything()
    broken = [*assertions, CoverageAssertion(
        target_framework="pci-dss-4.0.1", target_control="10", source_controls=("NOPE-99",),
        result="full", rationale="test",
    )]
    with pytest.raises(ValidationError):
        validate_all(controls, implementations, mappings, frameworks, broken)


def test_no_two_controls_share_the_same_id_in_the_example_inventory():
    _, controls, _, _, _ = _load_everything()
    ids = [c.id for c in controls]
    assert len(ids) == len(set(ids))
