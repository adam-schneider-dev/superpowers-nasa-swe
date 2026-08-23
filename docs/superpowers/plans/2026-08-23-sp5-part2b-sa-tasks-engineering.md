# SP5 Part 2b: SA/Safety Tasks, Engineering (NPR Ch.4) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new `sa-task-verification-management-engineering` skill that records NASA-STD-8739.8B §4.3 Table 1's Chapter 4 (Engineering) SA/safety-task confirmations — 37 rows — extending the `data/sa-task-catalog.yaml` Part 2a created (45 → 82 of 103 rows), plus small generalization fixes to `requirements-matrix`'s SA-task-matrix generation so it stops assuming Chapter 3 is the only chapter present.

**Architecture:** `data/sa-task-catalog.yaml` gains 37 more rows in the same bare `{swe_id, section}` shape. One row group — SWE-065's four lettered sub-tasks (065a-065d) — needs a fix this plan discovered during writing: `data/swe-catalog.yaml` only has one row, `SWE-065`, not four lettered rows, so the class-applicability join and the catalog integrity tests both need to strip a trailing letter suffix before looking a `swe_id` up against `swe-catalog.yaml`. `requirements-matrix`'s matrix-generation code already operates on "whatever the catalog currently covers," so it needs no logic change beyond this fix — only its user-facing prose stops hardcoding "Chapter 3." Recording follows the established `record_*.py` precedent exactly, in a fresh chapter-scoped skill rather than folding into Part 2a's.

**Tech Stack:** Python 3, PyYAML, pytest, ruff — matches every existing skill in this repo. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-08-23-sp5-part2b-sa-tasks-engineering-design.md`

## Plan-time correction to the spec

The spec's Background section states SWE-065's four lettered rows "all carry the same NPR section, `4.5.2`" — true, but it doesn't address a consequence: **`data/swe-catalog.yaml` has no `SWE-065a`/`b`/`c`/`d` rows, only a single `SWE-065` row.** Reading the spec's claim literally and adding catalog rows with `swe_id: "SWE-065a"` etc. would silently break two things: `sa_task_matrix.py`'s class-applicability join (a lettered id would never match anything in `swe-catalog.yaml`, so all four SWE-065 sub-rows would be excluded from every generated matrix regardless of class — a real correctness bug, not just a failing test) and the catalog integrity tests (`KeyError`/assertion failure). Fixed in this plan: both the join in `sa_task_matrix.py` (Task 2) and the two affected integrity test assertions (Task 1) strip a trailing lowercase letter from a `swe_id` before looking it up against `swe-catalog.yaml`, while the lettered id itself stays the unique key used everywhere else (catalog rows, matrix status rows, record-script calls) — needed so the four SWE-065 sub-tasks can be tracked as four independent matrix rows rather than colliding into one. This mirrors how Part 2a caught and fixed spec inaccuracies during plan-writing (commits `ea94bec`, `6c4b733`) rather than during implementation or review.

## Global Constraints

- No requirement or task text is ever stored in `data/sa-task-catalog.yaml` — cite by `swe_id`/`section` only, same as `data/swe-catalog.yaml` and `data/ivv-catalog.yaml`. All paraphrase lives only in `sa-task-verification-management-engineering/SKILL.md`'s interview prose.
- `sa-task-mapping-matrix.yaml` rows carry `swe_id`, `section`, `software_class`, `status`, `evidence`, `date` — **no `default_approver` field**, same as Part 2a. Do not invent one.
- Every record script's three mandated error paths, verbatim behavior: empty id list → `ValueError`; unknown id → `KeyError`; attempting to mark an already-`tailored-out` row `satisfied` → `ValueError` with the matrix left unmodified on disk.
- Record output is always Markdown, appended (never overwritten) to `docs/nasa-compliance/<subsystem>/<topic>.md` — never YAML.
- No `SKILL.md` interview question may reproduce 3+ consecutive words from `reference/NASA-STD-8739.8B.pdf`'s §4.3 Table 1 text, and no question may present its underlying tasks in the same relative order the standard lists them in. Every one of this plan's 7 interview questions has already been deliberately reordered relative to the source — each is stated in reverse order relative to how the standard lists its underlying tasks — and independently checked with a word-overlap script against the extracted PDF text until no run exceeded ~5 words (remaining short matches are unavoidable citations/proper nouns: section numbers like "4.5.2", acronym lists like "COTS, GOTS, MOTS", and named artifacts like "the system safety data package"). Do not "clean up" that ordering or phrasing to look more natural during implementation — both were deliberately shaped this way.
- All `cd` commands in this plan target the worktree at `/home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/sp5-part2b-sa-tasks-engineering` — branch `worktree-sp5-part2b-sa-tasks-engineering`, not `main`. Do not adapt paths to point at the main checkout.
- Run `ruff check .` (in addition to `pytest`) before considering any task done — CI on this repo now enforces it (`ruff.toml`: `E, F, I` selected, `E501`/`E402` ignored) and PRs fail without it.

---

### Task 1: Extend `data/sa-task-catalog.yaml` + coverage doc + integrity tests

**Files:**
- Modify: `data/sa-task-catalog.yaml`
- Modify: `data/SA-TASK-CATALOG-COVERAGE.md`
- Modify: `tests/test_sa_task_catalog_integrity.py`

**Interfaces:**
- Produces: `data/sa-task-catalog.yaml` now has 82 rows (45 existing Chapter 3 + 37 new Chapter 4). Task 2 and Task 3 read this file.
- Produces: `_base_swe_id(swe_id)` helper in the test file (strips a trailing lowercase letter if present) — Task 2 needs the identical helper in `sa_task_matrix.py`; keep both definitions in sync (same one-line body), do not import one from the other (this fork does not share code across a test file and a skill script).

- [ ] **Step 1: Append the 37 Chapter 4 rows to `data/sa-task-catalog.yaml`**

Open `data/sa-task-catalog.yaml` and append these rows after the existing 45 Chapter 3 rows (the file's trailing `SWE-052`/`3.12.1` row is currently last), keeping the existing header comment block as-is except updating its coverage-count line:

Change the header's third line from:
```yaml
# Coverage: 45 of the table's 103 total rows — NPR 7150.2D Chapter 3
```
to:
```yaml
# Coverage: 82 of the table's 103 total rows — NPR 7150.2D Chapters 3-4
```

Append these 37 rows in Table 1's own order (§4.1 through §4.6):

```yaml
- swe_id: "SWE-050"
  section: "4.1.2"
