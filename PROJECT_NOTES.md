# Project Notes

## Source

Migrated from `air-university-cybersecurity-projects/projects/hbl-contingency-framework`
into this workspace as an independent project on 2026-09-07.

## Cleanup decisions

None needed — the report already contains an explicit disclaimer that it
does not represent HBL's real systems or compliance status.

## Assumptions

- Group members listed are taken from the docx report's author table —
  kept per the decision to preserve standard academic group-project
  attribution.
- Flagged for the user's own awareness (per the original migration
  review): this project names a real bank as its reference organization
  for a hypothetical security-gap-style analysis. The report's own
  disclaimer mitigates this, and no non-public/real data is included, but
  it's worth being comfortable with that framing before treating this repo
  as fully public — no unilateral change was made here since the report's
  scoping was judged sufficient by design.

## Remaining work

None identified.

## 2026-09-08: Added grcmap (cross-framework GRC mapping and gap-analysis engine)

### What changed and why

The original report mapped one bank against four frameworks once, by
hand, in a Word document. The gap this fills: real GRC practice treats
control-to-framework mapping as reusable data (implement a control once,
map it outward, recompute readiness as either side changes), formalized
by NIST IR 8477's set-theory relationship model and NIST's own OSCAL
Control Mapping Model. Full research grounding (exact current framework
versions, why compliance is a verifier-behavior question not a
password-string-style property, OpenControl/OSCAL/SCF prior art) is in
`grcmap/README.md`.

Per the research's own recommendation, the example organization was
genericized from Habib Bank Limited (a real, named bank the original
report used as a disclaimed hypothetical reference) to **Meridian
Bank**, fictional. The original report/presentation are preserved
unmodified; only the new `grcmap/` example inventory uses the fictional
name -- see `grcmap/README.md` "Meridian Bank, not HBL" for the full
reasoning.

### A real methodological finding from parsing NIST's own official data

Rather than trust the "106 subcategories" figure as cited (including in
this project's own research brief), the actual NIST CSF 2.0 Core was
downloaded directly from NIST's official CPRT export
(`https://csrc.nist.gov/extensions/nudp/services/json/csf/download` --
the URL says "json", the real response is an XLSX workbook, confirmed via
content-type rather than assumed) and parsed programmatically
(`grcmap/scripts/build_nist_csf.py`). The raw dataset has **132**
subcategory ID rows, not 106. Investigating why revealed the real
explanation: NIST deliberately keeps 26 old CSF 1.1 subcategory IDs as
`[Withdrawn: Incorporated into ...]` placeholder stubs, documenting where
that content moved during the 1.1->2.0 renumbering, rather than reusing
or silently dropping the ID. 132 - 26 withdrawn = 106 active
subcategories -- exactly the commonly-cited figure. Both numbers are
correct; they were just counting different things. `gaps.py` excludes
withdrawn stubs from scoring, found necessary after `grcmap gaps
--framework nist-csf-2.0` initially printed `DE.AE-01 — [Withdrawn:
Incorporated into ID.AM-03] — GAP`, which is obviously wrong once you see
a withdrawn requirement treated as a real gap.

A second, separate parsing issue in the same export: the sheet also
contains legacy CSF 1.1 category codes (e.g. `PR.AC`, `ID.GV`, `RS.RP`)
interleaved with the real CSF 2.0 categories elsewhere in the workbook.
`build_nist_csf.py` filters to the authoritative 22 CSF 2.0 category
codes (cross-checked against the research brief) before extracting
subcategories, rather than trusting every category-shaped row in the file.

### Key engineering decisions and why

- **Four concepts kept strictly separate, everywhere**: mapping
  relationship != implementation status != risk priority != compliance
  determination. `Mapping.relationship` is a reviewer's one-time
  judgment; `Implementation.state` is the organization's real,
  evidence-backed status that changes independently over time.
  `coverage.py` is the one place they're combined, and every report ends
  with an explicit disclaimer that the output is a readiness indicator,
  never a certification or compliance claim (`report.py::DISCLAIMER`).
- **ISO 27001's copyrighted text is never reproduced.** Only control IDs
  and short (2-6 word) topic titles are recorded -- the same
  nomenclature independently published across public ISO reference
  material -- never the standard's normative control text. NIST CSF text
  (a U.S. government work, public domain) is used verbatim instead,
  since it carries no such restriction.
- **PCI DSS and SBP ETGRM model only top-level requirements/domains in
  v1** -- both standards have real hierarchical sub-requirements not
  enumerated here, a disclosed scope decision rather than a silent gap.
- **A `CoverageAssertion` requires explicit reviewer sign-off to elevate
  partial mappings to full coverage** -- never inferred automatically by
  summing fractional coverage claims (the research's own strong caution,
  taken seriously: OSCAL's own coverage field documentation warns partial
  relations only count as a fraction of complete mappings, i.e. don't
  invent false precision).

### Two real bugs found and fixed

1. **Independent partial mappings wrongly dragged down an unrelated,
   fully-implemented control down to GAP.** PCI Requirement 3 reported
   `GAP` despite a real, *implemented* `superset`-relationship control
   (`DAT-01`) being mapped to it, because a completely unrelated
   `intersects`-relationship, *not_implemented* control (`DAT-03`) was
   being combined via a single "worst state wins" rule across every
   contributing control regardless of why each was contributing. Fixed
   by distinguishing independently-sufficient mappings (combined with
   the BEST state -- any one being implemented is enough to realize that
   mapping's own claim) from a reviewer's explicit collective
   `CoverageAssertion` (combined with the WORST state -- the assertion's
   validity genuinely depends on every named member being done). See
   `coverage.py`'s module docstring for the full reasoning and
   `tests/test_coverage.py` for the regression test.
2. **A `CoverageAssertion` for one requirement was silently accepted for
   a different one.** `conceptual_coverage()` assumed its caller had
   already filtered assertions to the right (framework, requirement)
   target and never verified that itself -- caught by a unit test that
   deliberately called the function directly with a mismatched
   assertion, specifically to probe that boundary. Fixed by having the
   function re-check each assertion's own target fields before trusting it.

### Verification performed

53 pytest tests pass, covering: catalog structural tests against the
real published counts (ISO's 93/37/8/14/34, PCI's 12, NIST's real
6/22/106-active/132-raw with the withdrawn-stub distinction, SBP's 6),
the exact combine-conceptual-with-implementation matrix as unit tests,
validator reference-integrity tests (unknown control/requirement,
duplicate mapping IDs, not_applicable without justification), and
CLI/report tests (including an explicit assertion that no report ever
contains a fake coverage percentage or a certification/compliance
claim). Ruff reports zero issues across `src`, `tests`, and `scripts`.
All three catalog-generation scripts were re-run from their permanent
location and verified to reproduce their target files byte-for-byte
(not merely "should work" -- actually diffed). `grcmap report` was
actually run end-to-end over all four real frameworks and the 33-control
Meridian Bank inventory; the output is committed under `grcmap/results/`.

### Remaining work / honest limitations

See `grcmap/README.md` "Limitations" -- notably: PCI/SBP catalogs are
top-level-only in v1, the 33-control/100-mapping Meridian Bank inventory
is a representative example, not an exhaustive real bank's control set,
and the tool deliberately never emits a compliance percentage or
certification claim.
