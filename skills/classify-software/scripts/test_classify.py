from classify import classify


def base_answers(**overrides):
    answers = {
        "class_a_human_rated": False,
        "class_b_non_human_space_or_large_aero": False,
        "class_c_mission_support_or_facility": False,
        "class_d_basic_science_or_research": False,
        "class_e_design_concept_general_purpose": False,
        "is_safety_critical": False,
    }
    answers.update(overrides)
    return answers

def test_class_a_human_rated_wins():
    result = classify(base_answers(class_a_human_rated=True))
    assert result["class"] == "A"
    assert result["ambiguous"] is False

def test_class_b_non_human_space():
    result = classify(base_answers(class_b_non_human_space_or_large_aero=True))
    assert result["class"] == "B"

def test_class_c_mission_support():
    result = classify(base_answers(class_c_mission_support_or_facility=True))
    assert result["class"] == "C"

def test_class_d_basic_science():
    result = classify(base_answers(class_d_basic_science_or_research=True))
    assert result["class"] == "D"

def test_class_e_design_concept():
    result = classify(base_answers(class_e_design_concept_general_purpose=True))
    assert result["class"] == "E"

def test_no_criteria_match_falls_back_to_class_f():
    result = classify(base_answers())
    assert result["class"] == "F"
    assert result["ambiguous"] is False

def test_safety_critical_bumps_class_e_to_class_d():
    result = classify(base_answers(class_e_design_concept_general_purpose=True, is_safety_critical=True))
    assert result["class"] == "D"

def test_safety_critical_does_not_affect_class_a_through_d():
    result = classify(base_answers(class_c_mission_support_or_facility=True, is_safety_critical=True))
    assert result["class"] == "C"

def test_multiple_matching_classes_are_flagged_ambiguous_and_higher_wins():
    result = classify(base_answers(class_b_non_human_space_or_large_aero=True, class_d_basic_science_or_research=True))
    assert result["class"] == "B"
    assert result["ambiguous"] is True
    assert result["candidates"] == ["B", "D"]

def test_no_match_has_empty_candidates():
    result = classify(base_answers())
    assert result["candidates"] == []
