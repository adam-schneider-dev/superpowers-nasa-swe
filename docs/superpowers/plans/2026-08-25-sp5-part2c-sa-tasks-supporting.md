# SP5 Part 2c — SA/Safety Tasks, Supporting (NPR Ch.5) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add NASA-STD-8739.8B §4.3 Table 1's 21 Chapter 5 rows to the SA task catalog and ship a `sa-task-verification-supporting` skill that records evidence against them, completing the catalog at 103/103.

**Architecture:** Extend the existing `data/sa-task-catalog.yaml` by 21 `{swe_id, section}` rows; add a third chapter-scoped recording skill that reads the same per-subsystem `sa-task-mapping-matrix.yaml` the other two read, touching only rows whose section starts `5.`. No matrix-generation code changes — `sa_task_matrix.py` already filters whatever the catalog contains.

**Tech Stack:** Python 3, PyYAML, pytest, ruff. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-08-25-sp5-part2c-sa-tasks-supporting-design.md`

## Global Constraints

- **Zero new dependencies.** PyYAML and pytest only, both already used.
- **No task text in the catalog.** Every catalog row has exactly the keys `swe_id` and `section` — nothing else. Guarded by `test_every_row_has_no_task_text_fields`.
- **No verbatim PDF phrasing in interview questions.** Commit `149b2ff` rewrote Part 2a's questions specifically to remove copied wording from the standard. Paraphrase in plain language; never paste the task column.
- **Skill directories are self-contained.** No cross-skill imports, no shared module. The record script is a near-identical copy by design.
- **Evidence standard:** every interview answer must point at something a human auditor could check. Ids without checkable evidence are left out of the run's `swe_ids`.
- **Branch:** `sp5-part2c-sa-tasks-supporting` (already created; the spec commit `2888064` is on it).
- **Baseline:** 185 tests pass, `ruff check .` clean, as of the spec commit.

---

### Task 1: Catalog extension — 21 Chapter 5 rows

**Files:**
- Modify: `data/sa-task-catalog.yaml` (append after the `SWE-196` / `4.6.6` row at end of file; update header comment lines 4-6)
- Modify: `tests/test_sa_task_catalog_integrity.py` (docstring; `test_bundled_sa_task_catalog_has_82_rows`; `test_all_rows_are_chapter_3_or_4`; add two new tests)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: 21 catalog rows that Task 2's matrix fixtures and Task 3's interview questions both reference by `swe_id`.

- [ ] **Step 1: Write the failing tests**

Replace `test_bundled_sa_task_catalog_has_82_rows` and `test_all_rows_are_chapter_3_or_4` in `tests/test_sa_task_catalog_integrity.py` with the versions below, and add the two new tests after `test_chapter_4_has_37_rows`:

```python
def test_bundled_sa_task_catalog_has_103_rows():
    assert len(load_sa_task_catalog()) == 103


def test_all_rows_are_chapter_3_4_or_5():
    for row in load_sa_task_catalog():
        assert (
            row["section"].startswith("3.")
            or row["section"].startswith("4.")
            or row["section"].startswith("5.")
        )


def test_chapter_5_has_21_rows():
    ch5 = [r for r in load_sa_task_catalog() if r["section"].startswith("5.")]
    assert len(ch5) == 21


def test_chapter_5_rows_match_table_1_exactly():
    """Pins Chapter 5's exact (swe_id, section) pairs so a dropped or altered
    row fails loudly rather than only shifting a count another test asserts."""
    expected = [
        ("SWE-079", "5.1.2"), ("SWE-080", "5.1.3"), ("SWE-081", "5.1.4"),
        ("SWE-082", "5.1.5"), ("SWE-083", "5.1.6"), ("SWE-084", "5.1.7"),
        ("SWE-085", "5.1.8"), ("SWE-045", "5.1.9"), ("SWE-086", "5.2.1"),
        ("SWE-087", "5.3.2"), ("SWE-088", "5.3.3"), ("SWE-089", "5.3.4"),
        ("SWE-090", "5.4.2"), ("SWE-093", "5.4.3"), ("SWE-094", "5.4.4"),
        ("SWE-199", "5.4.5"), ("SWE-200", "5.4.6"), ("SWE-201", "5.5.1"),
        ("SWE-202", "5.5.2"), ("SWE-203", "5.5.3"), ("SWE-204", "5.5.4"),
    ]
    actual = [
        (r["swe_id"], r["section"])
        for r in load_sa_task_catalog()
        if r["section"].startswith("5.")
    ]
    assert actual == expected
