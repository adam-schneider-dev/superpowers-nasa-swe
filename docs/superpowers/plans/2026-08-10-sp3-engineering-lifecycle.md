# SP3 — Engineering Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the catalog's one remaining gap (§4.1, Software Requirements) and build six new skills — one per NPR 7150.2D §4.1-4.6 subsection — that record engineering-lifecycle compliance decisions against the subsystem's classification and Requirements Mapping Matrix.

**Architecture:** Same as SP1/SP2 — each skill is a thin `SKILL.md` prompt delegating all decision/record logic to a pure, unit-tested Python script under that skill's `scripts/` directory. Every skill records a decision and cites evidence; none performs the underlying engineering work (no architecture authored, no code written, no tests run). All six are standalone — no edits to `brainstorming`, `writing-plans`, `test-driven-development`, `code-review`, or `finishing-a-development-branch`, and no hooks. Enforcement was explicitly deferred during brainstorming (`docs/superpowers/specs/2026-08-10-sp3-engineering-lifecycle-design.md`, "Decisions Made This Session") — do not add any in this plan.

**Tech Stack:** Python 3.14, PyYAML 6.0, pytest 9.0 (already pinned in `scripts/requirements.txt` from SP1).

## Global Constraints

- Repo root: `/home/adam/RiderProjects/superpowers-nasa-swe`
- No verbatim NPR 7150.2D requirement text is ever stored in the catalog or emitted compliance files — every requirement is cited as `NPR 7150.2D §<section>, SWE-<id>` only. A `SKILL.md`'s own interview questions may paraphrase a requirement's intent, but never quote its sentence.
- Current catalog schema (one row per SWE requirement): `section` (str), `swe_id` (str, format `SWE-\d+`), `class_ae_authority` (non-empty str), `classes` (dict with exactly keys `A,B,C,D,E,F` → bool), `class_f_authority` (str or `null`, non-null only where `classes.F` is `true`)
- Catalog extraction method: `pdftotext -bbox-layout`, binning cells by x-coordinate — never visual reading. Appendix C's fixed column coordinates: `47 Section | 95 SWE # | 131 Requirement Text | 310 Class A-E Authority | 373 A | 390 B | 407 C | 424 D | 441 E | 467 Class F Authority | 530 F`
- Output paths (in the *consuming* project, under `docs/nasa-compliance/<subsystem>/`): `requirements-definition.md`, `architecture-record.md`, `design-record.md`, `implementation-record.md`, `test-record.md`, `operations-retirement.md`, alongside SP1/SP2's existing `classification.yaml`, `requirements-mapping-matrix.yaml`, `requirements-mapping-matrix.md`, `tailoring-log.md`.
- Reference to an unknown/missing SWE-id → hard error (`KeyError`), never silently skipped.
- Every one of the six new scripts must guard against marking a `tailored-out` row `satisfied` — raise `ValueError` naming the row, leave the matrix unchanged. This is a carry-forward invariant from SP2's fix wave, not new design.
- None of the six skills perform the underlying engineering work (no architecture authored in `architecture-record`, no code written in `implementation-record`, no tests run in `test-record`) — if the underlying artifact doesn't exist yet, the skill says so and does not fabricate a value.
- Do not edit `skills/brainstorming/`, `skills/writing-plans/`, `skills/test-driven-development/`, `skills/code-review/`, or `skills/finishing-a-development-branch/`, and do not add any hook under `hooks/`. This was explicitly decided during brainstorming and reaffirmed after reconsideration — see the spec's "Decisions Made This Session".
- Final review for this plan must check the diff against **both** `docs/superpowers/specs/2026-08-10-sp3-engineering-lifecycle-design.md` and this plan, not just this plan — per the project memory from SP2's `reuse-assessment` spec-vs-plan drift finding.

---

### Task 1: Extend the catalog with NPR §4.1 rows (Software Requirements)

**Files:**
- Modify: `data/swe-catalog.yaml`
- Modify: `data/CATALOG-COVERAGE.md`
- Modify: `tests/test_catalog_integrity.py`
- Modify: `skills/requirements-matrix/SKILL.md`

**Interfaces:**
- Consumes: `validate_catalog()` (`skills/requirements-matrix/scripts/validate_catalog.py`, SP1) and `filter_rows_for_class()` (`skills/requirements-matrix/scripts/filter_matrix.py`, SP1).
- Produces: 6 additional rows appended to `data/swe-catalog.yaml` (100 total, closing the catalog), readable by every later task's `requirements-definition` skill via the subsystem's `requirements-mapping-matrix.yaml`.

The 6 rows (Appendix C pages 69-70) were already extracted and verified with `pdftotext -bbox-layout` during this plan's brainstorming — the values below are real, not placeholders.

- [ ] **Step 1: Re-verify the extraction**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
pdftotext -bbox-layout -f 69 -l 70 reference/NPR_7150.2D.pdf - > /tmp/appendix-c-sec4.1.bbox.xml
grep -c '4\.1\.' /tmp/appendix-c-sec4.1.bbox.xml
```

Expected: at least 6 matches (one `<word>` tag per row's section label, e.g. `4.1.2`, plus any line-wrapped repeats).

- [ ] **Step 2: Insert the 6 rows into `data/swe-catalog.yaml`**

Insert immediately after the existing `3.12.1`/`SWE-052` entry and before the existing `4.2.3`/`SWE-057` entry, preserving Appendix C order:

```yaml
- section: "4.1.2"
  swe_id: "SWE-050"
  class_ae_authority: "Center"
  classes: {A: true, B: true, C: true, D: true, E: false, F: true}
  class_f_authority: "CIO"
- section: "4.1.3"
  swe_id: "SWE-051"
  class_ae_authority: "Center"
  classes: {A: true, B: true, C: true, D: false, E: false, F: false}
  class_f_authority: null
- section: "4.1.4"
  swe_id: "SWE-184"
  class_ae_authority: "Center"
  classes: {A: true, B: true, C: true, D: false, E: false, F: false}
  class_f_authority: null