- swe_id: "SWE-051"
  section: "4.1.3"
- swe_id: "SWE-184"
  section: "4.1.4"
- swe_id: "SWE-053"
  section: "4.1.5"
- swe_id: "SWE-054"
  section: "4.1.6"
- swe_id: "SWE-055"
  section: "4.1.7"
- swe_id: "SWE-057"
  section: "4.2.3"
- swe_id: "SWE-143"
  section: "4.2.4"
- swe_id: "SWE-058"
  section: "4.3.2"
- swe_id: "SWE-060"
  section: "4.4.2"
- swe_id: "SWE-061"
  section: "4.4.3"
- swe_id: "SWE-135"
  section: "4.4.4"
- swe_id: "SWE-062"
  section: "4.4.5"
- swe_id: "SWE-186"
  section: "4.4.6"
- swe_id: "SWE-063"
  section: "4.4.7"
- swe_id: "SWE-136"
  section: "4.4.8"
- swe_id: "SWE-065a"
  section: "4.5.2"
- swe_id: "SWE-065b"
  section: "4.5.2"
- swe_id: "SWE-065c"
  section: "4.5.2"
- swe_id: "SWE-065d"
  section: "4.5.2"
- swe_id: "SWE-066"
  section: "4.5.3"
- swe_id: "SWE-187"
  section: "4.5.4"
- swe_id: "SWE-068"
  section: "4.5.5"
- swe_id: "SWE-070"
  section: "4.5.6"
- swe_id: "SWE-071"
  section: "4.5.7"
- swe_id: "SWE-073"
  section: "4.5.8"
- swe_id: "SWE-189"
  section: "4.5.9"
- swe_id: "SWE-190"
  section: "4.5.10"
- swe_id: "SWE-191"
  section: "4.5.11"
- swe_id: "SWE-192"
  section: "4.5.12"
- swe_id: "SWE-193"
  section: "4.5.13"
- swe_id: "SWE-211"
  section: "4.5.14"
- swe_id: "SWE-075"
  section: "4.6.2"
- swe_id: "SWE-077"
  section: "4.6.3"
- swe_id: "SWE-194"
  section: "4.6.4"
- swe_id: "SWE-195"
  section: "4.6.5"
- swe_id: "SWE-196"
  section: "4.6.6"
```

- [ ] **Step 2: Update `data/SA-TASK-CATALOG-COVERAGE.md`**

Replace its full contents with:

```markdown
# SA Task Catalog Coverage

**`data/sa-task-catalog.yaml` covers 82 of NASA-STD-8739.8B §4.3 Table 1's 103 rows.**

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

## Covered — Chapter 4, Software Engineering, 37 rows (SP5 Part 2b)

- 4.1 Software Requirements
- 4.2 Software Architecture
- 4.3 Software Design
- 4.4 Software Implementation
- 4.5 Software Testing
- 4.6 Software Operations, Maintenance, and Retirement

Note: SWE-065's four lettered sub-tasks (065a-065d, all under NPR section
4.5.2) share a single row in `data/swe-catalog.yaml` (`SWE-065`). Class
applicability for all four is looked up against that one shared row —
`sa_task_matrix.py` strips a trailing letter suffix before the lookup.

## Not yet covered

- **Chapter 5, Supporting Lifecycle, 21 rows** — SP5 Part 2c, not started.

