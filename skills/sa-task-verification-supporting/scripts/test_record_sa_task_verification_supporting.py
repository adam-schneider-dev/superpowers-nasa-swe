import os

import pytest
import yaml
from record_sa_task_verification_supporting import record_sa_task_verification_supporting


def sample_matrix_rows():
    return [
        {"swe_id": "SWE-079", "section": "5.1.2", "software_class": "C", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-084", "section": "5.1.7", "software_class": "C", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-200", "section": "5.4.6", "software_class": "C", "status": "tailored-out", "evidence": None, "date": None},
    ]


def write_matrix(tmp_path):
    matrix_path = tmp_path / "sa-task-mapping-matrix.yaml"
    with open(matrix_path, "w") as f:
        yaml.dump(sample_matrix_rows(), f, sort_keys=False)
    return str(matrix_path)


def test_marks_rows_satisfied_and_appends_record(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "sa-task-verification-supporting.md")

    record_sa_task_verification_supporting(
        matrix_yaml_path=matrix_path,
        record_md_path=record_path,
        swe_ids=["SWE-079", "SWE-084"],
        fields={"cm_planning_and_change_control": "SCM plan baselined; configuration items and levels of control identified."},
        evidence="docs/nasa-compliance/widget-firmware/scm-plan.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    by_id = {r["swe_id"]: r for r in updated}
    assert by_id["SWE-079"]["status"] == "satisfied"
    assert by_id["SWE-079"]["evidence"] == "docs/nasa-compliance/widget-firmware/scm-plan.md"
    assert by_id["SWE-079"]["date"] is not None
    assert by_id["SWE-084"]["status"] == "satisfied"

    with open(record_path) as f:
        record = f.read()
    assert "SWE-079" in record
    assert "SWE-084" in record
    assert "SCM plan baselined" in record


def test_empty_swe_ids_raises_value_error(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")
    with pytest.raises(ValueError, match="at least one swe_id"):
        record_sa_task_verification_supporting(
            matrix_yaml_path=matrix_path, record_md_path=record_path,
            swe_ids=[], fields={}, evidence="x",
        )


def test_unknown_swe_id_raises_key_error(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")
    with pytest.raises(KeyError):
        record_sa_task_verification_supporting(
            matrix_yaml_path=matrix_path, record_md_path=record_path,
            swe_ids=["SWE-999"], fields={}, evidence="x",
        )


def test_tailored_out_row_raises_value_error_and_matrix_unmodified(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")
    with pytest.raises(ValueError, match="tailored-out"):
        record_sa_task_verification_supporting(
            matrix_yaml_path=matrix_path, record_md_path=record_path,
            swe_ids=["SWE-200"], fields={}, evidence="x",
        )
    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    by_id = {r["swe_id"]: r for r in unchanged}
    assert by_id["SWE-200"]["status"] == "tailored-out"
    assert not os.path.exists(record_path)


def test_second_call_appends_new_record_entry(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")

    record_sa_task_verification_supporting(
        matrix_yaml_path=matrix_path, record_md_path=record_path,
        swe_ids=["SWE-079"], fields={"cm_planning_and_change_control": "First pass."},
        evidence="ev1.md",
    )
    with open(record_path) as f:
        first_len = len(f.read())

    record_sa_task_verification_supporting(
        matrix_yaml_path=matrix_path, record_md_path=record_path,
        swe_ids=["SWE-084"], fields={"cm_audits_and_release": "Second pass."},
        evidence="ev2.md",
    )
    with open(record_path) as f:
        content = f.read()
    assert len(content) > first_len
    assert content.count("## Recorded") == 2
