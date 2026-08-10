from filter_matrix import filter_rows_for_class, render_matrix_markdown, render_matrix_status_yaml

def sample_rows():
    return [
        {
            "section": "4.1.5", "swe_id": "SWE-053", "responsible_role": "Center",
            "classes": {"A": True, "B": True, "C": True, "D": True, "E": False, "F": False},
            "technical_authority": "CIO", "ta_required": True,
        },
        {
            "section": "4.2.3", "swe_id": "SWE-057", "responsible_role": "Center",
            "classes": {"A": True, "B": True, "C": True, "D": False, "E": False, "F": False},
            "technical_authority": None, "ta_required": False,
        },
        {
            "section": "5.5.4", "swe_id": "SWE-204", "responsible_role": "Center",
            "classes": {"A": True, "B": True, "C": False, "D": False, "E": False, "F": False},
            "technical_authority": None, "ta_required": False,
        },
    ]

def test_filter_returns_only_matching_class():
    rows = filter_rows_for_class(sample_rows(), "D")
    assert [r["swe_id"] for r in rows] == ["SWE-053"]

def test_filter_class_with_no_matches_returns_empty():
    rows = filter_rows_for_class(sample_rows(), "F")
    assert rows == []

def test_render_markdown_includes_citation_not_requirement_text():
    rows = filter_rows_for_class(sample_rows(), "B")
    md = render_matrix_markdown(rows, subsystem="widget-firmware", software_class="B")
    assert "NPR 7150.2D §4.1.5, SWE-053" in md
    assert "widget-firmware" in md
    assert "Class B" in md

def test_render_status_yaml_defaults():
    rows = filter_rows_for_class(sample_rows(), "A")
    status_rows = render_matrix_status_yaml(rows)
    assert len(status_rows) == 3
    assert all(r["status"] == "not-started" for r in status_rows)
    assert all(r["evidence"] is None for r in status_rows)
    assert all(r["date"] is None for r in status_rows)
    assert {r["swe_id"] for r in status_rows} == {"SWE-053", "SWE-057", "SWE-204"}
