# NASA-SWE Foundation (SP1) Implementation Plan

> **Status: executed, and partly superseded.** This plan is kept as the build
> record. Two things in it are no longer current and should not be copied:
>
> - **The catalog schema** in Global Constraints and Tasks 3, 6, and 7
>   (`responsible_role` / `technical_authority` / `ta_required`) was wrong. Those
>   last two fields were Appendix C's *Class F Authority* and *Class F
>   applicability* columns read out of alignment, which forced `classes.F` false
>   on every row. The live schema is `section`, `swe_id`, `class_ae_authority`,
>   `classes`, `class_f_authority` — see `skills/requirements-matrix/SKILL.md`.
> - **Task 6's transcription method** ("read the pages carefully and slowly")
>   is what produced that error. Extract Appendix C with `pdftotext
>   -bbox-layout` and assign cells to columns by x-coordinate instead; see
>   `data/CATALOG-COVERAGE.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fork obra/superpowers and build the foundation layer — software classification (NPR 7150.2D Appendix D), a Requirements Mapping Matrix (Appendix C), and a tailoring/relief workflow — as three testable Claude Code skills backed by deterministic Python scripts.

**Architecture:** Each skill is a thin `SKILL.md` prompt that orchestrates an interview/interaction, then delegates all actual decision logic (classification, catalog filtering, tailoring validation) to a pure, unit-tested Python script under that skill's `scripts/` directory. Compliance state lives in per-subsystem YAML/Markdown files under `docs/nasa-compliance/<subsystem>/`.

**Tech Stack:** Python 3.14, PyYAML 6.0, pytest 9.0 (all confirmed present; pinned in `scripts/requirements.txt` for reproducibility). `gh` CLI for the fork.

## Global Constraints

- Fork target: `/home/adam/scratch-claude/superpowers-nasa-swe`
- Plugin identity after fork: `.claude-plugin/plugin.json` `name` field → `"superpowers-nasa-swe"`
- No verbatim NPR 7150.2D requirement text is ever stored in the catalog or emitted files — every requirement is cited as `NPR 7150.2D §<section>, SWE-<id>` only
- Catalog schema (one row per SWE requirement): `section` (str, e.g. `"4.1.5"`), `swe_id` (str, format `SWE-\d+`), `responsible_role` (str), `classes` (dict with exactly keys `A,B,C,D,E,F` → bool), `technical_authority` (str or `null`), `ta_required` (bool)
- Output paths: `docs/nasa-compliance/<subsystem>/classification.yaml`, `.../requirements-mapping-matrix.md`, `.../requirements-mapping-matrix.yaml`, `.../tailoring-log.md`
- Ambiguous classification (more than one class's criteria match) → surfaced to the user, never silently auto-resolved
- Reference to an unknown/missing SWE-id → hard error, never silently skipped
- A tailoring entry without a named approving authority → blocked, cannot be written

---

### Task 1: Fork the repo and rename plugin identity

**Files:**
- Create (via `gh`): `/home/adam/scratch-claude/superpowers-nasa-swe/` (full clone of the fork)
- Modify: `/home/adam/scratch-claude/superpowers-nasa-swe/.claude-plugin/plugin.json`

**Interfaces:**
- Produces: a working local clone at the path above, with `plugin.json`'s `"name"` field equal to `"superpowers-nasa-swe"`. All later tasks create files inside this directory.

- [ ] **Step 1: Fork and clone**

```bash
cd /home/adam/scratch-claude
gh repo fork obra/superpowers --clone=true --remote=true --fork-name superpowers-nasa-swe
mv superpowers-nasa-swe /home/adam/scratch-claude/superpowers-nasa-swe 2>/dev/null || true
ls /home/adam/scratch-claude/superpowers-nasa-swe/.claude-plugin/plugin.json
```

Expected: the file `plugin.json` exists at that path. (If `gh repo fork --fork-name` clones into a differently-named directory, `mv` it to `superpowers-nasa-swe` — `gh` names the local clone dir after `--fork-name` in current versions, so the `mv` is a no-op safety net.)

- [ ] **Step 2: Rename plugin identity**

Edit `/home/adam/scratch-claude/superpowers-nasa-swe/.claude-plugin/plugin.json`, changing only the `name` field:

```json
{
  "name": "superpowers-nasa-swe",
  "description": "NASA NPR 7150.2D / NASA-STD-8739.8B software engineering compliance layer, forked from Superpowers",
  "version": "0.1.0",
  "author": {
    "name": "Jesse Vincent",
    "email": "jesse@fsck.com"
  },
  "homepage": "https://github.com/obra/superpowers",
  "repository": "https://github.com/obra/superpowers",
  "license": "MIT",
  "keywords": [
    "skills",
    "nasa",
    "npr-7150.2",
    "nasa-std-8739.8",
    "software-assurance",
    "compliance"
  ]
}
```

- [ ] **Step 3: Verify and commit**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe
git log --oneline -1
git diff .claude-plugin/plugin.json
git add .claude-plugin/plugin.json
git commit -m "chore: rename plugin identity to superpowers-nasa-swe"
```

Expected: commit succeeds, `git diff` before committing showed only the `name`/`description`/`version`/`keywords` fields changed.

---

### Task 2: Save reference copies of the source standards

**Files:**
- Create: `reference/NPR_7150.2D.pdf`
- Create: `reference/NASA-STD-8739.8B.pdf`
- Create: `reference/README.md`

