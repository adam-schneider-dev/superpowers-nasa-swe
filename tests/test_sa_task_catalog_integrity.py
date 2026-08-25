# tests/test_sa_task_catalog_integrity.py
"""Guards data/sa-task-catalog.yaml (NASA-STD-8739.8B §4.3 Table 1's Chapter
3-5 rows) against a bad edit or transcription pass — same purpose as
test_catalog_integrity.py for the SWE catalog and test_ivv_catalog_integrity.py
for the IV&V catalog. Extended (not replaced) by Part 2b for Chapter 4 and
Part 2c for Chapter 5, which completes the table at 103 rows.
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


def test_bundled_sa_task_catalog_has_103_rows():
    assert len(load_sa_task_catalog()) == 103


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


def test_all_rows_are_chapter_3_4_or_5():
    for row in load_sa_task_catalog():
        assert (
            row["section"].startswith("3.")
            or row["section"].startswith("4.")
            or row["section"].startswith("5.")
        )


def test_chapter_4_has_37_rows():
    ch4 = [r for r in load_sa_task_catalog() if r["section"].startswith("4.")]
    assert len(ch4) == 37


def test_chapter_5_has_21_rows():
    ch5 = [r for r in load_sa_task_catalog() if r["section"].startswith("5.")]
    assert len(ch5) == 21


def test_chapter_5_rows_match_table_1_exactly():
    """Pins Chapter 5's exact (swe_id, section) pairs so a dropped or altered
    row fails loudly rather than only shifting a count another test asserts."""
    expected = [
        ("SWE-079", "5.1.2"), ("SWE-080", "5.1.3"), ("SWE-081", "5.1.4"),
        ("SWE-082", "5.1.5"), ("SWE-083", "5.1.6"), ("SWE-084", "5.1.7"),
        ("SWE-085", "5.1.8"), ("SWE-045", "5.1.9"), ("SWE-086", "5.2"),
        ("SWE-087", "5.3.2"), ("SWE-088", "5.3.3"), ("SWE-089", "5.3.4"),
        ("SWE-090", "5.4.2"), ("SWE-093", "5.4.3"), ("SWE-094", "5.4.4"),
        ("SWE-199", "5.4.5"), ("SWE-200", "5.4.6"), ("SWE-201", "5.5.1"),
        ("SWE-202", "5.5.2"), ("SWE-203", "5.5.3"), ("SWE-204", "5.5.4"),
    ]
    actual = [
        (r["swe_id"], r["section"])
        for r in load_sa_task_catalog()
        if r["section"].startswith("5.")
    ]
    assert actual == expected


def test_swe_065_lettered_rows_all_share_section_4_5_2():
    lettered = [r for r in load_sa_task_catalog() if r["swe_id"].startswith("SWE-065")]
    assert {r["swe_id"] for r in lettered} == {"SWE-065a", "SWE-065b", "SWE-065c", "SWE-065d"}
    assert all(r["section"] == "4.5.2" for r in lettered)
