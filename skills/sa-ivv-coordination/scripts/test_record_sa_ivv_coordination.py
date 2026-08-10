import yaml
import pytest
from record_sa_ivv_coordination import record_sa_ivv_coordination


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-022", "section": "3.6.1", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "sa-ivv-coordination.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_sa_ivv_coordination(str(matrix_path), str(record_path), swe_ids=[], fields={"roles": "r"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "sa-ivv-coordination.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_sa_ivv_coordination(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"roles": "r"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "sa-ivv-coordination.md"
    write_matrix(matrix_path, sample_rows())

    record_sa_ivv_coordination(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-022"],
        fields={
            "sa_safety_ivv_roles": "Jane Doe (SA lead), John Roe (software safety)",
            "plan_reference": "docs/plans/software-assurance-plan.md",
        },
        evidence="docs/plans/software-assurance-plan.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    assert updated[0]["status"] == "satisfied"
    assert updated[0]["date"] is not None

    content = record_path.read_text()
    assert "Jane Doe" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "sa-ivv-coordination.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Assurance and IV&V Coordination (NPR 7150.2D §3.6)\n\n")

    record_sa_ivv_coordination(str(matrix_path), str(record_path), swe_ids=["SWE-022"], fields={"sa_safety_ivv_roles": "a"}, evidence="e1")
    record_sa_ivv_coordination(str(matrix_path), str(record_path), swe_ids=["SWE-022"], fields={"sa_safety_ivv_roles": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "sa-ivv-coordination.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_sa_ivv_coordination(str(matrix_path), str(record_path), swe_ids=["SWE-022"], fields={"sa_safety_ivv_roles": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-022")["status"] == "tailored-out"