- section: "4.1.5"
  swe_id: "SWE-053"
  class_ae_authority: "Center"
  classes: {A: true, B: true, C: true, D: true, E: false, F: true}
  class_f_authority: "CIO"
- section: "4.1.6"
  swe_id: "SWE-054"
  class_ae_authority: "Center"
  classes: {A: true, B: true, C: true, D: true, E: false, F: true}
  class_f_authority: "CIO"
- section: "4.1.7"
  swe_id: "SWE-055"
  class_ae_authority: "Center"
  classes: {A: true, B: true, C: true, D: true, E: false, F: true}
  class_f_authority: "CIO"
```

None of the six carry a Class E mark — consistent with §4.1 contributing zero rows to Appendix C's 12 Class-E marks (all 12 already sit in Chapter 3, per SP2).

- [ ] **Step 3: Validate the transcription**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
python3 -c "
import yaml, sys
sys.path.insert(0, 'skills/requirements-matrix/scripts')
from validate_catalog import validate_catalog
from filter_matrix import filter_rows_for_class

with open('data/swe-catalog.yaml') as f:
    rows = yaml.safe_load(f)

errors = validate_catalog(rows)
if errors:
    for e in errors:
        print('ERROR:', e)
    sys.exit(1)

print(f'{len(rows)} rows valid')
print('Class E rows:', len(filter_rows_for_class(rows, 'E')))
"
```

Expected: `100 rows valid` and `Class E rows: 12` (unchanged from SP2 — §4.1 adds no Class E marks). If either number differs, re-check the transcription in Step 2 before proceeding.

- [ ] **Step 4: Update `tests/test_catalog_integrity.py`**

Change line 31 from:

```python
def test_bundled_catalog_row_count_matches_documented_coverage():
    assert len(load_catalog()) == 94
```

to:

```python
def test_bundled_catalog_row_count_matches_documented_coverage():
    assert len(load_catalog()) == 100
```

No other assertion in this file needs to change — `test_class_e_has_exactly_the_documented_row_count`, `test_swe_015_f_mark_has_no_named_authority`, and `test_class_f_authority_is_only_named_where_class_f_applies` are all unaffected by §4.1's rows.

- [ ] **Step 5: Run the full test suite**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
python3 -m pytest tests/test_catalog_integrity.py -v
```

Expected: all 5 tests pass.

- [ ] **Step 6: Update `data/CATALOG-COVERAGE.md`**

Replace the file's content with:

```markdown
# SWE Catalog Coverage

**`data/swe-catalog.yaml` covers all 100 rows in NPR 7150.2D Appendix C.**

The 100-row figure is the count of `Section` + `SWE #` pairs in the Appendix C
table (`reference/NPR_7150.2D.pdf`, pages 56-78), extracted programmatically
rather than counted by eye — see "Verifying coverage" below to reproduce it.

## Covered — Appendix C pages 56-78, 100 rows

- 3.1 Software Life Cycle Planning
- 3.2 Software Cost Estimation
- 3.3 Software Schedules
- 3.4 Software Training
- 3.5 Software Classification Assessments
- 3.6 Software Assurance and Software Independent Verification & Validation
- 3.7 Safety-Critical Software
- 3.8 Automatic Generation of Software Source Code
- 3.9 Software Development Processes and Practices
- 3.10 Software Reuse
- 3.11 Software Cybersecurity
- 3.12 Software Bi-Directional Traceability
- 4.1 Software Requirements
- 4.2 Software Architecture
- 4.3 Software Design
- 4.4 Software Implementation
- 4.5 Software Testing
- 4.6 Software Operations, Maintenance, and Retirement
- 5.1 Software Configuration Management
- 5.2 Software Risk Management
- 5.3 Software Peer Reviews/Inspections
- 5.4 Software Measurements
- 5.5 Software Non-conformance or Defect Management

Chapter 2 (Roles/Responsibilities) is excluded permanently, not pending:
NPR 7150.2D §1.3.1 states Chapter 2's requirements are not part of the
Requirements Mapping Matrix. It is not counted in the 100.

## §3.2.1/SWE-015: a real null Class F Authority, not a bug

§3.2.1 carries a Class F mark (`classes.F: true`) with a blank Class F
Authority cell in the source standard itself (`class_f_authority: null`).
`skills/requirements-matrix/scripts/validate_catalog.py` deliberately does not
reject this combination — only the converse (an authority with no F mark) is
an error. `skills/tailoring-request/SKILL.md` tells the user plainly when a
row's `default_approver` is `null` rather than presenting `null` as a name.

## Class E: no longer an empty-catalog gap

Earlier revisions of this file noted that Class E returned zero rows because
all 12 of Appendix C's Class E marks sat in the then-untranscribed Chapter 3.
Chapter 3 is now transcribed, so Class E returns its real 12 rows. §4.1
(SP3) contributes none of its own.

## Verifying coverage

The row count and every row's class marks are checked against the PDF with
`pdftotext -bbox-layout`, which reports each cell's x-coordinate. Appendix C's
columns sit at fixed offsets on every page:

```
 47 Section | 95 SWE # | 131 Requirement Text | 310 Class A-E Authority
 | 373 A | 390 B | 407 C | 424 D | 441 E | 467 Class F Authority | 530 F
```

Reading those columns by eye is what produced the original mismapping of the
Class F Authority and Class F applicability columns during SP1. Use the coordinates.

## Extending coverage

