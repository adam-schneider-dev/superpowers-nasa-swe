def filter_rows_for_class(rows, software_class):
    return [r for r in rows if r["classes"].get(software_class, False)]


def render_matrix_markdown(rows, subsystem, software_class):
    lines = [
        f"# Requirements Mapping Matrix — {subsystem} (Class {software_class})",
        "",
        "Source: NPR 7150.2D Appendix C. Requirement text is not reproduced here — "
        "each row cites the source standard by section and SWE-id.",
        "",
        "| Section | Citation | Responsible Role | Technical Authority | TA Required |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        citation = f"NPR 7150.2D §{r['section']}, {r['swe_id']}"
        ta = r["technical_authority"] or ""
        ta_required = "Yes" if r["ta_required"] else "No"
        lines.append(f"| {r['section']} | {citation} | {r['responsible_role']} | {ta} | {ta_required} |")
    lines.append("")
    return "\n".join(lines)


def render_matrix_status_yaml(rows):
    return [
        {
            "swe_id": r["swe_id"],
            "section": r["section"],
            "status": "not-started",
            "evidence": None,
            "date": None,
        }
        for r in rows
    ]
