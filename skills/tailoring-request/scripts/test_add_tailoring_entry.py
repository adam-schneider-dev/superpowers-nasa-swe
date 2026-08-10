import yaml
import pytest
from add_tailoring_entry import add_tailoring_entry

def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)

def sample_rows():
    # Same shape render_matrix_status_yaml emits, including the default_approver
    # field the tailoring-request skill offers as the default approving authority.
    return [
        {"swe_id": "SWE-057", "section": "4.2.3", "default_approver": "Center",
         "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-058", "section": "4.3.2", "default_approver": "Center",
         "status": "not-started", "evidence": None, "date": None},
    ]

def test_blocks_without_approver(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    log_path = tmp_path / "tailoring-log.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="approver"):
        add_tailoring_entry(
            str(matrix_path), str(log_path),
            swe_id="SWE-057", rationale="r", risk="low", mitigation="m", approver="",
        )

def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    log_path = tmp_path / "tailoring-log.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        add_tailoring_entry(
            str(matrix_path), str(log_path),
            swe_id="SWE-999", rationale="r", risk="low", mitigation="m", approver="Jane TA",
        )

def test_updates_matrix_status_and_writes_log(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    log_path = tmp_path / "tailoring-log.md"
    write_matrix(matrix_path, sample_rows())

    add_tailoring_entry(
        str(matrix_path), str(log_path),
        swe_id="SWE-057", rationale="Not applicable to CLI tool", risk="Low",
        mitigation="Manual review substitutes", approver="Jane TA",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    row = next(r for r in updated if r["swe_id"] == "SWE-057")
    assert row["status"] == "tailored-out"
    assert row["date"] is not None

    other = next(r for r in updated if r["swe_id"] == "SWE-058")
    assert other["status"] == "not-started"

    log_content = log_path.read_text()
    assert "SWE-057" in log_content
    assert "Not applicable to CLI tool" in log_content
    assert "Jane TA" in log_content

def test_appends_to_existing_log(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    log_path = tmp_path / "tailoring-log.md"
    write_matrix(matrix_path, sample_rows())
    log_path.write_text("# Tailoring Log\n\n")

    add_tailoring_entry(
        str(matrix_path), str(log_path),
        swe_id="SWE-057", rationale="r1", risk="low", mitigation="m1", approver="A",
    )
    add_tailoring_entry(
        str(matrix_path), str(log_path),
        swe_id="SWE-058", rationale="r2", risk="low", mitigation="m2", approver="B",
    )

    content = log_path.read_text()
    assert content.count("## SWE-") == 2
