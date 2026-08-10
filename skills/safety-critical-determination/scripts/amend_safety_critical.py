import yaml
from classify import classify


def amend_safety_critical(classification, is_safety_critical, rationale, date):
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
    answers["is_safety_critical"] = is_safety_critical
    result = classify(answers)

    amended = dict(classification)
    amended["class"] = result["class"]
    amended["ambiguous"] = result["ambiguous"]
    amended["candidates"] = result["candidates"]
    amended["answers"] = answers
    amended["safety_critical_history"] = history + [
        {"date": date, "is_safety_critical": is_safety_critical, "rationale": rationale}
    ]
    return amended


def mark_matrix_satisfied(matrix_yaml_path, swe_id, evidence, date):
    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row = next((r for r in rows if r["swe_id"] == swe_id), None)
    if row is None:
        raise KeyError(f"{swe_id} not found in requirements mapping matrix")

    row["status"] = "satisfied"
    row["evidence"] = evidence
    row["date"] = date

    with open(matrix_yaml_path, "w") as f:
        yaml.dump(rows, f, sort_keys=False)
