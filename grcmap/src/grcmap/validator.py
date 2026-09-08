"""Reference and invariant validation across the loaded model."""

from __future__ import annotations

from .models import (
    CoverageAssertion,
    FrameworkRequirement,
    Implementation,
    ImplementationState,
    InternalControl,
    Mapping,
)


class ValidationError(Exception):
    pass


def validate_all(
    controls: list[InternalControl],
    implementations: list[Implementation],
    mappings: list[Mapping],
    frameworks: dict[str, tuple[dict, list[FrameworkRequirement]]],
    coverage_assertions: list[CoverageAssertion] | None = None,
) -> None:
    errors: list[str] = []
    control_ids = {c.id for c in controls}

    requirement_ids_by_framework: dict[str, set[str]] = {
        fid: {r.id for r in reqs} for fid, (_, reqs) in frameworks.items()
    }

    seen_impl_controls: set[str] = set()
    for impl in implementations:
        if impl.control_id not in control_ids:
            errors.append(f"implementation references unknown control '{impl.control_id}'")
        if impl.control_id in seen_impl_controls:
            errors.append(f"duplicate implementation record for control '{impl.control_id}'")
        seen_impl_controls.add(impl.control_id)

        if impl.state == ImplementationState.NOT_APPLICABLE and not impl.justification:
            errors.append(
                f"control '{impl.control_id}' is marked not_applicable without a justification "
                "(SP 800-63B-4-style discipline applied here too: N/A always needs a reason)"
            )

    seen_mapping_ids: set[str] = set()
    for m in mappings:
        if m.id in seen_mapping_ids:
            errors.append(f"duplicate mapping id '{m.id}'")
        seen_mapping_ids.add(m.id)

        if m.source_control not in control_ids:
            errors.append(f"mapping '{m.id}' references unknown source control '{m.source_control}'")

        if m.target_framework not in requirement_ids_by_framework:
            errors.append(f"mapping '{m.id}' references unknown framework '{m.target_framework}'")
        elif m.target_control not in requirement_ids_by_framework[m.target_framework]:
            errors.append(
                f"mapping '{m.id}' references unknown requirement "
                f"'{m.target_control}' in framework '{m.target_framework}'"
            )

    for assertion in coverage_assertions or []:
        if assertion.target_framework not in requirement_ids_by_framework:
            errors.append(f"coverage assertion references unknown framework '{assertion.target_framework}'")
        elif assertion.target_control not in requirement_ids_by_framework[assertion.target_framework]:
            errors.append(
                f"coverage assertion references unknown requirement "
                f"'{assertion.target_control}' in framework '{assertion.target_framework}'"
            )
        for source in assertion.source_controls:
            if source not in control_ids:
                errors.append(f"coverage assertion references unknown source control '{source}'")

    if errors:
        raise ValidationError("Validation failed:\n  " + "\n  ".join(errors))