`requirements-matrix`'s `sa-task-mapping-matrix.yaml` output reflects
whatever this catalog currently covers — a subsystem generated before Part
2c lands gets a Chapter 3+4-only SA-task matrix. Re-running `requirements-matrix`
after it lands picks up the newly added rows.

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

- [ ] **Step 3: Update `tests/test_sa_task_catalog_integrity.py`**

Replace its full contents with:

```python
# tests/test_sa_task_catalog_integrity.py
"""Guards data/sa-task-catalog.yaml (NASA-STD-8739.8B §4.3 Table 1's Chapter
3-4 rows) against a bad edit or transcription pass — same purpose as
test_catalog_integrity.py for the SWE catalog and test_ivv_catalog_integrity.py
for the IV&V catalog. Extended (not replaced) by Part 2b to cover Chapter 4;
Part 2c will extend it again for Chapter 5.
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


def _base_swe_id(swe_id):
    """Strip a trailing lowercase letter (e.g. "SWE-065a" -> "SWE-065") so
    lettered sub-task ids can still be looked up against swe-catalog.yaml,
    which has one row per base id, not one per lettered sub-task."""
    return swe_id[:-1] if swe_id[-1].isalpha() else swe_id


def test_bundled_sa_task_catalog_has_82_rows():
    assert len(load_sa_task_catalog()) == 82


def test_every_swe_id_is_unique():
    catalog = load_sa_task_catalog()
    ids = [r["swe_id"] for r in catalog]
    assert len(ids) == len(set(ids))


def test_every_row_has_no_task_text_fields():
    for row in load_sa_task_catalog():
        assert set(row.keys()) == {"swe_id", "section"}


def test_every_swe_id_exists_in_swe_catalog():
    sa_task_ids = {_base_swe_id(r["swe_id"]) for r in load_sa_task_catalog()}
    swe_catalog_ids = {r["swe_id"] for r in load_swe_catalog()}
    assert sa_task_ids.issubset(swe_catalog_ids)


def test_section_matches_swe_catalog_section_for_every_row():
    swe_sections = {r["swe_id"]: r["section"] for r in load_swe_catalog()}
    for row in load_sa_task_catalog():
        assert row["section"] == swe_sections[_base_swe_id(row["swe_id"])]


def test_all_rows_are_chapter_3_or_4():
    for row in load_sa_task_catalog():
        assert row["section"].startswith("3.") or row["section"].startswith("4.")


def test_chapter_4_has_37_rows():
    ch4 = [r for r in load_sa_task_catalog() if r["section"].startswith("4.")]
    assert len(ch4) == 37


def test_swe_065_lettered_rows_all_share_section_4_5_2():
    lettered = [r for r in load_sa_task_catalog() if r["swe_id"].startswith("SWE-065")]
    assert {r["swe_id"] for r in lettered} == {"SWE-065a", "SWE-065b", "SWE-065c", "SWE-065d"}
    assert all(r["section"] == "4.5.2" for r in lettered)
```

- [ ] **Step 4: Run the tests**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/sp5-part2b-sa-tasks-engineering
python3 -m pytest tests/test_sa_task_catalog_integrity.py -v
```
Expected: all 8 tests PASS.

- [ ] **Step 5: Run the full suite and lint**

```bash
python3 -m pytest --ignore=.claude -q
python3 -m ruff check .
```
Expected: 177 passed (175 baseline — replacing `test_sa_task_catalog_integrity.py`'s existing 6 tests with this step's 8 is a net +2, not +8), ruff clean.

- [ ] **Step 6: Commit**

```bash
git add data/sa-task-catalog.yaml data/SA-TASK-CATALOG-COVERAGE.md tests/test_sa_task_catalog_integrity.py
git commit -m "feat: add SA task catalog Chapter 4 rows (NASA-STD-8739.8B §4.3 Table 1, 37 rows)"
```

---

### Task 2: Fix `sa_task_matrix.py`'s class-applicability join for lettered ids + generalize its header text

**Files:**
- Modify: `skills/requirements-matrix/scripts/sa_task_matrix.py`
- Modify: `skills/requirements-matrix/scripts/test_sa_task_matrix.py`

**Interfaces:**
- Consumes: `data/sa-task-catalog.yaml` rows including `SWE-065a`-`SWE-065d` (Task 1).
- Produces: `filter_sa_task_rows_for_class` now correctly includes lettered-id rows when their base id is applicable to the given class. `render_sa_task_matrix_markdown`'s header no longer claims "Chapter 3 / Software Management rows only." Task 4 and Task 5 rely on the corrected filter and the generalized header text.

- [ ] **Step 1: Write the failing tests**

Add to the end of `skills/requirements-matrix/scripts/test_sa_task_matrix.py`:

```python
def sample_lettered_sa_task_rows():
    return [
        {"swe_id": "SWE-065a", "section": "4.5.2"},
        {"swe_id": "SWE-065b", "section": "4.5.2"},
    ]