```

Also update the module docstring's first line from `Chapter 3-4 rows` to `Chapter 3-5 rows`, and replace its final sentence `Extended (not replaced) by Part 2b to cover Chapter 4; Part 2c will extend it again for Chapter 5.` with `Extended (not replaced) by Part 2b for Chapter 4 and Part 2c for Chapter 5, which completes the table at 103 rows.`

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_sa_task_catalog_integrity.py -v`
Expected: FAIL — `test_bundled_sa_task_catalog_has_103_rows` asserts `82 == 103`, `test_chapter_5_has_21_rows` asserts `0 == 21`, `test_chapter_5_rows_match_table_1_exactly` asserts `[] == [...]`. `test_all_rows_are_chapter_3_4_or_5` PASSES already (it is a widening, not a new constraint) — that is expected and correct.

- [ ] **Step 3: Append the 21 rows**

Append to the end of `data/sa-task-catalog.yaml`, immediately after the `SWE-196` / `"4.6.6"` row. Order is Table 1's own order:

```yaml
- swe_id: "SWE-079"
  section: "5.1.2"
- swe_id: "SWE-080"
  section: "5.1.3"
- swe_id: "SWE-081"
  section: "5.1.4"
- swe_id: "SWE-082"
  section: "5.1.5"
- swe_id: "SWE-083"
  section: "5.1.6"
- swe_id: "SWE-084"
  section: "5.1.7"
- swe_id: "SWE-085"
  section: "5.1.8"
- swe_id: "SWE-045"
  section: "5.1.9"
- swe_id: "SWE-086"
  section: "5.2.1"
- swe_id: "SWE-087"
  section: "5.3.2"
- swe_id: "SWE-088"
  section: "5.3.3"
- swe_id: "SWE-089"
  section: "5.3.4"
- swe_id: "SWE-090"
  section: "5.4.2"
- swe_id: "SWE-093"
  section: "5.4.3"
- swe_id: "SWE-094"
  section: "5.4.4"
- swe_id: "SWE-199"
  section: "5.4.5"
- swe_id: "SWE-200"
  section: "5.4.6"
- swe_id: "SWE-201"
  section: "5.5.1"
- swe_id: "SWE-202"
  section: "5.5.2"
- swe_id: "SWE-203"
  section: "5.5.3"
- swe_id: "SWE-204"
  section: "5.5.4"
```

- [ ] **Step 4: Update the catalog header comment**

In `data/sa-task-catalog.yaml`, replace these three lines:

```
# Coverage: 82 of the table's 103 total rows — NPR 7150.2D Chapters 3-4
# See data/SA-TASK-CATALOG-COVERAGE.md for the full coverage status;
# Chapter 5 is a separate, not-yet-built sub-project (SP5 Part 2c).
```

with:

```
# Coverage: all 103 of the table's rows — NPR 7150.2D Chapters 3-5.
# See data/SA-TASK-CATALOG-COVERAGE.md for the full coverage status.
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_sa_task_catalog_integrity.py -v`
Expected: PASS, 10 tests. Note that `test_every_swe_id_exists_in_swe_catalog` and `test_section_matches_swe_catalog_section_for_every_row` now also cover the new rows without modification — if either fails, a section number was transcribed wrong.

- [ ] **Step 6: Run the full suite**

Run: `python3 -m pytest -q && ruff check .`
Expected: 187 passed, `All checks passed!`

- [ ] **Step 7: Commit**

```bash
git add data/sa-task-catalog.yaml tests/test_sa_task_catalog_integrity.py
git commit -m "feat: extend SA task catalog with NPR Chapter 5 rows, completing 103/103

Adds NASA-STD-8739.8B section 4.3 Table 1's 21 Chapter 5 rows (5.1 through
5.5) to data/sa-task-catalog.yaml, growing it from 82 to 103 — the table's
full row count. Updates the integrity tests' hardcoded count and chapter
constraint, and pins Chapter 5's exact (swe_id, section) pairs so a dropped
or altered row fails loudly.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: Record script and its tests

**Files:**
- Create: `skills/sa-task-verification-supporting/scripts/record_sa_task_verification_supporting.py`
- Test: `skills/sa-task-verification-supporting/scripts/test_record_sa_task_verification_supporting.py`

**Interfaces:**
- Consumes: Task 1's catalog rows only indirectly — the fixtures below hardcode their own matrix rows.
- Produces: `record_sa_task_verification_supporting(matrix_yaml_path, record_md_path, swe_ids, fields, evidence)` — the exact name and signature Task 3's SKILL.md "Running the script" block calls.

- [ ] **Step 1: Write the failing tests**

Create `skills/sa-task-verification-supporting/scripts/test_record_sa_task_verification_supporting.py`:

```python
import os

