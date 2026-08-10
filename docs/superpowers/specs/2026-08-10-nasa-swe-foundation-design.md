# NASA-SWE Superpowers Fork — Foundation (SP1) Design

**Date:** 2026-08-10
**Status:** Draft — pending user review

## Background

Goal: fork [obra/superpowers](https://github.com/obra/superpowers) and implement two NASA software standards as enforced Claude Code skills, producing real compliance-grade deliverables:

- **NPR 7150.2D** — NASA Software Engineering Requirements (numbered SWE-xxx requirements, Chapters 2-6, Appendix C Requirements Mapping Matrix, Appendix D software classifications A-F)
- **NASA-STD-8739.8B** — Software Assurance and Software Safety Standard (safety-critical determination, hazard analysis, IV&V, tailoring)

## Scope Decomposition

Too large for one spec. Split into independent sub-projects, each with its own spec → plan → build cycle:

| # | Sub-project | Covers |
|---|---|---|
| SP1 | **Foundation** (this spec) | Software classification, Requirements Mapping Matrix, tailoring/relief tracking |
| SP2 | Software Management | NPR Ch. 2-3: lifecycle planning, cost estimation, SA/IV&V coordination, safety-critical trigger, reuse, cybersecurity, traceability |
| SP3 | Engineering Lifecycle | NPR Ch. 4: requirements→architecture→design→implementation→test→ops, layered onto Superpowers' existing brainstorming→writing-plans→TDD→code-review pipeline |
| SP4 | Supporting Lifecycle | NPR Ch. 5: config management, risk management, peer review/inspections, measurements, non-conformance |
| SP5 | Software Assurance & Safety | STD-8739.8B: hazard analysis (Appendix A), IV&V gating |
| SP6 | Documentation Generation | NPR Ch. 6 recommended doc content + full compliance artifact export |

SP1 is the dependency root — no other sub-project's skills can know which SWE-xxx requirements apply, or where to record compliance status, without a declared class and a live matrix.

## Decisions Already Made

- **Fork purpose:** real compliance tooling — generate actual NASA-format deliverables (Requirements Mapping Matrix, tailoring docs, SWE-xxx citations), not just borrowed process discipline.
- **Rigor level:** configurable per project — skills declare a software class (A-F) at project/subsystem start and gate which practices are mandatory, matching NASA's own tailoring model.
- **Fork mechanism:** literal `gh repo fork obra/superpowers`, kept mergeable with upstream.
- **Fork location:** `/home/adam/scratch-claude/superpowers-nasa-swe`.
- **Catalog storage:** the Requirements Mapping Matrix stores SWE-id / NPR section / class-applicability / responsible role / TA only — no verbatim requirement text embedded. Full wording stays in NPR 7150.2D itself, cited by SWE# (matches how real NASA compliance documents cite it).

## SP1 Architecture

### Fork & plugin identity

- `gh repo fork obra/superpowers --clone` into the path above.
- Rename plugin identity in `.claude-plugin/plugin.json`: `name: "superpowers-nasa-swe"` — avoids collision if upstream `superpowers` is ever installed alongside this fork. Skills invoke as `superpowers-nasa-swe:<skill-name>`.
- New skills live under `skills/`, flat directories with `SKILL.md` frontmatter (`name`, `description`), matching upstream convention exactly.

### Skill 1 — `classify-software`

- Interview walks NPR Appendix D's decision tree: the five classification factors (usage within a system, criticality to major programs, extent of human dependency, developmental/operational complexity, extent of Agency investment) against each class's actual definition, examples, and exclusions (e.g., Class A's four human-spaceflight criteria; Class E's explicit "cannot be safety-critical — if safety-critical, must be Class D or higher").
- Supports multiple named subsystems per project, each with its own class — both standards explicitly anticipate a project containing systems/subsystems of different classes.
- Ambiguous case (Appendix D.2): assign the higher class, but surface the ambiguity to the user rather than silently deciding.
- Output: `docs/nasa-compliance/<subsystem>/classification.yaml` — the five factor answers, chosen class, rationale, date.

### Skill 2 — `requirements-matrix`

- Backed by a bundled master catalog (`data/swe-catalog.yaml`, populated during implementation — see Data Population below): every SWE-xxx id, NPR section, class-applicability (A-F marks), responsible role, TA. Schema only, no requirement prose.
- Reads a subsystem's `classification.yaml`, filters the catalog to that class, emits:
  - `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.md` — human-readable table, same shape as NPR Appendix C.
  - `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` — machine-readable status per row (`not-started` / `in-progress` / `satisfied` / `tailored-out`, evidence pointer, date), which SP2-SP6 skills update as work proceeds.

### Skill 3 — `tailoring-request`

- Implements both standards' tailoring/request-for-relief principles (NPR Ch. 2, STD-8739.8B §4.5). For any RMM row not fully implemented: prompts for rationale, risk, mitigation, approving authority (defaults to the row's mapped TA role from the catalog).
- Writes to `docs/nasa-compliance/<subsystem>/tailoring-log.md`; flips the corresponding RMM row to `tailored-out`.

### Data flow

`classify-software` → `classification.yaml` → `requirements-matrix` (filter + instantiate) → `tailoring-request` (amend status) → feeds SP2-SP6.

### Data population (implementation-time, not brainstorming)

The master catalog needs the ~200+ SWE-xxx rows from NPR 7150.2D's full Appendix C (pages spanning Ch. 2-6 mappings) plus STD-8739.8B's Table 1 (SA/safety task per SWE-xxx). Implementation plan will dispatch parallel extraction agents over PDF page ranges, each returning structured rows; results merged and spot-checked by re-reading a sample of source pages against generated rows.

### Error handling

- Ambiguous classification → surfaced to user, not auto-resolved silently (per above).
- Missing/unknown SWE-id referenced by a later sub-project → hard error, not silently skipped (data integrity of the compliance record depends on it).
- Tailoring without a named approving authority → blocked; skill requires a role or name before writing the log entry.

### Testing / validation

- Catalog extraction correctness: spot-check generated rows against a sample of re-read source pages.
- Classification skill logic: run each class's documented examples and exclusions from Appendix D as test cases — confirm the interview lands them in the expected class.
- RMM filtering: confirm a declared class shows exactly the rows marked with an "X" for that class in the source catalog.

## Open Risks

- Full SWE-xxx catalog transcription is a large, mechanical, error-prone task — mitigated by parallel extraction + spot-check, but not proof against transcription error. Treat the generated catalog as a working draft to be corrected as discrepancies surface, not a certified reproduction of the NPR.
- This tooling produces NASA-*format* artifacts; it does not make a project NASA-*compliant* in the contractual sense (no actual NASA TA reviews these deliverables). Users should not represent output as an approved NASA deliverable.
