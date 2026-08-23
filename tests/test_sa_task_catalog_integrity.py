# tests/test_sa_task_catalog_integrity.py
"""Guards data/sa-task-catalog.yaml (NASA-STD-8739.8B §4.3 Table 1's Chapter
3-4 rows) against a bad edit or transcription pass — same purpose as
test_catalog_integrity.py for the SWE catalog and test_ivv_catalog_integrity.py
for the IV&V catalog. Extended (not replaced) by Part 2b to cover Chapter 4;
Part 2c will extend it again for Chapter 5.
"""
import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SA_TASK_CATALOG_PATH = os.path.join(ROOT, "data", "sa-task-catalog.yaml")
SWE_CATALOG_PATH = os.path.join(ROOT, "data", "swe-catalog.yaml")


def load_sa_task_catalog():
    with open(SA_TASK_CATALOG_PATH) as f:
        return yaml.safe_load(f)


def load_swe_catalog():
    with open(SWE_CATALOG_PATH) as f:
        return yaml.safe_load(f)


def _base_swe_id(swe_id):
    """Strip a trailing lowercase letter (e.g. "SWE-065a" -> "SWE-065") so
    lettered sub-task ids can still be looked up against swe-catalog.yaml,
    which has one row per base id, not one per lettered sub-task."""
    return swe_id[:-1] if swe_id[-1].isalpha() else swe_id


def test_bundled_sa_task_catalog_has_82_rows():
    assert len(load_sa_task_catalog()) == 82


def test_every_swe_id_is_unique():
    catalog = load_sa_task_catalog()
    ids = [r["swe_id"] for r in catalog]
    assert len(ids) == len(set(ids))


def test_every_row_has_no_task_text_fields():
    for row in load_sa_task_catalog():
        assert set(row.keys()) == {"swe_id", "section"}


def test_every_swe_id_exists_in_swe_catalog():
    sa_task_ids = {_base_swe_id(r["swe_id"]) for r in load_sa_task_catalog()}
    swe_catalog_ids = {r["swe_id"] for r in load_swe_catalog()}
    assert sa_task_ids.issubset(swe_catalog_ids)


def test_section_matches_swe_catalog_section_for_every_row():
    swe_sections = {r["swe_id"]: r["section"] for r in load_swe_catalog()}
    for row in load_sa_task_catalog():
        assert row["section"] == swe_sections[_base_swe_id(row["swe_id"])]


def test_all_rows_are_chapter_3_or_4():
    for row in load_sa_task_catalog():
        assert row["section"].startswith("3.") or row["section"].startswith("4.")


def test_chapter_4_has_37_rows():
    ch4 = [r for r in load_sa_task_catalog() if r["section"].startswith("4.")]
    assert len(ch4) == 37


def test_swe_065_lettered_rows_all_share_section_4_5_2():
    lettered = [r for r in load_sa_task_catalog() if r["swe_id"].startswith("SWE-065")]
    assert {r["swe_id"] for r in lettered} == {"SWE-065a", "SWE-065b", "SWE-065c", "SWE-065d"}
    assert all(r["section"] == "4.5.2" for r in lettered)
