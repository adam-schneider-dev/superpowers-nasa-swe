CLASS_ORDER = ["A", "B", "C", "D", "E"]
ANSWER_KEY_FOR_CLASS = {
    "A": "class_a_human_rated",
    "B": "class_b_non_human_space_or_large_aero",
    "C": "class_c_mission_support_or_facility",
    "D": "class_d_basic_science_or_research",
    "E": "class_e_design_concept_general_purpose",
}


def classify(answers):
    candidates = [c for c in CLASS_ORDER if answers.get(ANSWER_KEY_FOR_CLASS[c], False)]

    if not candidates:
        return {"class": "F", "ambiguous": False, "candidates": []}

    chosen = candidates[0]

    # Appendix D, Class E definition item 3: Class E cannot be safety-critical.
    if chosen == "E" and answers.get("is_safety_critical", False):
        chosen = "D"

    return {
        "class": chosen,
        "ambiguous": len(candidates) > 1,
        "candidates": candidates,
    }
