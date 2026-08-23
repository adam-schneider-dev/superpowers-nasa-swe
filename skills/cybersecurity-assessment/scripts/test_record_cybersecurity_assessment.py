import pytest
import yaml
from record_cybersecurity_assessment import record_cybersecurity_assessment


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-156", "section": "3.11.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-154", "section": "3.11.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "cybersecurity-assessment.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_cybersecurity_assessment(str(matrix_path), str(record_path), swe_ids=[], fields={"risk_categorization": "r"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "cybersecurity-assessment.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_cybersecurity_assessment(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"risk_categorization": "r"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "cybersecurity-assessment.md"
    write_matrix(matrix_path, sample_rows())

    record_cybersecurity_assessment(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-156", "SWE-154"],
        fields={
            "risk_categorization": "Moderate, per Center RMF categorization",
            "control_basis": "docs/security/ato.md",
            "cots_reused_component_risks": "libfoo-parser reviewed, no known CVEs at time of assessment",
        },
        evidence="docs/security/ato.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"

    content = record_path.read_text()
    assert "Moderate" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "cybersecurity-assessment.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Cybersecurity Assessment (NPR 7150.2D §3.11)\n\n")

    record_cybersecurity_assessment(str(matrix_path), str(record_path), swe_ids=["SWE-156"], fields={"risk_categorization": "a"}, evidence="e1")
    record_cybersecurity_assessment(str(matrix_path), str(record_path), swe_ids=["SWE-154"], fields={"risk_categorization": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "cybersecurity-assessment.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_cybersecurity_assessment(str(matrix_path), str(record_path), swe_ids=["SWE-156"], fields={"risk_categorization": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-156")["status"] == "tailored-out"
