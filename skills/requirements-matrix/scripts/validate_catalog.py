import re

REQUIRED_FIELDS = {"section", "swe_id", "responsible_role", "classes", "technical_authority", "ta_required"}
CLASS_KEYS = {"A", "B", "C", "D", "E", "F"}
SWE_ID_RE = re.compile(r"^SWE-\d+$")


def validate_catalog(rows):
    errors = []
    seen_ids = set()

    for i, row in enumerate(rows):
        missing = REQUIRED_FIELDS - row.keys()
        for field in missing:
            errors.append(f"row {i}: missing required field '{field}'")
        if missing:
            continue

        if not SWE_ID_RE.match(row["swe_id"]):
            errors.append(f"row {i}: swe_id '{row['swe_id']}' does not match required format 'SWE-<digits>'")
        elif row["swe_id"] in seen_ids:
            errors.append(f"row {i}: duplicate swe_id '{row['swe_id']}'")
        else:
            seen_ids.add(row["swe_id"])

        classes = row["classes"]
        if not isinstance(classes, dict) or set(classes.keys()) != CLASS_KEYS:
            errors.append(f"row {i}: classes must have exactly keys {sorted(CLASS_KEYS)}")
        elif not all(isinstance(v, bool) for v in classes.values()):
            errors.append(f"row {i}: classes values must all be bool")

        if row["technical_authority"] is not None and not isinstance(row["technical_authority"], str):
            errors.append(f"row {i}: technical_authority must be a string or null")

        if not isinstance(row["ta_required"], bool):
            errors.append(f"row {i}: ta_required must be a bool")

    return errors
