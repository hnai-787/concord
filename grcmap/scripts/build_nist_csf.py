"""Rebuild frameworks/nist-csf-2.0.yaml from NIST's own official CPRT export.

Re-download the source file with:
    curl -s "https://csrc.nist.gov/extensions/nudp/services/json/csf/download" \
        -o frameworks/provenance/nist-csf-2.0-official-export-<date>.xlsx

(the URL name says "json" but the endpoint actually returns an XLSX
workbook -- confirmed via `file`/content-type, not assumed.)

The CPRT export mixes real CSF 2.0 categories with legacy CSF 1.1
category codes elsewhere in the same sheet (e.g. `PR.AC`, `ID.GV`,
`RS.RP` -- pre-2.0 codes, not part of the current 22-category structure).
This script filters to the authoritative 22 CSF 2.0 category codes before
extracting subcategories, and keeps NIST's `[Withdrawn: ...]` placeholder
rows as-is (gaps.py filters those out at gap-analysis time, not here --
they're real data, just not scoreable requirements).
"""

import re
from pathlib import Path

import openpyxl
import yaml

SOURCE_XLSX = Path(__file__).resolve().parents[1] / "frameworks" / "provenance" / "nist-csf-2.0-official-export-2026-09-08.xlsx"
OUTPUT_YAML = Path(__file__).resolve().parents[1] / "frameworks" / "nist-csf-2.0.yaml"

# The real, authoritative CSF 2.0 category set (cross-checked against the
# research this project was built from) -- used to filter out legacy
# CSF 1.1 codes that appear elsewhere in the same exported sheet.
VALID_CATEGORIES = {
    "GV": ["GV.OC", "GV.RM", "GV.RR", "GV.PO", "GV.OV", "GV.SC"],
    "ID": ["ID.AM", "ID.RA", "ID.IM"],
    "PR": ["PR.AA", "PR.AT", "PR.DS", "PR.PS", "PR.IR"],
    "DE": ["DE.CM", "DE.AE"],
    "RS": ["RS.MA", "RS.AN", "RS.CO", "RS.MI"],
    "RC": ["RC.RP", "RC.CO"],
}


def parse_workbook(path: Path) -> dict:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["CSF 2.0"]
    rows = list(ws.iter_rows(values_only=True))

    functions: dict = {}
    current_function = None
    current_category = None

    for row in rows[2:]:  # skip title + header rows
        func_cell, cat_cell, subcat_cell = row[0], row[1], row[2]
        if func_cell:
            m = re.match(r"^(.*?)\s*\(([A-Z]{2})\):\s*(.*)$", func_cell.replace("\n", " ").strip())
            if m:
                name, code, desc = m.groups()
                current_function = code
                functions[code] = {"id": code, "name": name.strip(), "description": desc.strip(), "categories": {}}
        elif cat_cell:
            m = re.match(r"^(.*?)\s*\(([A-Z]{2}\.[A-Z]{2})\):\s*(.*)$", cat_cell.replace("\n", " ").strip())
            if m:
                name, code, desc = m.groups()
                current_category = code
                functions[current_function]["categories"][code] = {
                    "id": code, "name": name.strip(), "description": desc.strip(), "subcategories": {}
                }
        elif subcat_cell:
            m = re.match(r"^([A-Z]{2}\.[A-Z]{2}-\d{2}):\s*(.*)$", subcat_cell.replace("\n", " ").strip())
            if m:
                code, desc = m.groups()
                functions[current_function]["categories"][current_category]["subcategories"][code] = desc.strip()

    return functions


def main() -> None:
    raw = parse_workbook(SOURCE_XLSX)

    cleaned = {}
    for fcode, valid_cats in VALID_CATEGORIES.items():
        f = raw[fcode]
        cleaned[fcode] = {"id": fcode, "name": f["name"], "description": f["description"], "categories": {}}
        for ccode in valid_cats:
            cleaned[fcode]["categories"][ccode] = f["categories"][ccode]

    out = {
        "id": "nist-csf-2.0",
        "title": "NIST Cybersecurity Framework 2.0",
        "issuer": "National Institute of Standards and Technology (NIST)",
        "version": "2.0",
        "issued": "2024-02-26",
        "instrument": "NIST CSWP 29",
        "source": {
            "publisher": "NIST",
            "retrieved": "2026-09-08",
            "url": "https://csrc.nist.gov/extensions/nudp/services/json/csf/download",
            "note": (
                "Official NIST CPRT (Cybersecurity and Privacy Reference Tool) export. "
                "Text is a U.S. government work (public domain), used verbatim per NIST "
                "publication policy -- unlike ISO/IEC 27001, which is copyrighted "
                "(see iso27001-2022.yaml)."
            ),
        },
        "status": "active",
        "requirements": [],
    }

    for fcode, f in cleaned.items():
        out["requirements"].append({"id": fcode, "level": "function", "parent": None, "title": f["name"], "description": f["description"]})
        for ccode, c in f["categories"].items():
            out["requirements"].append({"id": ccode, "level": "category", "parent": fcode, "title": c["name"], "description": c["description"]})
            for scode, sdesc in c["subcategories"].items():
                out["requirements"].append({"id": scode, "level": "subcategory", "parent": ccode, "title": sdesc, "description": None})

    n_func = sum(1 for r in out["requirements"] if r["level"] == "function")
    n_cat = sum(1 for r in out["requirements"] if r["level"] == "category")
    n_sub = sum(1 for r in out["requirements"] if r["level"] == "subcategory")
    n_withdrawn = sum(1 for r in out["requirements"] if r["level"] == "subcategory" and r["title"].startswith("[Withdrawn"))
    print(f"functions={n_func} categories={n_cat} subcategories={n_sub} (withdrawn={n_withdrawn}, active={n_sub - n_withdrawn})")
    assert n_func == 6 and n_cat == 22

    with open(OUTPUT_YAML, "w", encoding="utf-8") as f:
        yaml.dump(out, f, sort_keys=False, allow_unicode=True, width=100)
    print(f"wrote {OUTPUT_YAML}")


if __name__ == "__main__":
    main()