**Interfaces:**
- Produces: stable, repo-local copies of both source PDFs so later tasks (and future contributors, in fresh sessions) don't depend on ephemeral fetch caches.

- [ ] **Step 1: Download both PDFs**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe
mkdir -p reference
curl -sL -o reference/NPR_7150.2D.pdf "https://nodis3.gsfc.nasa.gov/npg_img/N_PR_7150_002D_/N_PR_7150_002D_.pdf"
curl -sL -o reference/NASA-STD-8739.8B.pdf "https://standards.nasa.gov/sites/default/files/standards/NASA/B/0/NASA-STD-87398-Revision-B.pdf"
ls -la reference/
```

Expected: both files present, each larger than 400KB (NPR ≈553KB, STD ≈676KB per earlier fetch).

- [ ] **Step 2: Write reference/README.md**

```markdown
# Reference Standards

- `NPR_7150.2D.pdf` — NASA Software Engineering Requirements (effective 2022-03-08, expires 2027-03-08). Source: https://nodis3.gsfc.nasa.gov/npg_img/N_PR_7150_002D_/N_PR_7150_002D_.pdf
- `NASA-STD-8739.8B.pdf` — Software Assurance and Software Safety Standard (approved 2022-09-08). Source: https://standards.nasa.gov/sites/default/files/standards/NASA/B/0/NASA-STD-87398-Revision-B.pdf

These are the authoritative source documents. `data/swe-catalog.yaml` cites requirements by section/SWE-id against NPR 7150.2D — it does not reproduce requirement text. Before relying on any cited SWE-id, verify against these PDFs; NASA revises these standards periodically and this fork tracks the versions above only.
```

- [ ] **Step 3: Commit**

```bash
git add reference/
git commit -m "docs: add reference copies of NPR 7150.2D and NASA-STD-8739.8B"
```

---

### Task 3: Catalog schema and validation script (TDD)

**Files:**
- Create: `scripts/requirements.txt`
- Create: `skills/requirements-matrix/scripts/validate_catalog.py`
- Test: `skills/requirements-matrix/scripts/test_validate_catalog.py`

**Interfaces:**
- Produces: `validate_catalog(rows: list[dict]) -> list[str]` — returns a list of human-readable error strings; empty list means valid. Every later task that writes or reads `data/swe-catalog.yaml` calls this first.

- [ ] **Step 1: Pin dependencies**

```
# scripts/requirements.txt
PyYAML==6.0.2
pytest==9.0.2
```

- [ ] **Step 2: Write the failing tests**

```python
# skills/requirements-matrix/scripts/test_validate_catalog.py
from validate_catalog import validate_catalog

def valid_row(**overrides):
    row = {
        "section": "4.1.5",
        "swe_id": "SWE-053",
        "responsible_role": "Center",
        "classes": {"A": True, "B": True, "C": True, "D": True, "E": False, "F": False},
        "technical_authority": "CIO",
        "ta_required": True,
    }
    row.update(overrides)
    return row

def test_valid_catalog_has_no_errors():
    assert validate_catalog([valid_row()]) == []

def test_missing_required_field_is_reported():
    row = valid_row()
    del row["swe_id"]
    errors = validate_catalog([row])
    assert any("swe_id" in e for e in errors)

def test_bad_swe_id_format_is_reported():
    errors = validate_catalog([valid_row(swe_id="053")])
    assert any("SWE-" in e and "format" in e for e in errors)

def test_classes_must_have_exactly_six_keys():
    row = valid_row(classes={"A": True, "B": True})
    errors = validate_catalog([row])
    assert any("classes" in e for e in errors)

def test_classes_values_must_be_bool():
    row = valid_row(classes={"A": "yes", "B": True, "C": True, "D": True, "E": False, "F": False})
    errors = validate_catalog([row])
    assert any("classes" in e for e in errors)

def test_duplicate_swe_id_is_reported():
    errors = validate_catalog([valid_row(), valid_row(section="4.1.6")])
    assert any("duplicate" in e.lower() for e in errors)

def test_technical_authority_may_be_none():
    row = valid_row(technical_authority=None, ta_required=False)
    assert validate_catalog([row]) == []
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe
pip install -r scripts/requirements.txt --quiet
cd skills/requirements-matrix/scripts
python3 -m pytest test_validate_catalog.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'validate_catalog'`

- [ ] **Step 4: Implement validate_catalog.py**

```python
# skills/requirements-matrix/scripts/validate_catalog.py
import re

REQUIRED_FIELDS = {"section", "swe_id", "responsible_role", "classes", "technical_authority", "ta_required"}
CLASS_KEYS = {"A", "B", "C", "D", "E", "F"}
SWE_ID_RE = re.compile(r"^SWE-\d+$")


