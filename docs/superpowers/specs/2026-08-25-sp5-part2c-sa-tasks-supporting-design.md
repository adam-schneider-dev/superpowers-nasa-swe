# NASA-SWE Superpowers Fork — SP5 Part 2c: SA/Safety Tasks, Supporting (NPR Ch.5) Design

**Date:** 2026-08-25
**Status:** Approved

## Background

SP1-4, SP5 Part 1 (IV&V verification, §4.4.2), Part 2a (SA/safety tasks, NPR Ch.3 Management, 45 rows) and Part 2b (NPR Ch.4 Engineering, 37 rows) are all done and merged to `main` (PRs #1-#6). Part 2a's spec identified NASA-STD-8739.8B §4.3 Table 1 as splitting cleanly along NPR 7150.2D's own chapter boundaries; Parts 2a and 2b took Chapters 3 and 4.

This spec covers Chapter 5, Supporting Software Life Cycle Requirements — the table's last chapter. Reading the table directly (`pdftotext -layout reference/NASA-STD-8739.8B.pdf`, the rows between the §4.6.6/SWE-196 row and the point where the table ends and §4.4 IV&V Overview begins) rather than assuming Part 2b's shape carries over found:

- **21 rows across 5 subsections**: §5.1 Software Configuration Management (8 rows), §5.2 Software Risk Management (1), §5.3 Software Peer Reviews/Inspections (3), §5.4 Software Measurements (5), §5.5 Software Non-conformance or Defect (4).
- **Table 1 ends at §5.5.4 / SWE-204.** It has no Chapter 6 or 7 rows. 45 + 37 + 21 = 103, the table's documented total — **this sub-project completes the catalog at 103/103.**
- **No lettered sub-ids.** Chapter 4's `SWE-065a`-`SWE-065d` are the table's only lettered rows; every Chapter 5 `swe_id` is plain. `_base_swe_id()` in `sa_task_matrix.py` is therefore not exercised by these rows and stays in place solely for Chapter 4.
- **Every row maps 1:1 onto an existing `swe-catalog.yaml` row** — verified programmatically, the same property Parts 2a and 2b's rows had.
- **No `swe_id` collides with a row already in the catalog.** All 21 are new to `sa-task-catalog.yaml`.
- **Subsection sizes are far less skewed than Chapter 4's.** Range is 1-8 rows, versus Chapter 4's 1-16.
- **The 5 subsections map 1:1 onto SP4's five existing Chapter 5 skills** — `config-management`, `risk-management`, `peer-review-record`, `measurements`, `non-conformance-record`.
- **SWE-086's section is `5.2`, not `5.2.1`.** Corrected after implementation: this document originally took `5.2.1` from Table 1 without cross-checking NPR 7150.2D, which states the requirement directly under its `5.2 Software Risk Management` heading with no sub-number. Section numbers come from NPR via `swe-catalog.yaml`, and `test_section_matches_swe_catalog_section_for_every_row` enforces that, so `5.2` is what ships. It is the catalog's only two-part section.
- **Class E has zero applicable Chapter 5 rows.** Per-class applicable row counts, inherited from `swe-catalog.yaml`: A 21, B 21, C 19, D 8, E 0, F 13. A Class E subsystem's generated matrix contains no `5.` rows at all — the skill must treat that as a legitimate outcome, not a generation failure.

## Scope

NASA-STD-8739.8B §4.3 Table 1, restricted to the 21 rows whose NPR 7150.2D section falls under Chapter 5: §5.1 through §5.5.

One new skill, `sa-task-verification-supporting`. Extends the existing `data/sa-task-catalog.yaml` by 21 rows, growing it to 103 of 103 — no new catalog file. No changes to `requirements-matrix`'s matrix-generation code; only its supporting prose. Includes the completion close-out this sub-project makes possible: rewriting `data/SA-TASK-CATALOG-COVERAGE.md` around complete coverage, updating the README to present the three SA-task skills as covering the whole of Table 1, and pinning the Chapter 5 rows in tests so 103/103 cannot silently regress.

Out of scope: Appendix A hazard analysis (SP5 Part 3), which remains a separate un-brainstormed sub-project and inherits no decision from this document except what is already fork-wide.

## Decisions Made This Session

- **New skill name: `sa-task-verification-supporting`** — deliberately *not* the mechanical parallel `sa-task-verification-management-supporting`. Part 2b's `sa-task-verification-management-engineering` carries "management" from Chapter 3's title with "-engineering" appended; extending that pattern to Chapter 5 would produce a name asserting "management" about a chapter that is not management. The wart is not propagated. Part 2b's shipped name is left alone: renaming an already-merged skill is a separate concern, not a rider on a chapter addition.

- **Six interview groups, splitting §5.1 only.** §5.1's 8 rows would be the largest single question in the fork (Chapter 4's largest was 7), so it splits along its own internal topic boundary: CM planning and change control (the plan, the configuration items, the levels-of-control procedures, change tracking, status records) versus CM audits and release (configuration audits, joint NASA/developer audits, storage/handling/delivery/release procedures). Every other subsection stays whole, so each remaining question maps to exactly one NPR subsection and one existing SP4 skill — a user answering can point at one artifact. §5.2's single row stays its own short question rather than being merged into §5.5; risk management and non-conformance management are distinct NPR subsections with distinct existing skills, and straddling two subsections in one question is the pattern that made Part 2a's questions hard to verify.

