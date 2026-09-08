"""Load framework catalogs, an organization's control inventory, and
cross-framework mappings from YAML.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import (
    CoverageAssertion,
    FrameworkRequirement,
    Implementation,
    ImplementationState,
    InternalControl,
    Mapping,
    Rationale,
    Relationship,
)


def _read_yaml(path: str | Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_framework(path: str | Path) -> tuple[dict, list[FrameworkRequirement]]:
    data = _read_yaml(path)
    framework_id = data["id"]
    requirements = [
        FrameworkRequirement(
            framework_id=framework_id,
            id=str(r["id"]),
            level=r["level"],
            parent=r.get("parent"),
            title=r["title"],
            description=r.get("description"),
        )
        for r in data["requirements"]
    ]
    metadata = {k: v for k, v in data.items() if k != "requirements"}
    return metadata, requirements


def load_frameworks_dir(directory: str | Path) -> dict[str, tuple[dict, list[FrameworkRequirement]]]:
    directory = Path(directory)
    result = {}
    for path in sorted(directory.glob("*.yaml")):
        metadata, requirements = load_framework(path)
        result[metadata["id"]] = (metadata, requirements)
    return result


def load_organization_controls(path: str | Path) -> tuple[dict, list[InternalControl]]:
    data = _read_yaml(path)
    controls = [InternalControl(id=c["id"], title=c["title"], owner=c.get("owner")) for c in data["controls"]]
    return data["organization"], controls


def load_implementations(path: str | Path) -> list[Implementation]:
    data = _read_yaml(path)
    result = []
    for item in data["implementations"]:
        result.append(
            Implementation(
                control_id=item["control"],
                state=ImplementationState(item["state"]),
                evidence=tuple(item.get("evidence", [])),
                notes=item.get("notes"),
                justification=item.get("justification"),
            )
        )
    return result


def load_mappings(path: str | Path) -> list[Mapping]:
    data = _read_yaml(path)
    result = []
    for item in data.get("mappings", []):
        target = item["target"]
        result.append(
            Mapping(
                id=item["id"],
                source_control=item["source"],
                target_framework=target["framework"],
                target_control=str(target["control"]),
                relationship=Relationship(item["relationship"]),
                rationale=Rationale(item["rationale"]),
                evidence=tuple(item.get("evidence", [])),
                reviewed_by=item.get("reviewed_by"),
                reviewed_at=str(item.get("reviewed_at")) if item.get("reviewed_at") else None,
                notes=item.get("notes"),
            )
        )
    return result


def load_mappings_dir(directory: str | Path) -> list[Mapping]:
    directory = Path(directory)
    result: list[Mapping] = []
    for path in sorted(directory.glob("*.yaml")):
        result.extend(load_mappings(path))
    return result


def load_coverage_assertions(path: str | Path) -> list[CoverageAssertion]:
    if not Path(path).exists():
        return []
    data = _read_yaml(path)
    result = []
    for item in data.get("coverage_assertions", []):
        target = item["target"]
        result.append(
            CoverageAssertion(
                target_framework=target["framework"],
                target_control=str(target["control"]),
                source_controls=tuple(item["sources"]),
                result=item["result"],
                rationale=item.get("rationale", ""),
                evidence=tuple(item.get("evidence", [])),
            )
        )
    return result


def load_not_applicable(path: str | Path) -> list[dict]:
    if not Path(path).exists():
        return []
    data = _read_yaml(path)
    return data.get("not_applicable", [])
