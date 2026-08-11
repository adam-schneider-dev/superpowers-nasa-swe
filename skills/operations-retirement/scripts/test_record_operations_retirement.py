import yaml
import pytest
from record_operations_retirement import record_operations_retirement


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-075", "section": "4.6.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-077", "section": "4.6.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "operations-retirement.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_operations_retirement(str(matrix_path), str(record_path), swe_ids=[], fields={"ops_plan": "p"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "operations-retirement.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_operations_retirement(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"ops_plan": "p"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "operations-retirement.md"
    write_matrix(matrix_path, sample_rows())

    record_operations_retirement(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-075", "SWE-077"],
        fields={
            "ops_maintenance_retirement_plan": "docs/ops/operations-maintenance-plan.md",
            "delivery_records": "As-built records delivered with v1.0, see docs/ops/as-built-v1.0.md.",
        },
        evidence="docs/ops/operations-maintenance-plan.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "as-built-v1.0.md" in content
    assert "SWE-075" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "operations-retirement.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Operations, Maintenance, and Retirement (NPR 7150.2D §4.6)\n\n")

    record_operations_retirement(str(matrix_path), str(record_path), swe_ids=["SWE-075"], fields={"ops_plan": "a"}, evidence="e1")
    record_operations_retirement(str(matrix_path), str(record_path), swe_ids=["SWE-077"], fields={"ops_plan": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "operations-retirement.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_operations_retirement(str(matrix_path), str(record_path), swe_ids=["SWE-075"], fields={"ops_plan": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-075")["status"] == "tailored-out"