| # | Group | `fields` key | NPR sections | SWE-ids | Rows |
|---|---|---|---|---|---|
| 1 | CM planning & change control | `cm_planning_and_change_control` | §5.1.2-§5.1.6 | 079, 081, 082, 080, 083 | 5 |
| 2 | CM audits & release | `cm_audits_and_release` | §5.1.7-§5.1.9 | 084, 045, 085 | 3 |
| 3 | Risk management | `risk_management` | §5.2 | 086 | 1 |
| 4 | Peer reviews / inspections | `peer_reviews_and_inspections` | §5.3.2-§5.3.4 | 087, 088, 089 | 3 |
| 5 | Measurements | `measurements` | §5.4.2-§5.4.6 | 090, 093, 094, 199, 200 | 5 |
| 6 | Non-conformance & defect | `non_conformance_and_defect` | §5.5.1-§5.5.4 | 201, 202, 203, 204 | 4 |

- **Record script is a third near-identical copy, not a shared module.** The two existing SA-task record scripts are 53 lines each and differ by exactly two lines — a header string and the function name. Extracting a shared module was considered and rejected: per-skill-directory self-containment is a deliberate, documented property of this fork, stated outright at `skills/safety-critical-determination/scripts/amend_safety_critical.py:8`, where a duplication exists specifically so the script runs without another skill's `scripts` directory on `sys.path`. A shared module would also mean refactoring two already-merged, already-reviewed skills inside a chapter-addition PR — the bundled-unrelated-changes pattern this repo's own CLAUDE.md says gets closed. Collapsing all three chapters into one parameterized skill was rejected for the same reason Part 2b rejected it: it abandons the one-skill-set-per-chapter pattern used by all of SP2/SP3/SP4 and produces one interview file spanning 103 rows. Deduplicating all 15 `record_*.py` scripts is recorded as post-initial-pass backlog work, to be done as its own PR if at all.

- **Same catalog file, more rows.** `SA-TASK-CATALOG-COVERAGE.md` has documented since Part 2a that the catalog grows incrementally across Parts 2a-2c; this follows through rather than reopening it.

- **One shared per-subsystem matrix, now three chapter-scoped skills recording against it.** `requirements-matrix` Step 7 already generates a single `sa-task-mapping-matrix.yaml`/`.md` pair per subsystem spanning whatever the catalog covers. Once these rows land, a freshly generated matrix contains Chapters 3, 4 and 5 together. All three skills read that file; each touches only its own chapter's rows.

## Architecture

### Data layer

`data/sa-task-catalog.yaml` gains 21 `{swe_id, section}` rows in Table 1's own order (§5.1.2 first, §5.5.4 last), appended after the Chapter 4 rows. No task text — same convention as `swe-catalog.yaml` and `ivv-catalog.yaml`: cite by `swe_id`/section only; paraphrase lives in the skill's interview prose. No chapter marker of its own; a row's chapter stays implicit in its `section` prefix.

The file's header comment currently reads "Coverage: 82 of the table's 103 total rows — NPR 7150.2D Chapters 3-4" and points at Chapter 5 as a not-yet-built sub-project. It becomes a statement of complete coverage.

### Generation — `requirements-matrix`, wording only

No code change. `filter_sa_task_rows_for_class` in `skills/requirements-matrix/scripts/sa_task_matrix.py` operates on whatever the catalog contains and looks up class applicability per `swe_id` against `swe-catalog.yaml`; the generalized markdown header text introduced in Part 2b already avoids naming a specific chapter. `_base_swe_id()` continues to serve Chapter 4's lettered ids and is a no-op for these rows.

`skills/requirements-matrix/SKILL.md` gains a reference to the third skill alongside the two it already names.

