# tests/test_sp1_end_to_end.py
import sys
import os
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "classify-software", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "skills", "requirements-matrix", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "skills", "tailoring-request", "scripts"))

from classify import classify
from filter_matrix import filter_rows_for_class, render_matrix_markdown, render_matrix_status_yaml
from add_tailoring_entry import add_tailoring_entry


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
    with open(os.path.join(ROOT, "data", "swe-catalog.yaml")) as f:
        catalog = yaml.safe_load(f)
    rows = filter_rows_for_class(catalog, "D")
    assert len(rows) > 0, "expected at least one Class D requirement in the populated catalog slice"

    md = render_matrix_markdown(rows, subsystem="test-subsystem", software_class="D")
    status_rows = render_matrix_status_yaml(rows)

    matrix_md_path = tmp_path / "requirements-mapping-matrix.md"
    matrix_yaml_path = tmp_path / "requirements-mapping-matrix.yaml"
    matrix_md_path.write_text(md)
    with open(matrix_yaml_path, "w") as f:
        yaml.dump(status_rows, f, sort_keys=False)

    assert "Class D" in matrix_md_path.read_text()
    assert all(r["status"] == "not-started" for r in status_rows)

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
