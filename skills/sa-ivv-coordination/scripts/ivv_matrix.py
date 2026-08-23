def render_ivv_matrix_markdown(rows, subsystem):
    lines = [
        f"# IV&V Verification Requirements Matrix — {subsystem}",
        "",
        "Source: NASA-STD-8739.8B §4.4.2. Requirement text is not reproduced here — "
        "each row cites the source standard by section.",
        "",
        "Applies uniformly once IV&V is confirmed applicable (see sa-ivv-coordination, "
        "§3.6.2/SWE-141) — there is no per-class filtering for this content.",
        "",
        "| Section | Citation |",
        "|---|---|",
    ]
    for r in rows:
        citation = f"NASA-STD-8739.8B §{r['section']}"
        lines.append(f"| {r['section']} | {citation} |")
    lines.append("")
    return "\n".join(lines)


def render_ivv_matrix_status_yaml(rows):
    """Fresh status rows for a subsystem's IV&V verification matrix.

    Unlike the SWE matrix, there's no software_class or default_approver to stamp:
    every row applies uniformly once IV&V is confirmed applicable, and tailoring
    authority is the fixed Project SMA Technical Authority (§4.4.2.3), not a
    per-row lookup.
    """
    return [
        {
            "ivv_id": r["id"],
            "section": r["section"],
            "status": "not-started",
            "evidence": None,
            "date": None,
        }
        for r in rows
    ]