import pytest
import yaml
from record_sa_task_verification_supporting import record_sa_task_verification_supporting


def sample_matrix_rows():
    return [
        {"swe_id": "SWE-079", "section": "5.1.2", "software_class": "C", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-084", "section": "5.1.7", "software_class": "C", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-200", "section": "5.4.6", "software_class": "C", "status": "tailored-out", "evidence": None, "date": None},
    ]


def write_matrix(tmp_path):
    matrix_path = tmp_path / "sa-task-mapping-matrix.yaml"
    with open(matrix_path, "w") as f:
        yaml.dump(sample_matrix_rows(), f, sort_keys=False)
    return str(matrix_path)


def test_marks_rows_satisfied_and_appends_record(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "sa-task-verification-supporting.md")

    record_sa_task_verification_supporting(
        matrix_yaml_path=matrix_path,
        record_md_path=record_path,
        swe_ids=["SWE-079", "SWE-084"],
        fields={"cm_planning_and_change_control": "SCM plan baselined; configuration items and levels of control identified."},
        evidence="docs/nasa-compliance/widget-firmware/scm-plan.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    by_id = {r["swe_id"]: r for r in updated}
    assert by_id["SWE-079"]["status"] == "satisfied"
    assert by_id["SWE-079"]["evidence"] == "docs/nasa-compliance/widget-firmware/scm-plan.md"
    assert by_id["SWE-079"]["date"] is not None
    assert by_id["SWE-084"]["status"] == "satisfied"

    with open(record_path) as f:
        record = f.read()
    assert "SWE-079" in record
    assert "SWE-084" in record
    assert "SCM plan baselined" in record


def test_empty_swe_ids_raises_value_error(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")
    with pytest.raises(ValueError, match="at least one swe_id"):
        record_sa_task_verification_supporting(
            matrix_yaml_path=matrix_path, record_md_path=record_path,
            swe_ids=[], fields={}, evidence="x",
        )


def test_unknown_swe_id_raises_key_error(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")
    with pytest.raises(KeyError):
        record_sa_task_verification_supporting(
            matrix_yaml_path=matrix_path, record_md_path=record_path,
            swe_ids=["SWE-999"], fields={}, evidence="x",
        )


def test_tailored_out_row_raises_value_error_and_matrix_unmodified(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")
    with pytest.raises(ValueError, match="tailored-out"):
        record_sa_task_verification_supporting(
            matrix_yaml_path=matrix_path, record_md_path=record_path,
            swe_ids=["SWE-200"], fields={}, evidence="x",
        )
    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    by_id = {r["swe_id"]: r for r in unchanged}
    assert by_id["SWE-200"]["status"] == "tailored-out"
    assert not os.path.exists(record_path)


def test_second_call_appends_new_record_entry(tmp_path):
    matrix_path = write_matrix(tmp_path)
    record_path = str(tmp_path / "record.md")

    record_sa_task_verification_supporting(
        matrix_yaml_path=matrix_path, record_md_path=record_path,
        swe_ids=["SWE-079"], fields={"cm_planning_and_change_control": "First pass."},
        evidence="ev1.md",
    )
    with open(record_path) as f:
        first_len = len(f.read())

    record_sa_task_verification_supporting(
        matrix_yaml_path=matrix_path, record_md_path=record_path,
        swe_ids=["SWE-084"], fields={"cm_audits_and_release": "Second pass."},
        evidence="ev2.md",
    )
    with open(record_path) as f:
        content = f.read()
    assert len(content) > first_len
    assert content.count("## Recorded") == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd skills/sa-task-verification-supporting/scripts && python3 -m pytest test_record_sa_task_verification_supporting.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'record_sa_task_verification_supporting'`

- [ ] **Step 3: Write the implementation**

Create `skills/sa-task-verification-supporting/scripts/record_sa_task_verification_supporting.py`:

```python
import datetime

import yaml

DEFAULT_HEADER = (
    "# Software Assurance & Safety Task Verification Record "
    "(NASA-STD-8739.8B §4.3 Table 1, Chapter 5)\n\n"
)


def record_sa_task_verification_supporting(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
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

This differs from `skills/sa-task-verification-management-engineering/scripts/record_sa_task_verification_engineering.py` in exactly two places — the header string says `Chapter 5`, and the function name ends `_supporting`. That duplication is intentional per the spec's Decisions section; do not refactor it into a shared module.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd skills/sa-task-verification-supporting/scripts && python3 -m pytest test_record_sa_task_verification_supporting.py -v`
Expected: PASS, 5 tests.

- [ ] **Step 5: Run the full suite and lint**

Run: `python3 -m pytest -q && ruff check .`
Expected: 192 passed, `All checks passed!`. If ruff reports `I001` import-sorting on the new files, run `ruff check --fix .` and re-run.

- [ ] **Step 6: Commit**

```bash
git add skills/sa-task-verification-supporting/scripts/
git commit -m "feat: add record script for NPR Chapter 5 SA task verification

Mirrors the Chapter 3 and Chapter 4 record scripts — same signature, same
error handling (empty ids, unknown ids, tailored-out ids), same append-per-run
record format. Differs only in the record header's chapter and the function
name, matching this fork's per-skill-directory self-containment convention.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: `sa-task-verification-supporting` SKILL.md

**Files:**
- Create: `skills/sa-task-verification-supporting/SKILL.md`

**Interfaces:**
- Consumes: `record_sa_task_verification_supporting(matrix_yaml_path, record_md_path, swe_ids, fields, evidence)` from Task 2.
- Produces: the six `fields` keys the record file is written with — `cm_planning_and_change_control`, `cm_audits_and_release`, `risk_management`, `peer_reviews_and_inspections`, `measurements`, `non_conformance_and_defect`.

- [ ] **Step 1: Write the skill file**

Create `skills/sa-task-verification-supporting/SKILL.md` with exactly this content:

````markdown
---
name: sa-task-verification-supporting
description: Use to record a subsystem's NASA-STD-8739.8B §4.3 Table 1 software assurance and safety task evidence for NPR 7150.2D Chapter 5 (Supporting Software Life Cycle) requirements, once requirements-matrix has generated the SA task matrix
---

# Software Assurance & Safety Tasks — Supporting Life Cycle (NASA-STD-8739.8B §4.3 Table 1, NPR Ch.5)

## Overview

Records that software assurance and safety personnel actually performed the confirmation, assessment, audit, and analysis tasks §4.3 Table 1 assigns against each Chapter 5 (Supporting Software Life Cycle) requirement, and where the evidence for each lives. Does not perform software assurance or safety work itself — that's real engineering and assurance work this tool doesn't replace.

**Announce at start:** "I'm using the sa-task-verification-supporting skill to record your NASA-STD-8739.8B §4.3 Table 1 software assurance and safety task evidence for NPR Chapter 5."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.yaml` to already exist with at least one Chapter 5 row for this subsystem's class. This file is generated by `requirements-matrix` alongside the main requirements matrix — the same file `sa-task-verification-management` reads for Chapter 3 rows and `sa-task-verification-management-engineering` reads for Chapter 4, since all three skills share one matrix per subsystem.

If it's absent, or has no rows starting with `5.`, check `requirements-matrix` before assuming the chapter doesn't apply. Two things produce an empty result and they mean different things:

- **The class genuinely has no applicable Chapter 5 rows.** This is always true for **Class E**, which has zero of the 21 applicable. Class D has 8; Class F has 13; Class C has 19; Classes A and B have all 21.
- **`requirements-matrix` hasn't been re-run since these catalog rows existed.** Re-run it and the rows appear.

## The interview

Ask each group below in turn. For each, ask which of its listed SWE-ids have real, checkable evidence — an assurance assessment, a confirmed audit finding, a review record, a tracked risk or issue — and where that evidence lives. A vague "assurance handled it" answer is not sufficient, same standard `peer-review-record`, `ivv-verification-record`, `sa-task-verification-management`, and `sa-task-verification-management-engineering` established: the evidence must point at something a human auditor could actually go check. If a SWE-id has no real evidence yet, leave it out of that group's `swe_ids` below rather than recording an unverifiable claim.

1. **Configuration Management — Planning & Change Control (SWE-079, SWE-081, SWE-082, SWE-080, SWE-083).** Has someone assessed the project's software configuration management plan — does it exist, and does it actually satisfy what NPR 7150.2 and Center or project guidance ask for? Has the project pinned down which configuration items and which versions are under control, and are the safety-critical ones — hazard reports and safety analyses included — genuinely being configuration-managed? Are there procedures fixing the levels of control each item passes through, who may authorize a change, and who may make one at each level; does software assurance take part in the control activities themselves; and has anyone audited the project against those procedures to confirm they're followed rather than merely written? When changes to software or hardware are proposed, is their impact analyzed — safety and security impact specifically — and are those changes tracked, approved and documented before implementation, carried through to completion, tested, and run through the change control process? And is a record of each configuration item's status being kept current?

2. **Configuration Management — Audits & Release (SWE-084, SWE-045, SWE-085).** Has the project run software configuration audits to establish which version of each item is the correct one, and to confirm the audit's results line up with the records that define those items? For joint NASA/developer audits, has assurance either taken part or assessed the results, and are the findings tracked to closure rather than logged and forgotten? And on getting software out the door: are there established procedures for storing, processing, distributing, releasing, and supporting deliverable products, with audits confirming the project actually follows them?

3. **Risk Management (SWE-086).** Is there a risk management process that genuinely records, analyzes, plans, tracks, controls, and communicates every software risk along with its mitigation plan — and has anyone audited that process as it applies to the software activities, rather than assuming it works because it exists?

4. **Peer Reviews & Inspections (SWE-087, SWE-088, SWE-089).** Are software peer reviews actually performed and reported on across project activities, are the findings the project accepted then addressed, and have peer reviews been performed on the software assurance and software safety plans themselves? At each code inspection, is the source code confirmed against the conditions NPR 7150.2's SWE-134 lists "a" through "l", judged against what the software actually does for the applicable safety-critical requirements? Separately, does each peer review meet the NPR's own criteria "a" through "d", are the actions coming out of those reviews resolved, and has the peer-review process been audited? And are the reviews and their inspection measurements recorded?

5. **Measurements (SWE-090, SWE-093, SWE-094, SWE-199, SWE-200).** Is there a measurement program that establishes, records, maintains, reports, and uses software assurance, management, and technical measures — with trending analysis run and reported on quality and defect metrics, and any organizational metrics collected and sent to the organizational repository? Does the analysis of measurement data follow documented analysis procedures, and is the assurance measurement data itself analyzed? Is access to the measurement data, its analysis, and its status provided on request to at least the sponsoring Mission Directorate, the NASA Chief Engineer, the Center Technical Authorities, and Headquarters SMA? Does the project monitor and update its planned measurements so the software meets or beats its performance and functionality requirements including constraints, and are requirements that are missed — or heading that way — being tracked? And are software volatility metrics collected, tracked, reported, and analyzed as an early warning on requirements stability?

6. **Non-conformance & Defect Management (SWE-201, SWE-202, SWE-203, SWE-204).** Are all software non-conformances recorded and tracked through to resolution, and where one is accepted, is the rationale captured with it? Are severity levels defined, is the way they're applied assessed for accuracy, are severities assigned to non-conformances in tools and in COTS, GOTS, MOTS, open-source, and reused components, and is the count at each severity level per configuration item maintained or accessible? Are reported non-conformances in those acquired and reused components evaluated throughout the life cycle rather than only at acceptance, and is their impact on the software's safety, quality, and reliability assessed? And for high-severity non-conformances: has root cause analysis been completed and its results recorded and assessed for adequacy, have the processes that analysis implicates been examined, have improvement opportunities been assessed, and are the corrective actions tracked to closure?

## Running the script

```bash
cd <this-plugin's-install-path>/skills/sa-task-verification-supporting/scripts
python3 -c "
from record_sa_task_verification_supporting import record_sa_task_verification_supporting

record_sa_task_verification_supporting(
    matrix_yaml_path='<path to the subsystem's sa-task-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's sa-task-verification-supporting.md>',
    swe_ids=[<ids answered above with checkable evidence, e.g. 'SWE-079', 'SWE-084'>],
    fields={
        'cm_planning_and_change_control': '<answer to question 1>',
        'cm_audits_and_release': '<answer to question 2>',
        'risk_management': '<answer to question 3>',
        'peer_reviews_and_inspections': '<answer to question 4>',
        'measurements': '<answer to question 5>',
        'non_conformance_and_defect': '<answer to question 6>',
    },
    evidence='<the primary evidence artifact's path or reference>',
)
print('Recorded.')
"
```

Only pass ids that actually have checkable evidence for the fields you're filling in this run — you don't need to answer all 6 groups in one pass. Run the script again later as more evidence becomes available; each run appends a new `## Recorded` entry.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
````

- [ ] **Step 2: Verify the questions cover all 21 ids exactly once**

Run this from the repo root:

```bash
python3 -c "
import re, yaml
skill = open('skills/sa-task-verification-supporting/SKILL.md').read()
body = skill.split('## The interview')[1].split('## Running the script')[0]
CROSS_REFS = {'SWE-134'}  # cited in Q4 as a cross-reference, not a Ch.5 row
found = [i for i in re.findall(r'SWE-\d+', body) if i not in CROSS_REFS]
catalog = [r['swe_id'] for r in yaml.safe_load(open('data/sa-task-catalog.yaml')) if r['section'].startswith('5.')]
print('in questions:', len(found), 'unique:', len(set(found)))
print('missing from questions:', sorted(set(catalog) - set(found)) or 'NONE')
print('extra in questions  :', sorted(set(found) - set(catalog)) or 'NONE')
dupes = [i for i in set(found) if found.count(i) > 1]
print('duplicated          :', sorted(dupes) or 'NONE')
"
```

Expected output — all four lines must read exactly this way:
```
in questions: 21 unique: 21
missing from questions: NONE
extra in questions  : NONE
duplicated          : NONE
```

`SWE-134` is filtered by the `CROSS_REFS` set above: question 4 cites it as a cross-reference to another NPR requirement, not as a Chapter 5 row, and it is substantive — keep it in the prose. If you add any other cross-reference to a non-Chapter-5 requirement, add it to `CROSS_REFS` too, and say so in the PR body.

- [ ] **Step 3: Confirm no verbatim PDF phrasing**

Run:
```bash
pdftotext -layout reference/NASA-STD-8739.8B.pdf - \
  | awk '/^5 +Supporting Software Life Cycle Requirements/,/^4\.4 +Independent Verification/' > /tmp/ch5.txt
wc -l /tmp/ch5.txt                                  # expect 217
grep -cE "^5\.[0-9]+\.[0-9]+ +[0-9]{3}" /tmp/ch5.txt  # expect 21
```
If either number is off, the extraction is wrong — fix it before reviewing, do not eyeball a partial table. Then read `skills/sa-task-verification-supporting/SKILL.md`'s six questions side by side with `/tmp/ch5.txt`. Any run of six or more consecutive words shared with the source must be reworded. This is not optional — commit `149b2ff` exists solely because Part 2a shipped copied phrasing.

- [ ] **Step 4: Run the full suite and lint**

Run: `python3 -m pytest -q && ruff check .`
Expected: 192 passed, `All checks passed!` (SKILL.md is not executable content; this confirms nothing regressed.)

- [ ] **Step 5: Commit**

```bash
git add skills/sa-task-verification-supporting/SKILL.md
git commit -m "feat: add sa-task-verification-supporting skill for NPR Chapter 5

Six interview groups covering all 21 of NASA-STD-8739.8B section 4.3 Table 1's
Chapter 5 rows exactly once: CM planning/change control, CM audits/release,
risk management, peer reviews, measurements, and non-conformance management.
Splits only the oversized 5.1 subsection; every other question maps to one NPR
subsection. Precondition documents that Class E has zero applicable rows.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: Documentation close-out

**Files:**
- Modify: `data/SA-TASK-CATALOG-COVERAGE.md` (headline; add Chapter 5 section; delete "Not yet covered")
- Modify: `README.md:61-62` (skill table), `README.md:74` (catalog coverage bullet)
- Modify: `skills/requirements-matrix/SKILL.md:101` (third skill reference)

**Interfaces:**
- Consumes: the completed 103-row catalog from Task 1 and the skill name from Task 3.
- Produces: no code interface — documentation only.

- [ ] **Step 1: Rewrite the coverage doc's headline and Chapter 5 status**

In `data/SA-TASK-CATALOG-COVERAGE.md`:

Replace the headline line:
```
**`data/sa-task-catalog.yaml` covers 82 of NASA-STD-8739.8B §4.3 Table 1's 103 rows.**
```
with:
```
**`data/sa-task-catalog.yaml` covers all 103 of NASA-STD-8739.8B §4.3 Table 1's rows.**
```

Replace the entire `## Not yet covered` section — its heading, the Chapter 5 bullet, and the trailing paragraph beginning `requirements-matrix's sa-task-mapping-matrix.yaml output reflects` — with:

```markdown
## Covered — Chapter 5, Supporting Software Life Cycle, 21 rows (SP5 Part 2c)

- 5.1 Software Configuration Management
- 5.2 Software Risk Management
- 5.3 Software Peer Reviews/Inspections
- 5.4 Software Measurements
- 5.5 Software Non-conformance or Defect

Table 1 ends at §5.5.4 / SWE-204 — it has no Chapter 6 or 7 rows. With Chapter
5 added, this catalog covers the table in full.

Note: Class E has no applicable Chapter 5 rows at all. Per-class applicable
counts, inherited from `swe-catalog.yaml`: A 21, B 21, C 19, D 8, E 0, F 13.

A subsystem whose `sa-task-mapping-matrix.yaml` was generated before this
chapter landed carries only Chapter 3-4 rows; re-running `requirements-matrix`
regenerates it against the full catalog.
```

Also update the sentence `This catalog is being built the same way, one chapter at a time.` to `This catalog was built the same way, one chapter at a time.`

- [ ] **Step 2: Update the README skill table and coverage bullet**

In `README.md`, replace line 61-62's two rows with these three:

```markdown
| `sa-task-verification-management` | Records §4.3 Table 1 SA/safety task evidence for the NPR's Chapter 3 (Management) requirements — 45 of the catalog's 103 rows. |
| `sa-task-verification-management-engineering` | Same pattern for Chapter 4 (Engineering) requirements — 37 rows. |
| `sa-task-verification-supporting` | Same pattern for Chapter 5 (Supporting Life Cycle) requirements — the final 21 rows. All three skills read the same generated `sa-task-mapping-matrix.yaml`, each touching only its own chapter's rows. |
```

Replace line 74:
```
- `data/sa-task-catalog.yaml` covers 82 of §4.3 Table 1's 103 rows — Chapter 3 (45) and Chapter 4 (37). Chapter 5's remaining 21 rows are not yet covered; see `data/SA-TASK-CATALOG-COVERAGE.md`.
```
with:
```
- `data/sa-task-catalog.yaml` covers all 103 rows of §4.3 Table 1 — Chapter 3 (45), Chapter 4 (37), and Chapter 5 (21). See `data/SA-TASK-CATALOG-COVERAGE.md`.
```

Leave line 75 (`Appendix A hazard analysis is not yet covered.`) unchanged — it is still true.

- [ ] **Step 3: Update requirements-matrix's skill reference**

In `skills/requirements-matrix/SKILL.md`, on line 101 replace:
```
`sa-task-verification-management` requires this file to exist before it can record Chapter 3 SA task evidence, and `sa-task-verification-management-engineering` requires it for Chapter 4.
```
with:
```
`sa-task-verification-management` requires this file to exist before it can record Chapter 3 SA task evidence, `sa-task-verification-management-engineering` requires it for Chapter 4, and `sa-task-verification-supporting` requires it for Chapter 5.
```

- [ ] **Step 4: Verify no stale coverage claims remain**

Run: `grep -rn "82 of\|not yet covered\|Part 2c" README.md data/ skills/ --include="*.md" --include="*.yaml"`
Expected: no hits referring to the SA task catalog being incomplete. Hits mentioning Appendix A hazard analysis as uncovered are correct and stay.

- [ ] **Step 5: Run the full suite and lint**

Run: `python3 -m pytest -q && ruff check .`
Expected: 192 passed, `All checks passed!`

- [ ] **Step 6: Commit**

```bash
git add data/SA-TASK-CATALOG-COVERAGE.md README.md skills/requirements-matrix/SKILL.md
git commit -m "docs: record SA task catalog as complete at 103/103

Rewrites SA-TASK-CATALOG-COVERAGE.md around full coverage — Chapter 5 listed
as covered, 'Not yet covered' section removed, per-class applicable counts
documented (Class E has none). README presents the three SA-task skills as
jointly covering all of section 4.3 Table 1. Appendix A hazard analysis
remains listed as uncovered, which is still accurate.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Mandatory second verification round

Part 2a shipped interview questions containing fabricated content; only a second independent review caught it. This task is that review, done with fresh eyes against the source rather than against Task 3's own reasoning. It produces no code.

**Files:**
- Modify (only if defects are found): `skills/sa-task-verification-supporting/SKILL.md`, `data/sa-task-catalog.yaml`

**Interfaces:**
- Consumes: everything from Tasks 1-4.
- Produces: the verification evidence pasted into the PR body.

- [ ] **Step 1: Re-extract the source rows independently**

Run:
```bash
pdftotext -layout reference/NASA-STD-8739.8B.pdf /tmp/std-verify.txt
grep -nE "^5\.[0-9]+\.[0-9]+ +[0-9]{3}" /tmp/std-verify.txt
```
Expected: exactly 21 lines, from `5.1.2 079` through `5.5.4 204`. Record the list. If the count is not 21, stop and report — the catalog is wrong, not the test.

- [ ] **Step 2: Diff that list against the catalog**

Run:
```bash
python3 -c "
import re, yaml
src = re.findall(r'^(5\.\d+\.\d+) +(\d{3})', open('/tmp/std-verify.txt').read(), re.M)
src_pairs = [(f'SWE-{n}', s) for s, n in src]
cat = [(r['swe_id'], r['section']) for r in yaml.safe_load(open('data/sa-task-catalog.yaml')) if r['section'].startswith('5.')]
print('source rows :', len(src_pairs))
print('catalog rows:', len(cat))
print('match       :', src_pairs == cat)
print('only in source :', sorted(set(src_pairs) - set(cat)) or 'NONE')
print('only in catalog:', sorted(set(cat) - set(src_pairs)) or 'NONE')
"
```
Expected: `match: True`, both "only in" lines `NONE`.

- [ ] **Step 3: Verify every question claim traces to a source task**

For each of the six questions in `SKILL.md`, read its SWE-ids' task text in the PDF and confirm every claim the question asks about appears there. Specifically confirm these five, which are the ones most likely to have been invented:
- Question 1's "levels of control / who may authorize / who may make changes at each level" — trace to SWE-082's requirement text.
- Question 4's "SWE-134 conditions a through l" and "NPR criteria a through d" — trace to SWE-087 and SWE-088's task text respectively; confirm the letters are right.
- Question 5's four named recipients (Sponsoring Mission Directorate, NASA Chief Engineer, Center Technical Authorities, Headquarters SMA) — trace to SWE-094's task text; confirm the list is complete and none invented.
- Question 5's "volatility metrics" — trace to SWE-200.
- Question 6's "root cause analysis on high severity non-conformances" and the four sub-tasks — trace to SWE-204.

Any claim that cannot be traced is removed from the question. Do not soften it, do not reword it — remove it.

- [ ] **Step 4: Re-run the coverage check from Task 3 Step 2**

Expected: unchanged — 21 unique, no missing, no extra, no duplicates. If Step 3 removed a claim, confirm no SWE-id was lost with it.

- [ ] **Step 5: Full verification**

Run: `python3 -m pytest -q && ruff check .`
Expected: 192 passed, `All checks passed!`

- [ ] **Step 6: Commit any corrections**

Only if Step 3 found defects:
```bash
git add skills/sa-task-verification-supporting/SKILL.md
git commit -m "fix: correct SA task interview claims that did not trace to the standard

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```
If no defects were found, make no commit — record the verification result for the PR body instead.

---

## Done Criteria

- [ ] `data/sa-task-catalog.yaml` has 103 rows; Chapter 5's 21 pinned by test
- [ ] `python3 -m pytest -q` → 192 passed; `ruff check .` clean
- [ ] `skills/sa-task-verification-supporting/` has SKILL.md, record script, and test file
- [ ] All 21 Chapter 5 SWE-ids appear in the interview exactly once
- [ ] Second verification round complete, its evidence captured for the PR body
- [ ] Coverage doc, README, and requirements-matrix SKILL.md reflect 103/103
- [ ] PR opened against `main` of `adam-schneider-dev/superpowers-nasa-swe`, PR template filled in full
