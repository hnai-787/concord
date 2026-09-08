"""grcmap CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import loader
from .engine import (
    coverage_for_control,
    gaps_for_framework,
    load_project,
    validate_project,
)
from .gaps import leaf_requirements
from .report import gap_results_to_json, gap_results_to_markdown
from .validator import ValidationError

DEFAULT_FRAMEWORKS_DIR = Path(__file__).resolve().parents[2] / "frameworks"
DEFAULT_MAPPINGS_DIR = Path(__file__).resolve().parents[2] / "mappings"


def _load(args) -> object:
    return load_project(DEFAULT_FRAMEWORKS_DIR, DEFAULT_MAPPINGS_DIR, args.example_dir)


def _cmd_frameworks_list(args: argparse.Namespace) -> int:
    frameworks = loader.load_frameworks_dir(DEFAULT_FRAMEWORKS_DIR)
    for fid, (metadata, requirements) in sorted(frameworks.items()):
        leaf_count = len(leaf_requirements(requirements))
        print(f"{fid}: {metadata['title']} (v{metadata['version']}) -- {leaf_count} scoreable leaf requirements")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    project = _load(args)
    try:
        validate_project(project)
    except ValidationError as exc:
        print(f"INVALID:\n{exc}", file=sys.stderr)
        return 1
    print(f"OK: {len(project.controls)} controls, {len(project.mappings)} mappings, all references resolve.")
    return 0


def _cmd_gaps(args: argparse.Namespace) -> int:
    project = _load(args)
    validate_project(project)
    results = gaps_for_framework(project, args.framework)

    if args.format == "json":
        print(gap_results_to_json(args.framework, results))
    else:
        title = project.frameworks[args.framework][0]["title"]
        print(gap_results_to_markdown(args.framework, title, results))
    return 0


def _cmd_coverage(args: argparse.Namespace) -> int:
    project = _load(args)
    mappings = coverage_for_control(project, args.control_id)
    if not mappings:
        print(f"No mappings found for control '{args.control_id}'.")
        return 1

    control = next((c for c in project.controls if c.id == args.control_id), None)
    impl = next((i for i in project.implementations if i.control_id == args.control_id), None)

    print(f"{args.control_id} -- {control.title if control else '(unknown control)'}")
    print(f"Implementation: {impl.state.value.upper() if impl else 'NOT RECORDED'}")
    print("Mapped requirements:")
    for m in sorted(mappings, key=lambda m: (m.target_framework, m.target_control)):
        print(f"  {m.target_framework:20s} {m.target_control:10s} {m.relationship.value.upper()}")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    project = _load(args)
    validate_project(project)

    outputs = []
    for framework_id in sorted(project.frameworks):
        results = gaps_for_framework(project, framework_id)
        if args.format == "json":
            outputs.append(gap_results_to_json(framework_id, results))
        else:
            title = project.frameworks[framework_id][0]["title"]
            outputs.append(gap_results_to_markdown(framework_id, title, results))

    separator = "\n\n---\n\n" if args.format == "markdown" else "\n"
    output = separator.join(outputs)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"wrote {args.output}")
    else:
        print(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="grcmap")
    parser.add_argument(
        "--example-dir",
        default=str(Path(__file__).resolve().parents[2] / "examples" / "meridian-bank"),
        help="organization inventory directory (default: examples/meridian-bank)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("frameworks-list", help="list loaded framework catalogs")
    p_list.set_defaults(func=_cmd_frameworks_list)

    p_validate = sub.add_parser("validate", help="validate an organization's inventory and mappings")
    p_validate.set_defaults(func=_cmd_validate)

    p_gaps = sub.add_parser("gaps", help="gap analysis for one framework")
    p_gaps.add_argument("--framework", required=True)
    p_gaps.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p_gaps.set_defaults(func=_cmd_gaps)

    p_coverage = sub.add_parser("coverage", help="show a single internal control's mapped coverage")
    p_coverage.add_argument("control_id")
    p_coverage.set_defaults(func=_cmd_coverage)

    p_report = sub.add_parser("report", help="gap analysis for every loaded framework")
    p_report.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p_report.add_argument("--output", "-o")
    p_report.set_defaults(func=_cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