def sample_swe_catalog_rows_with_065():
    return [
        {
            "section": "4.5.2", "swe_id": "SWE-065",
            "class_ae_authority": "Center",
            "classes": {"A": True, "B": True, "C": True, "D": True, "E": False, "F": True},
            "class_f_authority": "CIO",
        },
    ]


def test_filter_keeps_lettered_rows_when_base_id_applicable():
    rows = filter_sa_task_rows_for_class(
        sample_lettered_sa_task_rows(), sample_swe_catalog_rows_with_065(), "C"
    )
    assert {r["swe_id"] for r in rows} == {"SWE-065a", "SWE-065b"}


def test_filter_excludes_lettered_rows_when_base_id_not_applicable():
    rows = filter_sa_task_rows_for_class(
        sample_lettered_sa_task_rows(), sample_swe_catalog_rows_with_065(), "E"
    )
    assert rows == []


def test_render_markdown_header_does_not_name_a_specific_chapter():
    md = render_sa_task_matrix_markdown(sample_sa_task_rows(), subsystem="widget-firmware", software_class="C")
    assert "Chapter 3" not in md
    assert "SA-TASK-CATALOG-COVERAGE.md" in md
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/sp5-part2b-sa-tasks-engineering/skills/requirements-matrix/scripts
python3 -m pytest test_sa_task_matrix.py -v
```
Expected: `test_filter_keeps_lettered_rows_when_base_id_applicable` and `test_filter_excludes_lettered_rows_when_base_id_not_applicable` FAIL (lettered rows never match, so both currently return `[]`, making the first assertion fail). `test_render_markdown_header_does_not_name_a_specific_chapter` FAILS (current header contains "Chapter 3").

- [ ] **Step 3: Fix `sa_task_matrix.py`**

Replace the full contents of `skills/requirements-matrix/scripts/sa_task_matrix.py` with:

```python
from filter_matrix import _check_class, filter_rows_for_class


def _base_swe_id(swe_id):
    """Strip a trailing lowercase letter (e.g. "SWE-065a" -> "SWE-065") so
    lettered sub-task ids (Table 1 splits SWE-065 into four) can still be
    looked up against swe-catalog.yaml, which has one row per base id."""
    return swe_id[:-1] if swe_id[-1].isalpha() else swe_id


def filter_sa_task_rows_for_class(sa_task_rows, swe_catalog_rows, software_class):
    """SA-task rows carry no class marks of their own — applicability is inherited
    from the same swe_id's class marks in swe-catalog.yaml, reusing filter_matrix's
    own class filter rather than duplicating its validation and lookup logic.
    """
    applicable_ids = {r["swe_id"] for r in filter_rows_for_class(swe_catalog_rows, software_class)}
    return [r for r in sa_task_rows if _base_swe_id(r["swe_id"]) in applicable_ids]