Coverage is complete — there is no remaining gap to extend. If NPR 7150.2D is
ever revised, repeat this method: extract the changed page range with
`pdftotext -bbox-layout`, assign each cell to a column by x-coordinate (never
visually), append/update rows in Appendix C order, then run
`tests/test_catalog_integrity.py` and update its expected counts.
```

- [ ] **Step 7: Update `skills/requirements-matrix/SKILL.md`'s stale gap note**

In `skills/requirements-matrix/SKILL.md`, find this sentence in step 2:

```markdown
2. Read `<this plugin's install path>/data/swe-catalog.yaml`. Check `<this plugin's install path>/data/CATALOG-COVERAGE.md` and tell the user which NPR sections are and are not yet represented in the catalog — an incomplete catalog means an incomplete matrix, and the user needs to know that up front, not discover it later. The one remaining gap is **§4.1, Software Requirements** (6 rows), which is missing for every class: a matrix generated today carries no requirements-definition rows, and any subsystem tracking that area must be told so. Class E is no longer a special case — its 12 rows are populated.
```

Replace it with:

```markdown
2. Read `<this plugin's install path>/data/swe-catalog.yaml`. The catalog covers all 100 Appendix C rows — no gap to disclose. Class E returns its real 12 rows.
```

- [ ] **Step 8: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add data/swe-catalog.yaml data/CATALOG-COVERAGE.md tests/test_catalog_integrity.py skills/requirements-matrix/SKILL.md
git commit -m "data: close the catalog's last gap — NPR §4.1 Software Requirements (100/100 rows)"
```

---

### Task 2: `requirements-definition` record script (TDD)

**Files:**
- Create: `skills/requirements-definition/scripts/record_requirements_definition.py`
- Test: `skills/requirements-definition/scripts/test_record_requirements_definition.py`

**Interfaces:**
- Consumes: a `requirements-mapping-matrix.yaml` file (schema from SP1) and a `requirements-definition.md` path (may not yet exist).
- Produces: `record_requirements_definition(matrix_yaml_path: str, record_md_path: str, swe_ids: list[str], fields: dict, evidence: str) -> None`. Raises `ValueError` if `swe_ids` is empty, or if any target row is `tailored-out`. Raises `KeyError` naming unknown ids. On success: sets each matching row's `status` to `"satisfied"`, `evidence`, `date`; appends a formatted entry to the record markdown file (creating it with a header if absent).

- [ ] **Step 1: Write the failing tests**

```python
# skills/requirements-definition/scripts/test_record_requirements_definition.py
import yaml
import pytest
from record_requirements_definition import record_requirements_definition


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-050", "section": "4.1.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-051", "section": "4.1.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "requirements-definition.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_requirements_definition(str(matrix_path), str(record_path), swe_ids=[], fields={"requirements_capture": "r"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "requirements-definition.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_requirements_definition(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"requirements_capture": "r"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "requirements-definition.md"
    write_matrix(matrix_path, sample_rows())

    record_requirements_definition(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-050", "SWE-051"],
        fields={
            "requirements_capture": "Requirements captured in DOORS, baselined at PDR, includes 2 reused OSS components.",
            "requirements_analysis": "Flowed down from L2 systems requirements SYS-014, SYS-019; hardware spec HW-003.",
        },
        evidence="docs/requirements/software-requirements-spec.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "DOORS" in content
    assert "SWE-050" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "requirements-definition.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Requirements (NPR 7150.2D §4.1)\n\n")

    record_requirements_definition(str(matrix_path), str(record_path), swe_ids=["SWE-050"], fields={"requirements_capture": "a"}, evidence="e1")
    record_requirements_definition(str(matrix_path), str(record_path), swe_ids=["SWE-051"], fields={"requirements_capture": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "requirements-definition.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_requirements_definition(str(matrix_path), str(record_path), swe_ids=["SWE-050"], fields={"requirements_capture": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-050")["status"] == "tailored-out"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/skills/requirements-definition/scripts
python3 -m pytest test_record_requirements_definition.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'record_requirements_definition'`

- [ ] **Step 3: Implement `record_requirements_definition.py`**

```python
# skills/requirements-definition/scripts/record_requirements_definition.py
import datetime
import yaml

DEFAULT_HEADER = "# Software Requirements (NPR 7150.2D §4.1)\n\n"


def record_requirements_definition(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
    if not swe_ids:
        raise ValueError("at least one swe_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["swe_id"]: r for r in rows}
    missing = [s for s in swe_ids if s not in row_by_id]
    if missing:
        raise KeyError(f"unknown swe_id(s) in requirements mapping matrix: {', '.join(missing)}")

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
python3 -m pytest test_record_requirements_definition.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/requirements-definition/scripts/record_requirements_definition.py skills/requirements-definition/scripts/test_record_requirements_definition.py
git commit -m "feat: add requirements-definition record logic"
```

---

### Task 3: `requirements-definition` skill

**Files:**
- Create: `skills/requirements-definition/SKILL.md`

**Interfaces:**
- Consumes: `record_requirements_definition` from Task 2.
- Produces: `docs/nasa-compliance/<subsystem>/requirements-definition.md` and updates to `.../requirements-mapping-matrix.yaml`, in the consuming project.

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: requirements-definition
description: Use to record a subsystem's NPR 7150.2D §4.1 software requirements definition, analysis, safety constraints, change tracking, and validation
---

# Software Requirements (NPR 7150.2D §4.1)

## Overview

Records how software requirements are established, analyzed, tracked, and validated per §4.1. Depends on the catalog's §4.1 rows (added in this same sub-project) — regenerate the matrix with `requirements-matrix` first if it predates that.

**Announce at start:** "I'm using the requirements-definition skill to record your NPR 7150.2D §4.1 software requirements compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist (produced by `requirements-matrix`). If it doesn't exist, stop and run that skill first.

## The interview

1. **Requirements capture (§4.1.2, SWE-050).** How are software requirements established, captured, recorded, approved, and maintained as part of the technical specification? If any requirements cover COTS/GOTS/MOTS/OSS/reused components, say so.
2. **Requirements analysis (§4.1.3, SWE-051).** Point to the requirements analysis performed — based on flowed-down/derived requirements from top-level systems engineering requirements, safety and reliability analyses, and hardware specifications/design.
3. **Safety-related constraints (§4.1.4, SWE-184).** Are software-related safety constraints, controls, mitigations, and assumptions between hardware, operator, and software documented in the requirements? Point to where.
4. **Requirements change tracking (§4.1.5, SWE-053).** How are changes to software requirements tracked and managed?
5. **Inconsistency tracking (§4.1.6, SWE-054).** How are inconsistencies among requirements, project plans, and software products identified, corrective-actioned, and tracked to closure?
6. **Requirements validation (§4.1.7, SWE-055).** How was requirements validation performed to confirm the software will perform as intended in the customer environment?

