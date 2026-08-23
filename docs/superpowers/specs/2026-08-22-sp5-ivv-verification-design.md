# NASA-SWE Superpowers Fork — SP5 Part 1: IV&V Verification Requirements Design

**Date:** 2026-08-22
**Status:** Approved

## Background

SP1 (Foundation), SP2 (Software Management), SP3 (Engineering Lifecycle), and SP4 (Supporting Lifecycle) are done and merged to `main`. SP5 is the fifth sub-project from the original decomposition (`docs/superpowers/specs/2026-08-10-nasa-swe-foundation-design.md`), scoped there only as a one-line placeholder: "Software Assurance & Safety — STD-8739.8B: hazard analysis (Appendix A), IV&V gating."

That placeholder undersold the standard's actual size. Reading `reference/NASA-STD-8739.8B.pdf` directly (it was already present in `reference/` but untouched by SP1-4) shows it contains three separable, substantial bodies of content:

1. **§4.3 Table 1** (pp. 21-51, the bulk of the document) — a per-existing-SWE-id checklist of "Software Assurance and Software Safety Tasks." Roughly 90 rows, each keyed to a `swe-catalog.yaml` row already in this repo, each with its own multi-item task list.
2. **§4.4.2** (pp. 52-60) — 49 flat, standalone "the IV&V provider shall verify/validate/ensure/track that..." requirements (4.4.2.1-4.4.2.49), with their own numbering, entirely independent of SWE-ids. This is the "IV&V gating" half of the original scope note.
3. **Appendix A** (pp. 62-70) — hazard-analysis guidance: a taxonomy of software-caused hazard categories (Table 2) plus qualitative process guidance, referencing a handful of existing SWE-ids (SWE-184, SWE-62, SWE-65, SWE-68). This is the "hazard analysis" half of the original scope note.

Each is large enough to be its own spec. This document covers **only** body 2 — §4.4.2's 49 IV&V verification requirements. Bodies 1 and 3 are deliberately out of scope here and will get their own future specs; no design decision in this document applies to them.

Before scoping this spec, the two existing SP2 skills that touch adjacent territory were checked for overlap:

- `safety-critical-determination` already implements NASA-STD-8739.8B §4.2's 5-criteria safety-critical test (SWE-205), recording *that* a determination was made against a hazard analysis — it does not perform IV&V verification.
- `sa-ivv-coordination` already records SA/safety/IV&V role assignment and the §3.6.2/SWE-141 IV&V-applicability question — it does not record the 49 detailed IV&V verification duties themselves.

Neither skill needs to change in scope; `sa-ivv-coordination` gets one small extension (see Architecture) because it's the one place that already asks the applicability question this spec's matrix generation depends on.

## Scope

NASA-STD-8739.8B §4.4.2, 49 requirements (4.4.2.1-4.4.2.49). No existing catalog overlap — verified against all 100 `swe-catalog.yaml` rows and both `safety-critical-determination` and `sa-ivv-coordination`.

