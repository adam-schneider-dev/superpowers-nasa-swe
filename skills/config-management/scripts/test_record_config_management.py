import pytest
import yaml
from record_config_management import record_config_management


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-079", "section": "5.1.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-080", "section": "5.1.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-081", "section": "5.1.4", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-082", "section": "5.1.5", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-083", "section": "5.1.6", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-084", "section": "5.1.7", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-085", "section": "5.1.8", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-045", "section": "5.1.9", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "config-management.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_config_management(str(matrix_path), str(record_path), swe_ids=[], fields={"cm_plan": "d"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "config-management.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_config_management(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"cm_plan": "d"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "config-management.md"
    write_matrix(matrix_path, sample_rows())

    record_config_management(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-079", "SWE-080", "SWE-081", "SWE-082", "SWE-083", "SWE-084", "SWE-085", "SWE-045"],
        fields={
            "cm_plan": "docs/cm/software-configuration-management-plan.md",
            "change_tracking": "Jira project SCM, all software-product changes filed as issues.",
            "configuration_items": "Source repo tags, build scripts, and the toolchain manifest are all under version control.",
            "change_control_procedures": "Two-level CCB: engineering lead approves minor changes, project CCB approves baseline changes; documented in the CM plan.",
            "status_records": "Git tags plus a build manifest checked into the release branch.",
            "configuration_audits": "Quarterly physical/functional configuration audits per the CM plan's audit schedule.",
            "storage_release_procedures": "Release process documented in docs/cm/release-procedure.md; deliverables stored in the artifact registry.",
            "joint_audit_participation": "Project CM lead represents the project in any joint NASA/developer audit.",
        },
        evidence="docs/cm/software-configuration-management-plan.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "Two-level CCB" in content
    assert "SWE-045" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "config-management.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Configuration Management (NPR 7150.2D §5.1)\n\n")

    record_config_management(str(matrix_path), str(record_path), swe_ids=["SWE-079"], fields={"cm_plan": "a"}, evidence="e1")
    record_config_management(str(matrix_path), str(record_path), swe_ids=["SWE-080"], fields={"change_tracking": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "config-management.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_config_management(str(matrix_path), str(record_path), swe_ids=["SWE-079"], fields={"cm_plan": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-079")["status"] == "tailored-out"
