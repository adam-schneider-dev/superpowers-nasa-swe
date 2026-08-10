import yaml
import pytest
from record_cost_estimation import record_cost_estimation


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-015", "section": "3.2.1", "default_approver": None, "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-151", "section": "3.2.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-174", "section": "3.2.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "cost-estimation.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_cost_estimation(str(matrix_path), str(record_path), swe_ids=[], fields={"methodology": "m"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "cost-estimation.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_cost_estimation(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"methodology": "m"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "cost-estimation.md"
    write_matrix(matrix_path, sample_rows())

    record_cost_estimation(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-015", "SWE-151", "SWE-174"],
        fields={
            "methodology": "COCOMO II, one model (Class D project under $2M per §3.2.1c)",
            "basis_of_estimate": "docs/estimates/cost-basis.md",
            "size_and_effort_parameters": "12 KSLOC, 4 FTE-months",
        },
        evidence="docs/estimates/cost-basis.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "COCOMO" in content
    assert "SWE-015" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "cost-estimation.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Cost Estimation (NPR 7150.2D §3.2)\n\n")

    record_cost_estimation(str(matrix_path), str(record_path), swe_ids=["SWE-015"], fields={"methodology": "a"}, evidence="e1")
    record_cost_estimation(str(matrix_path), str(record_path), swe_ids=["SWE-151"], fields={"methodology": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "cost-estimation.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_cost_estimation(str(matrix_path), str(record_path), swe_ids=["SWE-015"], fields={"methodology": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-015")["status"] == "tailored-out"