def render_sa_task_matrix_markdown(rows, subsystem, software_class):
    _check_class(software_class)
    lines = [
        f"# Software Assurance & Safety Task Matrix — {subsystem} (Class {software_class})",
        "",
        "Source: NASA-STD-8739.8B §4.3 Table 1 (see data/SA-TASK-CATALOG-COVERAGE.md "
        "for which chapters are currently covered). Task text is not reproduced here "
        "— each row cites the source standard and the underlying NPR 7150.2D "
        "requirement by section and SWE-id.",
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

(Only the header text in `render_sa_task_matrix_markdown` and the new `_base_swe_id` helper plus its use in `filter_sa_task_rows_for_class` changed — `render_sa_task_matrix_status_yaml` is unchanged.)

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest test_sa_task_matrix.py -v
```
Expected: all tests PASS, including the pre-existing ones (`test_render_markdown_includes_citation_not_task_text` still passes — it never asserted the old "Chapter 3" text).

- [ ] **Step 5: Run the full suite and lint**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/sp5-part2b-sa-tasks-engineering
python3 -m pytest --ignore=.claude -q
python3 -m ruff check .
```
Expected: 180 passed (177 from Task 1 + 3 new), ruff clean.

- [ ] **Step 6: Commit**

```bash
git add skills/requirements-matrix/scripts/sa_task_matrix.py skills/requirements-matrix/scripts/test_sa_task_matrix.py
git commit -m "fix: sa_task_matrix.py class-applicability join for lettered SWE ids, generalize header"
```

---

### Task 3: New skill's record script + tests

**Files:**
- Create: `skills/sa-task-verification-management-engineering/scripts/record_sa_task_verification_engineering.py`
- Create: `skills/sa-task-verification-management-engineering/scripts/test_record_sa_task_verification_engineering.py`

**Interfaces:**
- Produces: `record_sa_task_verification_engineering(matrix_yaml_path, record_md_path, swe_ids, fields, evidence)` — Task 4's `SKILL.md` calls this exact function with this exact signature.

- [ ] **Step 1: Write the failing tests**

Create `skills/sa-task-verification-management-engineering/scripts/test_record_sa_task_verification_engineering.py`:

```python
import os

import pytest
import yaml
from record_sa_task_verification_engineering import record_sa_task_verification_engineering


def sample_matrix_rows():
    return [
        {"swe_id": "SWE-060", "section": "4.4.2", "software_class": "C", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-061", "section": "4.4.3", "software_class": "C", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-058", "section": "4.3.2", "software_class": "C", "status": "tailored-out", "evidence": None, "date": None},
    ]


def write_matrix(tmp_path):
    matrix_path = tmp_path / "sa-task-mapping-matrix.yaml"
    with open(matrix_path, "w") as f:
        yaml.dump(sample_matrix_rows(), f, sort_keys=False)
    return str(matrix_path)


def test_marks_rows_satisfied_and_appends_record(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "sa-task-verification-management-engineering.md")

    record_sa_task_verification_engineering(
        matrix_yaml_path=matrix_path,
        record_md_path=record_path,
        swe_ids=["SWE-060", "SWE-061"],
        fields={"software_implementation": "Reviewed code against design; no undocumented functionality found."},
        evidence="docs/nasa-compliance/widget-firmware/implementation-review.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    by_id = {r["swe_id"]: r for r in updated}
    assert by_id["SWE-060"]["status"] == "satisfied"
    assert by_id["SWE-060"]["evidence"] == "docs/nasa-compliance/widget-firmware/implementation-review.md"
    assert by_id["SWE-060"]["date"] is not None
    assert by_id["SWE-061"]["status"] == "satisfied"

    with open(record_path) as f:
        record = f.read()
    assert "SWE-060" in record
    assert "SWE-061" in record
    assert "Reviewed code against design" in record


def test_empty_swe_ids_raises_value_error(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")
    with pytest.raises(ValueError, match="at least one swe_id"):
        record_sa_task_verification_engineering(
            matrix_yaml_path=matrix_path, record_md_path=record_path,
            swe_ids=[], fields={}, evidence="x",
        )


def test_unknown_swe_id_raises_key_error(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")
    with pytest.raises(KeyError):
        record_sa_task_verification_engineering(
            matrix_yaml_path=matrix_path, record_md_path=record_path,
            swe_ids=["SWE-999"], fields={}, evidence="x",
        )


def test_tailored_out_row_raises_value_error_and_matrix_unmodified(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")
    with pytest.raises(ValueError, match="tailored-out"):
        record_sa_task_verification_engineering(
            matrix_yaml_path=matrix_path, record_md_path=record_path,
            swe_ids=["SWE-058"], fields={}, evidence="x",
        )
    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    by_id = {r["swe_id"]: r for r in unchanged}
    assert by_id["SWE-058"]["status"] == "tailored-out"
    assert not os.path.exists(record_path)


def test_second_call_appends_new_record_entry(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")

    record_sa_task_verification_engineering(
        matrix_yaml_path=matrix_path, record_md_path=record_path,
        swe_ids=["SWE-060"], fields={"software_implementation": "First pass."},
        evidence="ev1.md",
    )
    with open(record_path) as f:
        first_len = len(f.read())

    record_sa_task_verification_engineering(
        matrix_yaml_path=matrix_path, record_md_path=record_path,
        swe_ids=["SWE-061"], fields={"software_implementation": "Second pass."},
        evidence="ev2.md",
    )
    with open(record_path) as f:
        content = f.read()
    assert len(content) > first_len
    assert content.count("## Recorded") == 2
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/sp5-part2b-sa-tasks-engineering/skills/sa-task-verification-management-engineering/scripts
python3 -m pytest test_record_sa_task_verification_engineering.py -v
```
Expected: FAIL — `record_sa_task_verification_engineering.py` does not exist yet (`ModuleNotFoundError`).

- [ ] **Step 3: Write `record_sa_task_verification_engineering.py`**

```python
import datetime

import yaml

DEFAULT_HEADER = (
    "# Software Assurance & Safety Task Verification Record "
    "(NASA-STD-8739.8B §4.3 Table 1, Chapter 4)\n\n"
)


def record_sa_task_verification_engineering(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
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

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest test_record_sa_task_verification_engineering.py -v
```
Expected: all 5 tests PASS.

- [ ] **Step 5: Run the full suite and lint**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/sp5-part2b-sa-tasks-engineering
python3 -m pytest --ignore=.claude -q
python3 -m ruff check .
```
Expected: 185 passed (180 from Task 2 + 5 new), ruff clean.

- [ ] **Step 6: Commit**

```bash
git add skills/sa-task-verification-management-engineering/scripts/record_sa_task_verification_engineering.py skills/sa-task-verification-management-engineering/scripts/test_record_sa_task_verification_engineering.py
git commit -m "feat: add sa-task-verification-management-engineering record logic"
```

---

### Task 4: New skill `SKILL.md` — precondition + 7 pre-drafted interview questions

**Files:**
- Create: `skills/sa-task-verification-management-engineering/SKILL.md`

**Interfaces:**
- Consumes: `record_sa_task_verification_engineering` (Task 3), exact signature `(matrix_yaml_path, record_md_path, swe_ids, fields, evidence)`.

- [ ] **Step 1: Create `skills/sa-task-verification-management-engineering/SKILL.md`**

```markdown
---
name: sa-task-verification-management-engineering
description: Use to record a subsystem's NASA-STD-8739.8B §4.3 Table 1 software assurance and safety task evidence for NPR 7150.2D Chapter 4 (Engineering) requirements, once requirements-matrix has generated the SA task matrix
---

# Software Assurance & Safety Tasks — Engineering (NASA-STD-8739.8B §4.3 Table 1, NPR Ch.4)

## Overview

Records that software assurance and safety personnel actually performed the confirmation, assessment, and analysis tasks §4.3 Table 1 assigns against each Chapter 4 (Software Engineering) requirement, and where the evidence for each lives. Does not perform software assurance or safety work itself — that's real engineering and assurance work this tool doesn't replace.

**Announce at start:** "I'm using the sa-task-verification-management-engineering skill to record your NASA-STD-8739.8B §4.3 Table 1 software assurance and safety task evidence for NPR Chapter 4."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.yaml` to already exist with at least one Chapter 4 row for this subsystem's class. This file is generated by `requirements-matrix` alongside the main requirements matrix — the same file `sa-task-verification-management` reads for Chapter 3 rows, since both skills share one matrix per subsystem. If it's absent, or has no rows starting with `4.`, either this class has no applicable Chapter 4 rows or `requirements-matrix` hasn't been (re-)run since this catalog's rows existed — check there first, don't assume the chapter doesn't apply.

## The interview

Ask each group below in turn. For each, ask which of its listed SWE-ids have real, checkable evidence — an assurance assessment, a confirmed audit finding, a review record, a tracked risk or issue — and where that evidence lives. A vague "assurance handled it" answer is not sufficient, same standard `peer-review-record`, `ivv-verification-record`, and `sa-task-verification-management` established: the evidence must point at something a human auditor could actually go check. If a SWE-id has no real evidence yet, leave it out of that group's `swe_ids` below rather than recording an unverifiable claim.

1. **Software Requirements (SWE-055, SWE-054, SWE-053, SWE-184, SWE-051, SWE-050).** Has project testing actually demonstrated the software behaves as expected once it's in the customer's environment? Separately — when gaps turn up between the requirements, the project's plans, and what the software actually does, are those differences being watched for, flagged, and driven through corrective action to closure? Do requirement changes get logged, tracked, approved, and kept current for the life of the project? Does the requirements documentation capture the safety-relevant assumptions, mitigations, controls, and constraints that sit between the hardware, the operator, and the software? Has an assurance analysis of the detailed requirements been run to catch anything wrong, missing, or incomplete at the source? And, starting point: are all the requirements — COTS, GOTS, MOTS, open-source, or reused components included — actually established, captured, and written into the technical specification?
2. **Software Architecture & Design (SWE-058, SWE-143, SWE-057).** Has an assurance design analysis actually been performed, and separately: does the design implement every required safety-critical function and requirement, avoid introducing behavior or capability nobody asked for, stay consistent with the architecture's own concepts, and break the system down into the lower-level pieces still awaiting coding, compiling, and testing — with any gap against the hardware and software requirements identified? For projects that trigger it — Category 1, or Category 2 carrying Class A or B payload risk — has someone reviewed how that architecture review activity went, or taken part in it directly? And at the architecture level itself: does it capture the software's structure, its quality attributes, its interfaces, and its internal/external components, and has it been checked against what mission assurance and safety actually call for?
3. **Software Implementation (SWE-136, SWE-063, SWE-186, SWE-062, SWE-135, SWE-061, SWE-060).** Are the tools used to build and maintain the software themselves validated and accredited? For each release, does the project produce a correct version description, and is the software checked over for security-related defects and confirmed against the coding standard, with the outcome recorded? Is everything needed to repeat unit testing later — procedures, scripts, results, data — actually kept? Are the required unit tests, especially ones touching safety-critical functions, actually executed successfully, and are problems found during that testing tracked through to closure? On static analysis: is engineering data reviewed or independent static analysis run to catch defects, security issues, coverage gaps, and complexity problems; are the analysis tools set up with checkers that flag coding mistakes and security holes; does the project act on what those tools turn up; has a security-defect scan of the code actually run, with the outcome confirmed; are code-coverage and cyclomatic-complexity waivers for safety-critical components verified per the coverage and complexity requirements; and are quality thresholds actually defined for what the static checks are measuring against? Did the project pick and stick to defined criteria, standards, and methods for coding, and does the code actually conform to them? And at the base: does the code implement the design, with nothing in it that isn't called for by the design or the requirements?
4. **Test Planning & Environment (SWE-065d, SWE-065c, SWE-065b, SWE-065a).** Covering the four things §4.5.2 requires the project to establish and maintain. Starting with reports: are test reports actually produced and kept current throughout integration and test, do they capture the as-run data, the results, and the required sign-offs, and are problems spotted in any individual test run — plus any errors or defects turning up anywhere in testing — recorded and tracked all the way to closure? Is any code written specifically to run the test procedures itself kept under configuration management, with its own issues and defects recorded and tracked to closure? On the procedures: are they updated whenever the tests or requirements change, and do they actually cover what the requirements call for, spell out pass/fail criteria, include off-nominal and boundary conditions, address the hazard coverage called out for loaded/uplinked data and hazard-related testing, and cover cybersecurity requirements coverage? And on the plan itself: is it established with the right content and kept current, and does it specifically address verifying safety-critical software under off-nominal scenarios?
5. **Test Execution, Results & Validation (SWE-073, SWE-071, SWE-070, SWE-068, SWE-187, SWE-066).** Are the software's components actually validated on the real target platform, or a high-fidelity simulation standing in for it? Have the test plans and procedures been checked for whether they cover the requirements and verify the hazard controls thoroughly, off-nominal scenarios specifically included? Are the analysis tools, simulations, and models relied on to qualify flight equipment or flight software themselves validated and accredited? Are test results actually assessed and recorded, are nonconformances logged in a tracking system, and are the results good enough to serve as verification evidence for the hazard reports? Are the software items being tested placed under configuration management before testing starts, and kept there through the end of testing? And on execution itself: does running the test procedures actually demonstrate requirements coverage, is safety-critical software testing witnessed, and do any newly discovered software contributions to a hazard, event, or condition found during testing make it into the system safety data package?
6. **Coverage, Regression, Acceptance & Embedded-COTS Testing (SWE-211, SWE-193, SWE-192, SWE-191, SWE-190, SWE-189).** Are COTS, GOTS, MOTS, open-source, or reused components being tested to the same bar the project would hold a custom-built component to for the same use? For whatever gets loaded or sent up after launch — code, scripts, rules, or data — that shapes how the software or the wider system behaves: does the project build acceptance tests for it, is it baselined in the configuration-management system, and is it verified correct before operations — especially safety-critical ones? Does testing actually confirm that requirements tied to a hazard — its triggering event, its cause, or its mitigation — hold up? Is regression testing planned with adequate coverage — every safety-critical code component retested — actually carried out as planned, are risks in how the regression set was chosen or run identified, and do the regression procedures get updated to include tests that check anomaly fixes actually worked? Is code coverage analyzed from test results or a coverage tool, is uncovered code flagged and assessed for risk, and are the coverage measurements themselves selected, run, tracked, recorded, and reported in the first place?
7. **Software Operations, Maintenance & Retirement (SWE-196, SWE-195, SWE-194, SWE-077, SWE-075).** Has the project identified what records and tools need archiving, and does it actually archive everything selected as planned? Are audits run against the processes and standards followed during maintenance, scaled to the software's classification? Before delivery: has the project pinned down which requirements must be met, which approved changes go in, and which defects get resolved for that delivery; has it actually met every requirement identified for that delivery; have requirements that used to be slated for that delivery — yet don't show up anymore in its documentation — been properly dispositioned; have approved changes actually gone in and been verified through testing; have the changes and defects slated for resolution actually been resolved; and does someone sign off on the delivered products? Are audits run against every delivery, per the configuration-management process, to confirm the right versions of the right products actually went out, correct version included alongside as-built documentation and project records? And at the plan level: were the retirement, operations, and maintenance plans checked over to confirm they fully cover the engineering and assurance activities they're required to, and is the project actually carrying those plans out?

## Running the script

```bash
cd <this-plugin's-install-path>/skills/sa-task-verification-management-engineering/scripts
python3 -c "
from record_sa_task_verification_engineering import record_sa_task_verification_engineering

record_sa_task_verification_engineering(
    matrix_yaml_path='<path to the subsystem's sa-task-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's sa-task-verification-management-engineering.md>',
    swe_ids=[<ids answered above with checkable evidence, e.g. 'SWE-060', 'SWE-061'>],
    fields={
        'software_requirements': '<answer to question 1>',
        'software_architecture_and_design': '<answer to question 2>',
        'software_implementation': '<answer to question 3>',
        'test_planning_and_environment': '<answer to question 4>',
        'test_execution_results_and_validation': '<answer to question 5>',
        'coverage_regression_acceptance_and_cots_testing': '<answer to question 6>',
        'software_operations_maintenance_and_retirement': '<answer to question 7>',
    },
    evidence='<the primary evidence artifact's path or reference>',
)
print('Recorded.')
"
```

Only pass ids that actually have checkable evidence for the fields you're filling in this run — you don't need to answer all 7 groups in one pass. Run the script again later as more evidence becomes available; each run appends a new `## Recorded` entry.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
```

- [ ] **Step 2: Verify all 37 SWE-ids appear exactly once across the 7 groups**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/sp5-part2b-sa-tasks-engineering
python3 -c "
import re, yaml
catalog = yaml.safe_load(open('data/sa-task-catalog.yaml'))
ch4_ids = [r['swe_id'] for r in catalog if r['section'].startswith('4.')]
text = open('skills/sa-task-verification-management-engineering/SKILL.md').read()
interview = text.split('## The interview')[1].split('## Running the script')[0]
q_ids = re.findall(r'SWE-\d+[a-d]?', interview)
assert len(ch4_ids) == 37, len(ch4_ids)
assert len(q_ids) == 37, len(q_ids)
assert set(ch4_ids) == set(q_ids), (set(ch4_ids) - set(q_ids), set(q_ids) - set(ch4_ids))
assert len(q_ids) == len(set(q_ids)), 'duplicate id in interview'
print('OK: 37/37, zero gaps, zero duplicates')
"
```
Expected: `OK: 37/37, zero gaps, zero duplicates`.

- [ ] **Step 3: Commit**

```bash
git add skills/sa-task-verification-management-engineering/SKILL.md
git commit -m "feat: add sa-task-verification-management-engineering skill"
```

---

### Task 5: Extend `requirements-matrix/SKILL.md` wording + README update

**Files:**
- Modify: `skills/requirements-matrix/SKILL.md`
- Modify: `README.md`

**Interfaces:**
- None — this task only touches documentation/prose, no new functions or files other tasks depend on.

- [ ] **Step 1: Update `requirements-matrix/SKILL.md` step 7's closing sentence**

Find the sentence (in step 7, added by Part 2a):

```
Otherwise, write the printed markdown to `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.md` and the printed status YAML to `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.yaml` — the same two-file pattern used for the main matrix. `sa-task-verification-management` requires this file to exist before it can record Chapter 3 SA task evidence.
```

Replace it with:

```
Otherwise, write the printed markdown to `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.md` and the printed status YAML to `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.yaml` — the same two-file pattern used for the main matrix. `sa-task-verification-management` requires this file to exist before it can record Chapter 3 SA task evidence; `sa-task-verification-management-engineering` requires it before recording Chapter 4 SA task evidence. Both skills read the same file, each only touching its own chapter's rows.
```

- [ ] **Step 2: Update `README.md`**

Find this block (added by Part 2a, currently around line 47-51):

```markdown
**Software Assurance & Safety Tasks (SP5 Part 2a), NASA-STD-8739.8B §4.3 Table 1, Chapter 3:**

- `sa-task-verification-management` — record SA/safety task evidence for Chapter 3 (Management) requirements; driven by `data/sa-task-catalog.yaml` (45 rows) and filtered via `requirements-matrix` to produce `sa-task-mapping-matrix.yaml`

Hazard analysis (Appendix A) and the remaining §4.3 SA-task chapters (4-6, Parts 2b-2c) are separate, not-yet-started SP5 follow-ons — see `docs/superpowers/specs/2026-08-22-sp5-ivv-verification-design.md`'s Background for the full breakdown.
```

Replace it with:

```markdown
**Software Assurance & Safety Tasks (SP5 Parts 2a-2b), NASA-STD-8739.8B §4.3 Table 1, Chapters 3-4:**

- `sa-task-verification-management` — record SA/safety task evidence for Chapter 3 (Management) requirements; driven by `data/sa-task-catalog.yaml` (82 rows total) and filtered via `requirements-matrix` to produce `sa-task-mapping-matrix.yaml`
- `sa-task-verification-management-engineering` — same pattern, for Chapter 4 (Engineering) requirements (37 of the catalog's 82 rows); both skills read the same generated matrix, each only touching its own chapter's rows

Hazard analysis (Appendix A) and the remaining §4.3 SA-task chapter (5, Part 2c) are separate, not-yet-started SP5 follow-ons — see `docs/superpowers/specs/2026-08-22-sp5-ivv-verification-design.md`'s Background for the full breakdown.
```

(This also fixes a pre-existing typo from Part 2a's addition — "chapters (4-6, Parts 2b-2c)" should have read "chapters (4-5, Parts 2b-2c)"; §4.3 Table 1 only has Chapters 3-5, Chapter 6 is out of scope for this sub-project entirely.)

- [ ] **Step 3: Run the full suite and lint**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/sp5-part2b-sa-tasks-engineering
python3 -m pytest --ignore=.claude -q
python3 -m ruff check .
```
Expected: 185 passed (unchanged from Task 3 — Task 4 and this task add no tests), ruff clean.

- [ ] **Step 4: Commit**

```bash
git add skills/requirements-matrix/SKILL.md README.md
git commit -m "docs: extend requirements-matrix wording and README for SP5 Part 2b"
```
