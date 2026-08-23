
from ivv_matrix import render_ivv_matrix_markdown, render_ivv_matrix_status_yaml


def sample_rows():
    return [
        {"id": "IVV-4.4.2.1", "section": "4.4.2.1"},
        {"id": "IVV-4.4.2.2", "section": "4.4.2.2"},
    ]


def test_render_markdown_includes_citation_not_requirement_text():
    md = render_ivv_matrix_markdown(sample_rows(), subsystem="widget-firmware")
    assert "NASA-STD-8739.8B §4.4.2.1" in md
    assert "widget-firmware" in md


def test_render_markdown_lists_every_row():
    md = render_ivv_matrix_markdown(sample_rows(), subsystem="widget-firmware")
    assert "| 4.4.2.1 | NASA-STD-8739.8B §4.4.2.1 |" in md
    assert "| 4.4.2.2 | NASA-STD-8739.8B §4.4.2.2 |" in md


def test_render_status_yaml_defaults():
    status_rows = render_ivv_matrix_status_yaml(sample_rows())
    assert len(status_rows) == 2
    assert all(r["status"] == "not-started" for r in status_rows)
    assert all(r["evidence"] is None for r in status_rows)
    assert all(r["date"] is None for r in status_rows)
    assert {r["ivv_id"] for r in status_rows} == {"IVV-4.4.2.1", "IVV-4.4.2.2"}


def test_render_status_yaml_carries_section():
    status_rows = render_ivv_matrix_status_yaml(sample_rows())
    assert {r["section"] for r in status_rows} == {"4.4.2.1", "4.4.2.2"}
