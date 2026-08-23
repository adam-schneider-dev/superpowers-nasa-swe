from filter_matrix import _check_class, filter_rows_for_class


def filter_sa_task_rows_for_class(sa_task_rows, swe_catalog_rows, software_class):
    """SA-task rows carry no class marks of their own — applicability is inherited
    from the same swe_id's class marks in swe-catalog.yaml, reusing filter_matrix's
    own class filter rather than duplicating its validation and lookup logic.
    """
    applicable_ids = {r["swe_id"] for r in filter_rows_for_class(swe_catalog_rows, software_class)}
    return [r for r in sa_task_rows if r["swe_id"] in applicable_ids]


def render_sa_task_matrix_markdown(rows, subsystem, software_class):
    _check_class(software_class)
    lines = [
        f"# Software Assurance & Safety Task Matrix — {subsystem} (Class {software_class})",
        "",
        "Source: NASA-STD-8739.8B §4.3 Table 1 (Chapter 3 / Software Management rows "
        "only — see data/SA-TASK-CATALOG-COVERAGE.md for full coverage status). Task "
        "text is not reproduced here — each row cites the source standard and the "
        "underlying NPR 7150.2D requirement by section and SWE-id.",
        "",
        "Applicability is inherited from the same SWE-id's class marks in the main "
        "Requirements Mapping Matrix — this table has no class columns of its own.",
        "",
        "| Section | Citation |",
        "|---|---|",
    ]
    for r in rows:
        citation = f"NASA-STD-8739.8B §4.3 Table 1, NPR 7150.2D §{r['section']}, {r['swe_id']}"
        lines.append(f"| {r['section']} | {citation} |")
    lines.append("")
    return "\n".join(lines)


def render_sa_task_matrix_status_yaml(rows, software_class):
    """Fresh status rows for one class.

    No default_approver field, unlike the main matrix — Table 1 tailoring authority
    is an open design question this sub-spec deliberately defers (see the spec's
    Open Risks); do not add one without a fresh design decision.
    """
    _check_class(software_class)
    return [
        {
            "swe_id": r["swe_id"],
            "section": r["section"],
            "software_class": software_class,
            "status": "not-started",
            "evidence": None,
            "date": None,
        }
        for r in rows
    ]
