import yaml
import pytest
from record_traceability import record_traceability


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-052", "section": "3.12.1", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "traceability.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_traceability(str(matrix_path), str(record_path), swe_ids=[], fields={"mechanism": "m"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "traceability.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_traceability(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"mechanism": "m"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "traceability.md"
    write_matrix(matrix_path, sample_rows())

    record_traceability(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-052"],
        fields={
            "mechanism": "Requirements linked in the project's issue tracker via a 'traces-to' field",
            "linkage_locations": "higher-level reqs -> SWE reqs -> design -> code -> verification, per Table 1 links required for this subsystem's class",
        },
        evidence="issue-tracker query: traces-to:SWE-*",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    assert updated[0]["status"] == "satisfied"

    content = record_path.read_text()
    assert "traces-to" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "traceability.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Bi-Directional Traceability (NPR 7150.2D §3.12)\n\n")

    record_traceability(str(matrix_path), str(record_path), swe_ids=["SWE-052"], fields={"mechanism": "a"}, evidence="e1")
    record_traceability(str(matrix_path), str(record_path), swe_ids=["SWE-052"], fields={"mechanism": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2
