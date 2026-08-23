# tests/test_sp2_end_to_end.py
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "classify-software", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "skills", "requirements-matrix", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "skills", "safety-critical-determination", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "skills", "lifecycle-planning", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "skills", "cost-estimation", "scripts"))

from amend_safety_critical import amend_safety_critical, mark_matrix_satisfied
from classify import classify
from filter_matrix import filter_rows_for_class, render_matrix_status_yaml
from record_cost_estimation import record_cost_estimation
from record_lifecycle_planning import record_lifecycle_planning


def test_full_pipeline_for_a_class_e_subsystem_found_safety_critical(tmp_path):
    # 1. Classify: design-concept tool, not initially flagged safety-critical -> Class E
    result = classify({
        "class_a_human_rated": False,
        "class_b_non_human_space_or_large_aero": False,
        "class_c_mission_support_or_facility": False,
        "class_d_basic_science_or_research": False,
        "class_e_design_concept_general_purpose": True,
        "is_safety_critical": False,
    })
    assert result["class"] == "E"

    classification = {
        "subsystem": "test-subsystem",
        "class": result["class"],
        "ambiguous": result["ambiguous"],
        "candidates": result["candidates"],
        "answers": {
            "class_a_human_rated": False,
            "class_b_non_human_space_or_large_aero": False,
            "class_c_mission_support_or_facility": False,
            "class_d_basic_science_or_research": False,
            "class_e_design_concept_general_purpose": True,
            "is_safety_critical": False,
        },
        "rationale": "Design-concept exploration tool, general-purpose environment.",
        "date": "2026-08-10",
    }
    classification_path = tmp_path / "classification.yaml"
    with open(classification_path, "w") as f:
        yaml.dump(classification, f, sort_keys=False)

    # 2. Load the real catalog (now covering Chapter 3) and generate a Class E matrix
    with open(os.path.join(ROOT, "data", "swe-catalog.yaml")) as f:
        catalog = yaml.safe_load(f)
    rows = filter_rows_for_class(catalog, "E")
    assert len(rows) > 0, "expected Class E rows now that Chapter 3 is transcribed"

    status_rows = render_matrix_status_yaml(rows, "E")
    matrix_yaml_path = tmp_path / "requirements-mapping-matrix.yaml"
    with open(matrix_yaml_path, "w") as f:
        yaml.dump(status_rows, f, sort_keys=False)

    # 3. safety-critical-determination finds it IS safety-critical -> bumps Class E to D
    with open(classification_path) as f:
        loaded_classification = yaml.safe_load(f)
    amended = amend_safety_critical(
        loaded_classification, is_safety_critical=True,
        rationale="Controls a function identified in a system hazard.",
    )
    assert amended["class"] == "D"
    with open(classification_path, "w") as f:
        yaml.dump(amended, f, sort_keys=False)

    swe_205_row = next((r for r in status_rows if r["swe_id"] == "SWE-205"), None)
    if swe_205_row is not None:
        mark_matrix_satisfied(str(matrix_yaml_path), "SWE-205", evidence="classification.yaml safety_critical_history[-1]")
        with open(matrix_yaml_path) as f:
            updated = yaml.safe_load(f)
        assert next(r for r in updated if r["swe_id"] == "SWE-205")["status"] == "satisfied"

    # 4. Regenerate the matrix for the new class (D) after the bump
    rows_for_d = filter_rows_for_class(catalog, "D")
    assert len(rows_for_d) > 0
    status_rows_d = render_matrix_status_yaml(rows_for_d, "D")
    with open(matrix_yaml_path, "w") as f:
        yaml.dump(status_rows_d, f, sort_keys=False)

    # 5. Record lifecycle planning and cost estimation against the regenerated Class D matrix
    lifecycle_ids = [r["swe_id"] for r in status_rows_d if r["section"] in ("3.1.2", "3.1.3")]
    if lifecycle_ids:
        record_lifecycle_planning(
            str(matrix_yaml_path), str(tmp_path / "lifecycle-planning.md"),
            swe_ids=lifecycle_ids,
            fields={"acquisition_or_development": "Develop internally"},
            evidence="docs/plans/software-management-plan.md",
        )

    cost_ids = [r["swe_id"] for r in status_rows_d if r["section"].startswith("3.2")]
    if cost_ids:
        record_cost_estimation(
            str(matrix_yaml_path), str(tmp_path / "cost-estimation.md"),
            swe_ids=cost_ids,
            fields={"methodology": "One model, Class D (§3.2.1c)"},
            evidence="docs/estimates/cost-basis.md",
        )

    with open(matrix_yaml_path) as f:
        final_matrix = yaml.safe_load(f)
    satisfied_ids = {r["swe_id"] for r in final_matrix if r["status"] == "satisfied"}
    assert satisfied_ids, "expected at least one row marked satisfied by the recorded skills"
