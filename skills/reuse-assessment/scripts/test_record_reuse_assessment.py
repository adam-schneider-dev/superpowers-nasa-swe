import yaml
import pytest
from record_reuse_assessment import record_reuse_assessment


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-147", "section": "3.10.1", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-148", "section": "3.10.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "reuse-assessment.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_reuse_assessment(str(matrix_path), str(record_path), swe_ids=[], fields={"component_name": "c"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "reuse-assessment.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_reuse_assessment(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"component_name": "c"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "reuse-assessment.md"
    write_matrix(matrix_path, sample_rows())

    record_reuse_assessment(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-147", "SWE-148"],
        fields={
            "component_name": "libfoo-parser",
            "description": "Third-party XML parsing library",
            "technical_poc": "Jane Doe",
            "language": "C++",
            "third_party_license_info": "MIT, see vendor/libfoo/LICENSE",
        },
        evidence="vendor/libfoo/LICENSE",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"

    content = record_path.read_text()
    assert "libfoo-parser" in content


def test_appends_one_entry_per_component(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "reuse-assessment.md"
    write_matrix(matrix_path, sample_rows())

    record_reuse_assessment(str(matrix_path), str(record_path), swe_ids=["SWE-147"], fields={"component_name": "libfoo"}, evidence="e1")
    record_reuse_assessment(str(matrix_path), str(record_path), swe_ids=["SWE-148"], fields={"component_name": "libbar"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2
    assert "libfoo" in content
    assert "libbar" in content
