# NASA-SWE Superpowers Fork — SP5 Part 2b: SA/Safety Tasks, Engineering (NPR Ch.4) Design

**Date:** 2026-08-23
**Status:** Approved

## Background

SP1-4, SP5 Part 1 (IV&V verification, §4.4.2), and SP5 Part 2a (SA/safety tasks, NPR Ch.3 Management, 45 rows) are all done and merged to `main`. Part 2a's spec identified NASA-STD-8739.8B §4.3 Table 1 as splitting cleanly along NPR 7150.2D's own chapter boundaries — the same ones SP2/SP3/SP4 already used to build `data/swe-catalog.yaml`: Ch.3 Management (45 rows, done), Ch.4 Engineering (37 rows, this spec), Ch.5 Supporting (21 rows, not started).

This spec covers Chapter 4. Reading the table directly (`pdftotext -layout reference/NASA-STD-8739.8B.pdf`, §4.3 Table 1's Ch.4 rows) rather than assuming Part 2a's shape carries over unchanged found:

- **37 rows across 6 subsections**: §4.1 Software Requirements (6 rows), §4.2 Software Architecture (2), §4.3 Software Design (1), §4.4 Software Implementation (7), §4.5 Software Testing (16), §4.6 Software Operations, Maintenance, and Retirement (5).
- **Every row maps 1:1 onto an existing `swe-catalog.yaml` row** — verified programmatically, same property Part 2a's rows had.
- **SWE-065's four lettered sub-items (065a-065d) all carry the same NPR section, `4.5.2`** — the `swe_id` carries the letter suffix, not the section. This corrects a guess in Part 2a's spec, which speculated the section itself would be lettered (`"4.5.2a"` etc.) without having read Chapter 4's actual table yet; the real table shows all four rows share `section: "4.5.2"` and are distinguished only by their `swe_id`.
- **Row-count-per-subsection is more skewed than Chapter 3 was**: 1 row (§4.3 Design) up to 16 rows (§4.5 Testing), versus Ch.3's 1-to-13 range.
- **No class-applicability columns of its own** — same as every other Table 1 row, inherited from the matching `swe_id`'s class marks in `swe-catalog.yaml`.

## Scope

NASA-STD-8739.8B §4.3 Table 1, restricted to the 37 rows whose NPR 7150.2D section falls under Chapter 4 (Software Engineering): §4.1 through §4.6.

One new skill, `sa-task-verification-management-engineering`. Extends the existing `data/sa-task-catalog.yaml` (37 more rows, growing it to 82 of 103) — no new catalog file. No changes needed to `requirements-matrix`'s matrix-generation code, which already operates on "whatever the catalog currently covers" rather than a hardcoded chapter; only its supporting prose needs updating to stop saying "Chapter 3 SA task evidence" specifically. Chapter 5 (21 rows) is a separate future spec (Part 2c) and inherits no design decision from this document except what's already fork-wide.

## Decisions Made This Session

- **New skill, not folded into `sa-task-verification-management`.** Every other NPR chapter in this fork gets its own dedicated skill(s) for the main compliance track (SP2's six Ch.3 skills, SP3's six Ch.4 skills, SP4's five Ch.5 skills); `sa-task-verification-management` was itself scoped and named specifically to Chapter 3 ("Use to record a subsystem's NASA-STD-8739.8B §4.3 Table 1 software assurance and safety task evidence for NPR 7150.2D Chapter 3 (Management) requirements" — its literal `description` frontmatter). Extending it to also cover Chapter 4 would mean renaming/rescoping a shipped skill and roughly doubling its interview question count in one file, rather than following the fork's established one-skill-set-per-chapter pattern.
- **New skill name: `sa-task-verification-management-engineering`.** Mirrors Part 2a's name with Chapter 4's own NPR title ("Engineering") appended, the same way Part 2a's name carried "management" for Chapter 3's title.
- **Same catalog file, more rows — not a new catalog per chapter.** `data/sa-task-catalog.yaml` was already documented (in `SA-TASK-CATALOG-COVERAGE.md`, written during Part 2a) as growing incrementally across Parts 2a-2c; this spec follows through on that rather than reopening it. The catalog is a pure `{swe_id, section}` index with no chapter marker of its own — a row's chapter is implicit in its `section` prefix (`"3."` vs `"4."`).
- **One shared per-subsystem matrix file, two chapter-scoped skills recording against it.** `requirements-matrix`'s Step 7 already generates a single `sa-task-mapping-matrix.yaml`/`.md` pair per subsystem spanning whatever the catalog currently covers — it was built generically in Part 2a, not hardcoded to Chapter 3, so once this spec's rows land, a freshly generated matrix will contain both Ch.3 and Ch.4 rows together in one file. Both `sa-task-verification-management` and `sa-task-verification-management-engineering` point at that same file; each only touches its own chapter's subset (mirroring `sa-task-verification-management`'s existing precondition text, which already scopes itself to "at least one Chapter 3 row" rather than claiming the whole file). This needs no new matrix-generation code — only each skill's own precondition wording.
- **Record script is a fresh near-identical copy, not a shared import.** Matches this fork's established, deliberate convention (13+ record scripts across SP1-4 and Part 1/2a, near-byte-identical, not refactored into a shared library) — `record_sa_task_verification_engineering.py` differs from Part 2a's `record_sa_task_verification.py` only in its header text ("Chapter 4" instead of "Chapter 3").
- **Interview rebalanced into 7 questions, not one per subsection.** §4.3 Design (1 row) through §4.5 Testing (16 rows) is too skewed for a 1:1 mapping — it would produce one question covering nearly half the chapter's rows and several trivial single-row questions. Grouping instead: §4.1 alone (6 rows), §4.2+§4.3 merged since both are tiny (3 rows), §4.4 alone (7 rows), §4.5 split into three roughly-even parts by its own natural sub-topics — test planning/procedures/data/environment (SWE-065a-d, 4 rows), execution/results/validation (6 rows), coverage/regression/acceptance/COTS testing (6 rows) — and §4.6 alone (5 rows). Final group boundaries and exact question wording are drafted at plan-writing time, same as every prior sub-project.

| # | Group | NPR sections | Rows |
|---|---|---|---|
| 1 | Software Requirements | §4.1.2-§4.1.7 | 6 |
| 2 | Software Architecture & Design | §4.2.3, §4.2.4, §4.3.2 | 3 |
| 3 | Software Implementation | §4.4.2-§4.4.8 | 7 |
| 4 | Test planning & environment | §4.5.2 (SWE-065a-d) | 4 |
| 5 | Test execution, results & validation | §4.5.3-§4.5.8 | 6 |
| 6 | Coverage, regression, acceptance & embedded-COTS testing | §4.5.9-§4.5.14 | 6 |
| 7 | Software Operations, Maintenance & Retirement | §4.6.2-§4.6.6 | 5 |

## Architecture

### Data layer

- **`data/sa-task-catalog.yaml`** — extended, not replaced: 37 new rows appended (order: Table 1's own §4.1→§4.6 order, matching Part 2a's convention of storing rows in the table's own order even though the skill's interview presents them regrouped/reordered). Same `{swe_id, section}` shape, no task text. SWE-065's four rows: `swe_id: "SWE-065a"` through `"SWE-065d"`, all four with `section: "4.5.2"` (see Background — corrects Part 2a's speculative note).
- **`data/SA-TASK-CATALOG-COVERAGE.md`** — updated: move Chapter 4 from "Not yet covered" to "Covered," list its 6 subsections by name, update the total (82 of 103 rows now covered), leave Chapter 5 as the remaining gap.
- **`docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.yaml`/`.md`** — no schema change. Once this spec lands, a freshly generated matrix simply contains more rows (Ch.3 + Ch.4) than it did before, using the exact same generation code.

