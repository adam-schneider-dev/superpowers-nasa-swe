# tests/test_sa_task_catalog_integrity.py
"""Guards data/sa-task-catalog.yaml (NASA-STD-8739.8B §4.3 Table 1's Chapter 3
rows) against a bad edit or transcription pass — same purpose as
test_catalog_integrity.py for the SWE catalog and test_ivv_catalog_integrity.py
for the IV&V catalog. Scoped to this sub-spec's 45 Chapter 3 rows; Parts 2b/2c
will extend (not replace) these assertions as they add Chapter 4/5 rows.
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


def test_bundled_sa_task_catalog_has_45_rows():
    assert len(load_sa_task_catalog()) == 45


def test_every_swe_id_is_unique():
    catalog = load_sa_task_catalog()
    ids = [r["swe_id"] for r in catalog]
    assert len(ids) == len(set(ids))


def test_every_row_has_no_task_text_fields():
    for row in load_sa_task_catalog():
        assert set(row.keys()) == {"swe_id", "section"}


def test_every_swe_id_exists_in_swe_catalog():
    sa_task_ids = {r["swe_id"] for r in load_sa_task_catalog()}
    swe_catalog_ids = {r["swe_id"] for r in load_swe_catalog()}
    assert sa_task_ids.issubset(swe_catalog_ids)


def test_section_matches_swe_catalog_section_for_every_row():
    swe_sections = {r["swe_id"]: r["section"] for r in load_swe_catalog()}
    for row in load_sa_task_catalog():
        assert row["section"] == swe_sections[row["swe_id"]]


def test_all_rows_are_chapter_3():
    for row in load_sa_task_catalog():
        assert row["section"].startswith("3.")
