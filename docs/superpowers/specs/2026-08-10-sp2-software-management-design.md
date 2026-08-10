# NASA-SWE Superpowers Fork — Software Management (SP2) Design

**Date:** 2026-08-10
**Status:** Draft — pending user review

## Background

SP1 (Foundation) shipped `classify-software`, `requirements-matrix`, and `tailoring-request`, backed by a catalog covering 49 of Appendix C's 100 rows (NPR 7150.2D §4.2-5.5). SP2 is the second sub-project from the original decomposition (see `docs/superpowers/specs/2026-08-10-nasa-swe-foundation-design.md`): NPR 7150.2D Chapter 3, Software Management Requirements.

## Scope

NPR 7150.2D Chapter 3 (§3.1-3.12), 45 Appendix C rows, **all currently untranscribed** (`data/CATALOG-COVERAGE.md`). Chapter 2 is not in scope — NPR §1.3.1 permanently excludes it from the Requirements Mapping Matrix (already documented, not a new decision).

Two parts, in order:

1. **Catalog extension** — transcribe all 45 Chapter 3 rows into `data/swe-catalog.yaml`.
2. **Seven new skills**, one per Chapter 3 subsection with real branching decision criteria.

### Chapter 3 subsection → skill mapping

| §  | Subsection | Skill |
|---|---|---|
| 3.1 | Software Life Cycle Planning | `lifecycle-planning` |
| 3.2 | Software Cost Estimation | `cost-estimation` |
| 3.3 | Software Schedules | *(no dedicated skill — see below)* |
| 3.4 | Software Training | *(no dedicated skill)* |
| 3.5 | Software Classification Assessments | *(no dedicated skill)* |
| 3.6 | Software Assurance and Software IV&V | `sa-ivv-coordination` |
| 3.7 | Safety-Critical Software | `safety-critical-determination` |
| 3.8 | Automatic Generation of Software Source Code | *(no dedicated skill)* |
| 3.9 | Software Development Processes and Practices | *(no dedicated skill)* |
| 3.10 | Software Reuse | `reuse-assessment` |
| 3.11 | Software Cybersecurity | `cybersecurity-assessment` |
| 3.12 | Software Bi-Directional Traceability | `traceability` |

The five subsections without a dedicated skill still get their Appendix C rows transcribed in the catalog extension (matrix completeness doesn't depend on which subsections have bespoke skills). They're satisfied or tailored through SP1's existing `requirements-matrix` / `tailoring-request` machinery — no new tooling needed for them.

## Decisions Made This Session

- **Catalog extension is part of SP2, not deferred.** SP2 cannot emit a real matrix for its own topics against an empty Chapter 3 slice — same posture SP1 already flagged as a known gap for Class E. Extension happens first, skills are built against real data, not stubs.
- **Seven thin skills, not one consolidated skill or a shared generic skill.** Matches SP1's proven pattern (`classify-software`, `requirements-matrix`, `tailoring-request`): thin `SKILL.md` + tested deterministic script, no coupling between skills. Rejected a single consolidated "software-management-plan" skill (monolith, harder to test/maintain, contradicts SP1's own no-coupling design note) and a two-tier shared-generic-skill approach (a generic record-skill can't ask topic-specific probing questions matching each subsection's actual NASA criteria — undermines the "real compliance tooling" goal).
- **Every SP2 skill records a decision and cites evidence; none performs the underlying engineering work.** No cost-model math in `cost-estimation`, no RMF execution in `cybersecurity-assessment`. NPR doesn't mandate a specific methodology for either, and fabricating one would be worse than not having the skill. Matches `tailoring-request`'s existing philosophy of recording rationale, not doing the engineering for the user.
- **`safety-critical-determination` amends `classification.yaml` rather than writing a separate record.** SP1's `classify-software` already carries a lightweight safety-critical flag that auto-bumps Class E to D. NPR §3.7 / STD-8739.8B define the fuller determination process. Keeping one authoritative record (this skill updates the existing flag and re-applies the auto-bump rule if it changes) avoids the two files disagreeing about the same subsystem's safety-critical status.
- **Catalog extension uses the `pdftotext -bbox-layout` word-coordinate method, not visual reading** — per `CATALOG-COVERAGE.md`'s extension procedure, written specifically because visual reading caused SP1's Class-F authority/applicability mislabeling.

## Architecture

### Catalog extension

