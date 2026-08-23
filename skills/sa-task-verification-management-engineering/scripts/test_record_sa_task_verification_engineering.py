import os

import pytest
import yaml
from record_sa_task_verification_engineering import record_sa_task_verification_engineering


def sample_matrix_rows():
    return [
        {"swe_id": "SWE-060", "section": "4.4.2", "software_class": "C", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-061", "section": "4.4.3", "software_class": "C", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-058", "section": "4.3.2", "software_class": "C", "status": "tailored-out", "evidence": None, "date": None},
    ]


def write_matrix(tmp_path):
    matrix_path = tmp_path / "sa-task-mapping-matrix.yaml"
    with open(matrix_path, "w") as f:
        yaml.dump(sample_matrix_rows(), f, sort_keys=False)
    return str(matrix_path)


def test_marks_rows_satisfied_and_appends_record(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "sa-task-verification-management-engineering.md")

    record_sa_task_verification_engineering(
        matrix_yaml_path=matrix_path,
        record_md_path=record_path,
        swe_ids=["SWE-060", "SWE-061"],
        fields={"software_implementation": "Reviewed code against design; no undocumented functionality found."},
        evidence="docs/nasa-compliance/widget-firmware/implementation-review.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    by_id = {r["swe_id"]: r for r in updated}
    assert by_id["SWE-060"]["status"] == "satisfied"
    assert by_id["SWE-060"]["evidence"] == "docs/nasa-compliance/widget-firmware/implementation-review.md"
    assert by_id["SWE-060"]["date"] is not None
    assert by_id["SWE-061"]["status"] == "satisfied"

    with open(record_path) as f:
        record = f.read()
    assert "SWE-060" in record
    assert "SWE-061" in record
    assert "Reviewed code against design" in record


def test_empty_swe_ids_raises_value_error(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")
    with pytest.raises(ValueError, match="at least one swe_id"):
        record_sa_task_verification_engineering(
            matrix_yaml_path=matrix_path, record_md_path=record_path,
            swe_ids=[], fields={}, evidence="x",
        )


def test_unknown_swe_id_raises_key_error(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")
    with pytest.raises(KeyError):
        record_sa_task_verification_engineering(
            matrix_yaml_path=matrix_path, record_md_path=record_path,
            swe_ids=["SWE-999"], fields={}, evidence="x",
        )


def test_tailored_out_row_raises_value_error_and_matrix_unmodified(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")
    with pytest.raises(ValueError, match="tailored-out"):
        record_sa_task_verification_engineering(
            matrix_yaml_path=matrix_path, record_md_path=record_path,
            swe_ids=["SWE-058"], fields={}, evidence="x",
        )
    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    by_id = {r["swe_id"]: r for r in unchanged}
    assert by_id["SWE-058"]["status"] == "tailored-out"
    assert not os.path.exists(record_path)


def test_second_call_appends_new_record_entry(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")

    record_sa_task_verification_engineering(
        matrix_yaml_path=matrix_path, record_md_path=record_path,
        swe_ids=["SWE-060"], fields={"software_implementation": "First pass."},
        evidence="ev1.md",
    )
    with open(record_path) as f:
        first_len = len(f.read())

    record_sa_task_verification_engineering(
        matrix_yaml_path=matrix_path, record_md_path=record_path,
        swe_ids=["SWE-061"], fields={"software_implementation": "Second pass."},
        evidence="ev2.md",
    )
    with open(record_path) as f:
        content = f.read()
    assert len(content) > first_len
    assert content.count("## Recorded") == 2
