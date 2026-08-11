# NASA-SWE Superpowers Fork — Engineering Lifecycle (SP3) Design

**Date:** 2026-08-10
**Status:** Draft — pending user review

## Background

SP1 (Foundation) and SP2 (Software Management) are done and merged to `main`. SP3 is the third sub-project from the original decomposition (see `docs/superpowers/specs/2026-08-10-nasa-swe-foundation-design.md`): NPR 7150.2D Chapter 4, Engineering Lifecycle Requirements — the phases (requirements, architecture, design, implementation, testing, operations/maintenance/retirement) that most directly overlap with Superpowers' own existing `brainstorming` → `writing-plans` → `test-driven-development` → `code-review` pipeline.

## Scope

NPR 7150.2D Chapter 4 (§4.1-4.6), 34 Appendix C rows. §4.2-4.6 (28 rows) are already transcribed in `data/swe-catalog.yaml`; §4.1 Software Requirements (6 rows, pages 69-70) is the catalog's one remaining gap (`data/CATALOG-COVERAGE.md`).

Two parts, in order:

1. **Catalog extension** — transcribe the 6 §4.1 rows into `data/swe-catalog.yaml`, closing the catalog to 100/100 Appendix C rows.
2. **Six new skills**, one per §4.1-4.6 subsection.

### Chapter 4 subsection → skill mapping

| §  | Subsection | Skill | SWE-ids | Rows |
|---|---|---|---|---|
| 4.1 | Software Requirements | `requirements-definition` | 050, 051, 184, 053, 054, 055 | 6 |
| 4.2 | Software Architecture | `architecture-record` | 057, 143 | 2 |
| 4.3 | Software Design | `design-record` | 058 | 1 |
| 4.4 | Software Implementation | `implementation-record` | 060, 061, 135, 062, 186, 063, 136 | 7 |
| 4.5 | Software Testing | `test-record` | 065, 066, 187, 068, 070, 071, 073, 189, 190, 191, 192, 193, 211 | 13 |
| 4.6 | Software Operations, Maintenance, and Retirement | `operations-retirement` | 075, 077, 194, 195, 196 | 5 |

Unlike SP2 (7 skills across 12 subsections, 5 of which had no dedicated skill), every §4.x subsection gets a dedicated skill here. Each subsection's row count is small (1-13) and each maps directly onto a concept Superpowers' own dev-lifecycle skills already use (requirements, architecture, design, implementation, test, ops) — per-topic clarity matters more here than in SP2's less-overlapping topics (cost estimation, reuse, cybersecurity), where consolidation would blur exactly the distinctions this fork exists to make legible.

## Decisions Made This Session

- **Six thin skills, no consolidation.** Same no-coupling pattern as SP1/SP2: thin `SKILL.md` + tested deterministic script per skill, each writing its own record file and stamping its own matrix rows.
- **Standalone, not chained.** Each new skill is self-contained and invoked manually — e.g. `requirements-definition` after `brainstorming` produces a spec, `test-record` after `test-driven-development` produces test evidence. No edits to `brainstorming`, `writing-plans`, `test-driven-development`, or `code-review` — neither their text nor their control flow. This was reconsidered mid-session (see below) and reaffirmed.
- **Compliance enforcement is explicitly deferred, not designed, for SP3.** The natural enforceable signal is `requirements-mapping-matrix.yaml` having zero `not-started` rows for the declared class — a chapter-agnostic concept that already spans SP1-SP3's rows and isn't tied to which sub-project built a given row's recording skill. That signal can't be meaningfully gated yet: Ch.5 and Ch.6 (SP4-6) have no recording skills at all today, so a hook or gate enforcing full-matrix completeness would block every merge in every project using this plugin until SP6 ships. Two enforcement mechanisms were considered and rejected for SP3 on this basis:
  - A **HARD-GATE text edit** to the generic skills (pointing each at its matching Ch.4 record skill) — rejected because it adds coupling to core, upstream-inherited skill text in exchange for enforcing a signal (full-matrix completeness) that isn't real yet.
  - A **PreToolUse hook** blocking `git merge`/`git commit` on incomplete records — rejected for the same reason, and because this plugin has no precedent for any hook beyond its existing `SessionStart` bootstrap hook; building one now would be scoped to a signal that doesn't yet mean anything.
  Revisit once SP4-6 give the matrix real cross-chapter coverage, or if a deliberately *scoped* (e.g. Ch.4-only) completeness check is separately designed and its scoping problem (how a merge declares which chapters it touches) is solved on its own terms.