If any answer doesn't exist yet as a real artifact, tell the user and leave that SWE-id out of `swe_ids` below rather than fabricating a pointer.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/requirements-definition/scripts
python3 -c "
from record_requirements_definition import record_requirements_definition

record_requirements_definition(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's requirements-definition.md>',
    swe_ids=[<the SWE-ids answered above with a real artifact, e.g. 'SWE-050', 'SWE-051', 'SWE-184', 'SWE-053', 'SWE-054', 'SWE-055'>],
    fields={
        'requirements_capture': '<answer to question 1>',
        'requirements_analysis': '<answer to question 2>',
        'safety_constraints': '<answer to question 3>',
        'change_tracking': '<answer to question 4>',
        'inconsistency_tracking': '<answer to question 5>',
        'requirements_validation': '<answer to question 6>',
    },
    evidence='<the single most authoritative pointer among the answers above, e.g. the requirements spec path>',
)
print('Recorded.')
"
```

Only include SWE-ids for questions with a real answer — do not mark a row satisfied on a placeholder.

## Writing the output

The script both updates `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` and appends to `.../requirements-definition.md`. Confirm to the user which SWE-ids were marked satisfied and where the record was written.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/requirements-definition/SKILL.md
git commit -m "feat: add requirements-definition skill"
```

---

### Task 4: `architecture-record` record script (TDD)

**Files:**
- Create: `skills/architecture-record/scripts/record_architecture_record.py`
- Test: `skills/architecture-record/scripts/test_record_architecture_record.py`

**Interfaces:**
- Consumes/Produces: same shape as Task 2, renamed `record_architecture_record(matrix_yaml_path, record_md_path, swe_ids, fields, evidence) -> None`, same error behavior (empty `swe_ids` → `ValueError`; unknown id → `KeyError`; `tailored-out` target → `ValueError`).

- [ ] **Step 1: Write the failing tests**

```python
# skills/architecture-record/scripts/test_record_architecture_record.py
import yaml
import pytest
from record_architecture_record import record_architecture_record


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-057", "section": "4.2.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-143", "section": "4.2.4", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "architecture-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_architecture_record(str(matrix_path), str(record_path), swe_ids=[], fields={"architecture_description": "d"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "architecture-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_architecture_record(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"architecture_description": "d"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "architecture-record.md"
    write_matrix(matrix_path, sample_rows())

    record_architecture_record(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-057", "SWE-143"],
        fields={
            "architecture_description": "docs/architecture/software-architecture.md, C4 container + component views.",
            "architecture_review": "Category 2 project, Class C payload risk — architecture review not required per NPR 8705.4.",
        },
        evidence="docs/architecture/software-architecture.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "C4 container" in content
    assert "SWE-057" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "architecture-record.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Architecture (NPR 7150.2D §4.2)\n\n")

    record_architecture_record(str(matrix_path), str(record_path), swe_ids=["SWE-057"], fields={"architecture_description": "a"}, evidence="e1")
    record_architecture_record(str(matrix_path), str(record_path), swe_ids=["SWE-143"], fields={"architecture_description": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "architecture-record.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_architecture_record(str(matrix_path), str(record_path), swe_ids=["SWE-057"], fields={"architecture_description": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-057")["status"] == "tailored-out"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/skills/architecture-record/scripts
python3 -m pytest test_record_architecture_record.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'record_architecture_record'`

- [ ] **Step 3: Implement `record_architecture_record.py`**

```python
# skills/architecture-record/scripts/record_architecture_record.py
import datetime
import yaml

DEFAULT_HEADER = "# Software Architecture (NPR 7150.2D §4.2)\n\n"


def record_architecture_record(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
    if not swe_ids:
        raise ValueError("at least one swe_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["swe_id"]: r for r in rows}
    missing = [s for s in swe_ids if s not in row_by_id]
    if missing:
        raise KeyError(f"unknown swe_id(s) in requirements mapping matrix: {', '.join(missing)}")

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
python3 -m pytest test_record_architecture_record.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/architecture-record/scripts/record_architecture_record.py skills/architecture-record/scripts/test_record_architecture_record.py
git commit -m "feat: add architecture-record record logic"
```

---

### Task 5: `architecture-record` skill

**Files:**
- Create: `skills/architecture-record/SKILL.md`

**Interfaces:**
- Consumes: `record_architecture_record` from Task 4.
- Produces: `docs/nasa-compliance/<subsystem>/architecture-record.md` and updates to `.../requirements-mapping-matrix.yaml`.

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: architecture-record
description: Use to record a subsystem's NPR 7150.2D §4.2 software architecture description and, where applicable, its architecture review
---

# Software Architecture (NPR 7150.2D §4.2)

## Overview

Records the software architecture description transformed from the requirements, and — for projects where NPR requires it — the architecture review. Does not author the architecture itself.

**Announce at start:** "I'm using the architecture-record skill to record your NPR 7150.2D §4.2 software architecture compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

## The interview

1. **Architecture description (§4.2.3, SWE-057).** Point to the recorded software architecture the requirements were transformed into. If it doesn't exist yet, say so.
2. **Architecture review (§4.2.4, SWE-143).** Is this a Category 1 project per NPR 7120.5, or a Category 2 project with Class A or B payload risk per NPR 8705.4? If yes, point to the software architecture review performed. If neither applies, record that this row doesn't apply to this subsystem rather than fabricating a review.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/architecture-record/scripts
python3 -c "
from record_architecture_record import record_architecture_record

