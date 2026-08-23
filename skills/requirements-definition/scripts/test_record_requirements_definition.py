import pytest
import yaml
from record_requirements_definition import record_requirements_definition


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-050", "section": "4.1.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-051", "section": "4.1.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "requirements-definition.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_requirements_definition(str(matrix_path), str(record_path), swe_ids=[], fields={"requirements_capture": "r"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "requirements-definition.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_requirements_definition(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"requirements_capture": "r"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "requirements-definition.md"
    write_matrix(matrix_path, sample_rows())

    record_requirements_definition(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-050", "SWE-051"],
        fields={
            "requirements_capture": "Requirements captured in DOORS, baselined at PDR, includes 2 reused OSS components.",
            "requirements_analysis": "Flowed down from L2 systems requirements SYS-014, SYS-019; hardware spec HW-003.",
        },
        evidence="docs/requirements/software-requirements-spec.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "DOORS" in content
    assert "SWE-050" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "requirements-definition.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Requirements (NPR 7150.2D §4.1)\n\n")

    record_requirements_definition(str(matrix_path), str(record_path), swe_ids=["SWE-050"], fields={"requirements_capture": "a"}, evidence="e1")
    record_requirements_definition(str(matrix_path), str(record_path), swe_ids=["SWE-051"], fields={"requirements_capture": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "requirements-definition.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_requirements_definition(str(matrix_path), str(record_path), swe_ids=["SWE-050"], fields={"requirements_capture": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-050")["status"] == "tailored-out"