def validate_catalog(rows):
    errors = []
    seen_ids = set()

    for i, row in enumerate(rows):
        missing = REQUIRED_FIELDS - row.keys()
        for field in missing:
            errors.append(f"row {i}: missing required field '{field}'")
        if missing:
            continue

        if not SWE_ID_RE.match(row["swe_id"]):
            errors.append(f"row {i}: swe_id '{row['swe_id']}' does not match required format 'SWE-<digits>'")
        elif row["swe_id"] in seen_ids:
            errors.append(f"row {i}: duplicate swe_id '{row['swe_id']}'")
        else:
            seen_ids.add(row["swe_id"])

        classes = row["classes"]
        if not isinstance(classes, dict) or set(classes.keys()) != CLASS_KEYS:
            errors.append(f"row {i}: classes must have exactly keys {sorted(CLASS_KEYS)}")
        elif not all(isinstance(v, bool) for v in classes.values()):
            errors.append(f"row {i}: classes values must all be bool")

        if row["technical_authority"] is not None and not isinstance(row["technical_authority"], str):
            errors.append(f"row {i}: technical_authority must be a string or null")

        if not isinstance(row["ta_required"], bool):
            errors.append(f"row {i}: ta_required must be a bool")

    return errors
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python3 -m pytest test_validate_catalog.py -v
```

Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe
git add scripts/requirements.txt skills/requirements-matrix/scripts/validate_catalog.py skills/requirements-matrix/scripts/test_validate_catalog.py
git commit -m "feat: add SWE catalog schema validation"
```

---

### Task 4: Classification decision script (TDD)

**Files:**
- Create: `skills/classify-software/scripts/classify.py`
- Test: `skills/classify-software/scripts/test_classify.py`

**Interfaces:**
- Consumes: nothing from earlier tasks (pure function, standalone).
- Produces: `classify(answers: dict) -> dict` returning `{"class": str, "ambiguous": bool, "candidates": list[str]}`. The `classify-software` SKILL.md (Task 5) is the only consumer.

Per NPR 7150.2D Appendix D: classes are evaluated in stringency order A→F; if more than one of A-E's criteria match, the higher (earlier) class wins (D.2, "assign the higher of the classes"); Class E explicitly cannot be safety-critical — if the software is safety-critical and would otherwise land in E, it must be bumped to D (Appendix D, Class E definition item 3); software matching none of A-E is Class F.

- [ ] **Step 1: Write the failing tests**

```python
# skills/classify-software/scripts/test_classify.py
from classify import classify

def base_answers(**overrides):
    answers = {
        "class_a_human_rated": False,
        "class_b_non_human_space_or_large_aero": False,
        "class_c_mission_support_or_facility": False,
        "class_d_basic_science_or_research": False,
        "class_e_design_concept_general_purpose": False,
        "is_safety_critical": False,
    }
    answers.update(overrides)
    return answers

def test_class_a_human_rated_wins():
    result = classify(base_answers(class_a_human_rated=True))
    assert result["class"] == "A"
    assert result["ambiguous"] is False

def test_class_b_non_human_space():
    result = classify(base_answers(class_b_non_human_space_or_large_aero=True))
    assert result["class"] == "B"

def test_class_c_mission_support():
    result = classify(base_answers(class_c_mission_support_or_facility=True))
    assert result["class"] == "C"

def test_class_d_basic_science():
    result = classify(base_answers(class_d_basic_science_or_research=True))
    assert result["class"] == "D"

def test_class_e_design_concept():
    result = classify(base_answers(class_e_design_concept_general_purpose=True))
    assert result["class"] == "E"

def test_no_criteria_match_falls_back_to_class_f():
    result = classify(base_answers())
    assert result["class"] == "F"
    assert result["ambiguous"] is False

def test_safety_critical_bumps_class_e_to_class_d():
    result = classify(base_answers(class_e_design_concept_general_purpose=True, is_safety_critical=True))
    assert result["class"] == "D"

def test_safety_critical_does_not_affect_class_a_through_d():
    result = classify(base_answers(class_c_mission_support_or_facility=True, is_safety_critical=True))
    assert result["class"] == "C"

def test_multiple_matching_classes_are_flagged_ambiguous_and_higher_wins():
    result = classify(base_answers(class_b_non_human_space_or_large_aero=True, class_d_basic_science_or_research=True))
    assert result["class"] == "B"
    assert result["ambiguous"] is True
    assert result["candidates"] == ["B", "D"]

def test_no_match_has_empty_candidates():
    result = classify(base_answers())
    assert result["candidates"] == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe/skills/classify-software/scripts
python3 -m pytest test_classify.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'classify'`

- [ ] **Step 3: Implement classify.py**

```python
# skills/classify-software/scripts/classify.py

CLASS_ORDER = ["A", "B", "C", "D", "E"]
ANSWER_KEY_FOR_CLASS = {
    "A": "class_a_human_rated",
    "B": "class_b_non_human_space_or_large_aero",
    "C": "class_c_mission_support_or_facility",
    "D": "class_d_basic_science_or_research",
    "E": "class_e_design_concept_general_purpose",
}


def classify(answers):
    candidates = [c for c in CLASS_ORDER if answers.get(ANSWER_KEY_FOR_CLASS[c], False)]

    if not candidates:
        return {"class": "F", "ambiguous": False, "candidates": []}

    chosen = candidates[0]

    # Appendix D, Class E definition item 3: Class E cannot be safety-critical.
    if chosen == "E" and answers.get("is_safety_critical", False):
        chosen = "D"

    return {
        "class": chosen,
        "ambiguous": len(candidates) > 1,
        "candidates": candidates,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest test_classify.py -v
```

Expected: 10 passed

