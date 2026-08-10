# SWE Catalog Coverage

**`data/swe-catalog.yaml` covers 49 of the 100 rows in NPR 7150.2D Appendix C.**

The 100-row figure is the count of `Section` + `SWE #` pairs in the Appendix C
table (`reference/NPR_7150.2D.pdf`, pages 56-78), extracted programmatically
rather than counted by eye — see "Verifying coverage" below to reproduce it.

## Covered — Appendix C pages 70-78, 49 rows

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

## Not covered — 51 rows

Tracked here, not silently missing.

| Missing | Rows | Appendix C pages |
|---|---|---|
| Chapter 3, Software Management Requirements (§3.1-3.12) | 45 | 56-69 |
| **§4.1, Software Requirements — all of it** | 6 | 69-70 |

§4.1 is missing in full, not merely truncated at its start. The absent rows are
§4.1.2/SWE-050, §4.1.3/SWE-051, §4.1.4/SWE-184, §4.1.5/SWE-053, §4.1.6/SWE-054,
and §4.1.7/SWE-055. Any subsystem tracking requirements-definition compliance
has **no** rows for it in the generated matrix today.

Chapter 2 (Roles/Responsibilities) is excluded permanently, not pending:
NPR 7150.2D §1.3.1 states Chapter 2's requirements are not part of the
Requirements Mapping Matrix. It is not counted in the 100.

## Class E: an empty matrix here means "not yet transcribed"

A subsystem classified **Class E** gets an empty Requirements Mapping Matrix
from this catalog. **That is a gap in this catalog, not a statement about the
standard.** Appendix C marks Class E on exactly 12 rows, and every one of them
sits in Chapter 3 — §3.1.2, §3.1.3, §3.1.10, §3.1.11, §3.1.12, §3.1.13, §3.5.1,
§3.5.2, §3.6.1, §3.7.1, §3.10.2, and §3.11.2 — which this catalog does not yet
cover. (§4.1 carries no Class E marks, so filling that gap alone will not
populate a Class E matrix; Chapter 3 is what is required.)

A user classifying as Class E must be told their empty matrix reflects this
known coverage gap. It is not an authoritative "no requirements apply," and it
must never be presented as one.

Classes A, B, C, D, and F all return rows from the current slice.

## Verifying coverage

The row count and every row's class marks are checked against the PDF with
`pdftotext -bbox-layout`, which reports each cell's x-coordinate. Appendix C's
columns sit at fixed offsets on every page:

```
 47 Section | 95 SWE # | 131 Requirement Text | 310 Class A-E Authority
 | 373 A | 390 B | 407 C | 424 D | 441 E | 467 Class F Authority | 530 F
```

Reading those columns by eye is what produced the original mismapping of the
Class F Authority and Class F applicability columns. Use the coordinates.

## Extending coverage

1. Extract the missing page range with `pdftotext -bbox-layout` and assign each
   cell to a column by x-coordinate — do not transcribe visually.
2. Append the rows to `swe-catalog.yaml` in Appendix C order.
3. Run `tests/test_catalog_integrity.py`, which calls `validate_catalog` on the
   real file. Update its expected row count and its Class E assertion.
4. Update this file.

See `docs/superpowers/plans/2026-08-10-nasa-swe-foundation.md` for how the layer
was built and `docs/superpowers/specs/2026-08-10-nasa-swe-foundation-design.md`
for the design rationale. Note that the plan's Task 6 describes the original
visual transcription method and the original catalog schema; both have been
superseded by the procedure above.