### Generation — `requirements-matrix`, wording only

No code change to `sa_task_matrix.py` or its render functions — they already operate on whatever rows the catalog and class filter produce, regardless of chapter. Two prose updates:
- `render_sa_task_matrix_markdown`'s output header currently states "Chapter 3 / Software Management rows only" — this becomes stale the moment this spec lands and must be generalized (e.g. reference `SA-TASK-CATALOG-COVERAGE.md` for current scope, as the skill's own `SKILL.md` step already does, rather than naming a specific chapter in generated output).
- `requirements-matrix/SKILL.md` step 7's closing sentence ("`sa-task-verification-management` requires this file to exist before it can record Chapter 3 SA task evidence") needs a second sentence added for the new skill's equivalent precondition on Chapter 4 rows.

### Recording — new `sa-task-verification-management-engineering` skill

`skills/sa-task-verification-management-engineering/scripts/record_sa_task_verification_engineering.py`, signature `(matrix_yaml_path, record_md_path, swe_ids, fields, evidence)` — identical shape to Part 2a's script and every other record script in this fork.

**Precondition:** `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.yaml` must already exist with at least one Chapter 4 row (`section` starting `"4."`) for the subsystem's class. `SKILL.md` states this plainly, same wording pattern as Part 2a's precondition section.

