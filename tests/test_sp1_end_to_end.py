# tests/test_sp1_end_to_end.py
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "classify-software", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "skills", "requirements-matrix", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "skills", "tailoring-request", "scripts"))

from add_tailoring_entry import add_tailoring_entry
from classify import classify
from filter_matrix import filter_rows_for_class, render_matrix_markdown, render_matrix_status_yaml


def load_catalog():
    with open(os.path.join(ROOT, "data", "swe-catalog.yaml")) as f:
        return yaml.safe_load(f)


def test_full_pipeline_for_a_class_d_subsystem(tmp_path):
    # 1. Classify: a research/engineering tool with no safety implications -> Class D
    result = classify({
        "class_a_human_rated": False,
        "class_b_non_human_space_or_large_aero": False,
        "class_c_mission_support_or_facility": False,
        "class_d_basic_science_or_research": True,
        "class_e_design_concept_general_purpose": False,
        "is_safety_critical": False,
    })
    assert result["class"] == "D"

    # 2. Load the real catalog and filter to Class D
    catalog = load_catalog()
    rows = filter_rows_for_class(catalog, "D")
    assert len(rows) > 0, "expected at least one Class D requirement in the populated catalog slice"

    md = render_matrix_markdown(rows, subsystem="test-subsystem", software_class="D")
    status_rows = render_matrix_status_yaml(rows, "D")

    matrix_md_path = tmp_path / "requirements-mapping-matrix.md"
    matrix_yaml_path = tmp_path / "requirements-mapping-matrix.yaml"
    matrix_md_path.write_text(md)
    with open(matrix_yaml_path, "w") as f:
        yaml.dump(status_rows, f, sort_keys=False)

    assert "Class D" in matrix_md_path.read_text()
    assert all(r["status"] == "not-started" for r in status_rows)
    # tailoring-request reads its default approver out of this file, so it has to be there.
    # Not a specific string: Appendix C names several Class A-E authorities (§3.11.2-3.11.7 read
    # "Center and Center CIO", §3.6.2 "HQ OSMA", §3.9.2 "HQ OCE and HQ OSMA").
    assert all(r["default_approver"] for r in status_rows)

    # 3. Tailor out the first requirement
    first_id = status_rows[0]["swe_id"]
    log_path = tmp_path / "tailoring-log.md"
    add_tailoring_entry(
        str(matrix_yaml_path), str(log_path),
        swe_id=first_id, rationale="Not applicable to a CLI-only tool",
        risk="Low — no external interface", mitigation="Manual code review",
        approver="Project Lead",
    )

    with open(matrix_yaml_path) as f:
        updated = yaml.safe_load(f)
    tailored_row = next(r for r in updated if r["swe_id"] == first_id)
    assert tailored_row["status"] == "tailored-out"
    assert first_id in log_path.read_text()


def test_full_pipeline_for_a_class_f_subsystem(tmp_path):
    """Class F is the business/IT case — before the Appendix C column fix its matrix was empty."""
    result = classify({
        "class_a_human_rated": False,
        "class_b_non_human_space_or_large_aero": False,
        "class_c_mission_support_or_facility": False,
        "class_d_basic_science_or_research": False,
        "class_e_design_concept_general_purpose": False,
        "is_safety_critical": False,
    })
    assert result["class"] == "F"

    rows = filter_rows_for_class(load_catalog(), "F")
    assert len(rows) == 65, "Appendix C marks Class F on 65 of the 100 transcribed rows"

    md = render_matrix_markdown(rows, subsystem="payroll-tool", software_class="F")
    status_rows = render_matrix_status_yaml(rows, "F")

    assert "Class F" in md
    # Class F tailoring is approved by the CIO, not the Center (NPR 7150.2D §2.1.5.4).
    for r in status_rows:
        if r["swe_id"] == "SWE-015":
            assert r["default_approver"] is None, (
                "§3.2.1/SWE-015 has no named Class F Authority in the source standard"
            )
        else:
            assert r["default_approver"] == "CIO"

    matrix_yaml_path = tmp_path / "requirements-mapping-matrix.yaml"
    log_path = tmp_path / "tailoring-log.md"
    with open(matrix_yaml_path, "w") as f:
        yaml.dump(status_rows, f, sort_keys=False)

    # Pick by "has an approver" rather than by index: SWE-015 carries no Class F Authority, so a
    # shift in catalog order could otherwise land index 0 on a row with nothing to approve it.
    approvable_row = next(r for r in status_rows if r["default_approver"])

    add_tailoring_entry(
        str(matrix_yaml_path), str(log_path),
        swe_id=approvable_row["swe_id"], rationale="Handled by the enterprise IT process",
        risk="Low", mitigation="Existing ITSM change control",
        approver=approvable_row["default_approver"],
    )

    assert "CIO" in log_path.read_text()
