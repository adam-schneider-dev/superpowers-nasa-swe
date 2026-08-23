import pytest
import yaml
from record_sa_task_verification import record_sa_task_verification


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-033", "section": "3.1.2", "software_class": "C", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "sa-task-mapping-matrix.yaml"
    record_path = tmp_path / "sa-task-verification-management.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_sa_task_verification(str(matrix_path), str(record_path), swe_ids=[], fields={"acquisition_and_plan_setup": "p"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "sa-task-mapping-matrix.yaml"
    record_path = tmp_path / "sa-task-verification-management.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_sa_task_verification(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"acquisition_and_plan_setup": "a"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "sa-task-mapping-matrix.yaml"
    record_path = tmp_path / "sa-task-verification-management.md"
    write_matrix(matrix_path, sample_rows())

    record_sa_task_verification(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-033"],
        fields={"acquisition_and_plan_setup": "Acquisition risk assessment on file, docs/sa/acq-risk.md"},
        evidence="docs/sa/acq-risk.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    assert updated[0]["status"] == "satisfied"
    assert updated[0]["date"] is not None

    content = record_path.read_text()
    assert "Acquisition risk assessment" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "sa-task-mapping-matrix.yaml"
    record_path = tmp_path / "sa-task-verification-management.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Assurance & Safety Task Verification Record (NASA-STD-8739.8B §4.3 Table 1, Chapter 3)\n\n")

    record_sa_task_verification(str(matrix_path), str(record_path), swe_ids=["SWE-033"], fields={"acquisition_and_plan_setup": "a"}, evidence="e1")
    record_sa_task_verification(str(matrix_path), str(record_path), swe_ids=["SWE-033"], fields={"acquisition_and_plan_setup": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "sa-task-mapping-matrix.yaml"
    record_path = tmp_path / "sa-task-verification-management.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_sa_task_verification(str(matrix_path), str(record_path), swe_ids=["SWE-033"], fields={"acquisition_and_plan_setup": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-033")["status"] == "tailored-out"