- [ ] **Step 5: Commit**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe
git add skills/classify-software/scripts/classify.py skills/classify-software/scripts/test_classify.py
git commit -m "feat: add software classification decision logic"
```

---

### Task 5: `classify-software` skill

**Files:**
- Create: `skills/classify-software/SKILL.md`

**Interfaces:**
- Consumes: `classify(answers: dict) -> dict` from Task 4.
- Produces: `docs/nasa-compliance/<subsystem>/classification.yaml` in the *consuming project* (not this repo) with keys `subsystem`, `class`, `ambiguous`, `candidates`, `answers`, `rationale`, `date`.

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: classify-software
description: Use when starting a new project or subsystem that needs a NASA-wide software classification (NPR 7150.2D Appendix D, Class A-F) before other NASA-SWE compliance skills can run
---

# Classify Software (NPR 7150.2D Appendix D)

## Overview

Determines which NASA software class (A-F) applies to a project or named subsystem, using NPR 7150.2D Appendix D's actual class definitions. This must run before `requirements-matrix`, since the matrix is filtered by class.

**Announce at start:** "I'm using the classify-software skill to determine your NASA software class per NPR 7150.2D Appendix D."

## Multiple subsystems

Ask first: is this a single system, or does the project contain subsystems that might warrant different classes (NPR 7150.2D Appendix D.1 explicitly anticipates this)? If subsystems exist, run this interview once per named subsystem, producing one `classification.yaml` per subsystem.

## The interview

Ask about each class in order, using the *exact* criteria below (from Appendix D). Stop at the first "yes" — but keep asking through Class E even after an earlier "yes", so the tool can detect and flag ambiguity (more than one class's criteria matching is a real signal, not noise).

1. **Class A — Human Rated Space Software Systems.** Does the software: operate a vehicle/space asset including commanding it, OR sustain a safe habitable environment for crew, OR directly achieve primary human-spaceflight mission objectives, OR directly prepare resources (data/fuel/power) consumed by those functions? Exclude software that's merely incidental to the mission (e.g., personal media on a crew device), aeronautics-only R&T software with no space-flight application, and simulator/test-environment software.

2. **Class B — Non-Human Space Rated Systems or Large-Scale Aeronautics.** For non-human space missions: does the software operate the vehicle/asset (commanding), achieve primary mission objectives, or directly prepare consumed resources? OR, for large-scale (>$250M lifecycle cost per NPR 7120.8) NASA-unique aeronautic vehicles: is the software integral to airborne vehicle control, or does it monitor/control the cabin environment or the vehicle's emergency systems? Exclude software solely supporting non-primary instruments, and simulator/test-environment software.

3. **Class C — Mission Support Software, Aeronautic Vehicles, or Major Engineering/Research Facility Software.** Any of: software for a single non-primary instrument's science return; software analyzing/processing mission data; software whose defect could affect secondary mission objectives or cause operational problems; software testing space assets or verifying system requirements by analysis; space flight ops software not covered by A/B; non-large-scale aeronautic vehicle software integral to control/cabin/emergency systems, or that records the official flight/test data; major engineering/research facility control, monitoring, or data-acquisition software; sounding rocket/payload software; NASA Class D payload software (NPR 8705.4).

4. **Class D — Basic Science/Engineering Design and Research and Technology Software.** Any of: secondary science data analysis tools; engineering development tools; informal software testing tools; mission planning/formulation tools; decision support for non-mission-critical situations; research/development/test/evaluation lab software (not a major facility); airborne-vehicle software with only a minor or no-effect failure condition (DO-178C Class D/E equivalent); research software independent of a major facility's operation.

5. **Class E — Design Concept, Research, Technology, and General Purpose Software.** Software exploring a design concept/hypothesis not used to make decisions for an operational A/B/C system; minor analyses of science/experimental data; a defect would affect at most a single user or small group, not mission objectives or system safety; runs in a general-purpose computing or board-top environment, not used for ground/flight tests or operations.

6. **Safety-critical check (always ask, regardless of the above).** Per NASA-STD-8739.8B §4.2.1, is the software determined by and traceable to a hazard analysis to: cause/contribute to a system hazardous condition, control functions identified in a system hazard, mitigate a hazardous condition, mitigate damage if a hazard occurs, or detect/report/correct a hazardous state? If yes, `is_safety_critical: true` — this can never leave the result at Class E; Class E software cannot be safety-critical.

If none of Classes A-E apply, the software is **Class F** — general-purpose computing, business, and IT software.

## Running the script

Translate your interview answers into the exact keys `classify.py` expects, then run it:

```bash
cd <this-plugin's-install-path>/skills/classify-software/scripts
python3 -c "
from classify import classify
import json
result = classify({
    'class_a_human_rated': False,
    'class_b_non_human_space_or_large_aero': False,
    'class_c_mission_support_or_facility': False,
    'class_d_basic_science_or_research': False,
    'class_e_design_concept_general_purpose': True,
    'is_safety_critical': False,
})
print(json.dumps(result, indent=2))
"
```

If `result[\"ambiguous\"]` is `true`, **do not silently accept the first candidate** — tell the user which classes matched (`result["candidates"]`) and ask them to confirm or override, per NPR 7150.2D Appendix D.2.

## Writing the output

Write `docs/nasa-compliance/<subsystem>/classification.yaml` in the *project being classified* (create the directory if needed):

```yaml
subsystem: <name, or "default" for a single-system project>
class: <A-F from the script result>
ambiguous: <bool from the script result>
candidates: <list from the script result>
answers: <the exact answers dict passed to classify()>
rationale: <one paragraph, in your own words, explaining why this class fits, citing the specific Appendix D criteria that matched>
date: <today's date, YYYY-MM-DD>
```
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe
git add skills/classify-software/SKILL.md
git commit -m "feat: add classify-software skill"
```

---

### Task 6: Populate the initial catalog slice (NPR pages 70-78)

**Files:**
- Create: `data/swe-catalog.yaml`
- Create: `data/CATALOG-COVERAGE.md`

**Interfaces:**
- Consumes: `validate_catalog()` from Task 3 to check the output.
- Produces: `data/swe-catalog.yaml` — a `list` of rows matching the Task 3 schema, readable by Task 7's `filter_matrix.py`.

This task deliberately covers only NPR 7150.2D Appendix C's rows for sections 4.2 (Software Architecture) through 5.5 (Non-conformance/Defect Management) — pages 70-78 of `reference/NPR_7150.2D.pdf`. Earlier Appendix C pages (Chapter 3, Software Management, and the start of 4.1) are out of scope for this task; `CATALOG-COVERAGE.md` tracks that explicitly so the gap is visible, not hidden.

- [ ] **Step 1: Dispatch a transcription pass**

Using a fresh read of `reference/NPR_7150.2D.pdf` pages 70-78 (Appendix C), transcribe every row into `data/swe-catalog.yaml`. For each row, read the section number, SWE-id, responsible-role column, the six class columns (in A,B,C,D,E,F order) marking `true` wherever an "X" appears and `false` for blank cells, and the trailing TA-role/TA-required columns (`technical_authority: null, ta_required: false` when both are blank). Do not transcribe the requirement description text — only the structured fields.

Read the pages carefully and slowly, one row at a time, double-checking each row's X-marks against the column it appears under before writing it out — transcription errors here become silent compliance-tracking errors downstream.

- [ ] **Step 2: Validate the transcription**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe
python3 -c "
import yaml, sys
sys.path.insert(0, 'skills/requirements-matrix/scripts')
from validate_catalog import validate_catalog

with open('data/swe-catalog.yaml') as f:
    rows = yaml.safe_load(f)

errors = validate_catalog(rows)
if errors:
    for e in errors:
        print('ERROR:', e)
    sys.exit(1)
print(f'{len(rows)} rows valid')
"
```

Expected: `N rows valid` (N should be in the neighborhood of 45-55 rows, matching the section/SWE-id pairs visible on pages 70-78: sections 4.2, 4.3, 4.4, 4.5, 4.6, 5.1, 5.2, 5.3, 5.4, 5.5). Fix any reported error by correcting the corresponding row before proceeding — do not proceed with a failing validation.

- [ ] **Step 3: Write data/CATALOG-COVERAGE.md**

```markdown
# SWE Catalog Coverage

`data/swe-catalog.yaml` currently covers NPR 7150.2D Appendix C, pages 70-78:

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

**Not yet covered** (tracked here, not silently missing):

- Chapter 2 (Roles/Responsibilities) — excluded permanently: NPR 7150.2D §1.3.1 states Chapter 2 requirements are not part of the Requirements Mapping Matrix.
- Chapter 3 (Software Management Requirements, §3.1-3.12) and the start of §4.1 (Software Requirements) — Appendix C pages preceding page 70. Needs a follow-up transcription pass before `requirements-matrix` results are complete for any subsystem that needs Chapter 3 rows.

Extending coverage: re-run the transcription method from Task 6 of `docs/superpowers/plans/2026-08-10-nasa-swe-foundation.md` against the missing page range, append rows to `swe-catalog.yaml`, re-run `validate_catalog`, and update this file.
```

- [ ] **Step 4: Commit**

```bash
git add data/swe-catalog.yaml data/CATALOG-COVERAGE.md
git commit -m "data: populate SWE catalog for NPR Appendix C pages 70-78"
```

---

### Task 7: Matrix filter and render script (TDD)

**Files:**
- Create: `skills/requirements-matrix/scripts/filter_matrix.py`
- Test: `skills/requirements-matrix/scripts/test_filter_matrix.py`

**Interfaces:**
- Consumes: catalog rows matching the Task 3 schema.
- Produces: `filter_rows_for_class(rows: list[dict], software_class: str) -> list[dict]`, `render_matrix_markdown(rows: list[dict], subsystem: str, software_class: str) -> str`, `render_matrix_status_yaml(rows: list[dict]) -> list[dict]` (each entry: `swe_id`, `section`, `status` default `"not-started"`, `evidence` default `null`, `date` default `null`). Task 8's SKILL.md is the consumer.

- [ ] **Step 1: Write the failing tests**

```python
# skills/requirements-matrix/scripts/test_filter_matrix.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe/skills/requirements-matrix/scripts
python3 -m pytest test_filter_matrix.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'filter_matrix'`

- [ ] **Step 3: Implement filter_matrix.py**

```python
# skills/requirements-matrix/scripts/filter_matrix.py

def filter_rows_for_class(rows, software_class):
    return [r for r in rows if r["classes"].get(software_class, False)]


def render_matrix_markdown(rows, subsystem, software_class):
    lines = [
        f"# Requirements Mapping Matrix — {subsystem} (Class {software_class})",
        "",
        "Source: NPR 7150.2D Appendix C. Requirement text is not reproduced here — "
        "each row cites the source standard by section and SWE-id.",
        "",
        "| Section | Citation | Responsible Role | Technical Authority | TA Required |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        citation = f"NPR 7150.2D §{r['section']}, {r['swe_id']}"
        ta = r["technical_authority"] or ""
        ta_required = "Yes" if r["ta_required"] else "No"
        lines.append(f"| {r['section']} | {citation} | {r['responsible_role']} | {ta} | {ta_required} |")
    lines.append("")
    return "\n".join(lines)


def render_matrix_status_yaml(rows):
    return [
        {
            "swe_id": r["swe_id"],
            "section": r["section"],
            "status": "not-started",
            "evidence": None,
            "date": None,
        }
        for r in rows
    ]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest test_filter_matrix.py -v
```

Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe
git add skills/requirements-matrix/scripts/filter_matrix.py skills/requirements-matrix/scripts/test_filter_matrix.py
git commit -m "feat: add requirements matrix filtering and rendering"
```

---

### Task 8: `requirements-matrix` skill

**Files:**
- Create: `skills/requirements-matrix/SKILL.md`

**Interfaces:**
- Consumes: `filter_rows_for_class`, `render_matrix_markdown`, `render_matrix_status_yaml` from Task 7; reads `classification.yaml` written by Task 5's skill; reads `data/swe-catalog.yaml` from this plugin's install path.
- Produces: `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.md` and `.../requirements-mapping-matrix.yaml` in the *consuming project*.

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: requirements-matrix
description: Use after classify-software has produced a classification.yaml, to generate the project's NPR 7150.2D Requirements Mapping Matrix scoped to its declared software class
---

# Requirements Mapping Matrix (NPR 7150.2D Appendix C)

## Overview

Filters the bundled SWE requirement catalog to the subsystem's declared class and writes both a human-readable matrix and a machine-readable status file that later NASA-SWE skills update as compliance work proceeds.

**Announce at start:** "I'm using the requirements-matrix skill to generate your NPR 7150.2D Requirements Mapping Matrix."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/classification.yaml` to already exist (produced by the `classify-software` skill). If it doesn't exist, stop and run that skill first.

## Steps

1. Read the subsystem's `classification.yaml`, note its `class` field.
2. Read `<this plugin's install path>/data/swe-catalog.yaml`. Check `<this plugin's install path>/data/CATALOG-COVERAGE.md` and tell the user which NPR sections are and are not yet represented in the catalog — an incomplete catalog means an incomplete matrix, and the user needs to know that up front, not discover it later.
3. Run:

```bash
cd <this-plugin's-install-path>/skills/requirements-matrix/scripts
python3 -c "
import yaml
from filter_matrix import filter_rows_for_class, render_matrix_markdown, render_matrix_status_yaml

with open('../../../data/swe-catalog.yaml') as f:
    catalog = yaml.safe_load(f)

software_class = '<class from classification.yaml>'
subsystem = '<subsystem name>'

rows = filter_rows_for_class(catalog, software_class)
md = render_matrix_markdown(rows, subsystem, software_class)
status_rows = render_matrix_status_yaml(rows)

print(md)
print('---STATUS-YAML---')
print(yaml.dump(status_rows, sort_keys=False))
"
```

4. Write the printed markdown to `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.md` in the project being worked on.
5. Write the printed status YAML to `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` in the same location.
6. Tell the user how many requirements apply to their class and remind them the matrix only reflects the catalog's current coverage (per step 2).
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe
git add skills/requirements-matrix/SKILL.md
git commit -m "feat: add requirements-matrix skill"
```

---

### Task 9: Tailoring entry script (TDD)

**Files:**
- Create: `skills/tailoring-request/scripts/add_tailoring_entry.py`
- Test: `skills/tailoring-request/scripts/test_add_tailoring_entry.py`

**Interfaces:**
- Consumes: a `requirements-mapping-matrix.yaml` file (list of dicts, schema from Task 7's `render_matrix_status_yaml`) and a `tailoring-log.md` path (may not yet exist).
- Produces: `add_tailoring_entry(matrix_yaml_path: str, log_md_path: str, swe_id: str, rationale: str, risk: str, mitigation: str, approver: str) -> None`. Raises `ValueError` if `approver` is falsy. Raises `KeyError` if `swe_id` is not found in the matrix. On success: updates the matching row's `status` to `"tailored-out"` and `date` to today's date in the matrix YAML file, and appends a formatted entry to the log markdown file (creating it with a header if it doesn't exist).

- [ ] **Step 1: Write the failing tests**

```python
# skills/tailoring-request/scripts/test_add_tailoring_entry.py
import yaml
import pytest
from add_tailoring_entry import add_tailoring_entry

def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)