record_architecture_record(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's architecture-record.md>',
    swe_ids=[<SWE-ids answered above with a real artifact, e.g. 'SWE-057', 'SWE-143'>],
    fields={
        'architecture_description': '<answer to question 1>',
        'architecture_review': '<answer to question 2>',
    },
    evidence='<the architecture document's path>',
)
print('Recorded.')
"
```

If §4.2.4/SWE-143 genuinely doesn't apply (not Category 1, not Category 2 with Class A/B payload risk), still include it in `swe_ids` with a `fields` note explaining why it doesn't apply — the row is satisfied by that explicit non-applicability determination, not skipped silently.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/architecture-record/SKILL.md
git commit -m "feat: add architecture-record skill"
```

---

### Task 6: `design-record` record script (TDD)

**Files:**
- Create: `skills/design-record/scripts/record_design_record.py`
- Test: `skills/design-record/scripts/test_record_design_record.py`

**Interfaces:**
- Consumes/Produces: same shape as Task 2, renamed `record_design_record(matrix_yaml_path, record_md_path, swe_ids, fields, evidence) -> None`.

- [ ] **Step 1: Write the failing tests**

```python
# skills/design-record/scripts/test_record_design_record.py
import yaml
import pytest
from record_design_record import record_design_record


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-058", "section": "4.3.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "design-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_design_record(str(matrix_path), str(record_path), swe_ids=[], fields={"design_description": "d"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "design-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_design_record(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"design_description": "d"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "design-record.md"
    write_matrix(matrix_path, sample_rows())

    record_design_record(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-058"],
        fields={"design_description": "docs/design/software-design-document.md, module-level decomposition down to unit interfaces."},
        evidence="docs/design/software-design-document.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    assert updated[0]["status"] == "satisfied"
    assert updated[0]["date"] is not None

    content = record_path.read_text()
    assert "module-level decomposition" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "design-record.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Design (NPR 7150.2D §4.3)\n\n")

    record_design_record(str(matrix_path), str(record_path), swe_ids=["SWE-058"], fields={"design_description": "a"}, evidence="e1")
    record_design_record(str(matrix_path), str(record_path), swe_ids=["SWE-058"], fields={"design_description": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "design-record.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_design_record(str(matrix_path), str(record_path), swe_ids=["SWE-058"], fields={"design_description": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-058")["status"] == "tailored-out"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/skills/design-record/scripts
python3 -m pytest test_record_design_record.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'record_design_record'`

- [ ] **Step 3: Implement `record_design_record.py`**

```python
# skills/design-record/scripts/record_design_record.py
import datetime
import yaml

DEFAULT_HEADER = "# Software Design (NPR 7150.2D §4.3)\n\n"


def record_design_record(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
    if not swe_ids:
        raise ValueError("at least one swe_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["swe_id"]: r for r in rows}
    missing = [s for s in swe_ids if s not in row_by_id]
    if missing:
        raise KeyError(f"unknown swe_id(s) in requirements mapping matrix: {', '.join(missing)}")

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
python3 -m pytest test_record_design_record.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/design-record/scripts/record_design_record.py skills/design-record/scripts/test_record_design_record.py
git commit -m "feat: add design-record record logic"
```

---

### Task 7: `design-record` skill

**Files:**
- Create: `skills/design-record/SKILL.md`

**Interfaces:**
- Consumes: `record_design_record` from Task 6.
- Produces: `docs/nasa-compliance/<subsystem>/design-record.md` and updates to `.../requirements-mapping-matrix.yaml`.

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: design-record
description: Use to record a subsystem's NPR 7150.2D §4.3 software design, based on its architecture, down to codeable/testable units
---

# Software Design (NPR 7150.2D §4.3)

## Overview

Records the software design description — based on the architecture, describing lower-level units so they can be coded, compiled, and tested. Does not author the design itself.

**Announce at start:** "I'm using the design-record skill to record your NPR 7150.2D §4.3 software design compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

## The interview

1. **Design description (§4.3.2, SWE-058).** Point to the software design document, based on the architecture, that describes the lower-level units down to a level where they can be coded, compiled, and tested. If it doesn't exist yet, say so.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/design-record/scripts
python3 -c "
from record_design_record import record_design_record

record_design_record(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's design-record.md>',
    swe_ids=['SWE-058'],
    fields={'design_description': '<answer to question 1>'},
    evidence='<the design document's path>',
)
print('Recorded.')
"
```

If no design document exists yet, don't run the script — tell the user the row stays `not-started` until one exists.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/design-record/SKILL.md
git commit -m "feat: add design-record skill"
```

---

### Task 8: `implementation-record` record script (TDD)

**Files:**
- Create: `skills/implementation-record/scripts/record_implementation_record.py`
- Test: `skills/implementation-record/scripts/test_record_implementation_record.py`

**Interfaces:**
- Consumes/Produces: same shape as Task 2, renamed `record_implementation_record(matrix_yaml_path, record_md_path, swe_ids, fields, evidence) -> None`.

- [ ] **Step 1: Write the failing tests**

```python
# skills/implementation-record/scripts/test_record_implementation_record.py
import yaml
import pytest
from record_implementation_record import record_implementation_record


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-060", "section": "4.4.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-061", "section": "4.4.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "implementation-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_implementation_record(str(matrix_path), str(record_path), swe_ids=[], fields={"coding_standards": "s"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "implementation-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_implementation_record(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"coding_standards": "s"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "implementation-record.md"
    write_matrix(matrix_path, sample_rows())

    record_implementation_record(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-060", "SWE-061"],
        fields={
            "implementation": "Design realized in src/, traced via traceability matrix.",
            "coding_standards": "PEP 8 plus project style guide docs/standards/python-style.md; enforced via ruff in CI.",
        },
        evidence="docs/standards/python-style.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "PEP 8" in content
    assert "SWE-060" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "implementation-record.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Implementation (NPR 7150.2D §4.4)\n\n")

    record_implementation_record(str(matrix_path), str(record_path), swe_ids=["SWE-060"], fields={"coding_standards": "a"}, evidence="e1")
    record_implementation_record(str(matrix_path), str(record_path), swe_ids=["SWE-061"], fields={"coding_standards": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "implementation-record.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_implementation_record(str(matrix_path), str(record_path), swe_ids=["SWE-060"], fields={"coding_standards": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-060")["status"] == "tailored-out"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/skills/implementation-record/scripts
python3 -m pytest test_record_implementation_record.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'record_implementation_record'`

