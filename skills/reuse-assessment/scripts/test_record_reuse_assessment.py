import pytest
import yaml
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


def test_marks_swe_027_satisfied_for_an_incoming_component(tmp_path):
    """Part 2 of the skill (§3.1.14/SWE-027) records suitability of an INCOMING component."""
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "reuse-assessment.md"
    write_matrix(matrix_path, sample_rows() + [
        {"swe_id": "SWE-027", "section": "3.1.14", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ])

    record_reuse_assessment(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-027"],
        fields={
            "component_name": "libfoo-parser",
            "requirements_identified": "REQ-014, REQ-015 — XML ingest",
            "documentation": "vendor/libfoo/docs/usage.md",
            "ip_rights_coordination": "MIT license reviewed with Center IP Counsel 2026-07-02",
            "future_support_plan": "Vendor LTS through 2030; fork mirrored internally",
            "verification_validation_level": "Same unit/integration suite as in-house parsers",
            "vendor_defect_assessment_plan": "Quarterly review of vendor CVE/defect feed",
        },
        evidence="docs/reuse/libfoo-suitability.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    swe_027 = next(r for r in updated if r["swe_id"] == "SWE-027")
    assert swe_027["status"] == "satisfied"
    assert swe_027["evidence"] == "docs/reuse/libfoo-suitability.md"
    assert swe_027["date"] is not None
    # The outbound-contribution rows are untouched by an incoming-component assessment.
    assert next(r for r in updated if r["swe_id"] == "SWE-147")["status"] == "not-started"

    content = record_path.read_text()
    assert "SWE-027" in content
    assert "Center IP Counsel" in content


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "reuse-assessment.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_reuse_assessment(str(matrix_path), str(record_path), swe_ids=["SWE-147"], fields={"component_name": "c"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-147")["status"] == "tailored-out"
