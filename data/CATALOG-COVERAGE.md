# SWE Catalog Coverage

**`data/swe-catalog.yaml` covers all 100 rows in NPR 7150.2D Appendix C.**

The 100-row figure is the count of `Section` + `SWE #` pairs in the Appendix C
table (`reference/NPR_7150.2D.pdf`, pages 56-78), extracted programmatically
rather than counted by eye — see "Verifying coverage" below to reproduce it.

## Covered — Appendix C pages 56-78, 100 rows

- 3.1 Software Life Cycle Planning
- 3.2 Software Cost Estimation
- 3.3 Software Schedules
- 3.4 Software Training
- 3.5 Software Classification Assessments
- 3.6 Software Assurance and Software Independent Verification & Validation
- 3.7 Safety-Critical Software
- 3.8 Automatic Generation of Software Source Code
- 3.9 Software Development Processes and Practices
- 3.10 Software Reuse
- 3.11 Software Cybersecurity
- 3.12 Software Bi-Directional Traceability
- 4.1 Software Requirements
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

Chapter 2 (Roles/Responsibilities) is excluded permanently, not pending:
NPR 7150.2D §1.3.1 states Chapter 2's requirements are not part of the
Requirements Mapping Matrix. It is not counted in the 100.

## §3.2.1/SWE-015: a real null Class F Authority, not a bug

§3.2.1 carries a Class F mark (`classes.F: true`) with a blank Class F
Authority cell in the source standard itself (`class_f_authority: null`).
`skills/requirements-matrix/scripts/validate_catalog.py` deliberately does not
reject this combination — only the converse (an authority with no F mark) is
an error. `skills/tailoring-request/SKILL.md` tells the user plainly when a
row's `default_approver` is `null` rather than presenting `null` as a name.

## Class E: no longer an empty-catalog gap

Earlier revisions of this file noted that Class E returned zero rows because
all 12 of Appendix C's Class E marks sat in the then-untranscribed Chapter 3.
Chapter 3 is now transcribed, so Class E returns its real 12 rows. §4.1
(SP3) contributes none of its own.

## Verifying coverage

The row count and every row's class marks are checked against the PDF with
`pdftotext -bbox-layout`, which reports each cell's x-coordinate. Appendix C's
columns sit at fixed offsets on every page:

```
 47 Section | 95 SWE # | 131 Requirement Text | 310 Class A-E Authority
 | 373 A | 390 B | 407 C | 424 D | 441 E | 467 Class F Authority | 530 F
```

Reading those columns by eye is what produced the original mismapping of the
Class F Authority and Class F applicability columns during SP1. Use the coordinates.

## Extending coverage

Coverage is complete — there is no remaining gap to extend. If NPR 7150.2D is
ever revised, repeat this method: extract the changed page range with
`pdftotext -bbox-layout`, assign each cell to a column by x-coordinate (never
visually), append/update rows in Appendix C order, then run
`tests/test_catalog_integrity.py` and update its expected counts.