- [ ] **Step 3: Implement `record_implementation_record.py`**

```python
# skills/implementation-record/scripts/record_implementation_record.py
import datetime
import yaml

DEFAULT_HEADER = "# Software Implementation (NPR 7150.2D §4.4)\n\n"


def record_implementation_record(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
    if not swe_ids:
        raise ValueError("at least one swe_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["swe_id"]: r for r in rows}
    missing = [s for s in swe_ids if s not in row_by_id]
    if missing:
        raise KeyError(f"unknown swe_id(s) in requirements mapping matrix: {', '.join(missing)}")

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
python3 -m pytest test_record_implementation_record.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/implementation-record/scripts/record_implementation_record.py skills/implementation-record/scripts/test_record_implementation_record.py
git commit -m "feat: add implementation-record record logic"
```

---

### Task 9: `implementation-record` skill

**Files:**
- Create: `skills/implementation-record/SKILL.md`

**Interfaces:**
- Consumes: `record_implementation_record` from Task 8.
- Produces: `docs/nasa-compliance/<subsystem>/implementation-record.md` and updates to `.../requirements-mapping-matrix.yaml`.

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: implementation-record
description: Use to record a subsystem's NPR 7150.2D §4.4 software implementation evidence — coding standards, static analysis, unit testing, version description, and tool validation
---

# Software Implementation (NPR 7150.2D §4.4)

## Overview

Records the implementation-phase evidence §4.4 requires: the design-to-code realization, coding standards adherence, static analysis coverage, unit testing and its repeatability, version descriptions, and development/maintenance tool validation. Does not write the code itself.

**Announce at start:** "I'm using the implementation-record skill to record your NPR 7150.2D §4.4 software implementation compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

## The interview

1. **Implementation (§4.4.2, SWE-060).** Point to evidence the software design was implemented into code (e.g. the traceability matrix linking design units to source).
2. **Coding standards (§4.4.3, SWE-061).** What coding methods, standards, and criteria were selected, and how is adherence checked?
3. **Static analysis (§4.4.4, SWE-135).** What static analysis tools ran during development/testing? Confirm they cover, at minimum, defects, software security, code coverage, and complexity.
4. **Unit testing (§4.4.5, SWE-062).** Point to evidence the code was unit tested.
5. **Repeatable unit tests (§4.4.6, SWE-186).** How is it assured that unit test results are repeatable (e.g. deterministic test environment, pinned dependencies, CI reruns)?
6. **Version description (§4.4.7, SWE-063).** Point to the software version description for this release.
7. **Tool validation (§4.4.8, SWE-136).** How were the software tool(s) used to develop or maintain the software validated and accredited for that use?

If any answer doesn't exist yet as a real artifact, tell the user and leave that SWE-id out of `swe_ids` below.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/implementation-record/scripts
python3 -c "
from record_implementation_record import record_implementation_record

record_implementation_record(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's implementation-record.md>',
    swe_ids=[<SWE-ids answered above with a real artifact, e.g. 'SWE-060', 'SWE-061', 'SWE-135', 'SWE-062', 'SWE-186', 'SWE-063', 'SWE-136'>],
    fields={
        'implementation': '<answer to question 1>',
        'coding_standards': '<answer to question 2>',
        'static_analysis': '<answer to question 3>',
        'unit_testing': '<answer to question 4>',
        'repeatable_unit_tests': '<answer to question 5>',
        'version_description': '<answer to question 6>',
        'tool_validation': '<answer to question 7>',
    },
    evidence='<the single most authoritative pointer among the answers above>',
)
print('Recorded.')
"
```

Only include SWE-ids for questions with a real answer.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/implementation-record/SKILL.md
git commit -m "feat: add implementation-record skill"
```

---

### Task 10: `test-record` record script (TDD)

**Files:**
- Create: `skills/test-record/scripts/record_test_record.py`
- Test: `skills/test-record/scripts/test_record_test_record.py`

**Interfaces:**
- Consumes/Produces: same shape as Task 2, renamed `record_test_record(matrix_yaml_path, record_md_path, swe_ids, fields, evidence) -> None`. Same shape regardless of §4.5 having 13 rows — no special-casing (per spec).

- [ ] **Step 1: Write the failing tests**

```python
# skills/test-record/scripts/test_record_test_record.py
import yaml
import pytest
from record_test_record import record_test_record


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-065", "section": "4.5.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-066", "section": "4.5.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "test-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_test_record(str(matrix_path), str(record_path), swe_ids=[], fields={"test_artifacts": "t"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "test-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_test_record(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"test_artifacts": "t"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "test-record.md"
    write_matrix(matrix_path, sample_rows())

    record_test_record(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-065", "SWE-066"],
        fields={
            "test_artifacts": "docs/test/software-test-plan.md, test procedures under tests/procedures/, reports under docs/test/reports/.",
            "requirements_testing": "100% of baselined requirements traced to at least one test case, see traceability.md.",
        },
        evidence="docs/test/software-test-plan.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "software-test-plan.md" in content
    assert "SWE-065" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "test-record.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Testing (NPR 7150.2D §4.5)\n\n")

    record_test_record(str(matrix_path), str(record_path), swe_ids=["SWE-065"], fields={"test_artifacts": "a"}, evidence="e1")
    record_test_record(str(matrix_path), str(record_path), swe_ids=["SWE-066"], fields={"test_artifacts": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "test-record.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_test_record(str(matrix_path), str(record_path), swe_ids=["SWE-065"], fields={"test_artifacts": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-065")["status"] == "tailored-out"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/skills/test-record/scripts
python3 -m pytest test_record_test_record.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'record_test_record'`

- [ ] **Step 3: Implement `record_test_record.py`**

