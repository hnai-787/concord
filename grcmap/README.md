# grcmap

A cross-framework compliance-mapping and gap-analysis engine. It models
a fictional bank's control inventory declaratively, maps it against four
real, current regulatory/industry frameworks using directional
set-theory relationships (NIST IR 8477 / OSCAL-inspired), and computes
readiness/gap reports without ever claiming certification.

```text
declarative control inventory (Meridian Bank, fictional)
        |
    schema + reference validation
        |
    mapping relationship (equal/subset/superset/intersects) x rationale
        |
    conceptual coverage  +  real implementation state   <- kept separate
        |
    COVERED / PARTIAL / PLANNED / GAP / NOT_APPLICABLE
        |
    readiness report (never a compliance certificate)
```

## Why this exists

The original version mapped one bank against four frameworks, once,
by hand, in a Word document. The real gap: an organization's controls
don't change every time a new framework comes along, so real GRC
practice treats mapping as reusable data — implement a control once, map
it outward to every framework it touches, and recompute readiness when
either side changes. This is a deliberately small implementation of that
same idea (see "Prior art" below), grounded throughout in the actual
current versions of the frameworks it models, not remembered/paraphrased
ones.

## The central architectural rule

```text
mapping relationship  !=  implementation status  !=  risk priority  !=  compliance determination
```

A `Mapping`'s `relationship` (`equal`/`equivalent`/`subset`/`superset`/
`intersects`/`no_relationship`) is a reviewer's one-time judgment about
how an internal control conceptually relates to an external requirement.
An `Implementation`'s `state` is the organization's actual, evidence
-backed status, which changes over time independently of the mapping.
`coverage.py` combines the two explicitly; nothing in this codebase ever
collapses them into one score, and no report ever says "ISO 27001
certified" or "PCI compliant" — see `report.py`'s `DISCLAIMER`.

## The frameworks, as they actually are today

- **ISO/IEC 27001:2022 Annex A** — 93 controls (37 organizational / 8
  people / 14 physical / 34 technological). Copyrighted; only control IDs
  and short (2-6 word) topic titles are recorded, never the standard's
  normative text — see `frameworks/iso27001-2022.yaml`'s `source.note`.
- **PCI DSS v4.0.1** — the 12 top-level requirements, PCI SSC's own
  published titles. v4.0.1 is a limited revision of v4.0 (no new/deleted
  requirements, only clarifications); v4.0 itself retired 2024-12-31.
  Hierarchical sub-requirements are a real part of the standard not
  enumerated in this v1 catalog (disclosed scope decision).
- **NIST CSF 2.0** — 6 Functions, 22 Categories, 106 active Subcategories
  (132 raw ID rows in NIST's own dataset, 26 of them `[Withdrawn: ...]`
  placeholder stubs from the CSF 1.1 -> 2.0 renumbering — see
  "A real methodological finding" below). Parsed directly from NIST's
  official CPRT export (`scripts/build_nist_csf.py`); text is a U.S.
  government work, public domain, used verbatim.
- **SBP ETGRM** (BPRD Circular No. 05 of 2017) — the 6 major domains of
  Pakistan's real Enterprise Technology Governance & Risk Management
  Framework for Financial Institutions, including its explicit
  Business Continuity and Disaster Recovery domain (Section 5) — the
  natural home for this project's original BCP/DR content.

## Meridian Bank, not HBL

The rebuilt example organization is **Meridian Bank** — fictional,
explicitly disclaimed in `examples/meridian-bank/controls.yaml`. The
original report used Habib Bank Limited (a real, named bank) as a
hypothetical reference organization, already carefully disclaimed. Now
that this rebuild produces *computed* gap/coverage results, using a real
bank's name would create unnecessary ambiguity about whether those
outputs assess the real institution — genericizing removes that ambiguity
entirely, at no cost, since none of the underlying figures were ever real
either way.

## Usage

```bash
pip install -e ".[dev]"

grcmap frameworks-list
grcmap validate
grcmap gaps --framework pci-dss-4.0.1
grcmap coverage IAM-01
grcmap report --format markdown -o results/full-report.md
```

## Running the tests

```bash
pytest -q
ruff check src tests scripts
```

## A real methodological finding worth knowing