**Interview — 7 grouped questions** per the table above, covering all 37 rows. Same evidence standard as every prior record skill: real, checkable evidence only (an assurance assessment, a confirmed audit finding, a review record), never a self-attested "assurance handled it." Output: Markdown record appended to `docs/nasa-compliance/<subsystem>/sa-task-verification-management-engineering.md`, matrix rows stamped `satisfied` + evidence + date.

### Data flow

`classify-software` → `requirements-matrix` (generates `requirements-mapping-matrix.yaml` and `sa-task-mapping-matrix.yaml`, the latter now spanning Ch.3+Ch.4 once both catalogs exist) → `sa-task-verification-management` (Ch.3 rows) and/or `sa-task-verification-management-engineering` (Ch.4 rows), independently, each interviewing its own group set and stamping its own chapter's rows in the shared matrix.

### Error handling

Same three mandated behaviors as every record script in this fork:
- Empty `swe_ids` → `ValueError`.
- Unknown `swe_id` (not present in the subsystem's `sa-task-mapping-matrix.yaml`) → `KeyError`.
- Attempting to mark an already-`tailored-out` row `satisfied` → `ValueError`, matrix left unmodified.

### Testing

- `tests/test_sa_task_catalog_integrity.py` — extended (not replaced) to assert 82 rows total, all 37 new `swe_id`s exist in `swe-catalog.yaml`, no duplicates, `section` matches the expected NPR section for each `swe_id` including the SWE-065a-d/`"4.5.2"` case.
- `record_sa_task_verification_engineering.py`: 5 tests, same bar as every prior record script — golden path, the 3 mandated error paths, append-to-existing-record.
- **Final whole-branch review must independently re-check all 7 interview questions against `reference/NASA-STD-8739.8B.pdf` §4.3 Table 1's Chapter 4 rows for both order-mirroring and content accuracy** — not just verbatim-phrase matches. Part 2a's own review process is the template to repeat here: draft each question against the source PDF directly at plan-writing time (not left for review alone), run an automated word-overlap check before implementation is considered complete, and get a second independent review round given how badly this exact defect class recurred in Part 2a (including a genuine fabrication, not just paraphrase drift, in one question).

## Open Risks

- **Tailoring authority for Table 1 rows remains undesigned**, same open item Part 2a deferred. Not blocking — every record skill in this fork already allows `tailored-out` without a matrix-enforced approver check.
- **Chapter 5 (Part 2c, 21 rows) is not designed.** This spec's shape (new chapter-scoped skill, same catalog file, shared matrix, rebalanced interview grouping) is expected to carry over, but Part 2c needs its own subsection row-count check and its own brainstorm — not assumed inherited wholesale, same caveat Part 2a stated about this document.
- **§4.5 Testing's 16-row split into three questions (groups 4-6) is a judgment call, not derived from any structural marker in the table.** The three sub-groupings (planning/execution/coverage) are a reasonable reading of the subsection's own row order, but should be sanity-checked against the actual task content at plan-writing time — a different split might read more naturally once the full task text for each row is in hand.
