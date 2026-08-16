import yaml
import pytest
from record_peer_review_record import record_peer_review_record


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-087", "section": "5.3.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-088", "section": "5.3.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-089", "section": "5.3.4", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "peer-review-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_peer_review_record(str(matrix_path), str(record_path), swe_ids=[], fields={"reviews_performed": "d"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "peer-review-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_peer_review_record(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"reviews_performed": "d"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "peer-review-record.md"
    write_matrix(matrix_path, sample_rows())

    record_peer_review_record(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-087", "SWE-088", "SWE-089"],
        fields={
            "reviews_performed": "Requirements, plans (incl. cybersecurity), the design items flagged in the software development plan, code, and test procedures all peer-reviewed via requesting-code-review/receiving-code-review; results reported in PR #142.",
            "review_procedure": "Checklist-based review (docs/reviews/peer-review-checklist.md), readiness/completion criteria in the same doc, action items tracked in Jira until resolved, required participants named per review type.",
            "review_measurements": "Defect counts and review duration recorded per review in docs/reviews/review-log.md.",
        },
        evidence="https://github.com/example/repo/pull/142",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "PR #142" in content
    assert "SWE-088" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "peer-review-record.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Peer Reviews/Inspections (NPR 7150.2D §5.3)\n\n")

    record_peer_review_record(str(matrix_path), str(record_path), swe_ids=["SWE-087"], fields={"reviews_performed": "a"}, evidence="e1")
    record_peer_review_record(str(matrix_path), str(record_path), swe_ids=["SWE-088"], fields={"review_procedure": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "peer-review-record.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_peer_review_record(str(matrix_path), str(record_path), swe_ids=["SWE-087"], fields={"reviews_performed": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-087")["status"] == "tailored-out"
