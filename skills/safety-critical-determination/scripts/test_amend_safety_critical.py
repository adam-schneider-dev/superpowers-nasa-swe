import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "classify-software", "scripts"))
sys.path.insert(0, os.path.dirname(__file__))

import yaml
import pytest
from amend_safety_critical import amend_safety_critical, mark_matrix_satisfied


def base_classification(**overrides):
    classification = {
        "subsystem": "widget-firmware",
        "class": "E",
        "ambiguous": False,
        "candidates": [],
        "answers": {
            "class_a_human_rated": False,
            "class_b_non_human_space_or_large_aero": False,
            "class_c_mission_support_or_facility": False,
            "class_d_basic_science_or_research": False,
            "class_e_design_concept_general_purpose": True,
            "is_safety_critical": False,
        },
        "rationale": "General-purpose board-top tool, no operational use.",
        "date": "2026-01-01",
    }
    classification.update(overrides)
    return classification


def test_amending_to_safety_critical_bumps_class_e_to_d():
    result = amend_safety_critical(
        base_classification(), is_safety_critical=True,
        rationale="Controls a function identified in a new system hazard.", date="2026-08-10",
    )
    assert result["class"] == "D"
    assert result["answers"]["is_safety_critical"] is True


def test_amending_does_not_affect_class_a_through_d():
    classification = base_classification()
    classification["class"] = "C"
    classification["answers"]["class_e_design_concept_general_purpose"] = False
    classification["answers"]["class_c_mission_support_or_facility"] = True

    result = amend_safety_critical(classification, is_safety_critical=True, rationale="r", date="2026-08-10")
    assert result["class"] == "C"


def test_original_rationale_field_is_untouched():
    classification = base_classification()
    result = amend_safety_critical(classification, is_safety_critical=True, rationale="r", date="2026-08-10")
    assert result["rationale"] == classification["rationale"]


def test_first_amendment_has_no_conflict_even_if_answers_default_disagreed():
    classification = base_classification()
    assert classification["answers"]["is_safety_critical"] is False
    result = amend_safety_critical(classification, is_safety_critical=True, rationale="r", date="2026-08-10")
    assert result["safety_critical_history"][0]["is_safety_critical"] is True


def test_conflicting_second_amendment_raises():
    classification = base_classification()
    first = amend_safety_critical(classification, is_safety_critical=True, rationale="first", date="2026-08-10")
    with pytest.raises(ValueError, match="conflicting"):
        amend_safety_critical(first, is_safety_critical=False, rationale="second", date="2026-08-11")


def test_matching_second_amendment_appends_history_without_conflict():
    classification = base_classification()
    first = amend_safety_critical(classification, is_safety_critical=True, rationale="first", date="2026-08-10")
    second = amend_safety_critical(first, is_safety_critical=True, rationale="reconfirmed", date="2026-09-01")
    assert len(second["safety_critical_history"]) == 2
    assert second["safety_critical_history"][1]["rationale"] == "reconfirmed"


def test_mark_matrix_satisfied_updates_matching_row(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    with open(matrix_path, "w") as f:
        yaml.dump([{"swe_id": "SWE-205", "section": "3.7.1", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None}], f)

    mark_matrix_satisfied(str(matrix_path), "SWE-205", evidence="classification.yaml safety_critical_history[-1]", date="2026-08-10")

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    assert updated[0]["status"] == "satisfied"
    assert updated[0]["evidence"] == "classification.yaml safety_critical_history[-1]"
    assert updated[0]["date"] == "2026-08-10"


def test_mark_matrix_satisfied_unknown_id_raises(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    with open(matrix_path, "w") as f:
        yaml.dump([{"swe_id": "SWE-205", "section": "3.7.1", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None}], f)

    with pytest.raises(KeyError, match="SWE-999"):
        mark_matrix_satisfied(str(matrix_path), "SWE-999", evidence="e", date="2026-08-10")
