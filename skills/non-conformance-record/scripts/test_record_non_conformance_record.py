# skills/non-conformance-record/scripts/test_record_non_conformance_record.py
import yaml
import pytest
from record_non_conformance_record import record_non_conformance_record


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-201", "section": "5.5.1", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-202", "section": "5.5.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-203", "section": "5.5.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-204", "section": "5.5.4", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "non-conformance-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_non_conformance_record(str(matrix_path), str(record_path), swe_ids=[], fields={"tracking_mechanism": "d"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "non-conformance-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_non_conformance_record(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"tracking_mechanism": "d"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "non-conformance-record.md"
    write_matrix(matrix_path, sample_rows())

    record_non_conformance_record(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-201", "SWE-202", "SWE-203", "SWE-204"],
        fields={
            "tracking_mechanism": "Jira project NCR tracks non-conformances across software, tools, and ground software.",
            "severity_levels": "Four levels defined in docs/quality/severity-levels.md: loss-of-life/vehicle, mission-success, user-visible-with-workaround, other.",
            "reused_component_assessment": "All COTS/GOTS/MOTS/OSS/reused components go through mandatory pre-flight assessment per docs/quality/reuse-assessment-procedure.md.",
            "high_severity_process_assessment": "Closed-loop process assessment triggered automatically for any high-severity NCR per the same procedure doc.",
        },
        evidence="docs/quality/severity-levels.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "Closed-loop" in content
    assert "SWE-204" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "non-conformance-record.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Non-conformance or Defect Management (NPR 7150.2D §5.5)\n\n")

    record_non_conformance_record(str(matrix_path), str(record_path), swe_ids=["SWE-201"], fields={"tracking_mechanism": "a"}, evidence="e1")
    record_non_conformance_record(str(matrix_path), str(record_path), swe_ids=["SWE-202"], fields={"severity_levels": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "non-conformance-record.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_non_conformance_record(str(matrix_path), str(record_path), swe_ids=["SWE-201"], fields={"tracking_mechanism": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-201")["status"] == "tailored-out"
