VALID_CLASSES = ("A", "B", "C", "D", "E", "F")


def _check_class(software_class):
    if software_class not in VALID_CLASSES:
        raise ValueError(
            f"software_class {software_class!r} is not a NASA software class; "
            f"expected one of {', '.join(VALID_CLASSES)}"
        )


def default_approver_for(row, software_class):
    """The Appendix C authority that approves tailoring of this row for this class.

    Class F rows are approved by the "Class F Authority" column (the NASA/Center CIO,
    per NPR 7150.2D §2.1.5.4); Classes A-E by the "Class A-E Authority" column.
    """
    _check_class(software_class)
    if software_class == "F":
        return row["class_f_authority"]
    return row["class_ae_authority"]


def filter_rows_for_class(rows, software_class):
    _check_class(software_class)
    return [r for r in rows if r["classes"].get(software_class, False)]


def render_matrix_markdown(rows, subsystem, software_class):
    _check_class(software_class)
    lines = [
        f"# Requirements Mapping Matrix — {subsystem} (Class {software_class})",
        "",
        "Source: NPR 7150.2D Appendix C. Requirement text is not reproduced here — "
        "each row cites the source standard by section and SWE-id.",
        "",
        "The two authority columns are Appendix C's own: \"Class A-E Authority\" governs tailoring "
        "for Classes A-E, \"Class F Authority\" governs it for Class F. Only the column matching "
        "this matrix's class is the operative one.",
        "",
        "| Section | Citation | Class A-E Authority | Class F Authority |",
        "|---|---|---|---|",
    ]
    for r in rows:
        citation = f"NPR 7150.2D §{r['section']}, {r['swe_id']}"
        f_authority = r["class_f_authority"] or ""
        lines.append(f"| {r['section']} | {citation} | {r['class_ae_authority']} | {f_authority} |")
    lines.append("")
    return "\n".join(lines)


def render_matrix_status_yaml(rows, software_class):
    """Fresh status rows for one class.

    Every row is stamped with the `software_class` it was generated for. Regeneration resets
    status/evidence/date, so the stamp is what lets a later caller tell a matrix that matches the
    subsystem's current `classification.yaml` from one left over from a previous class.
    """
    _check_class(software_class)
    return [
        {
            "swe_id": r["swe_id"],
            "section": r["section"],
            "software_class": software_class,
            "default_approver": default_approver_for(r, software_class),
            "status": "not-started",
            "evidence": None,
            "date": None,
        }
        for r in rows
    ]
