import yaml
import pytest
from record_implementation_record import record_implementation_record


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-060", "section": "4.4.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-061", "section": "4.4.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "implementation-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_implementation_record(str(matrix_path), str(record_path), swe_ids=[], fields={"coding_standards": "s"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "implementation-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_implementation_record(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"coding_standards": "s"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "implementation-record.md"
    write_matrix(matrix_path, sample_rows())

    record_implementation_record(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-060", "SWE-061"],
        fields={
            "implementation": "Design realized in src/, traced via traceability matrix.",
            "coding_standards": "PEP 8 plus project style guide docs/standards/python-style.md; enforced via ruff in CI.",
        },
        evidence="docs/standards/python-style.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "PEP 8" in content
    assert "SWE-060" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "implementation-record.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Implementation (NPR 7150.2D §4.4)\n\n")

    record_implementation_record(str(matrix_path), str(record_path), swe_ids=["SWE-060"], fields={"coding_standards": "a"}, evidence="e1")
    record_implementation_record(str(matrix_path), str(record_path), swe_ids=["SWE-061"], fields={"coding_standards": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "implementation-record.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_implementation_record(str(matrix_path), str(record_path), swe_ids=["SWE-060"], fields={"coding_standards": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-060")["status"] == "tailored-out"