- Extract §3.1-3.12 (Appendix C pages 56-69, per `CATALOG-COVERAGE.md`) with `pdftotext -bbox-layout`, bin cells by the documented x-coordinates.
- Append 45 rows to `data/swe-catalog.yaml` in Appendix C order, same schema as the existing 49 rows (`section`, `swe_id`, `class_ae_authority`, `classes`, `class_f_authority`).
- Update `tests/test_catalog_integrity.py`'s row-count assertion (49 → 94) and Class E assertion (Chapter 3 carries all 12 of Appendix C's Class E marks — the matrix should stop being empty for Class E once this lands).
- Update `data/CATALOG-COVERAGE.md` to reflect the new coverage and the remaining gap (§4.1, 6 rows).

### Skill 1 — `safety-critical-determination`

- Interview walks §3.7 and STD-8739.8B's safety-critical criteria (command/control functions, hazard potential, human/mission/asset risk).
- Reads the subsystem's `classification.yaml`. If the determination is safety-critical and the existing record isn't (or vice versa), **amends `classification.yaml`** — updates the safety-critical flag, re-applies SP1's Class-E→D auto-bump rule, records rationale and date for the change.
- Conflict rule: if `classification.yaml`'s safety-critical flag already carries a rationale (i.e. it was explicitly set by a prior `classify-software` or `safety-critical-determination` run, not left at its unset default) and disagrees with this run's determination, surface the conflict to the user rather than silently overwriting. If the existing flag has no rationale (still at default), amend it directly. Same posture as SP1's ambiguous-classification handling.
- Output: amended `docs/nasa-compliance/<subsystem>/classification.yaml`, plus rationale appended (not overwritten) so the history of the determination is preserved.

### Skill 2 — `lifecycle-planning`

- Records, per §3.1: acquisition-vs-development decision (§3.1.2), pointer to the software plans required (§3.1.3, including security), milestones (§3.1.7), acceptance criteria (§3.1.5).
- Cites existing project artifacts (plan documents, milestone lists) rather than generating them.
- Output: `docs/nasa-compliance/<subsystem>/lifecycle-planning.md`.

### Skill 3 — `cost-estimation`

- Records methodology name, basis of estimate, and the size/effort parameters §3.2.3 requires reporting to NASA.
- Does not compute an estimate. If no estimate exists yet, the skill says so rather than inventing one.
- Output: `docs/nasa-compliance/<subsystem>/cost-estimation.md`.

### Skill 4 — `sa-ivv-coordination`

- Records SA, software safety, and IV&V roles assigned to the subsystem and the plan reference required by §3.6.1.
- Output: `docs/nasa-compliance/<subsystem>/sa-ivv-coordination.md`.

### Skill 5 — `reuse-assessment`

- Walks §3.1.14's COTS/GOTS/MOTS/reused-software suitability conditions, one assessment per reused component.
- Output: `docs/nasa-compliance/<subsystem>/reuse-assessment.md` (appends one entry per component).

### Skill 6 — `cybersecurity-assessment`

- Records the software's cybersecurity risk categorization and control basis (§3.11), citing the project's existing ATO/RMF artifact.
- Does not perform RMF categorization itself.
- Output: `docs/nasa-compliance/<subsystem>/cybersecurity-assessment.md`.

### Skill 7 — `traceability`

- Records the requirements-to-design/code/test linkage mechanism in use (§3.12) and where it lives.
- Output: `docs/nasa-compliance/<subsystem>/traceability.md`.

### Data flow

`classification.yaml` (SP1; possibly amended by `safety-critical-determination`) → each SP2 skill reads it, writes its own record under `docs/nasa-compliance/<subsystem>/`, updates `requirements-mapping-matrix.yaml` rows it satisfies (same convention `tailoring-request` uses: `status`, evidence pointer, date) → feeds SP3-SP6.

### Error handling

- Unknown SWE-id referenced → hard error, matching SP1.
- `safety-critical-determination` conflicting with an existing rationale-backed flag → surfaced to user, not silently overwritten.
- `cost-estimation` / `cybersecurity-assessment` with no underlying estimate/RMF artifact to cite → skill records "not yet available," does not fabricate a value.

### Testing

- Catalog: `pdftotext -bbox-layout` spot-check against a sample of re-read source pages (same method as SP1's re-verification), plus updated `test_catalog_integrity.py` assertions.
- Each skill: Python tests using the NPR's own documented criteria/examples as test cases, same pattern as `classify-software`'s Appendix D test cases.
- `safety-critical-determination`'s `classification.yaml` amend path: test that the Class-E→D auto-bump re-fires correctly and that rationale is appended, not overwritten.

## Open Risks

- Same transcription-error risk as SP1's original catalog population — mitigated by the bbox-layout method plus spot-check, not eliminated. Treat the extended catalog as a working draft.
- `safety-critical-determination` amending SP1's `classification.yaml` introduces a second skill that can mutate a file the first skill owns — the amend path needs careful test coverage so SP1's existing classify-software behavior doesn't regress.
