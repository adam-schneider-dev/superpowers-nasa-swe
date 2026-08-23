# NASA-SWE Superpowers Fork — SP5 Part 2a: SA/Safety Tasks, Management (NPR Ch.3) Design

**Date:** 2026-08-22
**Status:** Approved

## Background

SP1-4 are done and merged to `main`. SP5 Part 1 (IV&V verification, NASA-STD-8739.8B §4.4.2) is also done and merged (PR #2). That spec's Background identified NASA-STD-8739.8B as three separable bodies of content:

1. **§4.3 Table 1** (pp. 21-51, the bulk of the document) — a per-existing-SWE-id checklist of "Software Assurance and Software Safety Tasks."
2. **§4.4.2** (pp. 52-60) — 49 flat IV&V verification requirements. **Done — SP5 Part 1.**
3. **Appendix A** (pp. 62-70) — hazard-analysis guidance. Not started.

This spec covers body 1, Table 1. Reading the table directly (not assumed from the ~90-row placeholder estimate) found:

- **103 rows** (100 base SWE-ids, plus SWE-065 split into four lettered sub-items 065a-065d), each carrying **1-8 numbered "Software Assurance and Software Safety Tasks"** — roughly 5x Part 1's item count.
- **Every row maps 1:1 onto an existing `swe-catalog.yaml` row** — verified programmatically: the 100 base SWE-ids in Table 1 exactly match the 100 ids already in `swe-catalog.yaml`, with none missing on either side.
- **No class-applicability columns of its own.** A row's applicability is inherited from the same SWE-id's existing class marks in `swe-catalog.yaml` — unlike Part 1's §4.4.2, which needed its own applicability question because it had no such anchor.
- The table splits cleanly along NPR 7150.2D's existing chapter boundaries, the same ones SP2/SP3/SP4 already used to build the underlying catalog: **Ch.3 Management = 45 rows across 12 subsections (§3.1-§3.12), Ch.4 Engineering = 37 rows, Ch.5 Supporting = 21 rows.**

103 rows / ~150-200 discrete task items is too large for one interview — Part 1 found 49 flat items already needed 9 grouped questions to stay paraphrase-safe. Decomposing further, by the same chapter boundaries the fork already uses everywhere else, avoids inventing new structure and keeps each sub-spec's interview roughly Part-1-sized. **This document covers only Chapter 3 (45 rows).** Chapters 4 and 5 are separate future specs (Parts 2b and 2c) and inherit no design decision from this document except the record-only posture, which is fork-wide.

Checked for overlap before scoping: `sa-ivv-coordination` (§3.6 role assignment + IV&V applicability), `safety-critical-determination` (§4.2's 5-criteria test), and `ivv-verification-record` (§4.4.2) all touch adjacent NPR sections but none records the SA/safety-task performance checklist itself. Table 1's content — a distinct role (SA/safety personnel confirming or assessing) attesting to distinct work against each existing requirement — is new.

## Scope

NASA-STD-8739.8B §4.3 Table 1, restricted to the 45 rows whose NPR 7150.2D section falls under Chapter 3 (Software Management): §3.1 through §3.12.

One new skill, `sa-task-verification-management`, plus an extension to the existing `requirements-matrix` skill. New data file `data/sa-task-catalog.yaml`, built incrementally (45 rows now, 37 more in Part 2b, 21 more in Part 2c). New per-subsystem `sa-task-mapping-matrix.yaml`.

## Decisions Made This Session

- **Decompose Table 1 into three sub-specs by NPR chapter (3/4/5), not one spec or one skill.** Mirrors the exact chapter boundaries SP2/SP3/SP4 already established for the underlying catalog and its 13 record skills. Starting with Chapter 3 first, matching the original SP2→SP3→SP4 build order.
- **New parallel catalog + matrix, not folded into `swe-catalog.yaml`/`requirements-mapping-matrix.yaml`.** Table 1 rows are performed by a different role (SA/safety personnel confirming a requirement, not the PM/team fulfilling it) — the same reasoning Part 1 used for keeping IV&V's matrix separate, applied here even though (unlike Part 1) these rows do map onto existing SWE-ids. Mixing the PM's requirement-completion status and the SA role's task-verification status into one matrix row would conflate two different actors' state in the same file.
- **New catalog keys on the existing `swe_id`, not a new namespaced id scheme.** Unlike Part 1's flat §4.4.2 items (which had no existing anchor and needed new `IVV-4.4.2.<n>` ids), every Table 1 row already has a home: the same SWE-id already in `swe-catalog.yaml`. Reusing it keeps the two catalogs joinable by a plain key lookup.
- **`requirements-matrix` generates the new matrix, not a new standalone generator skill or the new record skill itself.** `requirements-matrix` already reads `classification.yaml`, filters `swe-catalog.yaml` by class, and runs once per subsystem as the first compliance step. Table 1's applicability is exactly that same class filter — there is no new gate to ask about (unlike Part 1, where `sa-ivv-coordination` owned a genuine new applicability question). Extending the skill that already computes the filter avoids a second skill re-deriving it.
- **One new skill this sub-spec, `sa-task-verification-management`**, separate from the six existing §3.x-scoped skills (`lifecycle-planning`, `cost-estimation`, `sa-ivv-coordination`, `reuse-assessment`, `cybersecurity-assessment`, `traceability`). Folding SA-task confirmation into those would mix the SA role's attestation into skills built around the PM/team's own requirement fulfillment — the same role-separation argument that motivated the parallel-matrix decision above.
- **Interview grouped into ~14 rebalanced questions, not one question per §3.x subsection.** The 12 subsections range from 1 row (§3.4, §3.9, §3.12) to 13 rows (§3.1) — a rigid 1:1 mapping would produce one enormous question and several trivial ones. Groups are sized for even coverage instead, splitting oversized subsections and merging undersized ones. Per this fork's recurring paraphrase-drift defect (SP3, SP4 x2, all in generated interview/prose text), grouping deliberately does not preserve the source table's row order within a group — this is decided at spec time, not left for the final review to catch, matching Part 1's approach.
- **Catalog coverage gap is documented, not hidden**, the same way `swe-catalog.yaml` documented its own pre-SP3 gap: a header comment plus a coverage doc, both stating plainly that 45 of 103 Table 1 rows are covered (Ch.3 only) until Parts 2b/2c land.

## Architecture

### Data layer

- **`data/sa-task-catalog.yaml`** — new, 45 rows for this sub-spec (grows to 103 across Parts 2a-2c). Row shape: `swe_id` (matches `swe-catalog.yaml`'s existing id, e.g. `"SWE-033"`), `section` (e.g. `"3.1.2"`). **No task text stored** — matching `swe-catalog.yaml` and `ivv-catalog.yaml`, which both store zero requirement text; this catalog is a pure id/section index. The corrected earlier draft of this spec had a `tasks` field holding paraphrased task text directly in the catalog; that would have been the first catalog in this fork to carry prose, doubling the surface area the fork's recurring paraphrase-drift defect could hide in. All paraphrased SA/safety-task content lives only in `sa-task-verification-management`'s `SKILL.md` interview prose, same as every other record skill. SWE-065's four lettered sub-items become four rows with `swe_id: "SWE-065a"` through `"SWE-065d"`, each carrying its own `section` (`"4.5.2a"` etc. — out of scope for Ch.3, noted here only so Part 2b's spec doesn't have to re-derive this from the PDF).
- **`data/SA-TASK-CATALOG-COVERAGE.md`** — new, mirrors `data/CATALOG-COVERAGE.md`'s structure: states the catalog covers 45 of 103 Table 1 rows (Ch.3 only), lists the 12 covered §3.x subsections by name, and names Ch.4/Ch.5 as the known gap pending Parts 2b/2c.
- **`docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.yaml`** — new, per-subsystem, generated by `requirements-matrix` alongside the existing `requirements-mapping-matrix.yaml`. Contains only rows present in `sa-task-catalog.yaml` at generation time, filtered to the subsystem's class using the exact same `filter_rows_for_class` logic already applied to the main catalog — so a subsystem generated before Parts 2b/2c land simply gets a Ch.3-only SA-task matrix, and re-running `requirements-matrix` later (documented as safe to do, matching the main matrix's own regeneration behavior) picks up the newly added rows. Row shape: `swe_id`, `section`, `software_class`, `status` (`"not-started"` / `"satisfied"` / `"tailored-out"`), `evidence`, `date`. No `default_approver` field — Table 1 tailoring authority is out of scope for this sub-spec (see Open Risks).

### Generation — extending `requirements-matrix`

`requirements-matrix`'s existing pattern already separates data (library functions in `filter_matrix.py` returning markdown/status-row data) from action (the `SKILL.md`-directed agent writing files to disk). The extension keeps that separation:

- New `skills/requirements-matrix/scripts/sa_task_matrix.py` with `render_sa_task_matrix_markdown(rows, subsystem, software_class)` and `render_sa_task_matrix_status_yaml(rows, software_class)` — same shapes as `filter_matrix.py`'s renderers, reusing `filter_rows_for_class` from that module rather than duplicating the class-filter logic.
- `requirements-matrix`'s `SKILL.md` gets one new step after its existing matrix generation: load `data/sa-task-catalog.yaml`, filter by the same `software_class`, call the two new render functions, write `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.md` and `.yaml`. If the filtered result is empty (e.g. a class with no Ch.3 rows applicable, or before this sub-spec's rows existed), the step is skipped and no files are written — same documented-absence behavior as `ivv-mapping-matrix.yaml`'s "not applicable" case in Part 1.

### Recording — new `sa-task-verification-management` skill

`skills/sa-task-verification-management/scripts/record_sa_task_verification.py`, signature `(matrix_yaml_path, record_md_path, swe_ids, fields, evidence)` — byte-pattern-identical in shape to the other 13 record scripts in this fork, operating on `swe_id` (this catalog's key) rather than a new namespaced id, since none was introduced.

**Precondition:** `docs/nasa-compliance/<subsystem>/sa-task-mapping-matrix.yaml` must already exist with at least one Ch.3 row for the subsystem's class (i.e., `requirements-matrix` has been run since this sub-spec's rows were added to the catalog). `SKILL.md` states this plainly; if absent or empty for Ch.3, tell the user to re-run `requirements-matrix` rather than silently treating the chapter as not-applicable.

**Interview — 14 grouped questions**, covering all 45 rows, deliberately rebalanced rather than mapped 1:1 to the table's own 12 subsections, and with the source's own item order broken within each group:

| # | Group | SWE-ids covered |
|---|---|---|
| 1 | Acquisition & plan setup | SWE-033, SWE-013, SWE-034 |
| 2 | Plan tracking & commitments | SWE-024, SWE-036, SWE-037 |
| 3 | Developer oversight & reporting | SWE-039, SWE-040, SWE-042 |
| 4 | NPR compliance & matrix maintenance | SWE-139, SWE-121, SWE-125 |
| 5 | Reuse, COTS & software reuse assurance | SWE-027, SWE-147, SWE-148 |
| 6 | Cost estimation | SWE-015, SWE-151, SWE-174 |
| 7 | Schedule oversight | SWE-016, SWE-018, SWE-046 |
| 8 | Training & classification hygiene | SWE-017, SWE-020, SWE-176 |
| 9 | SA/safety role & independence | SWE-022, SWE-141, SWE-131, SWE-178, SWE-179 |
| 10 | Safety-critical & mission-critical software | SWE-205, SWE-023, SWE-134, SWE-219, SWE-220 |
| 11 | Auto-generated code & dev practices | SWE-146, SWE-206, SWE-032 |
| 12 | Cybersecurity, part 1 | SWE-156, SWE-154, SWE-157, SWE-159 |
| 13 | Cybersecurity, part 2 | SWE-207, SWE-185, SWE-210 |
| 14 | Bi-directional traceability | SWE-052 |

Each question asks which of its group's SWE-ids have real, checkable SA/safety-task evidence (an assurance assessment, a confirmed audit finding, a review record) and where it lives — same "must be checkable, not self-attested" standard `peer-review-record` and `ivv-verification-record` established. Output: Markdown record appended to `docs/nasa-compliance/<subsystem>/sa-task-verification-management.md`, matrix rows stamped `satisfied` + evidence + date.

### Data flow

`classify-software` → `requirements-matrix` (generates both `requirements-mapping-matrix.yaml` and, new, `sa-task-mapping-matrix.yaml`) → `sa-task-verification-management` interviews per group, records evidence → stamps matrix rows `satisfied`/`tailored-out`, appends to `sa-task-verification-management.md`.

### Error handling

Same three mandated behaviors as every SP1-4 record script:

- Empty `swe_ids` → `ValueError`.
- Unknown `swe_id` (not present in the subsystem's `sa-task-mapping-matrix.yaml`) → `KeyError`.
- Attempting to mark an already-`tailored-out` row `satisfied` → `ValueError`, matrix left unmodified.

### Testing

- `tests/test_sa_task_catalog_integrity.py` (new, mirrors `test_ivv_catalog_integrity.py`'s spirit): asserts 45 rows for this sub-spec, every `swe_id` exists in `swe-catalog.yaml`, no duplicate `swe_id`s, `section` matches the expected NPR section for its `swe_id`. Written to allow extension (not replacement) when Parts 2b/2c add their rows — same growth pattern `test_catalog_integrity.py` went through across SP1-3.
- `sa_task_matrix.py`'s two render functions: tested directly as library functions (input catalog rows → output markdown string / status-row list), mirroring `test_filter_matrix.py` and Part 1's `test_ivv_matrix.py`.
- `record_sa_task_verification.py`: 5 tests — golden path, the 3 mandated error paths, append-to-existing-record. Same bar as every SP1-4 script.
- **Final whole-branch review must specifically re-check all 14 interview questions against `reference/NASA-STD-8739.8B.pdf` §4.3 Table 1's Chapter 3 rows for order-mirroring, not just verbatim-phrase matches.** This is the fork's standing top-priority review check (flagged after recurring across SP3, SP4 x2) and this sub-spec's compression (45 rows / ~100+ tasks into 14 groups) carries meaningfully more surface area than Part 1's 49-into-9.

## Open Risks

- **Tailoring authority for Table 1 rows is not designed in this sub-spec.** `swe-catalog.yaml` carries per-class tailoring authority columns for the underlying NPR requirement; whether SA-task rows inherit that same authority, need their own, or default to a single named role (as Part 1 did for §4.4.2's IPEP-based tailoring) is an open question. `sa-task-mapping-matrix.yaml` supports a `tailored-out` status per the mandated error-handling behavior, but this sub-spec does not specify who has authority to set it. Deferred to the implementation plan or a follow-up decision — not blocking, since every other SP1-4 record skill already allows `tailored-out` to be set without a matrix-enforced approver check.
- **Interview-question paraphrase risk is meaningfully higher than Part 1's**, both in raw item count and because each of the 45 rows itself contains a variable-length numbered task list (1-8 items) that must also avoid mirroring the source's own sub-enumeration order, not just the row-to-row order. Mitigation: explicit per-group instruction in the implementation plan, re-verified at final review, matching Part 1's approach.
- **Parts 2b (Ch.4, 37 rows) and 2c (Ch.5, 21 rows) are not designed.** This sub-spec's catalog/matrix/skill-per-chapter shape is expected to carry over, but each needs its own interview-grouping design (Ch.4/Ch.5's subsection row-count distribution hasn't been checked for the same lopsidedness §3.1 showed here) and its own brainstorm session — not assumed inherited wholesale.
