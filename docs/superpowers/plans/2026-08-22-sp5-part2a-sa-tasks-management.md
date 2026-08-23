# SP5 Part 2a: SA/Safety Tasks, Management (NPR Ch.3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new `sa-task-verification-management` skill that records NASA-STD-8739.8B §4.3 Table 1's Chapter 3 (Management) SA/safety-task confirmations — 45 rows, one per existing `swe-catalog.yaml` SWE-id — backed by a new parallel catalog/matrix, plus an extension to the existing `requirements-matrix` skill that generates the new matrix alongside the main one.

**Architecture:** A new `data/sa-task-catalog.yaml` (45 rows this sub-spec, growing to 103 across Parts 2a-2c) is a pure `swe_id`/`section` index — no task text stored, matching `swe-catalog.yaml` and `ivv-catalog.yaml`. `requirements-matrix` already computes the class filter every subsystem needs; it gains one more step that joins the new catalog against that same filter (via `filter_rows_for_class`, reused) and writes a parallel `sa-task-mapping-matrix.yaml`/`.md`. Recording follows the established `record_*.py` precedent exactly: one script, one function, three mandated error paths, Markdown output, keyed on `swe_id` (no new id namespace needed, since every row already has one).

**Tech Stack:** Python 3, PyYAML, pytest — matches every existing skill in this repo. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-08-22-sp5-part2a-sa-tasks-management-design.md`

## Global Constraints

- No requirement or task text is ever stored in `data/sa-task-catalog.yaml` — cite by `swe_id`/`section` only, same as `data/swe-catalog.yaml` and `data/ivv-catalog.yaml`. All paraphrase lives only in `sa-task-verification-management/SKILL.md`'s interview prose.
- `sa-task-mapping-matrix.yaml` rows carry `swe_id`, `section`, `software_class`, `status`, `evidence`, `date` — **no `default_approver` field**. Tailoring authority for Table 1 rows is an open risk deferred by the spec, not designed here; do not invent one.
- Every record script's three mandated error paths, verbatim behavior: empty id list → `ValueError`; unknown id → `KeyError`; attempting to mark an already-`tailored-out` row `satisfied` → `ValueError` with the matrix left unmodified on disk.
- Record output is always Markdown, appended (never overwritten) to `docs/nasa-compliance/<subsystem>/<topic>.md` — never YAML.
- No `SKILL.md` interview question may reproduce 3+ consecutive words from `reference/NASA-STD-8739.8B.pdf`'s §4.3 Table 1 text, and no question may present its underlying tasks in the same relative order the standard lists them in (the fork's single most recurring defect). Every one of this plan's 14 interview questions has already been deliberately reordered relative to the source — most are stated in reverse order relative to how the standard lists their underlying tasks — for this reason; do not "clean up" that ordering to look more logical during implementation.
- All `cd` commands in this plan target the worktree at `/home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management` — branch `worktree-worktree-sp5-part2a-sa-tasks-management`, not `main`. Do not adapt paths to point at the main checkout.

---

### Task 1: `data/sa-task-catalog.yaml` + coverage doc + integrity test

**Files:**
- Create: `data/sa-task-catalog.yaml`
- Create: `data/SA-TASK-CATALOG-COVERAGE.md`
- Test: `tests/test_sa_task_catalog_integrity.py`

**Interfaces:**
- Produces: `data/sa-task-catalog.yaml` — a list of 45 dicts, each `{"swe_id": "SWE-<n>", "section": "<NPR section>"}`, in NPR 7150.2D Appendix C / Table 1 order. Tasks 2 and 5 read this file.

- [ ] **Step 1: Write the failing test**

Create `tests/test_sa_task_catalog_integrity.py`:

```python
# tests/test_sa_task_catalog_integrity.py
"""Guards data/sa-task-catalog.yaml (NASA-STD-8739.8B §4.3 Table 1's Chapter 3
rows) against a bad edit or transcription pass — same purpose as
test_catalog_integrity.py for the SWE catalog and test_ivv_catalog_integrity.py
for the IV&V catalog. Scoped to this sub-spec's 45 Chapter 3 rows; Parts 2b/2c
will extend (not replace) these assertions as they add Chapter 4/5 rows.
"""
import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SA_TASK_CATALOG_PATH = os.path.join(ROOT, "data", "sa-task-catalog.yaml")
SWE_CATALOG_PATH = os.path.join(ROOT, "data", "swe-catalog.yaml")


def load_sa_task_catalog():
    with open(SA_TASK_CATALOG_PATH) as f:
        return yaml.safe_load(f)


def load_swe_catalog():
    with open(SWE_CATALOG_PATH) as f:
        return yaml.safe_load(f)


def test_bundled_sa_task_catalog_has_45_rows():
    assert len(load_sa_task_catalog()) == 45


def test_every_swe_id_is_unique():
    catalog = load_sa_task_catalog()
    ids = [r["swe_id"] for r in catalog]
    assert len(ids) == len(set(ids))


def test_every_row_has_no_task_text_fields():
    for row in load_sa_task_catalog():
        assert set(row.keys()) == {"swe_id", "section"}