- **§4.1's catalog gap is closed as SP3's first task, not deferred.** Same reasoning as SP2's own catalog-extension-first decision: `requirements-definition` cannot cite real evidence against six missing rows.

## Architecture

### Catalog extension

- Extract §4.1 (Appendix C pages 69-70) with `pdftotext -bbox-layout`, same method and x-coordinate binning as SP2's Chapter 3 extension.
- Append 6 rows to `data/swe-catalog.yaml`, same schema as the existing 94 rows.
- Update `tests/test_catalog_integrity.py`'s row-count assertion (94 → 100).
- Update `data/CATALOG-COVERAGE.md` to show full Appendix C coverage (Chapter 2 remains permanently excluded per NPR §1.3.1, already documented).

### Shared skill pattern (all six skills)

1. Read `docs/nasa-compliance/<subsystem>/classification.yaml` for `software_class`. Hard stop with a clear message if it doesn't exist — class must be established first (existing SP1/SP2 convention).
2. Filter the topic's catalog rows to those applicable to that class (`classes.<X>: true`).
3. Cross-check `requirements-mapping-matrix.yaml`; skip rows already `tailored-out` rather than re-asking the user to re-decide an excluded row.
4. Interview the user per applicable row, citing `NPR 7150.2D §<section>, SWE-<id>` only — never verbatim requirement text.
5. Write the decision and evidence reference to `docs/nasa-compliance/<subsystem>/<topic>.yaml`.
6. Stamp `satisfied`/`not-started` status onto the matching `requirements-mapping-matrix.yaml` rows, carrying forward SP2's guard: never silently flip a `tailored-out` row back to `satisfied`.

`test-record`'s 13 rows follow the same straight per-row interview as the other five skills — no special-casing. SP2's `traceability` skill already proved a larger per-row table works fine in this shape.

### Skill-specific notes

- **`requirements-definition`** (§4.1) — records how requirements are defined, analyzed, and baselined (SWE-050/051/184/053/054/055). Depends on the catalog extension landing first.
- **`architecture-record`** (§4.2) — records the architecture description and its basis (SWE-057/143).
- **`design-record`** (§4.3) — records the design description and its basis (SWE-058). Single-row skill; kept separate from `architecture-record` per the earlier per-subsection decision.
- **`implementation-record`** (§4.4) — records implementation standards/practices in use and evidence of adherence (SWE-060/061/135/062/186/063/136).
- **`test-record`** (§4.5) — records test planning, execution, and reporting evidence (SWE-065/066/187/068/070/071/073/189/190/191/192/193/211).
- **`operations-retirement`** (§4.6) — records operations, maintenance, and retirement planning and evidence (SWE-075/077/194/195/196).

None of the six perform the underlying engineering work (no architecture authored, no tests run) — same posture as every SP1/SP2 "record" skill: record the decision, cite the evidence, do not do the engineering for the user.

### Data flow

`classification.yaml` (SP1, possibly amended by SP2's `safety-critical-determination`) → each SP3 skill reads it, writes its own record under `docs/nasa-compliance/<subsystem>/`, updates the matching `requirements-mapping-matrix.yaml` rows (same `status`/evidence/date convention as SP1/SP2) → feeds SP4-SP6.

### Error handling

- Unknown SWE-id referenced → hard error, matching SP1/SP2.
- Missing `classification.yaml` → hard stop, matching SP1/SP2.
- Any of the six scripts attempting to flip a `tailored-out` row back to `satisfied` → guarded, matching SP2's fix-wave convention.

### Testing

- Catalog: `pdftotext -bbox-layout` spot-check against re-read source pages (same method as SP1/SP2's re-verification), plus the updated `test_catalog_integrity.py` assertion.
- Each skill: golden-path plus edge-case tests (tailored-out guard, missing `classification.yaml`, unknown swe_id) — same bar as SP2's 90 passing.
- Final whole-branch review checks the diff against **both** this spec and the implementation plan, not just the plan — per the project memory from SP2's `reuse-assessment` spec-vs-plan drift finding.

## Open Risks

- Same transcription-error risk as SP1/SP2's catalog population for §4.1 — mitigated by the bbox-layout method plus spot-check, not eliminated.
- Compliance enforcement remains undesigned by choice (see Decisions above). This is a deliberate scope boundary, not an oversight — do not silently reopen it inside SP3; it needs its own brainstorm once SP4-6 exist or a scoped-completeness concept is worked out on its own terms.
