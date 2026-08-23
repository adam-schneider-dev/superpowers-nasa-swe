import pytest
from filter_matrix import (
    filter_rows_for_class,
    render_matrix_markdown,
    render_matrix_status_yaml,
)


def sample_rows():
    return [
        {
            "section": "4.1.5", "swe_id": "SWE-053", "class_ae_authority": "Center",
            "classes": {"A": True, "B": True, "C": True, "D": True, "E": False, "F": True},
            "class_f_authority": "CIO",
        },
        {
            "section": "4.2.3", "swe_id": "SWE-057", "class_ae_authority": "Center",
            "classes": {"A": True, "B": True, "C": True, "D": False, "E": False, "F": False},
            "class_f_authority": None,
        },
        {
            "section": "5.5.4", "swe_id": "SWE-204", "class_ae_authority": "Center",
            "classes": {"A": True, "B": True, "C": False, "D": False, "E": False, "F": False},
            "class_f_authority": None,
        },
    ]

def test_filter_returns_only_matching_class():
    rows = filter_rows_for_class(sample_rows(), "D")
    assert [r["swe_id"] for r in rows] == ["SWE-053"]

def test_filter_class_with_no_matches_returns_empty():
    # No fixture row carries a Class E mark.
    rows = filter_rows_for_class(sample_rows(), "E")
    assert rows == []

def test_filter_returns_class_f_rows():
    rows = filter_rows_for_class(sample_rows(), "F")
    assert [r["swe_id"] for r in rows] == ["SWE-053"]

def test_filter_rejects_an_unknown_class():
    with pytest.raises(ValueError, match="G"):
        filter_rows_for_class(sample_rows(), "G")

def test_filter_rejects_a_lowercase_class():
    with pytest.raises(ValueError):
        filter_rows_for_class(sample_rows(), "d")

def test_render_markdown_includes_citation_not_requirement_text():
    rows = filter_rows_for_class(sample_rows(), "B")
    md = render_matrix_markdown(rows, subsystem="widget-firmware", software_class="B")
    assert "NPR 7150.2D §4.1.5, SWE-053" in md
    assert "widget-firmware" in md
    assert "Class B" in md

def test_render_markdown_separates_the_two_authority_columns():
    rows = filter_rows_for_class(sample_rows(), "A")
    md = render_matrix_markdown(rows, subsystem="widget-firmware", software_class="A")
    assert "| Section | Citation | Class A-E Authority | Class F Authority |" in md
    # SWE-053 applies to Class F and names the CIO; SWE-057 does not and leaves it blank.
    assert "| 4.1.5 | NPR 7150.2D §4.1.5, SWE-053 | Center | CIO |" in md
    assert "| 4.2.3 | NPR 7150.2D §4.2.3, SWE-057 | Center |  |" in md

def test_render_markdown_rejects_an_unknown_class():
    with pytest.raises(ValueError):
        render_matrix_markdown(sample_rows(), subsystem="s", software_class="Z")

def test_render_status_yaml_defaults():
    rows = filter_rows_for_class(sample_rows(), "A")
    status_rows = render_matrix_status_yaml(rows, "A")
    assert len(status_rows) == 3
    assert all(r["status"] == "not-started" for r in status_rows)
    assert all(r["evidence"] is None for r in status_rows)
    assert all(r["date"] is None for r in status_rows)
    assert {r["swe_id"] for r in status_rows} == {"SWE-053", "SWE-057", "SWE-204"}
    # Every row records the class it was generated for, so staleness is checkable later.
    assert all(r["software_class"] == "A" for r in status_rows)


def test_render_status_yaml_stamps_the_class_it_was_generated_for():
    rows = filter_rows_for_class(sample_rows(), "F")
    status_rows = render_matrix_status_yaml(rows, "F")
    assert all(r["software_class"] == "F" for r in status_rows)

def test_render_status_yaml_carries_the_class_ae_authority_as_default_approver():
    rows = filter_rows_for_class(sample_rows(), "A")
    status_rows = render_matrix_status_yaml(rows, "A")
    assert all(r["default_approver"] == "Center" for r in status_rows)

def test_render_status_yaml_carries_the_class_f_authority_for_class_f():
    rows = filter_rows_for_class(sample_rows(), "F")
    status_rows = render_matrix_status_yaml(rows, "F")
    assert [r["default_approver"] for r in status_rows] == ["CIO"]

def test_render_status_yaml_rejects_an_unknown_class():
    with pytest.raises(ValueError):
        render_matrix_status_yaml(sample_rows(), "AB")
