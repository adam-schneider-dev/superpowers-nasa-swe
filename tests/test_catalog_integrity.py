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
    assert len(load_catalog()) == 49


def test_every_class_a_through_d_and_f_has_rows():
    catalog = load_catalog()
    for software_class in ("A", "B", "C", "D", "F"):
        assert filter_rows_for_class(catalog, software_class), (
            f"expected Class {software_class} rows in the bundled catalog slice"
        )


def test_class_e_is_empty_because_of_the_documented_coverage_gap():
    """Every Class E mark in Appendix C sits in Chapter 3, which is not yet transcribed.

    This is a coverage gap, not an authoritative "no requirements apply" — see
    data/CATALOG-COVERAGE.md. If Chapter 3 is ever added, this test should be
    replaced with a positive assertion rather than deleted.
    """
    assert filter_rows_for_class(load_catalog(), "E") == []


def test_class_f_authority_is_only_named_where_class_f_applies():
    for row in load_catalog():
        if row["class_f_authority"] is not None:
            assert row["classes"]["F"], (
                f"{row['swe_id']}: class_f_authority set but Class F not invoked"
            )
