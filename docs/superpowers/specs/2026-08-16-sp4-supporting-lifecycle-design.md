# NASA-SWE Superpowers Fork — Supporting Lifecycle (SP4) Design

**Date:** 2026-08-16
**Status:** Draft — pending user review

## Background

SP1 (Foundation), SP2 (Software Management), and SP3 (Engineering Lifecycle) are done and merged to `main`. SP4 is the fourth sub-project from the original decomposition (see `docs/superpowers/specs/2026-08-10-nasa-swe-foundation-design.md`): NPR 7150.2D Chapter 5, Supporting Lifecycle Requirements — configuration management, risk management, peer reviews/inspections, measurements, and non-conformance management.

## Scope

NPR 7150.2D Chapter 5 (§5.1-5.5), 21 Appendix C rows — all already transcribed in `data/swe-catalog.yaml` as part of SP3's catalog-completion pass. **No catalog work in SP4**: the catalog is already 100/100 Appendix C rows, and Chapter 5 was fully covered before this sub-project started.

Five new skills, one per §5.1-5.5 subsection:

### Chapter 5 subsection → skill mapping

| §  | Subsection | Skill | SWE-ids | Rows |
|---|---|---|---|---|
| 5.1 | Software Configuration Management | `config-management` | 079, 080, 081, 082, 083, 084, 085, 045 | 8 |
| 5.2 | Software Risk Management | `risk-management` | 086 | 1 |
| 5.3 | Software Peer Reviews/Inspections | `peer-review-record` | 087, 088, 089 | 3 |
| 5.4 | Software Measurements | `measurements` | 090, 093, 094, 199, 200 | 5 |
| 5.5 | Software Non-conformance or Defect Management | `non-conformance-record` | 201, 202, 203, 204 | 4 |

Same 1:1 subsection-to-skill mapping SP3 used, for the same reason: each subsection is a distinct, nameable concept (configuration management, risk, peer review, measurement, non-conformance) and per-topic clarity matters more here than consolidation would help.

## Decisions Made This Session

- **Five thin skills, no consolidation.** Same no-coupling pattern as SP1-3: thin `SKILL.md` + tested deterministic script per skill, each writing its own record file and stamping its own matrix rows.
- **`peer-review-record` (§5.3) is record-only against existing Superpowers review skills — never duplicated.** This repo already ships `requesting-code-review`/`receiving-code-review` as core Superpowers skills. `peer-review-record` attests that a peer review/inspection happened via one of those (or an equivalent external review process) and cites concrete evidence (a PR URL, a review transcript reference) — it does not reimplement review, and no edits are made to `requesting-code-review` or `receiving-code-review`'s text or control flow. Mirrors SP3's decision to layer new skills onto Superpowers' existing dev-lifecycle skills rather than duplicate them.
- **`measurements` (§5.4) and `non-conformance-record` (§5.5) record mechanism only, not an appendable log of individual measurements or defects.** Both topics are naturally repeating — measurements get taken and non-conformances get logged throughout a project's life, unlike the single point-in-time decisions SP1-3's skills record (one classification, one cost basis, one traceability mechanism). Deliberately kept single-record-shaped anyway: each records *what* metrics/tracking mechanism is in use and *where* it lives, not a running log of values or defect entries. Keeps every skill in the fork the same shape; an appendable-log skill would be a new precedent this session chose not to introduce.
- **Compliance enforcement remains deferred, reaffirmed rather than re-examined.** Same reasoning as SP3: the natural enforceable signal (`requirements-mapping-matrix.yaml` having zero `not-started` rows for the declared class) still isn't chapter-complete until SP5-6 exist. Explicitly considered re-examining a Chapter-5-scoped completeness check for SP4 and chose not to — carrying the deferral forward unchanged rather than reopening it piecemeal per sub-project.
- **Class-applicability tables are written into each skill's `SKILL.md` from the start**, not added retroactively. SP3's final-review fix wave had to add this after the fact to all six of its skills; SP4's plan builds it in from each skill's first draft, pulled directly from the catalog rows in the mapping table above.

## Architecture

### Shared skill pattern (all five skills)