def sample_rows():
    return [
        {"swe_id": "SWE-057", "section": "4.2.3", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-058", "section": "4.3.2", "status": "not-started", "evidence": None, "date": None},
    ]

def test_blocks_without_approver(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    log_path = tmp_path / "tailoring-log.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="approver"):
        add_tailoring_entry(
            str(matrix_path), str(log_path),
            swe_id="SWE-057", rationale="r", risk="low", mitigation="m", approver="",
        )

def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    log_path = tmp_path / "tailoring-log.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        add_tailoring_entry(
            str(matrix_path), str(log_path),
            swe_id="SWE-999", rationale="r", risk="low", mitigation="m", approver="Jane TA",
        )

def test_updates_matrix_status_and_writes_log(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    log_path = tmp_path / "tailoring-log.md"
    write_matrix(matrix_path, sample_rows())

    add_tailoring_entry(
        str(matrix_path), str(log_path),
        swe_id="SWE-057", rationale="Not applicable to CLI tool", risk="Low",
        mitigation="Manual review substitutes", approver="Jane TA",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    row = next(r for r in updated if r["swe_id"] == "SWE-057")
    assert row["status"] == "tailored-out"
    assert row["date"] is not None

    other = next(r for r in updated if r["swe_id"] == "SWE-058")
    assert other["status"] == "not-started"

    log_content = log_path.read_text()
    assert "SWE-057" in log_content
    assert "Not applicable to CLI tool" in log_content
    assert "Jane TA" in log_content

def test_appends_to_existing_log(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    log_path = tmp_path / "tailoring-log.md"
    write_matrix(matrix_path, sample_rows())
    log_path.write_text("# Tailoring Log\n\n")

    add_tailoring_entry(
        str(matrix_path), str(log_path),
        swe_id="SWE-057", rationale="r1", risk="low", mitigation="m1", approver="A",
    )
    add_tailoring_entry(
        str(matrix_path), str(log_path),
        swe_id="SWE-058", rationale="r2", risk="low", mitigation="m2", approver="B",
    )

    content = log_path.read_text()
    assert content.count("## SWE-") == 2
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe/skills/tailoring-request/scripts
python3 -m pytest test_add_tailoring_entry.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'add_tailoring_entry'`

- [ ] **Step 3: Implement add_tailoring_entry.py**

```python
# skills/tailoring-request/scripts/add_tailoring_entry.py
import datetime
import yaml


def add_tailoring_entry(matrix_yaml_path, log_md_path, swe_id, rationale, risk, mitigation, approver):
    if not approver:
        raise ValueError("A named approver is required before a tailoring entry can be recorded")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row = next((r for r in rows if r["swe_id"] == swe_id), None)
    if row is None:
        raise KeyError(f"{swe_id} not found in requirements mapping matrix")

    today = datetime.date.today().isoformat()
    row["status"] = "tailored-out"
    row["date"] = today

    with open(matrix_yaml_path, "w") as f:
        yaml.dump(rows, f, sort_keys=False)

    try:
        with open(log_md_path) as f:
            existing = f.read()
    except FileNotFoundError:
        existing = "# Tailoring Log\n\n"

    entry = (
        f"## {swe_id} — {today}\n\n"
        f"- **Rationale:** {rationale}\n"
        f"- **Risk:** {risk}\n"
        f"- **Mitigation:** {mitigation}\n"
        f"- **Approved by:** {approver}\n\n"
    )

    with open(log_md_path, "w") as f:
        f.write(existing + entry)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest test_add_tailoring_entry.py -v
```

Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe
git add skills/tailoring-request/scripts/add_tailoring_entry.py skills/tailoring-request/scripts/test_add_tailoring_entry.py
git commit -m "feat: add tailoring/relief entry recording"
```

---

### Task 10: `tailoring-request` skill

**Files:**
- Create: `skills/tailoring-request/SKILL.md`

**Interfaces:**
- Consumes: `add_tailoring_entry` from Task 9.
- Produces: updates to `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` and `.../tailoring-log.md` in the consuming project.

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: tailoring-request
description: Use when a requirement in the project's requirements-mapping-matrix.yaml cannot be fully implemented, to record a NASA-style tailoring/request-for-relief entry with rationale, risk, mitigation, and approving authority
---

# Tailoring / Request for Relief

## Overview

Implements the tailoring principles from NPR 7150.2D Chapter 2 and NASA-STD-8739.8B §4.5: a requirement that isn't fully implemented must have a documented, approved rationale — never a silent gap.

**Announce at start:** "I'm using the tailoring-request skill to record a tailoring/relief entry."

## Steps

1. Ask which SWE-id (from the subsystem's `requirements-mapping-matrix.yaml`) is being tailored, and confirm it's actually present in that file — if you're not sure, look it up rather than guessing the id.
2. Ask for, in the user's own words: rationale (why this doesn't apply or can't be met as written), risk (what could go wrong if this is skipped), mitigation (what reduces that risk), and approver (a named person or role — the matrix row's `technical_authority` field is the default suggestion, from `filter_matrix.py`'s output, but the user may name someone else).
3. If the user has no approver to name, stop — do not record an entry without one. Explain that NPR 7150.2D 2.1.5.4's note requires tailoring to be approved and recorded with rationale, not simply asserted.
4. Run:

```bash
cd <this-plugin's-install-path>/skills/tailoring-request/scripts
python3 -c "
from add_tailoring_entry import add_tailoring_entry

add_tailoring_entry(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    log_md_path='<path to the subsystem's tailoring-log.md>',
    swe_id='<SWE-id>',
    rationale='<rationale>',
    risk='<risk>',
    mitigation='<mitigation>',
    approver='<approver>',
)
print('Recorded.')
"
```

5. Confirm to the user which SWE-id was tailored and where the log entry was written.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe
git add skills/tailoring-request/SKILL.md
git commit -m "feat: add tailoring-request skill"
```

---

### Task 11: End-to-end integration test

**Files:**
- Test: `tests/test_sp1_end_to_end.py`

**Interfaces:**
- Consumes: `classify` (Task 4), `filter_rows_for_class`/`render_matrix_markdown`/`render_matrix_status_yaml` (Task 7), `add_tailoring_entry` (Task 9), and reads `data/swe-catalog.yaml` (Task 6).
- Produces: nothing consumed by later tasks — this is the final verification that the three skills' scripts compose correctly end-to-end.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_sp1_end_to_end.py
import sys
import os
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "classify-software", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "skills", "requirements-matrix", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "skills", "tailoring-request", "scripts"))

from classify import classify
from filter_matrix import filter_rows_for_class, render_matrix_markdown, render_matrix_status_yaml
from add_tailoring_entry import add_tailoring_entry


def test_full_pipeline_for_a_class_d_subsystem(tmp_path):
    # 1. Classify: a research/engineering tool with no safety implications -> Class D
    result = classify({
        "class_a_human_rated": False,
        "class_b_non_human_space_or_large_aero": False,
        "class_c_mission_support_or_facility": False,
        "class_d_basic_science_or_research": True,
        "class_e_design_concept_general_purpose": False,
        "is_safety_critical": False,
    })
    assert result["class"] == "D"

    # 2. Load the real catalog and filter to Class D
    with open(os.path.join(ROOT, "data", "swe-catalog.yaml")) as f:
        catalog = yaml.safe_load(f)
    rows = filter_rows_for_class(catalog, "D")
    assert len(rows) > 0, "expected at least one Class D requirement in the populated catalog slice"

    md = render_matrix_markdown(rows, subsystem="test-subsystem", software_class="D")
    status_rows = render_matrix_status_yaml(rows)

    matrix_md_path = tmp_path / "requirements-mapping-matrix.md"
    matrix_yaml_path = tmp_path / "requirements-mapping-matrix.yaml"
    matrix_md_path.write_text(md)
    with open(matrix_yaml_path, "w") as f:
        yaml.dump(status_rows, f, sort_keys=False)

    assert "Class D" in matrix_md_path.read_text()
    assert all(r["status"] == "not-started" for r in status_rows)

    # 3. Tailor out the first requirement
    first_id = status_rows[0]["swe_id"]
    log_path = tmp_path / "tailoring-log.md"
    add_tailoring_entry(
        str(matrix_yaml_path), str(log_path),
        swe_id=first_id, rationale="Not applicable to a CLI-only tool",
        risk="Low — no external interface", mitigation="Manual code review",
        approver="Project Lead",
    )

    with open(matrix_yaml_path) as f:
        updated = yaml.safe_load(f)
    tailored_row = next(r for r in updated if r["swe_id"] == first_id)
    assert tailored_row["status"] == "tailored-out"
    assert first_id in log_path.read_text()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe
python3 -m pytest tests/test_sp1_end_to_end.py -v
```

Expected: FAIL initially only if any earlier task's file is missing; if Tasks 1-10 are complete, this should mostly pass already except for possibly needing `PYYAML`/module path fixes — treat any failure here as a real integration bug between the three scripts, not a placeholder to skip.

- [ ] **Step 3: Fix any integration issues found, then re-run**

```bash
python3 -m pytest tests/test_sp1_end_to_end.py -v
```

Expected: 1 passed

- [ ] **Step 4: Commit**

```bash
git add tests/test_sp1_end_to_end.py
git commit -m "test: add SP1 end-to-end integration test"
```

---

### Task 12: Fork README and final commit

**Files:**
- Modify: `README.md` (prepend a new section)

**Interfaces:**
- Produces: none — documentation only.

- [ ] **Step 1: Prepend a NASA-SWE section to README.md**

Add this section immediately after the top-level title/badge block of the existing `README.md` (leave the rest of the upstream README intact below it):

```markdown
## NASA-SWE Compliance Layer

This fork adds a NASA NPR 7150.2D / NASA-STD-8739.8B compliance layer on top of upstream Superpowers:

- `classify-software` — determine a project or subsystem's NASA software class (A-F) per NPR 7150.2D Appendix D
- `requirements-matrix` — generate a class-scoped Requirements Mapping Matrix per NPR 7150.2D Appendix C
- `tailoring-request` — record NASA-style tailoring/request-for-relief entries for requirements that aren't fully implemented

See `data/CATALOG-COVERAGE.md` for which parts of NPR 7150.2D Appendix C are currently represented in the bundled requirements catalog — this is a working draft, extended incrementally, not a certified reproduction of the standard. See `docs/superpowers/specs/2026-08-10-nasa-swe-foundation-design.md` for the design rationale and `docs/superpowers/plans/2026-08-10-nasa-swe-foundation.md` for how this layer was built.

---
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/scratch-claude/superpowers-nasa-swe
git add README.md
git commit -m "docs: document NASA-SWE compliance layer in README"
```

---

## Self-Review Notes

- **Spec coverage:** classify-software (Tasks 4-5) ✓, requirements-matrix (Tasks 3, 6, 7, 8) ✓, tailoring-request (Tasks 9-10) ✓, fork mechanics (Task 1) ✓, data population strategy (Task 6, with explicit coverage tracking) ✓, error handling — ambiguous classification (Task 4 test `test_multiple_matching_classes_are_flagged_ambiguous_and_higher_wins`, surfaced in Task 5's SKILL.md) ✓, missing SWE-id hard error (Task 9 test `test_blocks_unknown_swe_id`) ✓, tailoring without approver blocked (Task 9 test `test_blocks_without_approver`) ✓.
- **Type consistency:** `classify()` return shape (`class`/`ambiguous`/`candidates`) used identically in Tasks 4, 5, 11. `filter_rows_for_class`/`render_matrix_markdown`/`render_matrix_status_yaml` signatures used identically in Tasks 7, 8, 11. `add_tailoring_entry` keyword arguments used identically in Tasks 9, 10, 11.
- **No placeholders:** every step has literal code or literal file content; Task 6 names an exact page range and exact validation command rather than "transcribe the requirements."
