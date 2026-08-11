# tests/test_catalog_integrity.py
"""Guards the bundled catalog against a bad edit or a bad transcription pass.

`validate_catalog` existed but nothing ever ran it against the real file, so a
schema-shaped mistake in `data/swe-catalog.yaml` could ship unnoticed.
"""
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "requirements-matrix", "scripts"))

from filter_matrix import filter_rows_for_class
from validate_catalog import validate_catalog

CATALOG_PATH = os.path.join(ROOT, "data", "swe-catalog.yaml")


def load_catalog():
    with open(CATALOG_PATH) as f:
        return yaml.safe_load(f)


def test_bundled_catalog_is_valid():
    assert validate_catalog(load_catalog()) == []


def test_bundled_catalog_row_count_matches_documented_coverage():
    assert len(load_catalog()) == 100


def test_every_class_a_through_f_has_rows():
    catalog = load_catalog()
    for software_class in ("A", "B", "C", "D", "E", "F"):
        assert filter_rows_for_class(catalog, software_class), (
            f"expected Class {software_class} rows in the bundled catalog slice"
        )


def test_class_e_has_exactly_the_documented_row_count():
    """All 12 of Appendix C's Class E marks sit in Chapter 3 (data/CATALOG-COVERAGE.md).

    An exact count, not just non-empty, so a future partial edit to Chapter 3's
    rows that drops a Class E mark fails loudly instead of silently passing a
    weaker "at least one" check.
    """
    assert len(filter_rows_for_class(load_catalog(), "E")) == 12


def test_swe_015_f_mark_has_no_named_authority():
    """§3.2.1/SWE-015 carries a Class F mark with a blank Class F Authority cell
    in the source standard itself — not a transcription error. See
    data/CATALOG-COVERAGE.md and skills/tailoring-request/SKILL.md's handling
    of a null default_approver.
    """
    catalog = load_catalog()
    row = next(r for r in catalog if r["swe_id"] == "SWE-015")
    assert row["classes"]["F"] is True
    assert row["class_f_authority"] is None


def test_class_f_authority_is_only_named_where_class_f_applies():
    for row in load_catalog():
        if row["class_f_authority"] is not None:
            assert row["classes"]["F"], (
                f"{row['swe_id']}: class_f_authority set but Class F not invoked"
            )