def test_every_swe_id_exists_in_swe_catalog():
    sa_task_ids = {r["swe_id"] for r in load_sa_task_catalog()}
    swe_catalog_ids = {r["swe_id"] for r in load_swe_catalog()}
    assert sa_task_ids.issubset(swe_catalog_ids)


def test_section_matches_swe_catalog_section_for_every_row():
    swe_sections = {r["swe_id"]: r["section"] for r in load_swe_catalog()}
    for row in load_sa_task_catalog():
        assert row["section"] == swe_sections[row["swe_id"]]


def test_all_rows_are_chapter_3():
    for row in load_sa_task_catalog():
        assert row["section"].startswith("3.")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management && python3 -m pytest tests/test_sa_task_catalog_integrity.py -v`
Expected: FAIL — `FileNotFoundError` (or similar) because `data/sa-task-catalog.yaml` does not exist yet.

- [ ] **Step 3: Create `data/sa-task-catalog.yaml`**

```yaml
# SA Task Catalog — NASA-STD-8739.8B §4.3 Table 1, Software Assurance and
# Software Safety Tasks Mapping Matrix
#
# Coverage: 45 of the table's 103 total rows — NPR 7150.2D Chapter 3
# (Software Management) only. See data/SA-TASK-CATALOG-COVERAGE.md for the
# full coverage status; Chapters 4 and 5 are separate, not-yet-built
# sub-projects (SP5 Parts 2b/2c).
#
# Every row's swe_id matches an existing row in data/swe-catalog.yaml —
# Table 1 has no per-class applicability of its own; a row's applicability
# is inherited from the same swe_id's class marks in that catalog. No task
# text is stored here — same convention as swe-catalog.yaml and
# ivv-catalog.yaml: cite by swe_id/section only, paraphrase lives in the
# sa-task-verification-management skill's SKILL.md interview prose.
#
# Rows are in Table 1's own order (which matches Appendix C order for every
# shared swe_id).
- swe_id: "SWE-033"
  section: "3.1.2"
- swe_id: "SWE-013"
  section: "3.1.3"
- swe_id: "SWE-024"
  section: "3.1.4"
- swe_id: "SWE-034"
  section: "3.1.5"
- swe_id: "SWE-036"
  section: "3.1.6"
- swe_id: "SWE-037"
  section: "3.1.7"
- swe_id: "SWE-039"
  section: "3.1.8"
- swe_id: "SWE-040"
  section: "3.1.9"
- swe_id: "SWE-042"
  section: "3.1.10"
- swe_id: "SWE-139"
  section: "3.1.11"
- swe_id: "SWE-121"
  section: "3.1.12"
- swe_id: "SWE-125"
  section: "3.1.13"
- swe_id: "SWE-027"
  section: "3.1.14"
- swe_id: "SWE-015"
  section: "3.2.1"
- swe_id: "SWE-151"
  section: "3.2.2"
- swe_id: "SWE-174"
  section: "3.2.3"
- swe_id: "SWE-016"
  section: "3.3.1"
- swe_id: "SWE-018"
  section: "3.3.2"
- swe_id: "SWE-046"
  section: "3.3.3"
- swe_id: "SWE-017"
  section: "3.4.1"
- swe_id: "SWE-020"
  section: "3.5.1"
- swe_id: "SWE-176"
  section: "3.5.2"
- swe_id: "SWE-022"
  section: "3.6.1"
- swe_id: "SWE-141"
  section: "3.6.2"
- swe_id: "SWE-131"
  section: "3.6.3"
- swe_id: "SWE-178"
  section: "3.6.4"
- swe_id: "SWE-179"
  section: "3.6.5"
- swe_id: "SWE-205"
  section: "3.7.1"
- swe_id: "SWE-023"
  section: "3.7.2"
- swe_id: "SWE-134"
  section: "3.7.3"
- swe_id: "SWE-219"
  section: "3.7.4"
- swe_id: "SWE-220"
  section: "3.7.5"
- swe_id: "SWE-146"
  section: "3.8.1"
- swe_id: "SWE-206"
  section: "3.8.2"
- swe_id: "SWE-032"
  section: "3.9.2"
- swe_id: "SWE-147"
  section: "3.10.1"
- swe_id: "SWE-148"
  section: "3.10.2"
- swe_id: "SWE-156"
  section: "3.11.2"
- swe_id: "SWE-154"
  section: "3.11.3"
- swe_id: "SWE-157"
  section: "3.11.4"
- swe_id: "SWE-159"
  section: "3.11.5"
- swe_id: "SWE-207"
  section: "3.11.6"
- swe_id: "SWE-185"
  section: "3.11.7"
- swe_id: "SWE-210"
  section: "3.11.8"
- swe_id: "SWE-052"
  section: "3.12.1"
```

- [ ] **Step 4: Create `data/SA-TASK-CATALOG-COVERAGE.md`**

```markdown
# SA Task Catalog Coverage

**`data/sa-task-catalog.yaml` covers 45 of NASA-STD-8739.8B §4.3 Table 1's 103 rows.**

