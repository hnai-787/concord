# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

### Changed

### Fixed

## [1.1.0] - 2026-09-08

### Added

- **`grcmap/`**: a new cross-framework compliance-mapping and
  gap-analysis engine. Real, current framework catalogs (`frameworks/`):
  ISO/IEC 27001:2022 Annex A (93 controls, non-copyrighted short titles
  only), PCI DSS v4.0.1 (12 top-level requirements), NIST CSF 2.0 (6
  Functions / 22 Categories / 106 active Subcategories, parsed directly
  from NIST's official CPRT export), and SBP's real ETGRM framework
  (BPRD Circular 05/2017, 6 domains).
- A directed, many-to-many mapping model (`equal`/`equivalent`/`subset`/
  `superset`/`intersects`/`no_relationship` + syntactic/semantic/
  functional rationale, NIST IR 8477/OSCAL-inspired) and an
  implementation-state model kept strictly independent of it
  (`implemented`/`partial`/`planned`/`alternative`/`not_implemented`/
  `not_applicable`, the last always requiring a justification).
- A gap-analysis engine (`coverage.py`/`gaps.py`) computing COVERED/
  PARTIAL/PLANNED/GAP/NOT_APPLICABLE per requirement, with explicit,
  reviewer-signed `CoverageAssertion`s for cases where several controls
  jointly (not individually) satisfy a requirement.
- `examples/meridian-bank/`: a 33-control, 100-mapping example inventory
  for a fictional bank, replacing the original report's real-named
  reference organization for this new, computation-producing tool.
- `scripts/`: three re-runnable, byte-for-byte-verified catalog
  -generation scripts, including `build_nist_csf.py` which parses NIST's
  own official data export directly.
- `grcmap` CLI (`frameworks-list`, `validate`, `gaps`, `coverage`,
  `report`) and JSON/Markdown report generation, every report ending
  with an explicit non-certification disclaimer.
- 53 pytest tests. `.github/workflows/grcmap-ci.yml`: Ruff + pytest +
  validate + report, SHA-pinned actions, scoped to `grcmap/` changes.

### Changed

- `project.yaml`: `portfolio.featured` set to `true`.

### Fixed

- (within `grcmap`, new code) two real bugs found while building this --
  see PROJECT_NOTES.md for both: an aggregation-logic bug where an
  unrelated not-implemented control dragged an otherwise-fully-covered
  requirement down to GAP, and a `CoverageAssertion` target-matching gap
  where an assertion for one requirement could be silently applied to a
  different one.
- A real data-parsing finding: NIST CSF 2.0's officially commonly-cited
  "106 subcategories" and this project's initially-parsed "132" are both
  correct -- 26 of the 132 raw rows in NIST's own export are
  `[Withdrawn: ...]` placeholder stubs from the CSF 1.1 -> 2.0
  renumbering, now correctly excluded from gap-analysis scoring.
