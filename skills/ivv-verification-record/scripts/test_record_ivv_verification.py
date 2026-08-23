import pytest
import yaml
from record_ivv_verification import record_ivv_verification


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"ivv_id": "IVV-4.4.2.1", "section": "4.4.2.1", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_ivv_ids(tmp_path):
    matrix_path = tmp_path / "ivv-mapping-matrix.yaml"
    record_path = tmp_path / "ivv-verification-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="ivv_id"):
        record_ivv_verification(str(matrix_path), str(record_path), ivv_ids=[], fields={"planning_and_ipep": "p"}, evidence="ev")


def test_blocks_unknown_ivv_id(tmp_path):
    matrix_path = tmp_path / "ivv-mapping-matrix.yaml"
    record_path = tmp_path / "ivv-verification-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="IVV-4.4.2.99"):
        record_ivv_verification(str(matrix_path), str(record_path), ivv_ids=["IVV-4.4.2.99"], fields={"planning_and_ipep": "p"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "ivv-mapping-matrix.yaml"
    record_path = tmp_path / "ivv-verification-record.md"
    write_matrix(matrix_path, sample_rows())

    record_ivv_verification(
        str(matrix_path), str(record_path),
        ivv_ids=["IVV-4.4.2.1"],
        fields={"planning_and_ipep": "IPEP concurred by Center SMA TA 2026-08-20, docs/ivv/ipep.md"},
        evidence="docs/ivv/ipep.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    assert updated[0]["status"] == "satisfied"
    assert updated[0]["date"] is not None

    content = record_path.read_text()
    assert "Center SMA TA" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "ivv-mapping-matrix.yaml"
    record_path = tmp_path / "ivv-verification-record.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# IV&V Verification Record (NASA-STD-8739.8B §4.4.2)\n\n")

    record_ivv_verification(str(matrix_path), str(record_path), ivv_ids=["IVV-4.4.2.1"], fields={"planning_and_ipep": "a"}, evidence="e1")
    record_ivv_verification(str(matrix_path), str(record_path), ivv_ids=["IVV-4.4.2.1"], fields={"planning_and_ipep": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "ivv-mapping-matrix.yaml"
    record_path = tmp_path / "ivv-verification-record.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_ivv_verification(str(matrix_path), str(record_path), ivv_ids=["IVV-4.4.2.1"], fields={"planning_and_ipep": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["ivv_id"] == "IVV-4.4.2.1")["status"] == "tailored-out"