```python
# skills/test-record/scripts/record_test_record.py
import datetime
import yaml

DEFAULT_HEADER = "# Software Testing (NPR 7150.2D §4.5)\n\n"


def record_test_record(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
    if not swe_ids:
        raise ValueError("at least one swe_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["swe_id"]: r for r in rows}
    missing = [s for s in swe_ids if s not in row_by_id]
    if missing:
        raise KeyError(f"unknown swe_id(s) in requirements mapping matrix: {', '.join(missing)}")

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
python3 -m pytest test_record_test_record.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/test-record/scripts/record_test_record.py skills/test-record/scripts/test_record_test_record.py
git commit -m "feat: add test-record record logic"
```

---

### Task 11: `test-record` skill

**Files:**
- Create: `skills/test-record/SKILL.md`

**Interfaces:**
- Consumes: `record_test_record` from Task 10.
- Produces: `docs/nasa-compliance/<subsystem>/test-record.md` and updates to `.../requirements-mapping-matrix.yaml`.

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: test-record
description: Use to record a subsystem's NPR 7150.2D §4.5 software testing evidence — test artifacts, requirements-based testing, coverage, regression, and reused-component testing
---

# Software Testing (NPR 7150.2D §4.5)

## Overview

Records the testing-phase evidence §4.5 requires across its 13 rows: test plans/procedures/reports, requirements-based testing, configuration management before test, evaluation, qualification tooling, platform validation, code coverage, regression testing, hazard-traced tests, loaded/uplinked-data acceptance tests, and reused-component testing. Does not run the tests itself — this is a real, larger interview than SP2's skills, but the same straight per-row walk applies; there is no special-casing for its row count.

**Announce at start:** "I'm using the test-record skill to record your NPR 7150.2D §4.5 software testing compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

## The interview

1. **Test artifacts (§4.5.2, SWE-065).** Point to the software test plan(s), test procedure(s), test(s) — including any code written specifically to perform test procedures — and test report(s).
2. **Requirements testing (§4.5.3, SWE-066).** Point to evidence the software was tested against its requirements.
3. **Configuration management before test (§4.5.4, SWE-187).** Were software items placed under configuration management prior to testing?
4. **Test evaluation (§4.5.5, SWE-068).** Point to the recorded evaluation of test results.
5. **Qualification tooling (§4.5.6, SWE-070).** If this subsystem involves flight software or flight equipment qualification, were validated and accredited models, simulations, and analysis tools used? If not applicable, record that explicitly.
6. **Plan/procedure currency (§4.5.7, SWE-071).** Were the test and verification plan(s)/procedure(s) updated to stay consistent with the current software requirements?
7. **Platform validation (§4.5.8, SWE-073).** Point to evidence the software system was validated on the targeted platform or a high-fidelity simulation.
8. **Code coverage program (§4.5.9, SWE-189).** How are code coverage measurements selected, implemented, tracked, recorded, and reported?
9. **Code coverage verification (§4.5.10, SWE-190).** How is code coverage verified by analysis of the results of test execution?
10. **Regression testing (§4.5.11, SWE-191).** Point to the regression testing plan/results demonstrating that defects have not been introduced into previously integrated/tested software and no security vulnerability was produced.
11. **Hazard-traced tests (§4.5.12, SWE-192).** Point to test evidence for any software requirements that trace to a hazardous event, cause, or mitigation technique. If none trace to a hazard, record that explicitly.
12. **Loaded/uplinked-data acceptance tests (§4.5.13, SWE-193).** If the software accepts loaded or uplinked data, rules, or code that affects software/system behavior, point to the acceptance tests developed for it. If not applicable, record that explicitly.
13. **Reused-component testing (§4.5.14, SWE-211).** If embedded COTS/GOTS/MOTS/OSS/reused components exist, were they tested to the same level required to accept a custom-developed component for its intended use? If there are none, record that explicitly.

If any answer doesn't exist yet as a real artifact, tell the user and leave that SWE-id out of `swe_ids` below. Where a row genuinely doesn't apply (e.g. no reused components, no hazard-traced requirements), still record the explicit non-applicability determination rather than leaving the row silently `not-started`.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/test-record/scripts
python3 -c "
from record_test_record import record_test_record

record_test_record(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's test-record.md>',
    swe_ids=[<SWE-ids answered above, e.g. 'SWE-065', 'SWE-066', 'SWE-187', 'SWE-068', 'SWE-070', 'SWE-071', 'SWE-073', 'SWE-189', 'SWE-190', 'SWE-191', 'SWE-192', 'SWE-193', 'SWE-211'>],
    fields={
        'test_artifacts': '<answer to question 1>',
        'requirements_testing': '<answer to question 2>',
        'configuration_management_before_test': '<answer to question 3>',
        'test_evaluation': '<answer to question 4>',
        'qualification_tooling': '<answer to question 5>',
        'plan_procedure_currency': '<answer to question 6>',
        'platform_validation': '<answer to question 7>',
        'code_coverage_program': '<answer to question 8>',
        'code_coverage_verification': '<answer to question 9>',
        'regression_testing': '<answer to question 10>',
        'hazard_traced_tests': '<answer to question 11>',
        'loaded_uplinked_data_tests': '<answer to question 12>',
        'reused_component_testing': '<answer to question 13>',
    },
    evidence='<the single most authoritative pointer among the answers above, e.g. the test plan path>',
)
print('Recorded.')
"
```

Only include SWE-ids for questions with a real answer (including an explicit non-applicability determination).

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/test-record/SKILL.md
git commit -m "feat: add test-record skill"
```

---

### Task 12: `operations-retirement` record script (TDD)

**Files:**
- Create: `skills/operations-retirement/scripts/record_operations_retirement.py`
- Test: `skills/operations-retirement/scripts/test_record_operations_retirement.py`

**Interfaces:**
- Consumes/Produces: same shape as Task 2, renamed `record_operations_retirement(matrix_yaml_path, record_md_path, swe_ids, fields, evidence) -> None`.