Table 1 splits cleanly along NPR 7150.2D's own chapter boundaries — the same
ones SP2/SP3/SP4 used to build `data/swe-catalog.yaml` and its 13 record
skills. This catalog is being built the same way, one chapter at a time.

## Covered — Chapter 3, Software Management, 45 rows (SP5 Part 2a)

- 3.1 Software Life Cycle Planning
- 3.2 Software Cost Estimation
- 3.3 Software Schedules
- 3.4 Software Training
- 3.5 Software Classification Assessments
- 3.6 Software Assurance and Software Independent Verification & Validation
- 3.7 Safety-Critical and Mission-Critical Software
- 3.8 Automatic Generation of Software Source Code
- 3.9 Software Development Processes and Practices
- 3.10 Software Reuse
- 3.11 Software Cybersecurity
- 3.12 Software Bi-Directional Traceability

## Not yet covered

- **Chapter 4, Software Engineering, 37 rows** — SP5 Part 2b, not started.
- **Chapter 5, Supporting Lifecycle, 21 rows** — SP5 Part 2c, not started.

`requirements-matrix`'s `sa-task-mapping-matrix.yaml` output reflects
whatever this catalog currently covers — a subsystem generated before Parts
2b/2c land gets a Chapter-3-only SA-task matrix. Re-running `requirements-matrix`
after either lands picks up the newly added rows.

## Verifying coverage

```bash
python3 -c "
import yaml
with open('data/sa-task-catalog.yaml') as f:
    rows = yaml.safe_load(f)
print(len(rows), 'rows')
print(sorted({r['section'].split('.')[0] for r in rows}))
"
```
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management && python3 -m pytest tests/test_sa_task_catalog_integrity.py -v`
Expected: PASS — 6 tests.

- [ ] **Step 6: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management
git add data/sa-task-catalog.yaml data/SA-TASK-CATALOG-COVERAGE.md tests/test_sa_task_catalog_integrity.py
git commit -m "feat: add SA task catalog (NASA-STD-8739.8B §4.3 Table 1, Ch.3, 45 rows)"
```

---

### Task 2: `sa_task_matrix.py` filter/render functions + tests

**Files:**
- Create: `skills/requirements-matrix/scripts/sa_task_matrix.py`
- Test: `skills/requirements-matrix/scripts/test_sa_task_matrix.py`

