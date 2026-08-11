import yaml
import pytest
from record_architecture_record import record_architecture_record


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-057", "section": "4.2.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-143", "section": "4.2.4", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "architecture-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_architecture_record(str(matrix_path), str(record_path), swe_ids=[], fields={"architecture_description": "d"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "architecture-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_architecture_record(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"architecture_description": "d"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "architecture-record.md"
    write_matrix(matrix_path, sample_rows())

    record_architecture_record(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-057", "SWE-143"],
        fields={
            "architecture_description": "docs/architecture/software-architecture.md, C4 container + component views.",
            "architecture_review": "Category 2 project, Class C payload risk — architecture review not required per NPR 8705.4.",
        },
        evidence="docs/architecture/software-architecture.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "C4 container" in content
    assert "SWE-057" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "architecture-record.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Architecture (NPR 7150.2D §4.2)\n\n")

    record_architecture_record(str(matrix_path), str(record_path), swe_ids=["SWE-057"], fields={"architecture_description": "a"}, evidence="e1")
    record_architecture_record(str(matrix_path), str(record_path), swe_ids=["SWE-143"], fields={"architecture_description": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "architecture-record.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_architecture_record(str(matrix_path), str(record_path), swe_ids=["SWE-057"], fields={"architecture_description": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-057")["status"] == "tailored-out"