### Recording — new `sa-task-verification-supporting` skill

`skills/sa-task-verification-supporting/` with `SKILL.md` and `scripts/record_sa_task_verification_supporting.py` plus its test file. The script differs from `record_sa_task_verification_engineering.py` in exactly the same two ways that one differs from Part 2a's: the header string says Chapter 5, and the function is named `record_sa_task_verification_supporting`.

`SKILL.md` follows the established shape: frontmatter `description` scoped to Chapter 5; an Overview stating the skill records evidence rather than performing assurance work; an announce line; a Precondition; the six interview questions; a Running the script block; and a Writing the output line.

**Precondition.** Requires `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.yaml` to exist with at least one row whose section starts `5.`. Absence means one of two things and the skill must say both: the subsystem's class has no applicable Chapter 5 rows — which for **Class E is always true, all 21 rows are inapplicable** — or `requirements-matrix` has not been re-run since these catalog rows existed. The user should check there rather than assume the chapter does not apply.

**Evidence standard.** Unchanged from Parts 2a/2b and from `peer-review-record` / `ivv-verification-record`: each answer must point at something a human auditor could go check — an assurance assessment, a confirmed audit finding, a review record, a tracked risk or issue. A vague "assurance handled it" is insufficient. Ids without real evidence are left out of that run's `swe_ids` rather than recorded as unverifiable claims.

### Data flow

`classify-software` → `requirements-matrix` (generates `sa-task-mapping-matrix.yaml` spanning Chapters 3-5) → the three chapter-scoped recording skills, each reading that one file and marking only its own chapter's rows → `sa-task-verification-supporting.md` per subsystem, one `## Recorded` entry appended per run.

### Error handling

Unchanged from Part 2b. The script raises on: an empty `swe_ids` list, ids absent from the matrix, and ids present but tailored out. Partial runs are supported — a run need not answer all six groups, and later runs append rather than overwrite.

### Testing

`tests/test_sa_task_catalog_integrity.py` currently hardcodes the catalog's shape and must be updated, not merely extended:

- `test_bundled_sa_task_catalog_has_82_rows` → 103 rows, renamed accordingly.
- `test_all_rows_are_chapter_3_or_4` → chapters 3, 4 or 5, renamed accordingly.
- New `test_chapter_5_has_21_rows`.
- New completeness test pinning the exact 21 `(swe_id, section)` pairs, so a dropped or altered row fails loudly rather than shifting a count another test also asserts.
- The existing per-row tests (unique ids, no task text, every id in `swe-catalog.yaml`, section matches `swe-catalog.yaml`) already cover the new rows without modification.

`skills/sa-task-verification-supporting/scripts/test_record_sa_task_verification_supporting.py` mirrors the engineering skill's five cases: marks satisfied, empty ids raises, unknown ids raises, tailored-out ids raises, second call appends.

Full suite (185 tests today) plus `ruff check .` must pass before the PR.

### Documentation close-out

- `data/SA-TASK-CATALOG-COVERAGE.md`: headline becomes 103 of 103; a Chapter 5 covered section listing §5.1-§5.5 is added; the "Not yet covered" section is deleted; the note about matrices generated before Part 2c landing is rewritten to describe re-running `requirements-matrix` to pick up full coverage; the Chapter 4 note about `SWE-065`'s lettered sub-tasks stays.
- `README.md`: the SA-task section presents `sa-task-verification-management`, `sa-task-verification-management-engineering` and `sa-task-verification-supporting` as jointly covering all 103 rows of §4.3 Table 1, and drops the language describing remaining chapters as not-yet-started follow-ons. Appendix A hazard analysis remains listed as a separate future sub-project.
- `skills/requirements-matrix/SKILL.md`: references the third skill.

## Open Risks

- **Fabricated interview content.** Part 2a shipped interview questions containing invented material, caught only by a second review round; Part 2b added a mandatory independent re-verification and found nothing. This sub-project carries the same mandatory second round: after the questions are drafted, all 21 SWE-ids are re-extracted from the questions and cross-checked against both the catalog and the table in the PDF, confirming no gaps, no extras, no duplicates, and no task text that is not in the source.
- **Class E produces an empty result.** Any manual end-to-end check must not use a Class E subsystem to validate the happy path, since a correct run there records nothing.
- **Row order versus question order.** The catalog is stored in Table 1 order; question 1 lists its ids in the order 079, 081, 082, 080, 083, which is topic order, not table order. This is intentional and mirrors Part 2b, where several groups do the same, but it means the coverage cross-check must compare sets, not sequences.