NIST's own CPRT export is the authoritative source, so it was trusted
over a secondary citation: the "106 subcategories" figure widely quoted
(including in this project's own research brief) is the count of
*active* subcategories. The raw dataset actually has 132 subcategory ID
rows — 26 of them are `[Withdrawn: Incorporated into ...]` placeholder
stubs NIST deliberately kept to document where CSF 1.1 content moved
during the 2.0 renumbering, rather than reusing or silently dropping the
ID. `gaps.py` excludes withdrawn stubs from scoring (a withdrawn
requirement isn't a real thing to have a gap against) — found and fixed
after `grcmap gaps --framework nist-csf-2.0` initially printed
`DE.AE-01 — [Withdrawn: Incorporated into ID.AM-03] — GAP`, which is
obviously wrong once you see it. See PROJECT_NOTES.md for the full story.

## Two real bugs found while building this (not hidden)

1. **Independent partial mappings wrongly dragged down an unrelated,
   fully-implemented control.** PCI Requirement 3 was reporting `GAP`
   despite a real `superset`-relationship control (`DAT-01`,
   *implemented*) mapped to it, because an entirely unrelated
   `intersects`-relationship control (`DAT-03`, *not_implemented*) was
   being combined via a single "worst state wins" rule across ALL
   contributing controls. Fixed by distinguishing *why* controls are
   contributing: independently-sufficient mappings (each individually
   claiming full or partial coverage) are combined with the BEST state
   found among them; only a reviewer's explicit `CoverageAssertion` — a
   claim that a SPECIFIC set of controls jointly and necessarily covers
   a requirement — is combined with the WORST state, since that claim's
   validity really does depend on every named member being done. See
   `coverage.py`'s module docstring and
   `tests/test_coverage.py::test_independent_partial_mappings_do_not_drag_down_an_unrelated_implemented_full_mapping`.
2. **A `CoverageAssertion` for one requirement was silently accepted for
   a different one.** `conceptual_coverage()` trusted its caller to have
   already filtered assertions to the right (framework, requirement)
   target, but nothing inside the function actually checked that — found
   by a unit test that (deliberately, to test the boundary) called the
   function directly with a mismatched assertion. Fixed by having the
   function re-verify each assertion's own `target_framework`/
   `target_control` before trusting it, rather than relying on caller
   discipline.

## Verification performed

53 pytest tests pass (algorithm unit tests matching every case in the
combine-conceptual-with-implementation matrix, catalog structural tests
against the real published counts, validator reference-integrity tests,
and CLI/report tests). Ruff reports zero issues on `src`, `tests`, and
`scripts`. All three catalog-generation scripts were re-run and verified
to reproduce their target files byte-for-byte. `grcmap report` was
actually run end-to-end over all four real frameworks and the 33-control
Meridian Bank inventory; the output is committed in `results/`.

## Prior art (this project doesn't invent compliance-as-code)

- **NIST IR 8477** (Feb 2024) — the set-theory relationship model
  (`equal`/`subset`/`superset`/`intersects`/`no-relationship` +
  syntactic/semantic/functional rationale) this project's `Relationship`
  and `Rationale` enums are drawn from directly.
- **NIST OSCAL Control Mapping Model** — a stronger, more general
  machine-readable precedent for the same relationships; this project is
  intentionally OSCAL-inspired without implementing full OSCAL.
- **OpenControl** — YAML-based compliance-as-code with implementation
  states (`partial`/`planned`/`complete`/`none`); this project's
  `ImplementationState` enum extends that idea with `alternative` and a
  justification-required `not_applicable`.
- **Secure Controls Framework (SCF)** — uses the same NIST IR 8477
  set-theory relationships for its own public crosswalks, corroborating
  this as a real, current industry approach rather than a one-off idea.

## Limitations

- PCI DSS and SBP ETGRM catalogs model only their top-level
  requirements/domains in this v1 — real hierarchical sub-requirements
  exist in both standards but aren't enumerated here (disclosed scope
  decision; the schema already supports adding them).
- 33 internal controls and 100 mappings is a representative, hand-curated
  example inventory, not an exhaustive real bank's control set.
- No quantitative coverage percentages by design (see `report.py` /
  OSCAL's own documented caution against false precision here).
- This tool computes readiness/gap indicators from a self-declared
  inventory — it is not, and does not claim to be, a certification, audit
  opinion, or regulatory compliance determination.

## Future Enhancements

- Hierarchical PCI/SBP sub-requirements.
- NIST CSF Implementation Tiers (organization/Function-level, per CSF
  2.0's own guidance — never per-Subcategory, and never conflated with
  per-control implementation state).
- A real second example organization to prove the framework catalogs are
  reusable across inventories, not just Meridian Bank-specific.
