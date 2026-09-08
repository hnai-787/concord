# How the framework catalogs were actually built

These scripts are real, re-runnable, and verified to reproduce their
target files byte-for-byte (checked during this project's build, not
assumed). Run all three from the `grcmap/` directory. They need
`openpyxl` in addition to the package's own runtime dependencies
(`pip install openpyxl` -- not a runtime dependency of `grcmap` itself,
only needed to rebuild a catalog from source).

`build_nist_csf.py` -- parses NIST's own official CPRT export
(`frameworks/provenance/nist-csf-2.0-official-export-2026-09-08.xlsx`,
downloaded directly from `csrc.nist.gov`) into `frameworks/nist-csf-2.0.yaml`.
Filters the sheet down to the 22 real CSF 2.0 category codes (the export
also contains legacy CSF 1.1 category codes like `PR.AC`/`ID.GV`
elsewhere in the same sheet -- a real thing this script had to discover
and filter, not something documented up front). See PROJECT_NOTES.md for
the "106 vs. 132 subcategories" finding this parsing work surfaced.

`build_iso27001.py` -- generates `frameworks/iso27001-2022.yaml` from a
hand-curated dict of the standard's own short (2-6 word) control titles.
ISO/IEC 27001 is copyrighted; this script deliberately does not fetch or
embed the standard's normative control text, only the widely-published
short-title nomenclature (see the framework file's own `source.note`).

`build_meridian_bank_example.py` -- generates the entire
`examples/meridian-bank/` inventory (controls, implementation states,
and all four `mappings/internal-to-*.yaml` files) from one script, so the
~130-entry example dataset stays internally consistent (matching IDs,
consistent formatting) rather than risking hand-authored drift.
