import pytest
import yaml
from record_risk_management import record_risk_management


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-086", "section": "5.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "risk-management.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_risk_management(str(matrix_path), str(record_path), swe_ids=[], fields={"risk_management_process": "d"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "risk-management.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_risk_management(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"risk_management_process": "d"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "risk-management.md"
    write_matrix(matrix_path, sample_rows())

    record_risk_management(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-086"],
        fields={"risk_management_process": "Continuous Risk Management process per docs/risk/risk-management-plan.md; risk list reviewed biweekly, residual risks after mitigation tracked to closure or formal acceptance."},
        evidence="docs/risk/risk-management-plan.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    assert updated[0]["status"] == "satisfied"
    assert updated[0]["date"] is not None

    content = record_path.read_text()
    assert "Continuous Risk Management" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "risk-management.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Risk Management (NPR 7150.2D §5.2)\n\n")

    record_risk_management(str(matrix_path), str(record_path), swe_ids=["SWE-086"], fields={"risk_management_process": "a"}, evidence="e1")
    record_risk_management(str(matrix_path), str(record_path), swe_ids=["SWE-086"], fields={"risk_management_process": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "risk-management.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_risk_management(str(matrix_path), str(record_path), swe_ids=["SWE-086"], fields={"risk_management_process": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-086")["status"] == "tailored-out"
