import re

REQUIRED_FIELDS = {"section", "swe_id", "class_ae_authority", "classes", "class_f_authority"}
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
        classes_ok = isinstance(classes, dict) and set(classes.keys()) == CLASS_KEYS
        if not classes_ok:
            errors.append(f"row {i}: classes must have exactly keys {sorted(CLASS_KEYS)}")
        elif not all(isinstance(v, bool) for v in classes.values()):
            errors.append(f"row {i}: classes values must all be bool")
            classes_ok = False

        if not isinstance(row["class_ae_authority"], str) or not row["class_ae_authority"]:
            errors.append(f"row {i}: class_ae_authority must be a non-empty string")

        if row["class_f_authority"] is not None and not isinstance(row["class_f_authority"], str):
            errors.append(f"row {i}: class_f_authority must be a string or null")

        # Appendix C leaves the "Class F Authority" cell blank on every row whose
        # Class F applicability column is unmarked, so an authority without an F
        # mark means the two columns were read out of alignment.
        #
        # The converse is NOT checked: §3.2.1 / SWE-015 really does carry an F mark
        # with a blank Class F Authority cell in the source, so requiring an
        # authority on every Class F row would reject a correct transcription.
        if classes_ok and isinstance(row["class_f_authority"], str) and not classes["F"]:
            errors.append(
                f"row {i}: class_f_authority is set but classes.F is false "
                "(Appendix C leaves the Class F Authority cell blank when Class F is not invoked)"
            )

    return errors
