# skills/measurements/scripts/test_record_measurements.py
import yaml
import pytest
from record_measurements import record_measurements


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-090", "section": "5.4.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-093", "section": "5.4.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-094", "section": "5.4.4", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-199", "section": "5.4.5", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-200", "section": "5.4.6", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "measurements.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_measurements(str(matrix_path), str(record_path), swe_ids=[], fields={"measurement_program": "d"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "measurements.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_measurements(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"measurement_program": "d"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "measurements.md"
    write_matrix(matrix_path, sample_rows())

    record_measurements(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-090", "SWE-093", "SWE-094", "SWE-199", "SWE-200"],
        fields={
            "measurement_program": "Effort, defect density, and schedule variance collected monthly per docs/measurement/measurement-plan.md.",
            "analysis_procedure": "Trend analysis per Center measurement handbook procedure MH-04.",
            "data_access": "Measurement dashboard shared with the Mission Directorate, Chief Engineer, Center Technical Authorities, and HQ SMA on request.",
            "performance_monitoring": "CPU/memory margin tracked against requirements each build; reported in the monthly status report.",
            "requirements_volatility": "Requirements-change rate tracked in the requirements tool, reported monthly.",
        },
        evidence="docs/measurement/measurement-plan.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "Trend analysis" in content
    assert "SWE-200" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "measurements.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Measurements (NPR 7150.2D §5.4)\n\n")

    record_measurements(str(matrix_path), str(record_path), swe_ids=["SWE-090"], fields={"measurement_program": "a"}, evidence="e1")
    record_measurements(str(matrix_path), str(record_path), swe_ids=["SWE-093"], fields={"analysis_procedure": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "measurements.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_measurements(str(matrix_path), str(record_path), swe_ids=["SWE-090"], fields={"measurement_program": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-090")["status"] == "tailored-out"