**Interfaces:**
- Consumes: `filter_rows_for_class(rows, software_class)` from `skills/requirements-matrix/scripts/filter_matrix.py` (already exists — reused, not reimplemented). Takes `sa_task_catalog` rows shaped `{"swe_id": str, "section": str}` (Task 1's shape) and `swe_catalog` rows shaped like `data/swe-catalog.yaml` (has a `"classes"` dict).
- Produces: `filter_sa_task_rows_for_class(sa_task_rows, swe_catalog_rows, software_class) -> list[dict]`, `render_sa_task_matrix_markdown(rows, subsystem, software_class) -> str`, `render_sa_task_matrix_status_yaml(rows, software_class) -> list[dict]`, each dict `{"swe_id": str, "section": str, "software_class": str, "status": "not-started", "evidence": None, "date": None}`. Task 3's record script consumes this exact row shape. Task 5's `requirements-matrix` extension calls all three functions by name.

- [ ] **Step 1: Write the failing test**

Create `skills/requirements-matrix/scripts/test_sa_task_matrix.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management/skills/requirements-matrix/scripts && python3 -m pytest test_sa_task_matrix.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sa_task_matrix'`.

- [ ] **Step 3: Write minimal implementation**

Create `skills/requirements-matrix/scripts/sa_task_matrix.py`:

```python
from filter_matrix import filter_rows_for_class, _check_class


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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management/skills/requirements-matrix/scripts && python3 -m pytest test_sa_task_matrix.py -v`
Expected: PASS — 7 tests.

- [ ] **Step 5: Run the full suite to confirm nothing broke**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management && python3 -m pytest --ignore=.claude -q`
Expected: PASS — all existing tests plus this task's new ones.

- [ ] **Step 6: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management
git add skills/requirements-matrix/scripts/sa_task_matrix.py skills/requirements-matrix/scripts/test_sa_task_matrix.py
git commit -m "feat: add SA task matrix filter/render functions"
```

---

### Task 3: `sa-task-verification-management` record script

**Files:**
- Create: `skills/sa-task-verification-management/scripts/record_sa_task_verification.py`
- Test: `skills/sa-task-verification-management/scripts/test_record_sa_task_verification.py`

**Interfaces:**
- Consumes: matrix rows shaped `{"swe_id": str, "section": str, "software_class": str, "status": str, "evidence": str|None, "date": str|None}` — exactly what Task 2's `render_sa_task_matrix_status_yaml` produces.
- Produces: `record_sa_task_verification(matrix_yaml_path, record_md_path, swe_ids, fields, evidence)`. Task 4's `SKILL.md` calls this function by this exact name and signature.

- [ ] **Step 1: Write the failing test**

Create `skills/sa-task-verification-management/scripts/test_record_sa_task_verification.py`:

```python
import yaml
import pytest
from record_sa_task_verification import record_sa_task_verification


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-033", "section": "3.1.2", "software_class": "C", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "sa-task-mapping-matrix.yaml"
    record_path = tmp_path / "sa-task-verification-management.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_sa_task_verification(str(matrix_path), str(record_path), swe_ids=[], fields={"acquisition_and_plan_setup": "p"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "sa-task-mapping-matrix.yaml"
    record_path = tmp_path / "sa-task-verification-management.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_sa_task_verification(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"acquisition_and_plan_setup": "p"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "sa-task-mapping-matrix.yaml"
    record_path = tmp_path / "sa-task-verification-management.md"
    write_matrix(matrix_path, sample_rows())

    record_sa_task_verification(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-033"],
        fields={"acquisition_and_plan_setup": "Acquisition risk assessment on file, docs/sa/acq-risk.md"},
        evidence="docs/sa/acq-risk.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    assert updated[0]["status"] == "satisfied"
    assert updated[0]["date"] is not None

    content = record_path.read_text()
    assert "Acquisition risk assessment" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "sa-task-mapping-matrix.yaml"
    record_path = tmp_path / "sa-task-verification-management.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Assurance & Safety Task Verification Record (NASA-STD-8739.8B §4.3 Table 1, Chapter 3)\n\n")

    record_sa_task_verification(str(matrix_path), str(record_path), swe_ids=["SWE-033"], fields={"acquisition_and_plan_setup": "a"}, evidence="e1")
    record_sa_task_verification(str(matrix_path), str(record_path), swe_ids=["SWE-033"], fields={"acquisition_and_plan_setup": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "sa-task-mapping-matrix.yaml"
    record_path = tmp_path / "sa-task-verification-management.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_sa_task_verification(str(matrix_path), str(record_path), swe_ids=["SWE-033"], fields={"acquisition_and_plan_setup": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-033")["status"] == "tailored-out"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management/skills/sa-task-verification-management/scripts && python3 -m pytest test_record_sa_task_verification.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'record_sa_task_verification'`.

- [ ] **Step 3: Write minimal implementation**

Create `skills/sa-task-verification-management/scripts/record_sa_task_verification.py`:

```python
import datetime
import yaml

DEFAULT_HEADER = (
    "# Software Assurance & Safety Task Verification Record "
    "(NASA-STD-8739.8B §4.3 Table 1, Chapter 3)\n\n"
)


def record_sa_task_verification(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
    if not swe_ids:
        raise ValueError("at least one swe_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["swe_id"]: r for r in rows}
    missing = [i for i in swe_ids if i not in row_by_id]
    if missing:
        raise KeyError(f"unknown swe_id(s) in SA task matrix: {', '.join(missing)}")

    for swe_id in swe_ids:
        if row_by_id[swe_id]["status"] == "tailored-out":
            raise ValueError(
                f"{swe_id} is already tailored-out — see tailoring-log.md; do not mark it "
                f"satisfied without first reviewing/reversing that tailoring entry"
            )

    today = datetime.date.today().isoformat()
    for swe_id in swe_ids:
        row_by_id[swe_id]["status"] = "satisfied"
        row_by_id[swe_id]["evidence"] = evidence
        row_by_id[swe_id]["date"] = today

    with open(matrix_yaml_path, "w") as f:
        yaml.dump(rows, f, sort_keys=False)

    try:
        with open(record_md_path) as f:
            existing = f.read()
    except FileNotFoundError:
        existing = DEFAULT_HEADER

    lines = [f"## Recorded {today}\n"]
    for key, value in fields.items():
        lines.append(f"- **{key}:** {value}")
    lines.append(f"- **Satisfies:** {', '.join(swe_ids)}")
    lines.append(f"- **Evidence:** {evidence}\n")
    entry = "\n".join(lines) + "\n"

    with open(record_md_path, "w") as f:
        f.write(existing + entry)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management/skills/sa-task-verification-management/scripts && python3 -m pytest test_record_sa_task_verification.py -v`
Expected: PASS — 5 tests.

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management
git add skills/sa-task-verification-management/scripts/record_sa_task_verification.py skills/sa-task-verification-management/scripts/test_record_sa_task_verification.py
git commit -m "feat: add sa-task-verification-management record logic"
```

---

### Task 4: `sa-task-verification-management` skill (`SKILL.md`)

**Files:**
- Create: `skills/sa-task-verification-management/SKILL.md`

**Interfaces:**
- Consumes: `record_sa_task_verification(matrix_yaml_path, record_md_path, swe_ids, fields, evidence)` from Task 3. Precondition file `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.yaml`, produced by Task 5's `requirements-matrix` extension.

No test — docs-only task, matching every SP1-4 `SKILL.md` task in this fork.

- [ ] **Step 1: Write `skills/sa-task-verification-management/SKILL.md`**

```markdown
---
name: sa-task-verification-management
description: Use to record a subsystem's NASA-STD-8739.8B §4.3 Table 1 software assurance and safety task evidence for NPR 7150.2D Chapter 3 (Management) requirements, once requirements-matrix has generated the SA task matrix
---

# Software Assurance & Safety Tasks — Management (NASA-STD-8739.8B §4.3 Table 1, NPR Ch.3)

## Overview

Records that software assurance and safety personnel actually performed the confirmation, assessment, and analysis tasks §4.3 Table 1 assigns against each Chapter 3 (Software Management) requirement, and where the evidence for each lives. Does not perform software assurance or safety work itself — that's real engineering and assurance work this tool doesn't replace.

**Announce at start:** "I'm using the sa-task-verification-management skill to record your NASA-STD-8739.8B §4.3 Table 1 software assurance and safety task evidence for NPR Chapter 3."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.yaml` to already exist with at least one Chapter 3 row for this subsystem's class. This file is generated by `requirements-matrix` alongside the main requirements matrix. If it's absent, or has no rows starting with `3.`, either this class has no applicable Chapter 3 rows or `requirements-matrix` hasn't been (re-)run since this catalog's rows existed — check there first, don't assume the chapter doesn't apply.

## The interview

Ask each group below in turn. For each, ask which of its listed SWE-ids have real, checkable evidence — an assurance assessment, a confirmed audit finding, a review record, a tracked risk or issue — and where that evidence lives. A vague "assurance handled it" answer is not sufficient, same standard `peer-review-record` and `ivv-verification-record` established: the evidence must point at something a human auditor could actually go check. If a SWE-id has no real evidence yet, leave it out of that group's `swe_ids` below rather than recording an unverifiable claim.

1. **Acquisition & plan setup (SWE-034, SWE-013, SWE-033).** Have software acceptance criteria been defined and checked against the Software Engineering Handbook's (NASA-HDBK-2203) guidance? Separately, are all life-cycle plans — security plans included — in place with tailoring that actually matches this software's classification, and has a Software Assurance Plan been written per HDBK-2203's content (safety included) and kept current? And for whichever acquisition path the project chose — enhancing or reusing an existing product, contracting the work out, developing it internally, acquiring an off-the-shelf product, or bringing in source code from outside NASA — was that choice actually evaluated, did the engineering/assurance/safety requirements flow down onto every acquisition activity, and were the risks of that decision assessed?
2. **Plan tracking & commitments (SWE-037, SWE-036, SWE-024).** Are the milestones at which the developer's progress gets reviewed and audited actually defined and documented, and does assurance personnel show up to those reviews? Separately: does the project confirm that any government action owed upon receiving a deliverable — an approval, a review — actually happens, and is the full set the project needs to run software development kept current and actually approved: the task list, the list of electronic deliverables, the documentation plans, and the processes themselves (including assurance, safety, and IV&V process)? And on the commitments side: are changes to commitments actually recorded and tracked rather than just verbally agreed to, are corrective actions closed out with documented rationale, and are the software plans still being checked for compliance against NPR 7150.2 and NASA-STD-8739.8 whenever something changes?
3. **Developer oversight & reporting (SWE-042, SWE-040, SWE-039).** Does NASA actually have electronic, modifiable access to the source code the project generates? Are software products, traceability data, change-tracking records, and nonconformance information likewise available to NASA electronically, development and management metrics included? And on the broader developer-oversight side — does the project manager both respond to and track assurance-raised issues through to closure, is there a maintained list of assurance discrepancies, risks, issues, and findings, are status reports actually produced, do audits of development process and practice happen on a cadence of at least once every 24 months, are trade studies, source data, reviews, and technical interchange meetings assessed, are verification activities analyzed for adequacy, is product integration actually monitored, and does the developer report status and give real insight into development and test work?
4. **Compliance & matrix maintenance (SWE-125, SWE-121, SWE-139).** Does the project maintain a requirements mapping matrix (or matrices) covering every NPR 7150.2 requirement — including one for NASA-STD-8739.8's own requirements? Where anything has been tailored out of that matrix, does the tailoring carry the required approval, and is there a separate tailoring matrix specifically for the assurance and safety requirements? And, stepping back, do the project's software requirements, products, procedures, and processes actually comply with NPR 7150.2 at the level its classification and safety criticality demand?
5. **Reuse, COTS & software reuse assurance (SWE-148, SWE-147, SWE-027).** When the project contributes something back as a reuse candidate, does the submission actually carry everything it needs — title, description, a named civil-servant technical point of contact, the language(s) used, a record of any third-party code and its license terms, release notes? Has the project also considered its own future reuse potential when planning development activities? And for anything the project itself acquires or reuses — commercial, government, open-source, or otherwise — have the necessary conditions been met: a plan to periodically check vendor-reported defects against the project's own use, verification and validation to the same bar as in-house code, adequate future-support planning, intellectual-property and licensing terms coordinated with Center Intellectual Property Counsel, sufficient documentation to fulfill its purpose, and clearly identified requirements the component needs to satisfy?
6. **Cost estimation (SWE-174, SWE-151, SWE-015).** Are the project's planning parameters — size and effort estimates, milestones, characteristics — actually submitted to the Center's measurement repository at major milestones, and are the assurance and safety side's own estimates and parameters likewise submitted to an organizational repository? Do the cost estimate(s) themselves hold up against the standard's criteria: capturing other direct costs, including the cost of required assurance support, factoring in risk and uncertainty including cybersecurity threat assessment, accounting for the maturation cost of the technology involved, grounded in the project's real attributes, and covering the whole software life cycle? And is the required number of cost estimates actually complete, with an assurance cost estimate included that separately accounts for handling safety-critical software and data?
7. **Schedule oversight (SWE-046, SWE-018, SWE-016).** When the developer provides an updated schedule, are the project's own schedules — including assurance's and safety's — updated to match? Are periodic reports on schedule activity, metrics, and status actually generated and distributed, covering assurance and safety's own schedule activity too, and are schedule issues tracked to closure? And does the software schedule itself hold up: does it account for dependencies with other projects and across programs, does it reflect the real critical-path dependencies for software development, does it document how milestones and deliverables interact across software, hardware, operations and the rest of the system, and does it coordinate with the overall project schedule — with a corresponding assurance schedule developed covering assurance's own products, audits, reporting, and reviews?
8. **Training & classification hygiene (SWE-176, SWE-020, SWE-017).** Are records kept — and kept current for the life of the project — of every classification determination made, every requirements mapping matrix produced, and the results of every independent classification assessment? Has a software classification actually been performed, or independently concurred with, using NPR 7150.2's class definitions? And on training: have assurance and safety personnel specifically completed the training needed to competently conduct assurance and safety work, and more broadly, is project-specific software training planned, tracked, and completed for personnel, assurance and safety staff included?
9. **SA/safety role & independence (SWE-179, SWE-178, SWE-131, SWE-141, SWE-022).** Where IV&V has raised issues or risks, does the project manager actually respond to them and track them to closure? Does IV&V, when engaged, have the access it needs to development artifacts, products, source code, and data to do its analysis efficiently and effectively? Where software IV&V is required, has an IV&V Project Execution Plan actually been developed, approved, kept current, and executed? For projects that trigger mandatory IV&V — Category 1 projects, Category 2 projects with Class A or B payload risk, or ones the Mission Directorate Associate Administrator specifically selected — are the §4.4 IV&V requirements actually being met? And, stepping back to the broader picture: is software assurance, software safety, and IV&V (where applicable) actually being performed per NASA-STD-8739.8 and the project's own Software Assurance Plan?
10. **Safety-critical & mission-critical software (SWE-220, SWE-219, SWE-134, SWE-023, SWE-205).** Take structural complexity and code coverage on identified safety-critical components: does each stay at or below a cyclomatic complexity value of 15, with any excursion above that reviewed and waived with a rationale accepted by the proper technical authority — and have complexity metrics actually been produced or analyzed for those components in the first place? Is 100% MC/DC test coverage addressed for each identified safety-critical component, with a documented, technically credible rationale wherever full coverage isn't achieved? Working from the actual implementation: does it support and stay consistent with the system hazard analysis, do reviews touching safety-critical products get assurance participation, has the design been analyzed for partitioning or isolation of safety-critical elements and data from everything that isn't, is it confirmed that the values of safety-critical loaded data, uplinked data, rules, and scripts affecting hazardous behavior have actually been tested, is the source code checked against the full safety-behavior list at every code inspection, test review, safety review, and project milestone, and were the requirements and design analyzed up front to make sure that behavior list gets implemented — error handling and the ability to reach a safe state, prerequisite checks before safety-critical commands execute and integrity checks on inputs and outputs, detecting and recovering from inadvertent memory changes, responding to off-nominal conditions in time to prevent a hazard and ensuring no single event or action can trigger one alone, rejecting commands received out of an order that would cause a hazard, requiring two independent operator actions to override a software function, and safely terminating and transitioning between operating states starting from a safe initialization at first start and every restart? And do the identified safety-critical components and data actually implement the safety-critical assurance requirements this standard sets out? Finally, at the hazard-tracking level: is a software safety analysis maintained across the whole development life cycle, does traceability exist between requirements and the hazards their software contributes to, and do hazard analyses and hazard reports actually identify the software components tied to system hazards and capture every known software contribution to one?
11. **Auto-generated code & dev practices (SWE-032, SWE-206, SWE-146).** For Class A and B software, are audits performed on both the development and assurance processes, are any process issues, findings, or risks the CMMI assessment turned up actually assessed, and is it being acquired, developed, and maintained by an organization holding a current CMMI-DEV maturity rating at the required level — 3 for Class A, 2 for Class B with the usual payload exception — from an accredited appraiser? Where software is auto-generated, do NASA, engineering, project, assurance, and IV&V all have electronic access to the models, simulations, and data used as generation inputs? And is the auto-generation approach itself actually defined and does it cover configuration management of the tool's inputs, outputs, and any later modifications, a policy for making manual changes to generated code, monitoring actual use against planned use, verifying and validating the generated code to the same standard as hand-written code, a stated scope for what auto-generated code may be used for, configuration management of the generation tools and their data, and verification/validation of the generation tools themselves?
12. **Cybersecurity, part 1 (SWE-159, SWE-157, SWE-154, SWE-156).** For the cybersecurity mitigations identified from the project's vulnerability and weakness analysis, is the quality of the mitigation testing and its results being assessed, and has testing actually been completed and recorded in the first place? For any software with communications capability, do the requirements, design documentation, and implementation actually address unauthorized access per the Space System Protection Standard, NASA-STD-1006? Are cybersecurity risks — across both flight and ground software — identified, with mitigations planned and actually managed, not just logged? And has a cybersecurity assessment been performed on the software components per Agency security policy and the project's own requirements, specifically including the risk introduced by any commercial, government, open-source, or reused components?
13. **Cybersecurity, part 2 (SWE-210, SWE-185, SWE-207).** Do software requirements actually exist covering the collection, reporting, and storage of data related to detecting adversarial actions? Independent of what the developer reports, has the code itself been checked against the project's secure coding standard — through independent static analysis or by analyzing the developer's own engineering data? And do the project's coding guidelines actually incorporate secure coding practices, not just general style rules?
14. **Bi-directional traceability (SWE-052).** Does the project's software traceability specifically extend to any hazard that involves software, not just to the ordinary development artifacts? And has bi-directional traceability across the software's elements — scoped per the class-specific table the standard defines — actually been completed, recorded, and kept current?

## Running the script

```bash
cd <this-plugin's-install-path>/skills/sa-task-verification-management/scripts
python3 -c "
from record_sa_task_verification import record_sa_task_verification

record_sa_task_verification(
    matrix_yaml_path='<path to the subsystem's sa-task-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's sa-task-verification-management.md>',
    swe_ids=[<ids answered above with checkable evidence, e.g. 'SWE-033', 'SWE-013', 'SWE-034'>],
    fields={
        'acquisition_and_plan_setup': '<answer to question 1>',
        'plan_tracking_and_commitments': '<answer to question 2>',
        'developer_oversight_and_reporting': '<answer to question 3>',
        'compliance_and_matrix_maintenance': '<answer to question 4>',
        'reuse_cots_and_reuse_assurance': '<answer to question 5>',
        'cost_estimation': '<answer to question 6>',
        'schedule_oversight': '<answer to question 7>',
        'training_and_classification_hygiene': '<answer to question 8>',
        'sa_safety_role_and_independence': '<answer to question 9>',
        'safety_critical_and_mission_critical': '<answer to question 10>',
        'auto_generated_code_and_dev_practices': '<answer to question 11>',
        'cybersecurity_part_1': '<answer to question 12>',
        'cybersecurity_part_2': '<answer to question 13>',
        'bi_directional_traceability': '<answer to question 14>',
    },
    evidence='<the primary evidence artifact's path or reference>',
)
print('Recorded.')
"
```

Only pass ids that actually have checkable evidence for the fields you're filling in this run — you don't need to answer all 14 groups in one pass. Run the script again later as more evidence becomes available; each run appends a new `## Recorded` entry.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management
git add skills/sa-task-verification-management/SKILL.md
git commit -m "feat: add sa-task-verification-management skill"
```

---

### Task 5: Extend `requirements-matrix` to generate the SA task matrix

**Files:**
- Modify: `skills/requirements-matrix/SKILL.md`

**Interfaces:**
- Consumes: `filter_sa_task_rows_for_class`, `render_sa_task_matrix_markdown`, `render_sa_task_matrix_status_yaml` from Task 2; `data/sa-task-catalog.yaml` from Task 1.
- Produces: `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.md` and `.yaml`, which Task 4's `sa-task-verification-management` skill requires as its precondition.

No test — docs-only task, and the functions it calls are already tested in Task 2 (this fork's `SKILL.md` bash snippets are never unit-tested directly).

- [ ] **Step 1: Add a new step to `skills/requirements-matrix/SKILL.md`**

Insert this new numbered step immediately after the existing step 6 (i.e., at the end of the `## Steps` list):

```markdown
7. Generate the parallel SA/safety task matrix (NASA-STD-8739.8B §4.3 Table 1) for whatever chapters `data/sa-task-catalog.yaml` currently covers — see `data/SA-TASK-CATALOG-COVERAGE.md` for its current scope:

```bash
cd <this-plugin's-install-path>/skills/requirements-matrix/scripts
python3 -c "
import yaml
from sa_task_matrix import filter_sa_task_rows_for_class, render_sa_task_matrix_markdown, render_sa_task_matrix_status_yaml

with open('../../../data/sa-task-catalog.yaml') as f:
    sa_task_catalog = yaml.safe_load(f)
with open('../../../data/swe-catalog.yaml') as f:
    swe_catalog = yaml.safe_load(f)

software_class = '<class from classification.yaml>'
subsystem = '<subsystem name>'

rows = filter_sa_task_rows_for_class(sa_task_catalog, swe_catalog, software_class)
if rows:
    md = render_sa_task_matrix_markdown(rows, subsystem, software_class)
    status_rows = render_sa_task_matrix_status_yaml(rows, software_class)
    print(md)
    print('---STATUS-YAML---')
    print(yaml.dump(status_rows, sort_keys=False))
else:
    print('NO SA TASK ROWS APPLICABLE — skip writing sa-task-mapping-matrix files')
"
```

If the script prints `NO SA TASK ROWS APPLICABLE`, do not write any SA task matrix files — this class has no applicable rows in the catalog's current coverage (either genuinely none, or the relevant chapter hasn't been added yet per `SA-TASK-CATALOG-COVERAGE.md`). Otherwise, write the printed markdown to `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.md` and the printed status YAML to `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.yaml` — the same two-file pattern used for the main matrix. `sa-task-verification-management` requires this file to exist before it can record Chapter 3 SA task evidence.
```

The full file after this edit should read, top to bottom: the existing frontmatter, `# Requirements Mapping Matrix (NPR 7150.2D Appendix C)`, `## Overview`, `## Precondition`, `## Catalog schema`, `## Steps` 1-6 (unchanged), then the new step 7 above.

- [ ] **Step 2: Run the full test suite to confirm nothing broke**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management && python3 -m pytest --ignore=.claude -q`
Expected: PASS — all existing tests plus Tasks 1-3's new tests, no regressions (this task only adds a Markdown section, no code changes).

- [ ] **Step 3: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management
git add skills/requirements-matrix/SKILL.md
git commit -m "feat: requirements-matrix generates the SA task matrix"
```

---

### Task 6: Add SP5 Part 2a to README

**Files:**
- Modify: `README.md`

**Interfaces:**
- None — pure documentation, references skill names from Tasks 4 and 5 by name only.

No test — docs-only task, matching SP4/SP5 Part 1's README tasks.

- [ ] **Step 1: Edit `README.md`**

Find this existing block (added by SP5 Part 1):

```
**Software Assurance & Safety (SP5 Part 1), NASA-STD-8739.8B §4.4.2:**

- `ivv-verification-record` — record the 49 IV&V provider verification requirements (planning, oversight, requirements/design/code/test verification, maintenance) once IV&V is confirmed applicable
- `sa-ivv-coordination` (SP2, extended) — now also generates the subsystem's IV&V verification matrix when it records IV&V as applicable

Hazard analysis (Appendix A) and the §4.3 SA-task catalog (~90 rows, keyed to existing SWE-ids) are separate, not-yet-started SP5 follow-ons — see `docs/superpowers/specs/2026-08-22-sp5-ivv-verification-design.md`'s Background for the full three-part breakdown.

See `data/CATALOG-COVERAGE.md` — the bundled requirements catalog now covers all 100 Appendix C rows, though it remains a working draft, not a certified reproduction of the standard. See `docs/superpowers/specs/` and `docs/superpowers/plans/` for the design rationale and build records of each sub-project.
```

Replace it with:

```
**Software Assurance & Safety (SP5 Part 1), NASA-STD-8739.8B §4.4.2:**

- `ivv-verification-record` — record the 49 IV&V provider verification requirements (planning, oversight, requirements/design/code/test verification, maintenance) once IV&V is confirmed applicable
- `sa-ivv-coordination` (SP2, extended) — now also generates the subsystem's IV&V verification matrix when it records IV&V as applicable

**Software Assurance & Safety (SP5 Part 2a), NASA-STD-8739.8B §4.3 Table 1, Chapter 3:**

- `sa-task-verification-management` — record the Chapter 3 (Software Management) software assurance/safety task confirmations, 45 rows keyed to existing SWE-ids
- `requirements-matrix` (SP1, extended) — now also generates the subsystem's SA task matrix alongside the main requirements matrix, reflecting `data/sa-task-catalog.yaml`'s current chapter coverage

Hazard analysis (Appendix A) and the §4.3 SA-task catalog's remaining chapters (Chapter 4, Engineering, 37 rows; Chapter 5, Supporting, 21 rows) are separate, not-yet-started SP5 follow-ons — see `docs/superpowers/specs/2026-08-22-sp5-part2a-sa-tasks-management-design.md`'s Background for the full breakdown.

See `data/CATALOG-COVERAGE.md` and `data/SA-TASK-CATALOG-COVERAGE.md` for each catalog's current coverage. See `docs/superpowers/specs/` and `docs/superpowers/plans/` for the design rationale and build records of each sub-project.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-part2a-sa-tasks-management
git add README.md
git commit -m "docs: add SP5 Part 2a skills to README"
```

---

## Plan Complete

After Task 6, run the full suite once more (`python3 -m pytest --ignore=.claude -q`) to confirm the final state is green, then proceed to `superpowers:requesting-code-review` for a final whole-branch review before merge — **explicitly re-check all 14 interview questions against `reference/NASA-STD-8739.8B.pdf` §4.3 Table 1's Chapter 3 rows for order-mirroring**, same standing check SP4's and SP5 Part 1's final reviews used, per the spec's own Testing section.
