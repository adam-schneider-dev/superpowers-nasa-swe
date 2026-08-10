import yaml
import pytest
from record_lifecycle_planning import record_lifecycle_planning


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-033", "section": "3.1.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-013", "section": "3.1.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "lifecycle-planning.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_lifecycle_planning(str(matrix_path), str(record_path), swe_ids=[], fields={"acquisition_or_development": "Develop internally"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "lifecycle-planning.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_lifecycle_planning(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"acquisition_or_development": "Develop internally"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "lifecycle-planning.md"
    write_matrix(matrix_path, sample_rows())

    record_lifecycle_planning(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-033", "SWE-013"],
        fields={
            "acquisition_or_development": "Develop internally (NPR 7150.2D §3.1.2 option b)",
            "plans_reference": "docs/plans/software-management-plan.md",
        },
        evidence="docs/plans/software-management-plan.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["evidence"] == "docs/plans/software-management-plan.md"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "SWE-033" in content
    assert "SWE-013" in content
    assert "Develop internally" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "lifecycle-planning.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Life Cycle Planning (NPR 7150.2D §3.1)\n\n")

    record_lifecycle_planning(str(matrix_path), str(record_path), swe_ids=["SWE-033"], fields={"acquisition_or_development": "a"}, evidence="e1")
    record_lifecycle_planning(str(matrix_path), str(record_path), swe_ids=["SWE-013"], fields={"acquisition_or_development": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2
