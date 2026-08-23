# tests/test_ivv_catalog_integrity.py
"""Guards data/ivv-catalog.yaml (NASA-STD-8739.8B §4.4.2's 49 IV&V provider
verification requirements) against a bad edit or transcription pass — same
purpose as test_catalog_integrity.py for the SWE catalog.
"""
import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(ROOT, "data", "ivv-catalog.yaml")


def load_catalog():
    with open(CATALOG_PATH) as f:
        return yaml.safe_load(f)


def test_bundled_ivv_catalog_has_49_rows():
    assert len(load_catalog()) == 49


def test_every_id_is_unique():
    catalog = load_catalog()
    ids = [r["id"] for r in catalog]
    assert len(ids) == len(set(ids))


def test_ids_cover_4_4_2_1_through_49_in_order():
    catalog = load_catalog()
    expected = [f"IVV-4.4.2.{n}" for n in range(1, 50)]
    assert [r["id"] for r in catalog] == expected


def test_section_matches_id_suffix_for_every_row():
    for row in load_catalog():
        suffix = row["id"].removeprefix("IVV-")
        assert row["section"] == suffix