- [ ] **Step 1: Write the failing tests**

```python
# skills/operations-retirement/scripts/test_record_operations_retirement.py
import yaml
import pytest
from record_operations_retirement import record_operations_retirement


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-075", "section": "4.6.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-077", "section": "4.6.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "operations-retirement.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_operations_retirement(str(matrix_path), str(record_path), swe_ids=[], fields={"ops_plan": "p"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "operations-retirement.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_operations_retirement(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"ops_plan": "p"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "operations-retirement.md"
    write_matrix(matrix_path, sample_rows())

    record_operations_retirement(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-075", "SWE-077"],
        fields={
            "ops_maintenance_retirement_plan": "docs/ops/operations-maintenance-plan.md",
            "delivery_records": "As-built records delivered with v1.0, see docs/ops/as-built-v1.0.md.",
        },
        evidence="docs/ops/operations-maintenance-plan.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "as-built-v1.0.md" in content
    assert "SWE-075" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "operations-retirement.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Operations, Maintenance, and Retirement (NPR 7150.2D §4.6)\n\n")

    record_operations_retirement(str(matrix_path), str(record_path), swe_ids=["SWE-075"], fields={"ops_plan": "a"}, evidence="e1")
    record_operations_retirement(str(matrix_path), str(record_path), swe_ids=["SWE-077"], fields={"ops_plan": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "operations-retirement.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_operations_retirement(str(matrix_path), str(record_path), swe_ids=["SWE-075"], fields={"ops_plan": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-075")["status"] == "tailored-out"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/skills/operations-retirement/scripts
python3 -m pytest test_record_operations_retirement.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'record_operations_retirement'`

- [ ] **Step 3: Implement `record_operations_retirement.py`**

```python
# skills/operations-retirement/scripts/record_operations_retirement.py
import datetime
import yaml

DEFAULT_HEADER = "# Software Operations, Maintenance, and Retirement (NPR 7150.2D §4.6)\n\n"


def record_operations_retirement(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
    if not swe_ids:
        raise ValueError("at least one swe_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["swe_id"]: r for r in rows}
    missing = [s for s in swe_ids if s not in row_by_id]
    if missing:
        raise KeyError(f"unknown swe_id(s) in requirements mapping matrix: {', '.join(missing)}")

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
python3 -m pytest test_record_operations_retirement.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/operations-retirement/scripts/record_operations_retirement.py skills/operations-retirement/scripts/test_record_operations_retirement.py
git commit -m "feat: add operations-retirement record logic"
```

---

### Task 13: `operations-retirement` skill

**Files:**
- Create: `skills/operations-retirement/SKILL.md`

**Interfaces:**
- Consumes: `record_operations_retirement` from Task 12.
- Produces: `docs/nasa-compliance/<subsystem>/operations-retirement.md` and updates to `.../requirements-mapping-matrix.yaml`.

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: operations-retirement
description: Use to record a subsystem's NPR 7150.2D §4.6 software operations, maintenance, and retirement planning and evidence
---

# Software Operations, Maintenance, and Retirement (NPR 7150.2D §4.6)

## Overview

Records the operations, maintenance, and retirement planning and evidence §4.6 requires: the ops/maintenance/retirement plan, delivery records, pre-delivery verification, maintenance standards, and archival planning. Does not perform operations or maintenance itself.

**Announce at start:** "I'm using the operations-retirement skill to record your NPR 7150.2D §4.6 software operations, maintenance, and retirement compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

## The interview

1. **Ops/maintenance/retirement plan (§4.6.2, SWE-075).** Point to the plan for software operations, maintenance, and retirement activities.
2. **Delivery records (§4.6.3, SWE-077).** Point to the as-built and other appropriate records delivered with the software product to support its operations and maintenance phase.
3. **Pre-delivery verification (§4.6.4, SWE-194).** Confirm, for this delivery: all identified software requirements have been met or dispositioned, all approved changes have been implemented, and all defects designated for pre-delivery resolution have been resolved. Point to the record of that verification.
4. **Maintenance standards (§4.6.5, SWE-195).** What standards and processes — per the subsystem's applicable software classification — govern maintenance throughout the maintenance phase?
5. **Archival planning (§4.6.6, SWE-196).** Point to the identified records and software tools to be archived, the archive's location, and the procedures for accessing the products for retirement or disposal.

If any answer doesn't exist yet as a real artifact, tell the user and leave that SWE-id out of `swe_ids` below.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/operations-retirement/scripts
python3 -c "
from record_operations_retirement import record_operations_retirement

record_operations_retirement(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's operations-retirement.md>',
    swe_ids=[<SWE-ids answered above with a real artifact, e.g. 'SWE-075', 'SWE-077', 'SWE-194', 'SWE-195', 'SWE-196'>],
    fields={
        'ops_maintenance_retirement_plan': '<answer to question 1>',
        'delivery_records': '<answer to question 2>',
        'pre_delivery_verification': '<answer to question 3>',
        'maintenance_standards': '<answer to question 4>',
        'archival_planning': '<answer to question 5>',
    },
    evidence='<the single most authoritative pointer among the answers above>',
)
print('Recorded.')
"
```

Only include SWE-ids for questions with a real answer.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/operations-retirement/SKILL.md
git commit -m "feat: add operations-retirement skill"
```

---

## Final Review

Once all 13 tasks are complete, dispatch a whole-branch review per `superpowers:requesting-code-review`. Point that reviewer at **both**:

- `docs/superpowers/specs/2026-08-10-sp3-engineering-lifecycle-design.md` (the spec)
- this plan

not just this plan — SP2's `reuse-assessment` targeted the wrong requirement because its plan drifted from its spec and no task-scoped review caught it. Confirm specifically that:

- All 34 §4.1-4.6 SWE-ids are covered by exactly one of the six skills, matching the spec's mapping table.
- No skill performs the underlying engineering work it records evidence for.
- No hook, gate, or edit to a generic Superpowers skill was introduced (enforcement was explicitly deferred).