1. Read `docs/nasa-compliance/<subsystem>/classification.yaml` for `software_class`. Hard stop with a clear message if it doesn't exist (existing SP1-3 convention).
2. Filter the topic's catalog rows to those applicable to that class (`classes.<X>: true`).
3. Cross-check `requirements-mapping-matrix.yaml`; skip rows already `tailored-out` rather than re-asking the user to re-decide an excluded row.
4. Interview the user per applicable row, citing `NPR 7150.2D §<section>, SWE-<id>` only — never verbatim requirement text.
5. Write the decision and evidence reference to `docs/nasa-compliance/<subsystem>/<topic>.yaml`.
6. Stamp `satisfied`/`not-started` status onto the matching `requirements-mapping-matrix.yaml` rows, carrying forward SP2's guard: never silently flip a `tailored-out` row back to `satisfied`.

### Skill-specific notes

- **`config-management`** (§5.1, 8 rows) — records the CM plan reference, baseline-identification approach, change-control mechanism, and version-control tool/location. Interview should ask which VCS/branching convention is in use; this repo's own `using-git-worktrees`/`finishing-a-development-branch` skills are a valid *answer* a user could cite as evidence, but `config-management` doesn't call them or depend on them — it only records what mechanism is in place.
- **`risk-management`** (§5.2, 1 row) — records the risk management plan reference and process. Single-row skill, same precedent as SP3's `design-record`.
- **`peer-review-record`** (§5.3, 3 rows) — records that a peer review/inspection occurred, citing concrete evidence (PR URL, review transcript reference from `requesting-code-review`/`receiving-code-review`, or an equivalent external process). The interview must reject a vague "we reviewed it" answer — evidence has to be something a human auditor could actually go check.
- **`measurements`** (§5.4, 5 rows) — records what software measures/metrics are collected and where they're maintained. Mechanism only, per the decision above — no log of actual metric values.
- **`non-conformance-record`** (§5.5, 4 rows) — records the non-conformance/defect tracking mechanism and where it lives. Mechanism only, per the decision above — no log of individual non-conformances.

None of the five perform the underlying engineering work (no CM tooling built, no risk analysis run, no review conducted, no metrics collected, no defects triaged) — same posture as every SP1-3 "record" skill: record the decision, cite the evidence, do not do the engineering for the user.

### Data flow

`classification.yaml` (SP1, possibly amended by SP2's `safety-critical-determination`) → each SP4 skill reads it, writes its own record under `docs/nasa-compliance/<subsystem>/`, updates the matching `requirements-mapping-matrix.yaml` rows (same `status`/evidence/date convention as SP1-3) → feeds SP5-SP6.

### Error handling

- Unknown SWE-id referenced → hard error, matching SP1-3.
- Missing `classification.yaml` → hard stop, matching SP1-3.
- Any of the five scripts attempting to flip a `tailored-out` row back to `satisfied` → guarded, matching SP2's fix-wave convention.

### Testing

- No catalog changes, so no `test_catalog_integrity.py` changes — it already asserts 100/100 rows.
- Each skill: golden-path plus edge-case tests (tailored-out guard, missing `classification.yaml`, unknown swe_id) — same bar as SP2/SP3's coverage growth.
- Final whole-branch review checks the diff against **both** this spec and the implementation plan (per the project memory from SP2's `reuse-assessment` spec-vs-plan drift finding), **and** diffs all five `SKILL.md` interview question sets word-for-word against the actual NPR 7150.2D §5.1-5.5 source text (per SP3's verbatim-phrasing finding), **and** confirms each skill's class-applicability table is present in the plan's first draft rather than added in a follow-up fix wave (per SP3's retroactive-fix finding).

## Open Risks

- **`peer-review-record`'s evidence requirement isn't script-verifiable.** A deterministic script can check that an `evidence` field is non-empty, but it cannot verify a cited PR URL or transcript reference is real or actually shows a review. Mitigation is procedural, not technical: the interview instructs the user to supply something a human auditor could check, same as every other "evidence" field in this fork — this is a documented limitation of the whole recording pattern, not new to this skill.
- Compliance enforcement remains undesigned by choice (see Decisions above). This is a deliberate scope boundary, not an oversight — do not silently reopen it inside SP4; it needs its own brainstorm once SP5-6 exist or a scoped-completeness concept is worked out on its own terms.
