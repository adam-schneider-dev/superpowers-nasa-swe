import datetime

import yaml


def amend_safety_critical(classification, is_safety_critical, rationale):
    # Imported inside the function so mark_matrix_satisfied — which never classifies anything —
    # can be used without classify-software/scripts on sys.path.
    from classify import classify

    history = classification.get("safety_critical_history", [])
    if history and history[-1]["is_safety_critical"] != is_safety_critical:
        raise ValueError(
            f"conflicting safety-critical determination for subsystem "
            f"{classification.get('subsystem')!r}: prior determination on "
            f"{history[-1]['date']} recorded is_safety_critical="
            f"{history[-1]['is_safety_critical']}, this run found "
            f"is_safety_critical={is_safety_critical}. Resolve manually before amending."
        )

    answers = dict(classification["answers"])
    prior = answers.get("is_safety_critical")

    # On the very first amendment there is no history to compare against, but classify-software
    # may already have recorded an affirmative safety-critical answer. Dropping that answer here
    # would silently rewrite the class (e.g. D back to E) with nothing to show a reviewer that a
    # safety-critical designation was ever made. Guard that case the same way as a history
    # conflict — but only when the class actually changes, since an unaffected class (e.g. C,
    # which the Appendix D bump does not touch) has nothing to lose.
    if not history and prior and not is_safety_critical:
        kept = dict(answers)
        kept["is_safety_critical"] = True
        dropped = dict(answers)
        dropped["is_safety_critical"] = False
        if classify(kept)["class"] != classify(dropped)["class"]:
            raise ValueError(
                f"conflicting safety-critical determination for subsystem "
                f"{classification.get('subsystem')!r}: classify-software's original "
                f"determination recorded is_safety_critical=True, this run found "
                f"is_safety_critical={is_safety_critical}, and the difference changes the "
                f"software class ({classify(kept)['class']} -> {classify(dropped)['class']}). "
                f"Resolve manually before amending."
            )

    answers["is_safety_critical"] = is_safety_critical
    result = classify(answers)

    amended = dict(classification)
    amended["class"] = result["class"]
    amended["ambiguous"] = result["ambiguous"]
    amended["candidates"] = result["candidates"]
    amended["answers"] = answers
    amended["safety_critical_history"] = history + [
        {
            "date": datetime.date.today().isoformat(),
            "is_safety_critical": is_safety_critical,
            "rationale": rationale,
        }
    ]
    return amended


def mark_matrix_satisfied(matrix_yaml_path, swe_id, evidence):
    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row = next((r for r in rows if r["swe_id"] == swe_id), None)
    if row is None:
        raise KeyError(f"{swe_id} not found in requirements mapping matrix")

    row["status"] = "satisfied"
    row["evidence"] = evidence
    row["date"] = datetime.date.today().isoformat()

    with open(matrix_yaml_path, "w") as f:
        yaml.dump(rows, f, sort_keys=False)