One new skill, `ivv-verification-record`, plus a small extension to the existing `sa-ivv-coordination` skill. No changes to `swe-catalog.yaml` or `requirements-mapping-matrix.yaml` — this spec introduces new, parallel files instead, because class-based filtering is the wrong model for this content: §4.4.2 applicability is a single project-level boolean (already captured by `sa-ivv-coordination`'s SWE-141 question), not a per-class table like Appendix C.

## Decisions Made This Session

- **Record-only, no gating/enforcement logic.** Every SP1-4 record skill only records evidence; none blocks or enforces anything (compliance enforcement was deliberately deferred at SP3's brainstorm — see that spec). "IV&V gating" in the original scope note means *tracking* IV&V verification status per requirement, not literal enforcement. This spec follows the same posture.
- **New parallel catalog + matrix, not folded into the existing SWE catalog/matrix.** The 49 requirements have no per-class applicability columns and are tailored per-project via a negotiated IV&V Project Execution Plan (IPEP, §4.4.2.2) rather than by software class. Stretching the existing class-based model to fit that would be a worse fit than a small new parallel structure.
- **`sa-ivv-coordination` generates the new matrix, rather than a new standalone matrix-generation skill.** It already asks the IV&V-applicability question (§3.6.2/SWE-141) that gates whether this matrix should exist at all — one place asks the question and acts on the answer, instead of splitting that logic across two skills.
- **One skill, `ivv-verification-record`, with 9 grouped interview questions — not split into several smaller phase-based skills.** NASA-STD-8739.8B's §4.4.2 has no formal subsections; all 49 requirements sit under one undivided heading. Inventing skill-level subsection boundaries would break the SP1-4 convention of one skill per document section rather than extend it. The 9 groups below follow the requirements' own natural artifact-phase progression (planning → oversight → tracking → concept → requirements → design → code → test → maintenance), which is the order the standard itself already presents them in — no structure invented that isn't already implicit in the source.
- **IDs namespaced `IVV-4.4.2.<n>`.** Keeps the standard's own numbering (traceable straight back to the PDF) while avoiding any visual or lookup collision with `SWE-<n>` ids already used elsewhere in the same subsystem's compliance docs.
- **Tailoring authority fixed to the Project SMA Technical Authority for every row.** §4.4.2.3 assigns IPEP review/concurrence to the "Project SMA Technical Authority (TA)." The standard's own tailoring model is more nuanced in principle (which products are subject to which analyses, negotiated per-IPEP) but this fork's `tailoring-request` pattern already assumes one named authority per tailored-out row — this spec reuses that existing shape rather than inventing a richer one. See Open Risks.

## Architecture

### Data layer

- **`data/ivv-catalog.yaml`** — new, 49 rows, one per §4.4.2 requirement. Row shape: `id` (`"IVV-4.4.2.<n>"`), `section` (`"4.4.2.<n>"`). No requirement text stored — same convention as `swe-catalog.yaml`: the catalog cites by id/section only, and each skill writes its own paraphrase in its `SKILL.md`.
- **`docs/nasa-compliance/<subsystem>/ivv-mapping-matrix.yaml`** — new, per-subsystem, generated only when `sa-ivv-coordination` records IV&V as applicable. All 49 rows, unfiltered (no class logic applies). Row shape mirrors `requirements-mapping-matrix.yaml`'s status-row convention minus the class-specific fields: `ivv_id`, `section`, `status` (`"not-started"` / `"satisfied"` / `"tailored-out"`), `evidence`, `date`. No `software_class` or `default_approver` fields — there is nothing class-driven to carry.

### Generation — extending `sa-ivv-coordination`

When the existing interview's §3.6.2/SWE-141 question ("is this subsystem in a category that requires IV&V?") is answered yes, `sa-ivv-coordination`'s script also writes `ivv-mapping-matrix.yaml` from `data/ivv-catalog.yaml`: all 49 rows, `status: "not-started"`, `evidence: null`, `date: null` — the same shape `render_matrix_status_yaml` already produces for the main matrix, just without a class filter (there is none to apply). When the question is answered no, no file is written; `ivv-verification-record`'s precondition (file must exist) makes that the documented, intentional failure mode for a subsystem where IV&V doesn't apply — matching how an absent matrix row already behaves everywhere else in this fork.

### Recording — new `ivv-verification-record` skill

`skills/ivv-verification-record/scripts/record_ivv_verification.py`, signature `(matrix_yaml_path, record_md_path, ivv_ids, fields, evidence)` — byte-pattern-identical in shape to the other 12 record scripts in the fork (`design-record`'s script is the direct precedent), operating on `ivv_id` instead of `swe_id`.

**Precondition:** `docs/nasa-compliance/<subsystem>/ivv-mapping-matrix.yaml` must already exist (i.e., `sa-ivv-coordination` has recorded IV&V as applicable for this subsystem). `SKILL.md` states this plainly and tells the user to check `sa-ivv-coordination`'s determination first if the file is absent.

**Interview — 9 grouped questions**, each covering the IDs listed, each paraphrased at both the vocabulary *and* structural level (no group may walk its requirements in the standard's own numeric order, per the fork's recurring defect — see Testing):

| # | Group | IDs covered |
|---|---|---|
| 1 | Planning & IPEP | 4.4.2.1-3 |
| 2 | Reporting & review participation | 4.4.2.4-8 |
| 3 | Tracking & risk management | 4.4.2.9-15 |
| 4 | Concept, reuse & architecture basis | 4.4.2.16-21 |
| 5 | Requirements verification | 4.4.2.22-26 |
| 6 | Design verification | 4.4.2.27-30 |
| 7 | Code & security verification | 4.4.2.31-39 |
| 8 | Test verification | 4.4.2.40-47 |
| 9 | Maintenance & audit participation | 4.4.2.48-49 |

Each question asks which of its group's IDs have real, checkable evidence (an IV&V analysis artifact, a report reference, a tracked finding) and where that evidence lives — same "must be checkable, not self-attested" standard `peer-review-record` (SP4) established. Output: Markdown record appended to `docs/nasa-compliance/<subsystem>/ivv-verification-record.md`, matrix rows stamped `satisfied` + evidence + date, following the exact SP1-4 pattern.

### Data flow

`sa-ivv-coordination` (SWE-141 = applicable) → generates `ivv-mapping-matrix.yaml` → `ivv-verification-record` interviews per group, records evidence → stamps matrix rows `satisfied`/`tailored-out`, appends to `ivv-verification-record.md`.

### Error handling

Same three mandated behaviors as every SP1-4 record script, applied to the new `ivv_id` namespace:

- Empty `ivv_ids` → `ValueError`.
- Unknown `ivv_id` → `KeyError`.
- Attempting to mark an already-`tailored-out` row `satisfied` → `ValueError`, matrix left unmodified.

### Testing

- `test_ivv_catalog_integrity.py` (new, mirrors `test_catalog_integrity.py`'s spirit, scoped to the new file): asserts 49 rows, ids `IVV-4.4.2.1` through `IVV-4.4.2.49`, no duplicates, sections match ids.
- `record_ivv_verification.py`: 5 tests — golden path, the 3 mandated error paths, append-to-existing-record. Same bar as every SP1-4 script.
- `sa-ivv-coordination` extension: test that answering IV&V-applicable = yes generates the 49-row matrix with `status: not-started`; answering no does not write the file; re-running with yes again regenerates cleanly (matches the existing main-matrix regeneration behavior).
- **Final whole-branch review must specifically re-check the 9 interview questions against the §4.4.2 source text for order-mirroring, not just verbatim-phrase matches.** This is the highest-surface-area interview yet for the fork's single most recurring defect (verbatim/list-order phrasing drift from NPR/NASA-STD source text) — 49 source items funneled into 9 questions is more compression, and more risk of accidentally reproducing the standard's own ordering, than any prior sub-project's interviews. SP4's final review caught exactly this failure mode in a task that had shipped without independent review; this spec calls it out at the plan level up front instead of relying on review alone to catch it.

## Open Risks

- **Interview-question paraphrase risk is higher here than in any prior sub-project**, precisely because of the 49-into-9 compression noted above. Mitigation: explicit task-level instruction in the implementation plan (not just a general reminder) to avoid list-order mirroring for each of the 9 groups, re-verified at final review.
- **Tailoring authority is coarser than the source standard's own model.** §4.4.2.2's IPEP negotiates which products are subject to which analyses at a granularity finer than "tailored-out per row" — this spec's fixed single-authority-per-row model (Project SMA TA) is simpler than that. If this proves too coarse in practice (e.g., a subsystem needs partial tailoring within a single requirement), it will need its own follow-up design; not attempted here.
- **§4.3 Table 1 (SA task catalog, ~90 rows) and Appendix A (hazard analysis guidance) are separate, not-yet-started future specs.** No design decision in this document constrains either. In particular, Table 1's per-SWE-id task lists may eventually want to reference `ivv-mapping-matrix.yaml` rows (IV&V verification often mirrors an SA task for the same underlying requirement) — that linkage, if wanted, is a decision for Table 1's own spec, not retrofitted here.
