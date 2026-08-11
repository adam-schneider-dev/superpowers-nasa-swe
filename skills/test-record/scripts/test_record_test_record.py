import yaml
import pytest
from record_test_record import record_test_record


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-065", "section": "4.5.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-066", "section": "4.5.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "test-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_test_record(str(matrix_path), str(record_path), swe_ids=[], fields={"test_artifacts": "t"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "test-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_test_record(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"test_artifacts": "t"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "test-record.md"
    write_matrix(matrix_path, sample_rows())

    record_test_record(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-065", "SWE-066"],
        fields={
            "test_artifacts": "docs/test/software-test-plan.md, test procedures under tests/procedures/, reports under docs/test/reports/.",
            "requirements_testing": "100% of baselined requirements traced to at least one test case, see traceability.md.",
        },
        evidence="docs/test/software-test-plan.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "software-test-plan.md" in content
    assert "SWE-065" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "test-record.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Testing (NPR 7150.2D §4.5)\n\n")

    record_test_record(str(matrix_path), str(record_path), swe_ids=["SWE-065"], fields={"test_artifacts": "a"}, evidence="e1")
    record_test_record(str(matrix_path), str(record_path), swe_ids=["SWE-066"], fields={"test_artifacts": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "test-record.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_test_record(str(matrix_path), str(record_path), swe_ids=["SWE-065"], fields={"test_artifacts": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-065")["status"] == "tailored-out"
