import pytest

from sa_task_matrix import (
    filter_sa_task_rows_for_class,
    render_sa_task_matrix_markdown,
    render_sa_task_matrix_status_yaml,
)


def sample_sa_task_rows():
    return [
        {"swe_id": "SWE-033", "section": "3.1.2"},
        {"swe_id": "SWE-013", "section": "3.1.3"},
    ]


def sample_swe_catalog_rows():
    return [
        {
            "section": "3.1.2", "swe_id": "SWE-033",
            "class_ae_authority": "Center",
            "classes": {"A": True, "B": True, "C": True, "D": True, "E": True, "F": True},
            "class_f_authority": "CIO",
        },
        {
            "section": "3.1.3", "swe_id": "SWE-013",
            "class_ae_authority": "Center",
            "classes": {"A": True, "B": True, "C": True, "D": True, "E": False, "F": True},
            "class_f_authority": "CIO",
        },
    ]


def test_filter_keeps_only_rows_applicable_to_class():
    rows = filter_sa_task_rows_for_class(
        sample_sa_task_rows(), sample_swe_catalog_rows(), "E"
    )
    assert [r["swe_id"] for r in rows] == ["SWE-033"]


def test_filter_rejects_invalid_class():
    with pytest.raises(ValueError, match="software class"):
        filter_sa_task_rows_for_class(sample_sa_task_rows(), sample_swe_catalog_rows(), "Z")


def test_render_markdown_includes_citation_not_task_text():
    md = render_sa_task_matrix_markdown(sample_sa_task_rows(), subsystem="widget-firmware", software_class="C")
    assert "NASA-STD-8739.8B §4.3 Table 1" in md
    assert "NPR 7150.2D §3.1.2" in md
    assert "SWE-033" in md
    assert "widget-firmware" in md


def test_render_markdown_lists_every_row():
    md = render_sa_task_matrix_markdown(sample_sa_task_rows(), subsystem="widget-firmware", software_class="C")
    assert "| 3.1.2 |" in md
    assert "| 3.1.3 |" in md


def test_render_status_yaml_defaults():
    status_rows = render_sa_task_matrix_status_yaml(sample_sa_task_rows(), software_class="C")
    assert len(status_rows) == 2
    assert all(r["status"] == "not-started" for r in status_rows)
    assert all(r["evidence"] is None for r in status_rows)
    assert all(r["date"] is None for r in status_rows)
    assert all(r["software_class"] == "C" for r in status_rows)
    assert {r["swe_id"] for r in status_rows} == {"SWE-033", "SWE-013"}


def test_render_status_yaml_has_no_default_approver_field():
    status_rows = render_sa_task_matrix_status_yaml(sample_sa_task_rows(), software_class="C")
    assert "default_approver" not in status_rows[0]
